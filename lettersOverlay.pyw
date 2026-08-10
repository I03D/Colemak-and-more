from PyQt5.QtWidgets import QApplication, QGridLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
import sys

# Виджет, который рисует круг и текст внутри него
class CircleLabel(QWidget):
    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        # Разрешаем растягиваться в клетке сетки
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Сглаживание краёв

        rect = self.rect()
        if rect.isNull():
            return

        # Вычисляем максимально вписывающийся в клетку круг
        diameter = int(min(rect.width(), rect.height()) * 0.3)

        x = (rect.width() - diameter) // 2
        y = (rect.height() - diameter) // 2
        circle_rect = QRect(x, y, diameter, diameter)

        # Полупрозрачный чёрный фон внутри круга и тонкая обводка
        bg_color = QColor(0, 0, 0, 75)
        painter.setBrush(bg_color)
        painter.setPen(QPen(QColor(0, 0, 0, 125), 2))

        painter.drawEllipse(circle_rect)

        # Центрируем букву внутри круга
        font = painter.font()
        font.setBold(True)
        font_size = 34
        font.setPointSize(font_size)
        painter.setFont(font)

        painter.setPen(QColor("yellow"))
        painter.drawText(circle_rect, Qt.AlignCenter, self.letter)


class Window(QWidget):
    def __init__(self, screen_size):
        super().__init__()

        # Настройка геометрии на весь экран
        self.setGeometry(0, 0, screen_size.width(), screen_size.height())

        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WA_NoSystemBackground, True) 

        # Базовые флаги окна
        flags = self.windowFlags()
        # Убрали Qt.Tool, оставили только FramelessWindowHint
        self.setWindowFlags(flags | Qt.FramelessWindowHint | Qt.Tool)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(20, 20, 20, 20)

        new_letters = ['a', 'r', 's', 't', 'v', 'd', 'c', 'x', 'n', 'e', 'i', 'o', '/', '.', ',', 'h']

        idx = 0
        for row in range(4):
            for col in range(4):
                if idx < len(new_letters):
                    circle_label = CircleLabel(new_letters[idx])
                    grid_layout.addWidget(circle_label, row, col)
                idx += 1

        self.setLayout(grid_layout)

        # Равномерное распределение по сетке
        for i in range(4):
            grid_layout.setColumnStretch(i, 1)
            grid_layout.setRowStretch(i, 1)

        # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
        # Сначала устанавливаем состояние минимизации, ПОТОМ показываем окно
        self.setWindowState(Qt.WindowMinimized)
        self.showMinimized()
        # -------------------------

        # Применяем прозрачность и игнорирование мыши сразу при старте
        self._make_invisible()

    def _make_invisible(self):
        """Делает окно полностью прозрачным и некликабельным"""
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.clearFocus()

    def _make_visible(self):
        """Делает окно видимым и кликабельным"""
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

    def focusInEvent(self, event):
        """Срабатывает, когда окно получает фокус"""
        super().focusInEvent(event)
        self._make_visible()
        print("Окно в фокусе. Буквы видны.")

    def focusOutEvent(self, event):
        """Срабатывает, когда окно теряет фокус"""
        super().focusOutEvent(event)
        self._make_invisible()
        print("Фокус потерян. Окно прозрачно.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    if not screen:
        sys.exit("Не удалось получить экран")

    size = screen.size()

    window = Window(size)
    window.setWindowTitle("lettersOverlay.pyw run") # <-- установка заголовка

    sys.exit(app.exec_())
