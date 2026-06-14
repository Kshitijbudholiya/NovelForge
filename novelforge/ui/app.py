"""
novelforge.ui.app
~~~~~~~~~~~~~~~~~
MainWindow — assembles topbar, sidebar, chat panel, loader overlay,
and connects all signals to backend workers.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSplitter,
    QSizePolicy,
    QStatusBar,
)

from novelforge.ui.style import STYLESHEET, C_AMBER, C_TEXT_DIM, C_BG
from novelforge.ui.widgets import ToggleSwitch, LoaderOverlay
from novelforge.ui.sidebar import Sidebar
from novelforge.ui.chat_panel import ChatPanel
from novelforge.ui.dialogs import NewNovelDialog
from novelforge.ui.workers import CreateNovelWorker, SendMessageWorker

NOVELS_DIR = Path("novels")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        try:
            from novelforge.core.novel_manager import NovelManager

            self._manager = NovelManager()
            self._has_backend = True
        except ImportError:
            self._manager = None
            self._has_backend = False

        self._active_novel: str | None = None
        self._active_scope: str = "novel"
        self._active_chapter: int | None = None
        self._interactive: bool = True
        self._busy: bool = False
        self._worker = None

        self._histories: dict[str, list[dict]] = {}

        self.setWindowTitle("NovelForge — AI Novel Writer")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        main_vbox = QVBoxLayout(central)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        main_vbox.addWidget(self._build_topbar())

        body = QWidget()
        body_h = QHBoxLayout(body)
        body_h.setContentsMargins(0, 0, 0, 0)
        body_h.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.novel_selected.connect(self._on_novel_selected)
        self._sidebar.chapter_selected.connect(self._on_chapter_selected)
        body_h.addWidget(self._sidebar)

        self._chat = ChatPanel()
        self._chat.message_sent.connect(self._on_message_sent)
        body_h.addWidget(self._chat, 1)

        main_vbox.addWidget(body, 1)

        main_vbox.addWidget(self._build_statusbar())

        self._loader = LoaderOverlay(central)
        self._loader.resize(central.size())

        central.installEventFilter(self)

        self._sidebar.refresh()
        self._chat.set_interactive(False)

        sc = QShortcut(QKeySequence("Ctrl+N"), self)
        sc.activated.connect(self._open_new_novel_dialog)

    def eventFilter(self, obj, event) -> bool:
        from PyQt6.QtCore import QEvent

        if event.type() == QEvent.Type.Resize:
            self._loader.resize(obj.size())
        return super().eventFilter(obj, event)

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("topbar")

        h = QHBoxLayout(bar)
        h.setContentsMargins(14, 0, 14, 0)
        h.setSpacing(10)

        logo = QLabel("✦")
        logo.setObjectName("app_logo")
        title = QLabel("NovelForge")
        title.setObjectName("app_title")
        h.addWidget(logo)
        h.addSpacing(2)
        h.addWidget(title)
        h.addStretch()

        self._new_btn = QPushButton("＋  New Novel")
        self._new_btn.setObjectName("btn_primary")
        self._new_btn.setFixedHeight(34)
        self._new_btn.setToolTip("Create a new novel  (Ctrl+N)")
        self._new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._new_btn.clicked.connect(self._open_new_novel_dialog)
        h.addWidget(self._new_btn)

        h.addSpacing(20)

        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(8)
        toggle_row.setContentsMargins(0, 0, 0, 0)

        self._toggle_label = QLabel("Interactive")
        self._toggle_label.setObjectName("toggle_label_on")

        self._toggle = ToggleSwitch(checked=True)
        self._toggle.toggled.connect(self._on_toggle)

        toggle_row.addWidget(self._toggle_label)
        toggle_row.addWidget(self._toggle)

        toggle_container = QFrame()
        toggle_container.setObjectName("toggle_container")
        toggle_container.setLayout(toggle_row)
        toggle_container.setFixedHeight(32)
        h.addWidget(toggle_container)

        return bar

    def _build_statusbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("statusbar")

        h = QHBoxLayout(bar)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(12)

        self._status_lbl = QLabel("Ready")
        self._status_lbl.setObjectName("status_text")
        h.addWidget(self._status_lbl)
        h.addStretch()

        self._backend_lbl = QLabel(
            "Backend ready"
            if self._has_backend
            else "Demo mode — backend not available"
        )
        self._backend_lbl.setObjectName("status_text")
        h.addWidget(self._backend_lbl)

        return bar

    def _on_toggle(self, checked: bool) -> None:
        self._interactive = checked
        if checked:
            self._toggle_label.setText("Interactive")
            self._toggle_label.setObjectName("toggle_label_on")
        else:
            self._toggle_label.setText("Read-only")
            self._toggle_label.setObjectName("toggle_label_off")
        style = self._toggle_label.style()
        if style is not None:
            style.unpolish(self._toggle_label)
            style.polish(self._toggle_label)
        self._chat.set_interactive(checked and self._active_novel is not None)

    def _open_new_novel_dialog(self) -> None:
        if self._busy:
            return
        dlg = NewNovelDialog(self)
        if dlg.exec() != NewNovelDialog.DialogCode.Accepted:
            return

        title = dlg.title
        genre = dlg.genre
        premise = dlg.premise

        if not self._has_backend or self._manager is None:
            self._demo_create(title, genre, premise)
            return

        self._set_busy(True, "Creating novel…")
        self._loader.show_loading("Generating Novel", "Writing Chapter 1…")

        worker = CreateNovelWorker(self._manager, title, genre, premise)
        worker.progress.connect(self._loader.update_sub)
        worker.progress.connect(self._set_status)
        worker.finished.connect(self._on_novel_created)
        worker.error.connect(self._on_worker_error)
        worker.finished.connect(lambda _: self._cleanup_worker())
        worker.error.connect(lambda _: self._cleanup_worker())
        self._worker = worker
        worker.start()

    def _on_novel_created(self, result: dict) -> None:
        self._loader.hide_loading()
        self._set_busy(False)
        self._sidebar.refresh()

        nid = result["novel_id"]
        chapter = result["chapter"]
        summary = result["summary"]

        ts = datetime.now().strftime("%H:%M")
        key = f"{nid}_ch1"
        self._histories[key] = [
            {"role": "assistant", "text": chapter, "time": ts},
            {"role": "assistant", "text": "─── Summary ───\n" + summary, "time": ts},
        ]

        self._switch_context(nid, chapter_num=1)
        self._set_status("Chapter 1 ready.")

    def _on_novel_selected(self, nid: str) -> None:
        if self._manager and self._has_backend:
            try:
                self._manager.load_novel(nid)
            except Exception:
                pass
        self._switch_context(nid, chapter_num=None)

    def _on_chapter_selected(self, nid: str, cnum: int) -> None:
        if self._manager and self._has_backend:
            try:
                self._manager.load_novel(nid)
            except Exception:
                pass
        self._switch_context(nid, chapter_num=cnum)

    def _switch_context(self, nid: str, chapter_num: int | None) -> None:
        self._active_novel = nid
        self._active_chapter = chapter_num
        self._active_scope = "chapter" if chapter_num is not None else "novel"

        key = self._history_key(nid, chapter_num)
        if key not in self._histories:
            self._histories[key] = self._load_history_from_disk(nid, chapter_num)

        title = self._get_novel_title(nid)

        self._chat.set_context(
            novel_title=title,
            chapter=chapter_num,
            history=self._histories[key],
        )
        self._chat.set_interactive(self._interactive)
        self._sidebar.set_active(nid, chapter_num)

    def _on_message_sent(self, text: str) -> None:
        if self._busy:
            return
        if not self._active_novel:
            self._set_status("Select a novel first.")
            return
        if not self._interactive:
            self._set_status("Switch to Interactive mode to generate content.")
            return
        if not self._has_backend or self._manager is None:
            self._chat.add_message("user", text)
            self._chat.add_message("assistant", f"[Demo] You said: {text}")
            return

        self._chat.add_message("user", text)
        self._set_busy(True)
        self._chat.set_busy(True, "Thinking…")

        worker = SendMessageWorker(
            self._manager,
            self._active_novel,
            text,
            self._active_scope,
            self._active_chapter,
        )
        worker.progress.connect(self._chat.update_status)
        worker.answer.connect(self._on_answer_received)
        worker.chapter.connect(self._on_chapter_generated)
        worker.error.connect(self._on_worker_error)
        worker.answer.connect(lambda _: self._cleanup_worker())
        worker.chapter.connect(lambda _: self._cleanup_worker())
        worker.error.connect(lambda _: self._cleanup_worker())
        self._worker = worker
        worker.start()

    def _on_answer_received(self, text: str) -> None:
        self._chat.set_busy(False)
        self._set_busy(False)
        self._chat.add_message("assistant", text)
        key = self._history_key(self._active_novel, self._active_chapter)
        self._histories.setdefault(key, [])
        self._set_status("Done.")

    def _on_chapter_generated(self, pkg: dict) -> None:
        self._chat.set_busy(False)
        self._set_busy(False)

        ch_num = pkg.get("chapter_number", self._active_chapter)
        chapter = pkg["chapter"]
        summary = pkg["summary"]

        self._chat.add_message("assistant", chapter)
        self._chat.add_message("assistant", "─── Summary ───\n" + summary)

        ts = datetime.now().strftime("%H:%M")
        key = self._history_key(self._active_novel, ch_num)
        self._histories[key] = [
            {"role": "assistant", "text": chapter, "time": ts},
            {"role": "assistant", "text": "─── Summary ───\n" + summary, "time": ts},
        ]

        self._sidebar.refresh()
        self._sidebar.set_active(self._active_novel, ch_num)
        self._active_chapter = ch_num
        self._active_scope = "chapter"
        self._set_status(f"Chapter {ch_num} generated.")

    def _on_worker_error(self, msg: str) -> None:
        self._loader.hide_loading()
        self._chat.set_busy(False)
        self._set_busy(False)
        self._chat.add_message("assistant", f"⚠ Error: {msg}")
        self._set_status(f"Error: {msg}")

    def _cleanup_worker(self) -> None:
        if self._worker:
            self._worker.quit()
            self._worker.wait(2000)
            self._worker = None

    def _set_busy(self, busy: bool, msg: str = "") -> None:
        self._busy = busy
        self._new_btn.setEnabled(not busy)
        if msg:
            self._set_status(msg)

    def _set_status(self, msg: str) -> None:
        self._status_lbl.setText(msg)

    def _history_key(self, nid: str | None, chapter: int | None) -> str:
        if nid is None:
            return "__home__"
        if chapter is not None:
            return f"{nid}_ch{chapter}"
        return nid

    def _get_novel_title(self, nid: str) -> str:
        path = NOVELS_DIR / f"{nid}.json"
        try:
            return json.loads(path.read_text("utf-8")).get("title", "Novel")
        except Exception:
            return "Novel"

    def _load_history_from_disk(self, nid: str, chapter: int | None) -> list[dict]:
        """Pre-load a chapter's saved text into chat history on first open."""
        if chapter is None:
            return []
        d = NOVELS_DIR / nid
        ch_path = d / f"chapter_{chapter:03d}.txt"
        sm_path = d / f"summary_{chapter:03d}.txt"
        msgs: list[dict] = []
        if ch_path.exists():
            msgs.append(
                {
                    "role": "assistant",
                    "text": ch_path.read_text("utf-8"),
                    "time": "saved",
                }
            )
        if sm_path.exists():
            msgs.append(
                {
                    "role": "assistant",
                    "text": "─── Summary ───\n" + sm_path.read_text("utf-8"),
                    "time": "saved",
                }
            )
        return msgs

    def _demo_create(self, title: str, genre: str, premise: str) -> None:
        import uuid

        nid = str(uuid.uuid4())
        NOVELS_DIR.mkdir(exist_ok=True)
        (NOVELS_DIR / f"{nid}.json").write_text(
            json.dumps(
                {
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
                },
                indent=4,
            ),
            encoding="utf-8",
        )
        self._sidebar.refresh()
        self._switch_context(nid, chapter_num=None)
        self._set_status(f"'{title}' created (demo mode).")


def run() -> None:
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    if not isinstance(app, QApplication):
        app = QApplication(sys.argv)

    app.setApplicationName("NovelForge")
    app.setOrganizationName("NovelForge")
    app.setStyleSheet(STYLESHEET)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())
