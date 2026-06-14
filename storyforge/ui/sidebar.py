from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
)

NOVELS_DIR = Path("novels")


class NovelItem(QFrame):

    novel_selected = pyqtSignal(str)
    chapter_selected = pyqtSignal(str, int)

    def __init__(self, meta: dict, parent=None) -> None:
        super().__init__(parent)
        self._nid = meta.get("novel_id", "")
        self._title = meta.get("title", "Untitled")
        self._genre = meta.get("genre", "")
        self._expanded = False
        self._chapter_btns: dict[int, QPushButton] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 2, 0, 2)
        outer.setSpacing(0)

        self._header_btn = QPushButton()
        self._header_btn.setObjectName("novel_title_btn")
        self._header_btn.setFixedHeight(36)
        self._header_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._header_btn.clicked.connect(self._on_header_click)
        self._update_header_text()
        outer.addWidget(self._header_btn)

        genre_lbl = QLabel(self._genre or "")
        genre_lbl.setObjectName("novel_genre_label")
        outer.addWidget(genre_lbl)

        self._chapters_widget = QWidget()
        self._chapters_widget.setVisible(False)
        self._ch_layout = QVBoxLayout(self._chapters_widget)
        self._ch_layout.setContentsMargins(0, 2, 0, 4)
        self._ch_layout.setSpacing(1)
        outer.addWidget(self._chapters_widget)

        self._populate_chapters()

    def refresh_chapters(self) -> None:
        for btn in self._chapter_btns.values():
            btn.deleteLater()
        self._chapter_btns.clear()
        while self._ch_layout.count():
            item = self._ch_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self._populate_chapters()
        if self._chapter_btns and not self._expanded:
            self._set_expanded(True)

    def set_active_novel(self, active: bool) -> None:
        self._header_btn.setProperty("active", "true" if active else "false")
        style = self._header_btn.style()
        if style:
            style.unpolish(self._header_btn)
            style.polish(self._header_btn)

    def set_active_chapter(self, cnum: int | None) -> None:
        for n, btn in self._chapter_btns.items():
            val = "true" if n == cnum else "false"
            btn.setProperty("active", val)
            style = btn.style()
            if style:
                style.unpolish(btn)
                style.polish(btn)

    def expand(self) -> None:
        self._set_expanded(True)

    def _populate_chapters(self) -> None:
        d = NOVELS_DIR / self._nid
        chapter_files = sorted(d.glob("chapter_*.txt")) if d.exists() else []
        if chapter_files:
            hdr = QLabel("CHAPTERS")
            hdr.setObjectName("chapters_header")
            self._ch_layout.addWidget(hdr)
            for cf in chapter_files:
                try:
                    cnum = int(cf.stem.split("_")[1])
                except (IndexError, ValueError):
                    continue
                btn = QPushButton(f"Chapter {cnum}")
                btn.setObjectName("chapter_btn")
                btn.setFixedHeight(30)
                btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn.clicked.connect(
                    lambda checked, n=cnum: self.chapter_selected.emit(self._nid, n)
                )
                self._ch_layout.addWidget(btn)
                self._chapter_btns[cnum] = btn
        else:
            lbl = QLabel("No chapters yet")
            lbl.setObjectName("novel_genre_label")
            lbl.setContentsMargins(40, 4, 0, 4)
            self._ch_layout.addWidget(lbl)

    def _on_header_click(self) -> None:
        self._set_expanded(not self._expanded)
        self.novel_selected.emit(self._nid)

    def _set_expanded(self, val: bool) -> None:
        self._expanded = val
        self._chapters_widget.setVisible(val)
        self._update_header_text()

    def _update_header_text(self) -> None:
        arrow = "▾" if self._expanded else "▸"
        self._header_btn.setText(f"  {arrow}  {self._title}")


class Sidebar(QWidget):

    novel_selected = pyqtSignal(str)
    chapter_selected = pyqtSignal(str, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(260)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        hdr = QLabel("YOUR NOVELS")
        hdr.setObjectName("sidebar_header")
        root.addWidget(hdr)

        div = QFrame()
        div.setObjectName("sidebar_divider")
        div.setFixedHeight(1)
        root.addWidget(div)

        self._scroll = QScrollArea()
        self._scroll.setObjectName("sidebar_scroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(6, 8, 6, 8)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._list_widget)
        root.addWidget(self._scroll, 1)

        self._items: dict[str, NovelItem] = {}

        self._empty_lbl = QLabel("No novels yet.\nClick '+ New Novel' to begin.")
        self._empty_lbl.setObjectName("novel_genre_label")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setContentsMargins(12, 24, 12, 0)
        self._list_layout.insertWidget(0, self._empty_lbl)

    def refresh(self) -> None:
        novels = self._load_novels()
        nids_on_disk = {n.get("novel_id", "") for n in novels}

        for nid in list(self._items.keys()):
            if nid not in nids_on_disk:
                item = self._items.pop(nid)
                self._list_layout.removeWidget(item)
                item.deleteLater()

        for meta in novels:
            nid = meta.get("novel_id", "")
            if not nid:
                continue
            if nid in self._items:
                self._items[nid].refresh_chapters()
            else:
                item = NovelItem(meta)
                item.novel_selected.connect(self.novel_selected)
                item.chapter_selected.connect(self.chapter_selected)
                idx = self._list_layout.count() - 1
                self._list_layout.insertWidget(idx, item)
                self._items[nid] = item

        self._empty_lbl.setVisible(len(self._items) == 0)

    def set_active(self, novel_id: str | None, chapter: int | None = None) -> None:
        for nid, item in self._items.items():
            item.set_active_novel(nid == novel_id and chapter is None)
            if nid == novel_id:
                item.set_active_chapter(chapter)
                item.expand()
            else:
                item.set_active_chapter(None)

    @staticmethod
    def _load_novels() -> list[dict]:
        if not NOVELS_DIR.exists():
            return []
        out = []
        for f in sorted(NOVELS_DIR.glob("*.json")):
            try:
                out.append(json.loads(f.read_text("utf-8")))
            except Exception:
                pass
        return out
