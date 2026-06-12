"""
storyforge.ui.modals
~~~~~~~~~~~~~~~~~~~~
Modal dialogs — currently: New Novel creation form.
"""

from __future__ import annotations

import threading
import uuid
import json
from datetime import datetime
from pathlib import Path

import dearpygui.dearpygui as dpg

from storyforge.ui import state
from storyforge.ui.theme import AMBER, amber_button_theme, ghost_button_theme
from storyforge.ui.chat import push_message, push_status, render_chat
from storyforge.ui.sidebar import refresh_sidebar, _select_chapter

NOVELS_DIR = Path("novels")

# ── backend imports (graceful fallback) ───────────────────────────────────────

try:
    from storyforge.core.generators import (
        create_first_chapter,
        compress_memory,
        extract_characters,
        extract_lore,
    )
    from storyforge.core.rag import save_first_chapter

    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False


# ── modal builder (called once during UI construction) ───────────────────────


def build_new_novel_modal(win_w: int, win_h: int) -> None:
    amber_btn_t = amber_button_theme()
    ghost_btn_t = ghost_button_theme()

    with dpg.window(
        tag="modal_new_novel",
        label="New Novel",
        modal=True,
        show=False,
        width=500,
        height=340,
        pos=[win_w // 2 - 250, win_h // 2 - 170],
        no_resize=True,
    ):
        dpg.add_spacer(height=8)

        dpg.add_text("Title", color=AMBER)
        dpg.add_input_text(tag="inp_title", width=-1, hint="e.g. The Iron Tide")

        dpg.add_spacer(height=6)
        dpg.add_text("Genre", color=AMBER)
        dpg.add_input_text(
            tag="inp_genre", width=-1, hint="e.g. Fantasy, Sci-Fi, Slice of life"
        )

        dpg.add_spacer(height=6)
        dpg.add_text("Premise", color=AMBER)
        dpg.add_input_text(
            tag="inp_premise",
            width=-1,
            height=90,
            multiline=True,
            hint="Describe your story concept …",
        )

        dpg.add_spacer(height=14)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=1)
            cb = dpg.add_button(
                label="Cancel", width=100, callback=close_new_novel_modal
            )
            dpg.bind_item_theme(cb, ghost_btn_t)
            dpg.add_spacer(width=8)
            ok = dpg.add_button(
                label="Generate  ◆", width=150, callback=submit_new_novel
            )
            dpg.bind_item_theme(ok, amber_btn_t)


# ── open / close ──────────────────────────────────────────────────────────────


def open_new_novel_modal() -> None:
    dpg.configure_item("modal_new_novel", show=True)


def close_new_novel_modal() -> None:
    dpg.configure_item("modal_new_novel", show=False)
    dpg.set_value("inp_title", "")
    dpg.set_value("inp_genre", "")
    dpg.set_value("inp_premise", "")


# ── submit ────────────────────────────────────────────────────────────────────


def submit_new_novel() -> None:
    title = dpg.get_value("inp_title").strip()
    genre = dpg.get_value("inp_genre").strip()
    premise = dpg.get_value("inp_premise").strip()

    if not title or not premise:
        push_status("Title and premise are required.")
        return

    close_new_novel_modal()

    if HAS_BACKEND and state.manager is not None:
        push_status("Generating Chapter 1 …")

        def _worker() -> None:
            state.busy = True
            manager = state.manager
            assert manager is not None
            try:
                nid = manager.create_novel(title, genre, premise)
                chapter = create_first_chapter(premise)
                summary = compress_memory(chapter)
                chars = extract_characters(chapter)
                lore = extract_lore(chapter)

                save_first_chapter(nid, chapter, summary, chars, lore)
                manager.save_chapter_to_disk(1, chapter, summary)

                for c in chars:
                    if isinstance(c, dict) and c.get("name"):
                        manager.add_character(c["name"])
                if lore:
                    manager.apply_lore_extraction(lore)

                # seed chapter chat history
                ts = datetime.now().strftime("%H:%M")
                key = f"{nid}_ch1"
                state.chat_history[key] = [
                    {"role": "assistant", "text": chapter, "time": ts},
                    {
                        "role": "assistant",
                        "text": "─── Summary ───\n" + summary,
                        "time": ts,
                    },
                ]

                refresh_sidebar()
                _select_chapter(nid, 1)
                push_status("Chapter 1 complete.")
            except Exception as exc:
                push_status(f"Error: {exc}")
            finally:
                state.busy = False

        threading.Thread(target=_worker, daemon=True).start()

    else:
        # demo / no-backend path
        nid = _demo_create(title, genre, premise)
        refresh_sidebar()
        # select the novel-level scope since no chapter was generated
        state.active_novel = nid
        state.active_scope = "novel"
        state.active_chap = None
        from storyforge.ui.chat import update_chat_header

        update_chat_header()
        render_chat()
        push_status(f"'{title}' created (demo mode — backend not available).")


# ── demo helper ───────────────────────────────────────────────────────────────


def _demo_create(title: str, genre: str, premise: str) -> str:
    nid = str(uuid.uuid4())
    meta = {
        "novel_id": nid,
        "title": title,
        "genre": genre,
        "premise": premise,
        "current_chapter": 1,
        "characters": [],
        "locations": [],
        "factions": [],
        "lore_topics": [],
        "created": True,
    }
    NOVELS_DIR.mkdir(exist_ok=True)
    (NOVELS_DIR / f"{nid}.json").write_text(
        json.dumps(meta, indent=4), encoding="utf-8"
    )
    return nid
