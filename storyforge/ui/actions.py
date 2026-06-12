"""
storyforge.ui.actions
~~~~~~~~~~~~~~~~~~~~~
User-action handlers — send message, toggle, and generation worker thread.
"""

from __future__ import annotations

import threading

import dearpygui.dearpygui as dpg

from storyforge.ui import state
from storyforge.ui.chat import push_message, push_status, render_chat, update_toggle_label
from storyforge.ui.sidebar import refresh_sidebar

# ── backend imports (graceful fallback) ───────────────────────────────────────

try:
    from storyforge.core.generators import classify_intent
    from storyforge.core.rag import generate_next_chapter, ask_story_question
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False


# ── toggle ────────────────────────────────────────────────────────────────────

def on_toggle(sender, app_data, user_data=None) -> None:
    state.interactive = bool(app_data)
    update_toggle_label()
    _sync_input_state()


def _sync_input_state() -> None:
    enabled = state.interactive and bool(state.active_novel)
    dpg.configure_item("chat_input",  enabled=enabled)
    dpg.configure_item("send_button", enabled=enabled)


# ── send ──────────────────────────────────────────────────────────────────────

def send_message(sender=None, app_data=None, user_data=None) -> None:
    if state.busy:
        push_status("Please wait — generation in progress …")
        return

    if not state.active_novel:
        push_status("Select or create a novel first.")
        return

    text = dpg.get_value("chat_input").strip()
    if not text:
        return

    dpg.set_value("chat_input", "")
    push_message("user", text)

    manager = state.manager
    if not HAS_BACKEND or manager is None:
        push_message("assistant", f"[Demo mode] You said: {text}")
        return

    assert manager is not None
    if not state.interactive:
        push_status("Switch to Interactive mode to generate content.")
        return

    push_status("Thinking …")
    state.busy = True

    def _worker() -> None:
        try:
            intent = classify_intent(text)
            bible  = manager.get_story_bible()
            nid    = state.active_novel
            assert nid is not None, "No active novel selected."

            if intent == "QUESTION" or state.active_scope == "novel":
                answer = ask_story_question(nid, text, bible)
                push_message("assistant", answer)
                push_status("Done.")

            else:
                ch_num = manager.update_chapter()
                pkg    = generate_next_chapter(nid, text, ch_num, bible)

                manager.save_chapter_to_disk(
                    ch_num, pkg["chapter"], pkg["summary"]
                )

                for c in pkg.get("characters", []):
                    if isinstance(c, dict) and c.get("name"):
                        manager.add_character(c["name"])
                if pkg.get("lore"):
                    manager.apply_lore_extraction(pkg["lore"])

                push_message("assistant", pkg["chapter"])
                push_message("assistant", "─── Summary ───\n" + pkg["summary"])

                # ensure this chapter appears in history
                key = f"{nid}_ch{ch_num}"
                state.chat_history.setdefault(key, [])

                refresh_sidebar()
                push_status(f"Chapter {ch_num} generated.")

        except Exception as exc:
            push_message("assistant", f"⚠ Error: {exc}")
            push_status(f"Error: {exc}")
        finally:
            state.busy = False

    threading.Thread(target=_worker, daemon=True).start()
