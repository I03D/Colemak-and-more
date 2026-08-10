import sys
import random
import argparse
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush, QFontMetrics, QPixmap
from PyQt5.QtCore import Qt, QTimer, QRectF

# --- ЧАСТЬ 1: Виджет выпрыгивающего объекта ---
class AnimatedWordWidget(QWidget):
    def __init__(self, word='A', font_size=34):
        super().__init__()
        self.word = word
        self.font_size = font_size
        
        # Настройки окна
        self.setWindowFlags(Qt.WindowTransparentForInput | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.resize(800, 600)
        self.center_widget()

        # Анимационные параметры
        self.reset_animation_params()

        # Таймер анимации (16 мс ≈ 60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        
        self._exit_on_esc = True
        self.alpha = 0
        self.is_animating = False
        self.initial_angle = random.uniform(-9, 9)

    def reset_animation_params(self):
        self.frame_count = 0
        self.bounce = 0.0
        self.velocity = -16.5
        self.gravity = 0.8
        self.initial_angle = random.uniform(-9, 9)
        self.alpha = 255

    def center_widget(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2)
        )

    def update_animation(self):
        if not self.is_animating:
            return

        self.frame_count += 1
        self.velocity += self.gravity
        self.bounce += self.velocity
        
        decay_rate = 5
        self.alpha -= decay_rate
        
        if self.alpha <= 0:
            self.alpha = 0
            self.is_animating = False
            self.timer.stop()
            
            # ЗАКРЫТИЕ ПРОГРАММЫ ПОСЛЕ АНИМАЦИИ
            app = QApplication.instance()
            if app:
                app.quit()
            return

        self.update()

    def start_animation(self):
        """Запускает новую анимацию с текущими параметрами."""
        self.reset_animation_params()
        self.is_animating = True
        self.timer.start(16)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        center = rect.center()

        painter.save()
        painter.translate(0, self.bounce)

        painter.translate(center.x(), center.y())
        painter.rotate(self.initial_angle)
        painter.translate(-center.x(), -center.y())

        corner_radius = 15 
        padding = 10 

        font = QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(self.font_size)
        font.setBold(True)
        painter.setFont(font)

        metrics = QFontMetrics(font)
        text_rect_raw = metrics.boundingRect(self.word)

        content_width = text_rect_raw.width() + 2 * padding
        content_height = text_rect_raw.height() + 2 * padding

        target_rect = QRectF(
            center.x() - content_width / 2,
            center.y() - content_height / 2,
            content_width,
            content_height
        )

        # Фон
        bg_base_alpha = 100 
        final_bg_alpha = max(0, int(bg_base_alpha * (self.alpha / 255.0)))
        bg_color = QColor(0, 0, 0, final_bg_alpha)
        brush = QBrush(bg_color)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(target_rect, corner_radius, corner_radius)

        # Рамка
        frame_base_alpha = 200 
        final_frame_alpha = max(0, int(frame_base_alpha * (self.alpha / 255.0)))
        frame_color = QColor(30, 30, 30, final_frame_alpha)
        pen = QPen(frame_color, 2)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(target_rect, corner_radius, corner_radius)

        # Текст
        text_color = QColor("yellow")
        final_text_alpha = max(0, int(255 * (self.alpha / 255.0)))
        text_color.setAlpha(final_text_alpha)
        painter.setPen(text_color)

        text_draw_rect = target_rect.adjusted(padding, padding, -padding, -padding)
        painter.drawText(text_draw_rect, Qt.AlignCenter, self.word)
        painter.restore()


# --- ГЛАВНЫЙ КОНТРОЛЛЕР ---
class MainWindow(QWidget):
    def __init__(self, screen_size, message_text):
        super().__init__()

        # Используем переданный screen_size вместо self.size
        self.setGeometry(0, 0, screen_size.width(), screen_size.height())
        
        flags = self.windowFlags()
        self.setWindowFlags(flags | Qt.WindowTransparentForInput | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # --- ЛОГИКА ЗАПУСКА ---
        # Теперь текст передается извне
        self.active_widget = AnimatedWordWidget(message_text, font_size=48)
        self.active_widget.start_animation()
        
        self.show()

if __name__ == '__main__':
    # 1. Настройка парсера аргументов
    parser = argparse.ArgumentParser(description="Анимированная надпись, принимает строку в аргумент.")
    parser.add_argument('text', nargs='?', default="Empty label", help='Текст для отображения в анимации')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    screen_size = app.primaryScreen().size()

    # Установка стиля для корректной работы прозрачности
    app.setStyle("Fusion")

    # 2. Передача текста в MainWindow
    window = MainWindow(screen_size, args.text)
    window.setWindowTitle("labelWidget.pyw run")  # <-- установка заголовка
    
    sys.exit(app.exec_())
