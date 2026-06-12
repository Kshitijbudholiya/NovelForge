"""
storyforge.ui.sidebar
~~~~~~~~~~~~~~~~~~~~~
Collapsible novel/chapter sidebar tree.
"""

from __future__ import annotations

from pathlib import Path

import dearpygui.dearpygui as dpg

from storyforge.ui import state
from storyforge.ui.theme import AMBER, TEXT_DIM, ghost_button_theme
from storyforge.ui.chat import render_chat, update_chat_header

NOVELS_DIR = Path("novels")


# ── public API ────────────────────────────────────────────────────────────────

def refresh_sidebar() -> None:
    """Rebuild the full sidebar novel list from disk."""
    dpg.delete_item("sidebar_novel_list", children_only=True)
    state.sidebar_nodes.clear()

    novels = state.novels_on_disk()
    if not novels:
        dpg.add_text(
            "No novels yet.\nClick '+ New Novel' to begin.",
            color=TEXT_DIM,
            parent="sidebar_novel_list",
        )
        return

    gt = ghost_button_theme()

    for nov in novels:
        nid     = nov.get("novel_id", "")
        title   = nov.get("title", "Untitled")
        genre   = nov.get("genre", "")

        with dpg.tree_node(
            label=f"  {title}",
            parent="sidebar_novel_list",
            default_open=False,
            tag=f"tn_{nid}",
        ) as tn:
            state.sidebar_nodes[nid] = {"tree_node": tn, "chapters": {}}

            # novel-level conversation button
            btn = dpg.add_button(
                label=f"  ◈  {genre or 'Novel'} chat",
                width=-1,
                callback=lambda s, a, u: _select_novel(u),
                user_data=nid,
            )
            dpg.bind_item_theme(btn, gt)
            dpg.add_separator()

            # chapter buttons
            chap_files = state.chapter_files(nid)
            if chap_files:
                dpg.add_text("  Chapters", color=TEXT_DIM)
                for cf in chap_files:
                    try:
                        cnum = int(cf.stem.split("_")[1])
                    except (IndexError, ValueError):
                        continue
                    cb = dpg.add_button(
                        label=f"    Chapter {cnum}",
                        width=-1,
                        callback=lambda s, a, u: _select_chapter(u[0], u[1]),
                        user_data=(nid, cnum),
                    )
                    dpg.bind_item_theme(cb, gt)
                    state.sidebar_nodes[nid]["chapters"][cnum] = cb
            else:
                dpg.add_text("  No chapters yet.", color=TEXT_DIM)

        dpg.add_spacer(height=4, parent="sidebar_novel_list")


# ── private selection handlers ────────────────────────────────────────────────

def _select_novel(nid: str) -> None:
    state.active_novel = nid
    state.active_scope = "novel"
    state.active_chap  = None

    if state.manager:
        try:
            state.manager.load_novel(nid)
        except Exception:
            pass

    update_chat_header()
    render_chat()


def _select_chapter(nid: str, cnum: int) -> None:
    state.active_novel = nid
    state.active_scope = "chapter"
    state.active_chap  = cnum

    if state.manager:
        try:
            state.manager.load_novel(nid)
        except Exception:
            pass

    # pre-load saved chapter text into history on first open
    key = f"{nid}_ch{cnum}"
    if key not in state.chat_history:
        ch_path = NOVELS_DIR / nid / f"chapter_{cnum:03d}.txt"
        sm_path = NOVELS_DIR / nid / f"summary_{cnum:03d}.txt"
        msgs: list[dict] = []
        if ch_path.exists():
            msgs.append({
                "role": "assistant",
                "text": ch_path.read_text("utf-8"),
                "time": "saved",
            })
        if sm_path.exists():
            msgs.append({
                "role": "assistant",
                "text": "─── Summary ───\n" + sm_path.read_text("utf-8"),
                "time": "saved",
            })
        if msgs:
            state.chat_history[key] = msgs

    update_chat_header()
    render_chat()
