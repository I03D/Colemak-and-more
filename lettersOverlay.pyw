from PyQt5.QtWidgets import QApplication, QGridLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QEvent, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
import sys
import ctypes


class CircleLabel(QWidget):
    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        self.show_letter = False
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        if not self.show_letter:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        if rect.isNull():
            return

        diameter = int(min(rect.width(), rect.height()) * 0.3)
        x = (rect.width() - diameter) // 2
        y = (rect.height() - diameter) // 2
        circle_rect = QRect(x, y, diameter, diameter)

        bg_color = QColor(0, 0, 0, 75)
        painter.setBrush(bg_color)
        painter.setPen(QPen(QColor(0, 0, 0, 125), 2))
        painter.drawEllipse(circle_rect)

        font = painter.font()
        font.setBold(True)
        font.setPointSize(34)
        painter.setFont(font)
        painter.setPen(QColor("yellow"))
        painter.drawText(circle_rect, Qt.AlignCenter, self.letter)


class Window(QWidget):
    def __init__(self, screen_size):
        super().__init__()

        self.setGeometry(0, 0, screen_size.width(), screen_size.height())

        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        flags = self.windowFlags()
        self.setWindowFlags(
            flags | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(20, 20, 20, 20)

        new_letters = [
            'a', 'r', 's', 't', 'v', 'd', 'c',
            'x', 'n', 'e', 'i', 'o', '/', '.', ',', 'h'
        ]

        self.circle_labels = []

        idx = 0
        for row in range(4):
            for col in range(4):
                if idx < len(new_letters):
                    circle_label = CircleLabel(new_letters[idx])
                    grid_layout.addWidget(circle_label, row, col)
                    self.circle_labels.append(circle_label)
                idx += 1

        self.setLayout(grid_layout)

        for i in range(4):
            grid_layout.setColumnStretch(i, 1)
            grid_layout.setRowStretch(i, 1)

        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Флаг: первая активация окна поглощается — оверлей
        # стартует в скрытом состоянии, как будто уже потерял фокус.
        self._first_activation = True

        self.show()

        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_TOOLWINDOW = 0x00000080
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            hwnd, GWL_EXSTYLE, ex_style | WS_EX_TOOLWINDOW
        )

        self._make_invisible()

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(150)
        self._debounce_timer.timeout.connect(self._make_invisible)

    def event(self, e):
        if e.type() == QEvent.WindowActivate:
            if self._first_activation:
                # Гасим первую активацию от show() — буквы остаются скрытыми
                self._first_activation = False
                self._make_invisible()
            else:
                self._debounce_timer.stop()
                self._make_visible()
        elif e.type() == QEvent.WindowDeactivate:
            self._debounce_timer.start()
        return super().event(e)

    def _make_invisible(self):
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        for cl in self.circle_labels:
            cl.show_letter = False
            cl.update()

    def _make_visible(self):
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        for cl in self.circle_labels:
            cl.show_letter = True
            cl.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    if not screen:
        sys.exit("Не удалось получить экран")

    size = screen.size()

    window = Window(size)
    window.setWindowTitle("lettersOverlay.pyw run")

    sys.exit(app.exec_())
