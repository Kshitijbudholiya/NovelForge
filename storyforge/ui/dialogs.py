"""
storyforge.ui.dialogs
~~~~~~~~~~~~~~~~~~~~~
Modal dialog windows — New Novel creation form.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtGui import QKeySequence, QShortcut

from storyforge.ui.style import C_AMBER, C_TEXT_DIM


class NewNovelDialog(QDialog):
    """
    Modal dialog to collect title, genre, and premise for a new novel.
    Returns via .exec(); retrieve results with .title / .genre / .premise.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Novel")
        self.setModal(True)
        self.setFixedSize(520, 400)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        card = QFrame(self)
        card.setObjectName("loader_card")
        card.setFixedSize(520, 400)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(0)

        hdr_row = QHBoxLayout()
        title_lbl = QLabel("✦  New Novel")
        title_lbl.setObjectName("dialog_title")
        close_btn = QPushButton("✕")
        close_btn.setObjectName("btn_ghost")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.reject)
        hdr_row.addWidget(title_lbl)
        hdr_row.addStretch()
        hdr_row.addWidget(close_btn)
        outer.addLayout(hdr_row)
        outer.addSpacing(18)

        self._add_field(outer, "Title", "e.g. The Iron Tide")
        self.title_edit = self._last_line

        self._add_field(outer, "Genre", "e.g. Fantasy, Sci-Fi, Slice of life")
        self.genre_edit = self._last_line

        p_lbl = QLabel("Premise")
        p_lbl.setObjectName("field_label")
        outer.addWidget(p_lbl)
        outer.addSpacing(4)
        self.premise_edit = QTextEdit()
        self.premise_edit.setPlaceholderText("Describe your story concept…")
        self.premise_edit.setFixedHeight(90)
        outer.addWidget(self.premise_edit)

        outer.addSpacing(16)

        self._err = QLabel("")
        self._err.setStyleSheet("color: #B84040; font-size: 11px;")
        outer.addWidget(self._err)

        outer.addSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("btn_ghost")
        cancel.setFixedHeight(36)
        cancel.clicked.connect(self.reject)

        self._ok = QPushButton("✦  Generate Chapter 1")
        self._ok.setObjectName("btn_primary")
        self._ok.setFixedHeight(36)
        self._ok.clicked.connect(self._submit)

        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(self._ok)
        outer.addLayout(btn_row)

        self.title = ""
        self.genre = ""
        self.premise = ""

        sc = QShortcut(QKeySequence("Ctrl+Return"), self)
        sc.activated.connect(self._submit)

    def _add_field(self, layout, label: str, placeholder: str) -> None:
        lbl = QLabel(label)
        lbl.setObjectName("field_label")
        layout.addWidget(lbl)
        layout.addSpacing(4)
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(36)
        layout.addWidget(edit)
        layout.addSpacing(10)
        self._last_line = edit

    def _submit(self) -> None:
        self.title = self.title_edit.text().strip()
        self.genre = self.genre_edit.text().strip()
        self.premise = self.premise_edit.toPlainText().strip()

        if not self.title:
            self._err.setText("Title is required.")
            self.title_edit.setFocus()
            return
        if not self.premise:
            self._err.setText("Premise is required.")
            self.premise_edit.setFocus()
            return

        self.accept()
