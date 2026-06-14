from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)

from storyforge.ui.style import (
    C_AMBER,
    C_PANEL3,
    C_TEXT_DIM,
    C_TEXT_MUTED,
    C_BUBBLE_USER,
    C_BUBBLE_AI,
    C_TEXT_BRIGHT,
    C_TEXT,
    C_BG,
)


class ToggleSwitch(QWidget):

    toggled = __import__("PyQt6.QtCore", fromlist=["pyqtSignal"]).pyqtSignal(bool)

    _W, _H, _D, _P = 44, 24, 18, 3

    def __init__(self, checked: bool = True, parent=None) -> None:
        super().__init__(parent)
        self._checked = checked
        self._anim_x = float(self._x_on() if checked else self._x_off())
        self.setFixedSize(self._W, self._H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._timer = QTimer(self)
        self._timer.setInterval(12)
        self._timer.timeout.connect(self._step)

    def _x_on(self) -> int:
        return self._W - self._D - self._P

    def _x_off(self) -> int:
        return self._P

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, val: bool) -> None:
        if val == self._checked:
            return
        self._checked = val
        self._timer.start()
        self.toggled.emit(val)

    def mousePressEvent(self, e) -> None:
        self.setChecked(not self._checked)

    def _step(self) -> None:
        target = float(self._x_on() if self._checked else self._x_off())
        diff = target - self._anim_x
        if abs(diff) < 0.8:
            self._anim_x = target
            self._timer.stop()
        else:
            self._anim_x += diff * 0.28
        self.update()

    def paintEvent(self, e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(C_AMBER if self._checked else C_PANEL3)))
        p.drawRoundedRect(0, 0, self._W, self._H, self._H / 2, self._H / 2)
        p.setBrush(QBrush(QColor("#FFFFFF" if self._checked else C_TEXT_DIM)))
        p.drawEllipse(int(self._anim_x), self._P, self._D, self._D)
        p.end()


class SpinnerWidget(QWidget):

    def __init__(self, size: int = 32, parent=None) -> None:
        super().__init__(parent)
        self._size = size
        self._angle = 0
        self.setFixedSize(size, size)
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def _tick(self) -> None:
        self._angle = (self._angle + 12) % 360
        self.update()

    def paintEvent(self, e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(C_AMBER), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        m = 4
        p.drawArc(
            m, m, self._size - 2 * m, self._size - 2 * m, (-self._angle) * 16, 270 * 16
        )
        p.end()


class LoaderOverlay(QWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("loader_overlay")
        self.hide()

        card = QFrame(self)
        card.setObjectName("loader_card")
        card.setFixedWidth(320)

        vbox = QVBoxLayout(card)
        vbox.setSpacing(10)
        vbox.setContentsMargins(28, 24, 28, 24)

        row = QHBoxLayout()
        self._spinner = SpinnerWidget(36)
        row.addWidget(self._spinner, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addSpacing(14)

        text_col = QVBoxLayout()
        self._title = QLabel("Generating…")
        self._title.setObjectName("loader_title")
        self._sub = QLabel("This may take a minute")
        self._sub.setObjectName("loader_subtitle")
        text_col.addWidget(self._title)
        text_col.addWidget(self._sub)
        row.addLayout(text_col)
        vbox.addLayout(row)

        dot_row = QHBoxLayout()
        dot_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dots: list[QLabel] = []
        for _ in range(3):
            d = QLabel("●")
            d.setObjectName("loader_dot_off")
            dot_row.addWidget(d)
            dot_row.addSpacing(6)
            self._dots.append(d)
        vbox.addLayout(dot_row)

        self._card = card
        self._dot_idx = 0
        self._dot_timer = QTimer(self)
        self._dot_timer.setInterval(400)
        self._dot_timer.timeout.connect(self._pulse_dot)

    def resizeEvent(self, e) -> None:
        self._card.move(
            (self.width() - self._card.width()) // 2,
            (self.height() - self._card.height()) // 2,
        )

    def paintEvent(self, e) -> None:
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(12, 14, 20, 210))
        p.end()

    def show_loading(self, title: str = "Generating…", sub: str = "") -> None:
        self._title.setText(title)
        self._sub.setText(sub or "This may take a minute…")
        self._spinner.start()
        self._dot_timer.start()
        self.show()
        self.raise_()

    def update_sub(self, msg: str) -> None:
        self._sub.setText(msg)

    def hide_loading(self) -> None:
        self._spinner.stop()
        self._dot_timer.stop()
        self.hide()

    def _pulse_dot(self) -> None:
        for i, d in enumerate(self._dots):
            if i == self._dot_idx:
                d.setObjectName("loader_dot_on")
                d.setStyleSheet(f"color: {C_AMBER}; font-size: 8px;")
            else:
                d.setObjectName("loader_dot_off")
                d.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 8px;")
        self._dot_idx = (self._dot_idx + 1) % len(self._dots)


class MessageBubble(QWidget):

    def __init__(self, role: str, text: str, timestamp: str, parent=None) -> None:
        super().__init__(parent)
        is_user = role == "user"

        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 4, 16, 4)
        outer.setSpacing(0)

        col = QVBoxLayout()
        col.setSpacing(3)

        label_row = QHBoxLayout()
        label_row.setSpacing(6)

        name = QLabel("You" if is_user else "StoryForge")
        name.setObjectName("msg_label_user" if is_user else "msg_label_ai")

        ts_label = QLabel(timestamp)
        ts_label.setObjectName("msg_time")

        if is_user:
            label_row.addStretch()
            label_row.addWidget(ts_label)
            label_row.addWidget(name)
        else:
            label_row.addWidget(name)
            label_row.addWidget(ts_label)
            label_row.addStretch()
        col.addLayout(label_row)

        bubble_row = QHBoxLayout()
        bubble_row.setSpacing(0)

        bubble = QFrame()
        bubble.setObjectName("bubble_user" if is_user else "bubble_ai")

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        body = QLabel(text)
        body.setObjectName("msg_text_user" if is_user else "msg_text_ai")
        body.setWordWrap(True)
        body.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        bubble_layout.addWidget(body)

        if is_user:
            bubble_row.addStretch()
            bubble_row.addWidget(bubble)
        else:
            bubble_row.addWidget(bubble)
            bubble_row.addStretch()

        col.addLayout(bubble_row)

        if is_user:
            outer.addStretch()
            outer.addLayout(col)
        else:
            outer.addLayout(col)
            outer.addStretch()


class EmptyState(QWidget):

    def __init__(self, has_novel: bool = False, parent=None) -> None:
        super().__init__(parent)
        vbox = QVBoxLayout(self)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.setSpacing(10)

        icon = QLabel("✦")
        icon.setObjectName("empty_icon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(icon)
        vbox.addSpacing(6)

        if has_novel:
            title = QLabel("No messages yet")
            sub = QLabel(
                "Type an instruction below to continue the story,\n"
                "or ask a question about it."
            )
        else:
            title = QLabel("Welcome to StoryForge")
            sub = QLabel(
                "Create a new novel with the button above,\n"
                "or select one from the sidebar."
            )

        title.setObjectName("empty_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setObjectName("empty_subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addWidget(title)
        vbox.addSpacing(4)
        vbox.addWidget(sub)
