C_BG = "#0C0E14"
C_PANEL = "#161928"
C_PANEL2 = "#1E2234"
C_PANEL3 = "#262A40"
C_BORDER = "#343A56"
C_BORDER2 = "#424A6A"
C_AMBER = "#D4AE4E"
C_AMBER_DIM = "#9A7E38"
C_AMBER_DARK = "#6B5726"
C_TEXT = "#DDD8C0"
C_TEXT_BRIGHT = "#F0ECD8"
C_TEXT_DIM = "#888070"
C_TEXT_MUTED = "#5A5648"
C_BUBBLE_USER = "#26324E"
C_BUBBLE_AI = "#181E2E"
C_SUCCESS = "#4EA866"
C_WARNING = "#C8A040"
C_ERROR = "#B84040"
C_ACCENT_BLUE = "#3A5080"
C_SCROLLBAR = "#2A2E44"
C_SCROLLBAR_H = "#9A7E38"

STYLESHEET = f"""
* {{
    background-color: transparent;
    color: {C_TEXT};
    font-family: "Segoe UI", "Inter", "SF Pro Display", Arial, sans-serif;
    font-size: 13px;
    selection-background-color: {C_AMBER_DARK};
    selection-color: {C_TEXT_BRIGHT};
    border: none;
    outline: none;
    box-sizing: border-box;
}}

QMainWindow,
QMainWindow > QWidget {{
    background-color: {C_BG};
}}

#topbar {{
    background-color: {C_PANEL};
    border-bottom: 1px solid {C_BORDER};
    min-height: 52px;
    max-height: 52px;
}}

#app_logo {{
    color: {C_AMBER};
    font-size: 20px;
    font-weight: bold;
}}

#app_title {{
    color: {C_AMBER};
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QPushButton {{
    background-color: {C_PANEL2};
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 5px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {C_PANEL3};
    border-color: {C_BORDER2};
    color: {C_TEXT_BRIGHT};
}}
QPushButton:pressed  {{ background-color: {C_BORDER}; }}
QPushButton:disabled {{
    color: {C_TEXT_MUTED};
    border-color: {C_BORDER};
    background-color: {C_PANEL};
}}

#btn_primary {{
    background-color: {C_AMBER};
    color: {C_BG};
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
    font-size: 13px;
    font-weight: 700;
}}
#btn_primary:hover    {{ background-color: {C_AMBER_DIM}; color: {C_BG}; }}
#btn_primary:pressed  {{ background-color: {C_AMBER_DARK}; color: {C_BG}; }}
#btn_primary:disabled {{ background-color: {C_AMBER_DARK}; color: {C_TEXT_MUTED}; }}

#btn_ghost {{
    background-color: transparent;
    color: {C_TEXT_DIM};
    border: 1px solid {C_BORDER};
    border-radius: 5px;
    padding: 6px 14px;
}}
#btn_ghost:hover {{
    background-color: {C_PANEL2};
    color: {C_TEXT};
    border-color: {C_BORDER2};
}}

#btn_send {{
    background-color: {C_AMBER};
    color: {C_BG};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 14px;
    font-weight: 700;
    min-width: 80px;
}}
#btn_send:hover    {{ background-color: {C_AMBER_DIM};  color: {C_BG}; }}
#btn_send:pressed  {{ background-color: {C_AMBER_DARK}; color: {C_BG}; }}
#btn_send:disabled {{ background-color: {C_PANEL3}; color: {C_TEXT_MUTED}; }}

#toggle_container {{
    background-color: {C_PANEL2};
    border: 1px solid {C_BORDER};
    border-radius: 16px;
    padding: 2px 8px;
}}

#toggle_label_on  {{ color: {C_SUCCESS}; font-size: 12px; font-weight: 600; }}
#toggle_label_off {{ color: {C_ERROR};   font-size: 12px; font-weight: 600; }}

#sidebar {{
    background-color: {C_PANEL};
    border-right: 1px solid {C_BORDER};
    min-width: 260px;
    max-width: 260px;
}}

#sidebar_header {{
    background-color: {C_PANEL};
    color: {C_AMBER};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 14px 16px 8px 16px;
}}

#sidebar_divider {{
    background-color: {C_BORDER};
    max-height: 1px;
    margin: 0px 12px;
}}

QScrollArea#sidebar_scroll,
QScrollArea#sidebar_scroll > QWidget,
QScrollArea#sidebar_scroll > QWidget > QWidget {{
    background-color: {C_PANEL};
    border: none;
}}

#novel_title_btn {{
    background-color: transparent;
    color: {C_TEXT};
    border: none;
    border-radius: 5px;
    padding: 8px 10px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}}
#novel_title_btn:hover                {{ background-color: {C_PANEL2}; color: {C_TEXT_BRIGHT}; }}
#novel_title_btn[active="true"]       {{ color: {C_AMBER}; background-color: {C_PANEL3}; }}
#novel_title_btn[active="true"]:hover {{ color: {C_AMBER}; background-color: {C_PANEL3}; }}

#novel_genre_label {{
    color: {C_TEXT_MUTED};
    font-size: 11px;
    padding: 0px 12px 4px 34px;
}}

#chapters_header {{
    color: {C_TEXT_MUTED};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    padding: 6px 10px 2px 34px;
}}

#chapter_btn {{
    background-color: transparent;
    color: {C_TEXT_DIM};
    border: none;
    border-radius: 4px;
    padding: 5px 10px 5px 40px;
    font-size: 12px;
    text-align: left;
}}
#chapter_btn:hover                {{ background-color: {C_PANEL2}; color: {C_TEXT}; }}
#chapter_btn[active="true"]       {{ color: {C_AMBER}; background-color: {C_PANEL3}; font-weight: 600; }}
#chapter_btn[active="true"]:hover {{ color: {C_AMBER}; background-color: {C_PANEL3}; }}

#chat_header {{
    background-color: {C_PANEL};
    border-bottom: 1px solid {C_BORDER};
}}

#hdr_novel  {{ color: {C_AMBER};    font-size: 14px; font-weight: 700; }}
#hdr_chevron{{ color: {C_BORDER2};  font-size: 15px; }}
#hdr_chapter{{ color: {C_TEXT_DIM}; font-size: 13px; }}
#hdr_status {{ color: {C_TEXT_MUTED}; font-size: 11px; }}
#hdr_icon   {{ color: {C_AMBER};    font-size: 14px; }}

QScrollArea#chat_scroll,
QScrollArea#chat_scroll > QWidget,
QScrollArea#chat_scroll > QWidget > QWidget {{
    background-color: {C_BG};
    border: none;
}}

#chat_messages_container {{
    background-color: {C_BG};
}}

#bubble_user {{
    background-color: {C_BUBBLE_USER};
    border-radius: 12px;
    border-bottom-right-radius: 3px;
    border: 1px solid #2E3E5E;
}}

#bubble_ai {{
    background-color: {C_BUBBLE_AI};
    border-radius: 12px;
    border-bottom-left-radius: 3px;
    border: 1px solid #1E2438;
}}

#msg_text_user {{
    color: {C_TEXT_BRIGHT};
    font-size: 13px;
    padding: 10px 14px;
}}

#msg_text_ai {{
    color: {C_TEXT};
    font-size: 13px;
    padding: 10px 14px;
}}

#msg_label_user {{ color: {C_AMBER};      font-size: 11px; font-weight: 600; }}
#msg_label_ai   {{ color: {C_TEXT_MUTED}; font-size: 11px; }}
#msg_time       {{ color: {C_TEXT_MUTED}; font-size: 10px; }}

#empty_icon     {{ color: {C_AMBER};    font-size: 36px; }}
#empty_title    {{ color: {C_AMBER};    font-size: 22px; font-weight: 700; }}
#empty_subtitle {{ color: {C_TEXT_DIM}; font-size: 13px; }}

#input_area {{
    background-color: {C_PANEL};
    border-top: 1px solid {C_BORDER};
    padding: 10px 12px;
}}

QTextEdit#chat_input {{
    background-color: {C_PANEL2};
    color: {C_TEXT_BRIGHT};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
}}
QTextEdit#chat_input:focus    {{ border-color: {C_AMBER_DIM}; background-color: {C_PANEL3}; }}
QTextEdit#chat_input:disabled {{ color: {C_TEXT_MUTED}; background-color: {C_PANEL}; border-color: {C_BORDER}; }}

#statusbar {{
    background-color: {C_PANEL};
    border-top: 1px solid {C_BORDER};
    min-height: 26px;
    max-height: 26px;
    padding: 0px 12px;
}}
#status_text {{ color: {C_TEXT_MUTED}; font-size: 11px; }}

QProgressBar {{
    background-color: {C_PANEL2};
    border: none;
    border-radius: 3px;
    max-height: 3px;
}}
QProgressBar::chunk {{ background-color: {C_AMBER}; border-radius: 3px; }}

QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background-color: {C_SCROLLBAR};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover    {{ background-color: {C_SCROLLBAR_H}; }}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical        {{ height: 0; background: none; }}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical        {{ background: none; }}
QScrollBar:horizontal                {{ height: 6px; background: transparent; }}
QScrollBar::handle:horizontal        {{ background-color: {C_SCROLLBAR}; border-radius: 3px; }}
QScrollBar::handle:horizontal:hover  {{ background-color: {C_SCROLLBAR_H}; }}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal      {{ width: 0; background: none; }}

QLineEdit {{
    background-color: {C_PANEL2};
    color: {C_TEXT_BRIGHT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}}
QLineEdit:focus    {{ border-color: {C_AMBER_DIM}; background-color: {C_PANEL3}; }}
QLineEdit:disabled {{ color: {C_TEXT_MUTED}; }}

QTextEdit {{
    background-color: {C_PANEL2};
    color: {C_TEXT_BRIGHT};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {C_AMBER_DARK};
}}
QTextEdit:focus {{ border-color: {C_AMBER_DIM}; }}

QDialog {{
    background-color: {C_PANEL};
    border: 1px solid {C_BORDER2};
    border-radius: 10px;
}}

#loader_card,
#dialog_card {{
    background-color: {C_PANEL2};
    border: 1px solid {C_BORDER2};
    border-radius: 12px;
}}

#dialog_title  {{ color: {C_AMBER};    font-size: 16px; font-weight: 700; }}
#field_label   {{ color: {C_AMBER};    font-size: 12px; font-weight: 600; }}
#dialog_error  {{ color: {C_ERROR};    font-size: 11px; }}

#loader_title    {{ color: {C_AMBER};    font-size: 15px; font-weight: 700; }}
#loader_subtitle {{ color: {C_TEXT_DIM}; font-size: 12px; }}

QToolTip {{
    background-color: {C_PANEL2};
    color: {C_TEXT};
    border: 1px solid {C_BORDER2};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}
"""
