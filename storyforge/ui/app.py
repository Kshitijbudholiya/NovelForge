"""
storyforge.ui.app
~~~~~~~~~~~~~~~~~
DearPyGui window construction and main event loop.
Entry point: storyforge.ui.app.run()
"""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from storyforge.ui import state
from storyforge.ui.theme import (
    apply_global_theme,
    amber_button_theme,
    panel_child_theme,
    AMBER, TEXT, TEXT_DIM, BG, PANEL, PANEL2, BORDER,
)
from storyforge.ui.chat import render_chat, update_chat_header, update_toggle_label, push_status
from storyforge.ui.sidebar import refresh_sidebar
from storyforge.ui.modals import build_new_novel_modal, open_new_novel_modal
from storyforge.ui.actions import on_toggle, send_message

# ── layout constants ──────────────────────────────────────────────────────────

WIN_W     = 1280
WIN_H     = 800
SIDEBAR_W = 280
TOPBAR_H  = 48
STATUSBAR_H = 28


# ── public entry point ────────────────────────────────────────────────────────

def run() -> None:
    """Initialise backend, build UI, start the render loop."""

    # ── backend bootstrap ─────────────────────────────────────────────────────
    try:
        from storyforge.core.novel_manager import NovelManager
        state.manager = NovelManager()
    except ImportError:
        state.manager = None

    # ── DPG setup ─────────────────────────────────────────────────────────────
    dpg.create_context()
    dpg.create_viewport(
        title="StoryForge — AI Novel Writer",
        width=WIN_W,
        height=WIN_H,
        resizable=False,
    )
    dpg.setup_dearpygui()

    apply_global_theme()

    amber_btn_t = amber_button_theme()

    # ── primary window ────────────────────────────────────────────────────────
    with dpg.window(
        tag="main_win",
        label="StoryForge",
        width=WIN_W,
        height=WIN_H,
        no_title_bar=True,
        no_resize=True,
        no_move=True,
        no_scrollbar=True,
    ):

        # ── top bar ───────────────────────────────────────────────────────────
        with dpg.child_window(
            tag="topbar",
            height=TOPBAR_H,
            no_scrollbar=True,
            border=False,
        ):
            dpg.bind_item_theme("topbar", panel_child_theme(PANEL))

            with dpg.group(horizontal=True):
                dpg.add_spacer(width=10)
                dpg.add_text("◆", color=AMBER)
                dpg.add_spacer(width=4)
                dpg.add_text("StoryForge", color=AMBER)
                dpg.add_spacer(width=16)
                dpg.add_text("", tag="header_title", color=TEXT)

                # right-aligned controls
                spacer_w = WIN_W - 390
                dpg.add_spacer(width=spacer_w)

                nb = dpg.add_button(
                    label="+ New Novel",
                    width=110,
                    callback=open_new_novel_modal,
                )
                dpg.bind_item_theme(nb, amber_btn_t)

                dpg.add_spacer(width=16)
                dpg.add_text("", tag="toggle_label", color=(60, 160, 90, 255))
                dpg.add_spacer(width=6)
                dpg.add_checkbox(
                    tag="toggle_cb",
                    default_value=True,
                    callback=on_toggle,
                )
                dpg.add_spacer(width=10)

        # ── body row ──────────────────────────────────────────────────────────
        body_h = WIN_H - TOPBAR_H - STATUSBAR_H

        with dpg.group(horizontal=True):

            # ── sidebar ───────────────────────────────────────────────────────
            with dpg.child_window(
                tag="sidebar",
                width=SIDEBAR_W,
                height=body_h,
                border=False,
            ):
                dpg.bind_item_theme("sidebar", panel_child_theme(PANEL))

                dpg.add_spacer(height=8)
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=10)
                    dpg.add_text("YOUR NOVELS", color=AMBER)
                dpg.add_separator()
                dpg.add_spacer(height=4)

                # scrollable novel list
                with dpg.child_window(
                    tag="sidebar_novel_list",
                    height=-1,
                    border=False,
                ):
                    dpg.bind_item_theme(
                        "sidebar_novel_list", panel_child_theme(PANEL)
                    )

            # ── chat area ─────────────────────────────────────────────────────
            with dpg.child_window(
                tag="chat_area",
                width=WIN_W - SIDEBAR_W,
                height=body_h,
                border=False,
            ):
                dpg.bind_item_theme("chat_area", panel_child_theme(BG))

                # message scroll area
                input_row_h = 58
                scroll_h    = body_h - input_row_h - 12

                with dpg.child_window(
                    tag="chat_scroll_area",
                    width=-1,
                    height=scroll_h,
                    border=False,
                ):
                    _theme = panel_child_theme(BG)
                    with dpg.theme() as _pad_t:
                        with dpg.theme_component(dpg.mvChildWindow):
                            dpg.add_theme_color(
                                dpg.mvThemeCol_ChildBg, BG,
                                category=dpg.mvThemeCat_Core,
                            )
                            dpg.add_theme_style(
                                dpg.mvStyleVar_WindowPadding, 12, 10,
                                category=dpg.mvThemeCat_Core,
                            )
                    dpg.bind_item_theme("chat_scroll_area", _pad_t)

                dpg.add_separator()

                # input row
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=8)
                    dpg.add_input_text(
                        tag="chat_input",
                        hint="Write an instruction or ask a question …",
                        width=WIN_W - SIDEBAR_W - 120,
                        height=36,
                        on_enter=True,
                        callback=send_message,
                        enabled=True,
                    )
                    dpg.add_spacer(width=6)
                    sb = dpg.add_button(
                        tag="send_button",
                        label="Send  ▶",
                        width=90,
                        height=36,
                        callback=send_message,
                    )
                    dpg.bind_item_theme(sb, amber_btn_t)
                    dpg.add_spacer(width=8)

        # ── status bar ────────────────────────────────────────────────────────
        with dpg.child_window(
            tag="statusbar",
            height=STATUSBAR_H,
            no_scrollbar=True,
            border=False,
        ):
            dpg.bind_item_theme("statusbar", panel_child_theme(PANEL))
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=10)
                dpg.add_text("Ready.", tag="status_bar", color=TEXT_DIM)

    # ── modals ────────────────────────────────────────────────────────────────
    build_new_novel_modal(WIN_W, WIN_H)

    # ── initial state ─────────────────────────────────────────────────────────
    update_toggle_label()
    refresh_sidebar()
    render_chat()

    # ── render loop ───────────────────────────────────────────────────────────
    dpg.set_primary_window("main_win", True)
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
