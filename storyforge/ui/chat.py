"""
storyforge.ui.chat
~~~~~~~~~~~~~~~~~~
Chat message rendering and input bar.
"""

from __future__ import annotations

from datetime import datetime

import dearpygui.dearpygui as dpg

from storyforge.ui import state
from storyforge.ui.theme import (
    TEXT, TEXT_DIM, AMBER, BUBBLE_USER, BUBBLE_AI,
    amber_button_theme, bubble_theme,
)

# ── layout constants (kept in sync with app.py) ───────────────────────────────

WIN_W     = 1280
SIDEBAR_W = 280


# ── public API ────────────────────────────────────────────────────────────────

def render_chat() -> None:
    """Rebuild the entire chat scroll area from state.chat_history."""
    dpg.delete_item("chat_scroll_area", children_only=True)
    messages = state.get_chat()

    if not messages:
        _render_empty_hint()
        return

    avail      = WIN_W - SIDEBAR_W - 40
    bubble_max = int(avail * 0.72)

    for msg in messages:
        _render_message(msg, avail, bubble_max)

    # scroll to bottom
    dpg.set_y_scroll(
        "chat_scroll_area",
        dpg.get_y_scroll_max("chat_scroll_area") + 99999,
    )


def push_message(role: str, text: str) -> None:
    ts = datetime.now().strftime("%H:%M")
    state.get_chat().append({"role": role, "text": text, "time": ts})
    render_chat()


def push_status(msg: str) -> None:
    dpg.set_value("status_bar", msg)


def update_chat_header() -> None:
    novels = state.novels_on_disk()
    nmap   = {n["novel_id"]: n for n in novels}

    if state.active_novel and state.active_novel in nmap:
        nov = nmap[state.active_novel]
        if state.active_scope == "chapter" and state.active_chap:
            label = f"{nov['title']}  ›  Chapter {state.active_chap}"
        else:
            label = nov["title"]
    else:
        label = "StoryForge"

    dpg.set_value("header_title", label)


def update_toggle_label() -> None:
    from storyforge.ui.theme import STATUS_OK, STATUS_OFF
    if state.interactive:
        dpg.set_value("toggle_label", "● Interactive")
        dpg.configure_item("toggle_label", color=STATUS_OK)
    else:
        dpg.set_value("toggle_label", "○ Read-only")
        dpg.configure_item("toggle_label", color=STATUS_OFF)


# ── private helpers ───────────────────────────────────────────────────────────

def _render_empty_hint() -> None:
    dpg.add_spacer(height=60, parent="chat_scroll_area")
    dpg.add_text(
        "No messages yet.",
        color=TEXT_DIM,
        parent="chat_scroll_area",
    )
    if state.active_novel:
        dpg.add_text(
            "Type an instruction below to continue the story,\nor ask a question about it.",
            color=TEXT_DIM,
            parent="chat_scroll_area",
        )
    else:
        dpg.add_text(
            "Select a novel in the sidebar, or create a new one.",
            color=TEXT_DIM,
            parent="chat_scroll_area",
        )


def _render_message(msg: dict, avail: int, bubble_max: int) -> None:
    role    = msg["role"]
    text    = msg["text"]
    ts      = msg.get("time", "")
    is_user = role == "user"

    with dpg.group(parent="chat_scroll_area", horizontal=False):

        # label + timestamp row
        with dpg.group(horizontal=True):
            if is_user:
                dpg.add_spacer(width=avail - 80)
            label_color = AMBER if is_user else TEXT_DIM
            dpg.add_text("You" if is_user else "StoryForge", color=label_color)
            dpg.add_text(f"  {ts}", color=TEXT_DIM)

        # bubble
        with dpg.group(horizontal=True):
            if is_user:
                dpg.add_spacer(width=avail - bubble_max - 8)

            bg = BUBBLE_USER if is_user else BUBBLE_AI
            bw = dpg.add_child_window(
                width=bubble_max,
                autosize_y=True,
                border=False,
                no_scrollbar=True,
                parent="chat_scroll_area",
            )
            dpg.bind_item_theme(bw, bubble_theme(bg))
            dpg.add_text(text, wrap=bubble_max - 24, color=TEXT, parent=bw)

        dpg.add_spacer(height=6, parent="chat_scroll_area")
