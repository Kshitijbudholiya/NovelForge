"""
storyforge.ui.theme
~~~~~~~~~~~~~~~~~~~
Colour palette and DearPyGui theme builders.

Palette: amber-on-navy "candlelight manuscript" — warm writing-tool energy
without feeling like a generic dark mode.
"""

import dearpygui.dearpygui as dpg

# ── palette ───────────────────────────────────────────────────────────────────

BG           = (15,  17,  23,  255)   # #0F1117  deep navy background
PANEL        = (26,  29,  46,  255)   # #1A1D2E  sidebar / topbar panels
PANEL2       = (34,  38,  58,  255)   # #22263A  secondary panel / modal bg
BORDER       = (52,  58,  82,  255)   # #343A52  dividers, frame outlines
AMBER        = (201, 168,  76,  255)  # #C9A84C  primary accent (amber gold)
AMBER_DIM    = (140, 115,  50,  255)  # muted amber for hover / active
TEXT         = (232, 226, 208, 255)   # #E8E2D0  warm off-white body text
TEXT_DIM     = (140, 135, 120, 255)   # muted text for labels, timestamps
BUBBLE_USER  = (42,  52,  80,  255)   # right-side user message bubble
BUBBLE_AI    = (30,  35,  50,  255)   # left-side AI message bubble
STATUS_OK    = (60,  160,  90,  255)  # green for interactive indicator
STATUS_OFF   = (160,  60,  60,  255)  # red for read-only indicator


# ── global theme ──────────────────────────────────────────────────────────────

def apply_global_theme() -> None:
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvAll):
            _c = dpg.mvThemeCat_Core
            _s = dpg.mvStyleVar_FrameRounding

            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,             BG,        category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg,              PANEL,     category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg,              PANEL2,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_Border,               BORDER,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg,              PANEL2,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered,       PANEL2,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive,        BORDER,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg,              PANEL,     category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,        PANEL2,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg,            PANEL,     category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg,          BG,        category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab,        BORDER,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, AMBER_DIM, category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark,            AMBER,     category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_Button,               PANEL2,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,        BORDER,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,         AMBER_DIM, category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_Header,               PANEL2,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered,        BORDER,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive,         AMBER_DIM, category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_Separator,            BORDER,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_Text,                 TEXT,      category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled,         TEXT_DIM,  category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_Tab,                  PANEL,     category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered,           BORDER,    category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive,            AMBER_DIM, category=_c)

            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding,    0,      category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,     4,      category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding,     4,      category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding,      4,      category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding,     4,      category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding,  4,     category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,       8, 6, category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_IndentSpacing,     16,     category=_c)

    dpg.bind_theme(t)


# ── per-widget themes ─────────────────────────────────────────────────────────

def amber_button_theme() -> int:
    """Solid amber primary action button."""
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvButton):
            _c = dpg.mvThemeCat_Core
            dpg.add_theme_color(dpg.mvThemeCol_Button,        AMBER,     category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, AMBER_DIM, category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,  AMBER_DIM, category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_Text,          BG,        category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4,         category=_c)
    return t


def ghost_button_theme() -> int:
    """Transparent ghost button for sidebar navigation."""
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvButton):
            _c = dpg.mvThemeCat_Core
            dpg.add_theme_color(dpg.mvThemeCol_Button,        (0, 0, 0, 0), category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, PANEL2,       category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,  BORDER,       category=_c)
            dpg.add_theme_color(dpg.mvThemeCol_Text,          TEXT_DIM,     category=_c)
    return t


def panel_child_theme(bg: tuple = PANEL) -> int:
    """Child-window background override."""
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg,
                                category=dpg.mvThemeCat_Core)
    return t


def bubble_theme(bg: tuple) -> int:
    """Chat bubble child-window theme."""
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvChildWindow):
            _c = dpg.mvThemeCat_Core
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg,   bg,     category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding,  6,  category=_c)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 8, category=_c)
    return t
