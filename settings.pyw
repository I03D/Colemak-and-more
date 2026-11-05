import sys
import subprocess
import os
import configparser

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QFrame,
    QColorDialog,
    QSlider,
    QHBoxLayout,
    QMessageBox,
    QRadioButton,
    QVBoxLayout,
    QSizePolicy,
    QDialog,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPainter


script_dir = os.path.dirname(os.path.abspath(__file__))

class KeyboardDiagram(QWidget):
    """Рисует упрощённую схему клавиатуры Colemak."""

    def __init__(
        self,
        title,
        rows,
        iso=False,
        iso_bottom_row=None,
        fg="#000000",
        bg="#f0f0f0",
    ):
        super().__init__()

        self.title = title
        self.rows = rows
        self.iso = iso
        self.iso_bottom_row = (
            list(iso_bottom_row)
            if iso_bottom_row is not None
            else None
        )
        self.fg = QColor(fg)
        self.bg = QColor(bg)

        self.setMinimumSize(400, 170)

    def sizeHint(self):
        return QSize(440, 180)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(self.fg)
        painter.drawText(
            0,
            8,
            self.width(),
            26,
            Qt.AlignCenter,
            self.title,
        )

        key_width = 30
        key_height = 27
        gap = 4
        step = key_width + gap
        first_y = 43

        rows = [list(row) for row in self.rows]

        if self.iso:
            if self.iso_bottom_row is not None:
                # Для ISO-вариантов с явно заданным рядом используем
                # именно указанные для них клавиши и их порядок.
                rows[2] = list(self.iso_bottom_row)
            else:
                # Запасной вариант для ISO-схемы без отдельного ряда:
                # дополнительная клавиша слева от Z показывает "\".
                rows[2].insert(0, "\\")

        # Ступенчатое смещение рядов:
        # верхний — без смещения,
        # средний — на половину шага,
        # нижний — на один шаг вправо.
        row_offsets = [
            0,
            step / 2,
            step,
        ]

        if self.iso:
            # ISO: нижний ряд начинается немного левее клавиши Q.
            row_offsets[2] = -8

        # Рассчитываем ширину схемы с учётом смещений,
        # чтобы отцентрировать клавиши в области рисования.
        left_edge = min(row_offsets)
        right_edge = max(
            row_offsets[row_index]
            + len(keys) * key_width
            + (len(keys) - 1) * gap
            for row_index, keys in enumerate(rows)
        )

        total_width = right_edge - left_edge
        base_x = (self.width() - total_width) / 2 - left_edge

        for row_index, keys in enumerate(rows):
            x = base_x + row_offsets[row_index]
            y = first_y + row_index * (key_height + gap)

            for key in keys:
                key_x = int(round(x))
                key_y = int(y)

                painter.setBrush(self.bg)
                painter.setPen(self.fg)
                painter.drawRoundedRect(
                    key_x,
                    key_y,
                    key_width,
                    key_height,
                    4,
                    4,
                )
                painter.drawText(
                    key_x,
                    key_y,
                    key_width,
                    key_height,
                    Qt.AlignCenter,
                    key,
                )

                x += step


class KeyboardHelpDialog(QDialog):
    """Окно справки с вариантами раскладки Colemak."""

    def __init__(self, fg="#000000", bg="#f0f0f0", parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint
        )

        self.setWindowTitle("Раскладки Colemak")
        self.resize(940, 610)
        self.setStyleSheet(
            f"background-color: {bg}; color: {fg};"
        )

        classic = [
            ["Q", "W", "F", "P", "G", "J", "L", "U", "Y", ";"],
            ["A", "R", "S", "T", "D", "H", "N", "E", "I", "O"],
            ["Z", "X", "C", "V", "B", "K", "M", ",", ".", "/"],
        ]

        dhm = [
            ["Q", "W", "F", "P", "B", "J", "L", "U", "Y", ";"],
            ["A", "R", "S", "T", "G", "M", "N", "E", "I", "O"],
            ["Z", "X", "C", "D", "V", "K", "H", ",", ".", "/"],
        ]

        grid = QGridLayout()
        grid.setSpacing(12)

        diagrams = [
            KeyboardDiagram(
                "Classic",
                classic,
                fg=fg,
                bg=bg,
            ),
            KeyboardDiagram(
                "DHm",
                dhm,
                fg=fg,
                bg=bg,
            ),
            KeyboardDiagram(
                r"Classic ISO",
                classic,
                iso=True,
                iso_bottom_row=[
                    "\\",
                    "Z",
                    "X",
                    "C",
                    "V",
                    "B",
                    "K",
                    "M",
                    ",",
                    ".",
                    "/",
                ],
                fg=fg,
                bg=bg,
            ),
            KeyboardDiagram(
                r"DHm ISO Angle Mod",
                dhm,
                iso=True,
                iso_bottom_row=[
                    "Z",
                    "X",
                    "C",
                    "D",
                    "V",
                    "\\",
                    "K",
                    "H",
                    ",",
                    ".",
                    "/",
                ],
                fg=fg,
                bg=bg,
            ),
            KeyboardDiagram(
                "DHm ISO Angle Mod z->b",
                dhm,
                iso=True,
                iso_bottom_row=[
                    "<>",
                    "X",
                    "C",
                    "D",
                    "V",
                    "Z",
                    "K",
                    "H",
                    ",",
                    ".",
                    "/",
                ],
                fg=fg,
                bg=bg,
            ),
            KeyboardDiagram(
                "DHm ISO",
                dhm,
                iso=True,
                iso_bottom_row=[
                    "<>",
                    "Z",
                    "X",
                    "C",
                    "D",
                    "V",
                    "K",
                    "H",
                    ",",
                    ".",
                    "/",
                ],
                fg=fg,
                bg=bg,
            ),
        ]

        for index, diagram in enumerate(diagrams):
            grid.addWidget(diagram, index // 2, index % 2)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(close_button)
        button_row.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(grid)
        layout.addLayout(button_row)


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        # Создаём секцию, если config.ini ещё не содержит [settings].
        if not self.config.has_section("settings"):
            self.config.add_section("settings")

        bg_color = self.config.get(
            "settings",
            "background_color",
            fallback="#f0f0f0",
        )
        fg_color = self.config.get(
            "settings",
            "foreground_color",
            fallback="#000000",
        )
        bg_alpha = self.config.getint(
            "settings",
            "background_transparency",
            fallback=255,
        ) / 255.0

        self.setStyleSheet(
            f"background-color: {bg_color}; color: {fg_color};"
        )
        self.setWindowOpacity(bg_alpha)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Настройки")

        layout = QGridLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 3)

        row = 0

        title = QLabel("Colemak-and-more")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 35px; "
            "font-weight: bold; "
            "padding-bottom: 10px;"
        )
        layout.addWidget(
            title,
            row,
            0,
            1,
            2,
            alignment=Qt.AlignCenter,
        )
        row += 1

        separator_top = QFrame()
        separator_top.setFrameShape(QFrame.HLine)
        separator_top.setStyleSheet(
            "background-color: #222; height: 3px;"
        )
        layout.addWidget(separator_top, row, 0, 1, 2)
        row += 1

        self.check_start_show = QCheckBox(
            "Показывать настройки при запуске"
        )
        self.check_start_show.setChecked(
            self.config.getboolean(
                "settings",
                "start_show_settings",
                fallback=True,
            )
        )
        self.check_start_show.setStyleSheet(
            self._get_checkbox_style()
        )
        layout.addWidget(
            self.check_start_show,
            row,
            0,
            1,
            2,
            alignment=Qt.AlignCenter,
        )
        row += 1

        self.check_a = QCheckBox(
            "CapsLock = Esc (Shift+Capslock = CapsLock)"
        )
        self.check_a.setChecked(
            self.config.getboolean(
                "settings",
                "Capslock-eq-Escape",
                fallback=False,
            )
        )
        self.check_a.setStyleSheet(self._get_checkbox_style())
        layout.addWidget(
            self.check_a,
            row,
            0,
            1,
            2,
            alignment=Qt.AlignCenter,
        )
        row += 1

        self.check_b = QCheckBox("Alt+' = Enter")
        self.check_b.setChecked(
            self.config.getboolean(
                "settings",
                "Alt+Apostrophe-eq-Enter",
                fallback=False,
            )
        )
        self.check_b.setStyleSheet(self._get_checkbox_style())
        layout.addWidget(
            self.check_b,
            row,
            0,
            1,
            2,
            alignment=Qt.AlignCenter,
        )
        row += 1

        lbl_layout = QLabel("Вид Colemak:")
        layout.addWidget(
            lbl_layout,
            row,
            0,
            alignment=Qt.AlignRight | Qt.AlignVCenter,
        )

        radio_container = QWidget()
        radio_layout = QGridLayout()
        radio_layout.setSpacing(10)
        radio_container.setLayout(radio_layout)

        options = [
            "Classic",
            "DHm",
            "ISO",
            "DHm ISO Angle Mod",
            "DHm ISO Angle Mod z->b",
            "DHm ISO",
        ]
        self.radio_buttons = []

        radio_style = self._get_radio_style()

        for index, text in enumerate(options):
            radio_button = QRadioButton(text)
            radio_button.setStyleSheet(radio_style)
            self.radio_buttons.append(radio_button)

            radio_layout.addWidget(
                radio_button,
                index // 2,
                index % 2,
            )

        saved_type = self.config.get(
            "settings",
            "Colemak_type",
            fallback="Classic",
        )

        # Старое название соответствовало варианту Angle Mod.
        if saved_type == "DHm ISO":
            saved_type = "DHm ISO Angle Mod"

        for radio_button in self.radio_buttons:
            if radio_button.text() == saved_type:
                radio_button.setChecked(True)
                break
        else:
            self.radio_buttons[0].setChecked(True)

        # Кнопка справки рядом с выбором раскладки.
        self.btn_layout_hint = QPushButton("?")
        self.btn_layout_hint.clicked.connect(self.show_layout_help)
        self._apply_button_style(self.btn_layout_hint)

        radio_row = QHBoxLayout()
        radio_row.setContentsMargins(0, 0, 0, 0)
        radio_row.setSpacing(10)
        radio_row.addWidget(radio_container)
        radio_row.addWidget(
            self.btn_layout_hint,
            alignment=Qt.AlignTop,
        )

        radio_row_widget = QWidget()
        radio_row_widget.setLayout(radio_row)

##        layout.addWidget(
##            radio_row_widget,
##            row,
##            1,
##            1,
##            2,
##            alignment=Qt.AlignLeft | Qt.AlignTop,
##        )
        layout.addWidget(radio_row_widget, row, 1)

        row += 1

        # Выбор цвета фона.
        lbl_bg_color = QLabel("Цвет фона:")
        self.btn_bg_color = QPushButton("Выбрать цвет")
        self.btn_bg_color.setMaximumWidth(120)
        self.btn_bg_color.clicked.connect(
            lambda: self.open_color_dialog("bg")
        )
        self._apply_button_style(self.btn_bg_color)

        bg_btn_container = QWidget()
        bg_btn_layout = QHBoxLayout()
        bg_btn_layout.setContentsMargins(0, 0, 0, 0)
        bg_btn_layout.setSpacing(0)
        bg_btn_layout.addStretch()
        bg_btn_layout.addWidget(self.btn_bg_color)
        bg_btn_layout.addStretch()
        bg_btn_container.setLayout(bg_btn_layout)
        bg_btn_container.setMaximumWidth(300)

        layout.addWidget(
            lbl_bg_color,
            row,
            0,
            alignment=Qt.AlignRight | Qt.AlignVCenter,
        )
        layout.addWidget(bg_btn_container, row, 1)
        row += 1

        # Прозрачность окна.
        lbl_trans = QLabel("Прозрачность окна:")
        self.slider_trans = QSlider(Qt.Horizontal)
        self.slider_trans.setRange(0, 255)
        self.slider_trans.setValue(
            self.config.getint(
                "settings",
                "background_transparency",
                fallback=255,
            )
        )
        self.slider_trans.valueChanged.connect(
            self.update_window_opacity
        )
        self.slider_trans.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )
        self._apply_slider_style(self.slider_trans)

        layout.addWidget(
            lbl_trans,
            row,
            0,
            alignment=Qt.AlignRight | Qt.AlignVCenter,
        )
        layout.addWidget(self.slider_trans, row, 1)
        row += 1

        # Выбор цвета элементов.
        lbl_fg_color = QLabel("Цвет элементов:")
        self.btn_fg_color = QPushButton("Выбрать цвет")
        self.btn_fg_color.setMaximumWidth(120)
        self.btn_fg_color.clicked.connect(
            lambda: self.open_color_dialog("fg")
        )
        self._apply_button_style(self.btn_fg_color)

        fg_btn_container = QWidget()
        fg_btn_layout = QHBoxLayout()
        fg_btn_layout.setContentsMargins(0, 0, 0, 0)
        fg_btn_layout.setSpacing(0)
        fg_btn_layout.addStretch()
        fg_btn_layout.addWidget(self.btn_fg_color)
        fg_btn_layout.addStretch()
        fg_btn_container.setLayout(fg_btn_layout)
        fg_btn_container.setMaximumWidth(300)

        layout.addWidget(
            lbl_fg_color,
            row,
            0,
            alignment=Qt.AlignRight | Qt.AlignVCenter,
        )
        layout.addWidget(fg_btn_container, row, 1)
        row += 1

        self.btn_tutorial = QPushButton("Курсорный тренажёр")
        self.btn_tutorial.clicked.connect(self.run_tutorial)

        self.btn_hint = QPushButton("?")
        self.btn_hint.clicked.connect(self.show_hint_window)

        self._apply_button_style(self.btn_tutorial)
        self._apply_button_style(self.btn_hint)

        # Обе кнопки «?» получают одинаковую ширину.
        hint_button_width = self.btn_hint.sizeHint().width()
        self.btn_hint.setFixedWidth(hint_button_width)
        self.btn_layout_hint.setFixedWidth(hint_button_width)

        buttons_hbox = QHBoxLayout()
        buttons_hbox.setSpacing(12)
        buttons_hbox.setAlignment(Qt.AlignCenter)
        buttons_hbox.addWidget(self.btn_tutorial)
        buttons_hbox.addWidget(self.btn_hint)

        buttons_container = QWidget()
        buttons_container.setLayout(buttons_hbox)

        layout.addWidget(
            buttons_container,
            row,
            0,
            1,
            2,
            alignment=Qt.AlignCenter,
        )
        row += 1

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(
            "background-color: #222; height: 3px;"
        )
        layout.addWidget(separator, row, 0, 1, 2)
        row += 1

        self.btn_save = QPushButton("Сохранить и перезагрузить")
        self.btn_save.clicked.connect(self.save_settings)
        self._apply_button_style(self.btn_save)

        layout.addWidget(
            self.btn_save,
            row,
            0,
            1,
            2,
            alignment=Qt.AlignCenter,
        )

        self.setLayout(layout)
        self.adjustSize()
        self.setMinimumSize(400, 300)

    @staticmethod
    def _lighten_or_darken(hex_color, delta):
        try:
            color = QColor(hex_color)
            if not color.isValid():
                return "#888888"

            lightness = color.lightness()
            new_lightness = max(0, min(255, lightness + delta))
            color.setHsl(
                color.hue(),
                color.saturation(),
                new_lightness,
            )
            return color.name()
        except Exception:
            return "#888888"

    def _get_checkbox_style(self):
        fg_hex = self.config.get(
            "settings",
            "foreground_color",
            fallback="#000000",
        )
        border_color_base = self._lighten_or_darken(fg_hex, 40)
        border_hover = self._lighten_or_darken(
            border_color_base,
            30,
        )
        border_checked = self._lighten_or_darken(fg_hex, -20)

        return f"""
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {border_color_base};
                background-color: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {fg_hex};
                border-color: {border_checked};
            }}
            QCheckBox {{
                padding: 4px;
            }}
            QCheckBox::indicator:hover {{
                border-color: {border_hover};
            }}
        """

    def _get_radio_style(self):
        fg_hex = self.config.get(
            "settings",
            "foreground_color",
            fallback="#000000",
        )
        border_color_base = self._lighten_or_darken(fg_hex, 40)
        border_hover = self._lighten_or_darken(
            border_color_base,
            30,
        )
        border_checked = self._lighten_or_darken(fg_hex, -20)

        return f"""
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {border_color_base};
                background-color: transparent;
            }}
            QRadioButton::indicator:checked {{
                background-color: {fg_hex};
                border-color: {border_checked};
            }}
            QRadioButton {{
                padding: 4px;
            }}
            QRadioButton::indicator:hover {{
                border-color: {border_hover};
            }}
        """

    def _get_button_css(self):
        fg_hex = self.config.get(
            "settings",
            "foreground_color",
            fallback="#000000",
        )
        border_color_base = self._lighten_or_darken(fg_hex, 40)
        border_hover = self._lighten_or_darken(
            border_color_base,
            30,
        )
        border_pressed = self._lighten_or_darken(fg_hex, -15)

        return f"""
            QPushButton {{
                padding: 10px;
                background-color: transparent;
                color: {fg_hex};
                border: 2px solid {border_color_base};
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                border-color: {border_hover};
                color: {fg_hex};
            }}
            QPushButton:pressed {{
                border-color: {border_pressed};
                background-color: rgba(0, 0, 0, 0.1);
            }}
        """

    def _get_slider_css(self):
        fg_hex = self.config.get(
            "settings",
            "foreground_color",
            fallback="#000000",
        )
        border_base = self._lighten_or_darken(fg_hex, 40)
        border_hover = self._lighten_or_darken(border_base, 30)
        border_pressed = self._lighten_or_darken(fg_hex, -15)
        handle_border = self._lighten_or_darken(fg_hex, -20)

        return f"""
            QSlider::groove:horizontal {{
                border: 2px solid {border_base};
                border-radius: 8px;
                height: 16px;
                margin: 4px 0;
                background-color: transparent;
            }}
            QSlider::handle:horizontal {{
                background-color: {fg_hex};
                border: 2px solid {handle_border};
                width: 24px;
                height: 24px;
                border-radius: 12px;
                margin-top: -4px;
                margin-bottom: -4px;
            }}
            QSlider::handle:horizontal:hover {{
                border-color: {border_hover};
            }}
            QSlider::handle:horizontal:pressed {{
                border-color: {border_pressed};
                background-color: rgba(0, 0, 0, 0.1);
            }}
            QSlider:focus {{
                outline: none;
            }}
        """

    def _apply_button_style(self, button):
        button.setStyleSheet(self._get_button_css())

    def _apply_slider_style(self, slider):
        slider.setStyleSheet(self._get_slider_css())

    def open_color_dialog(self, mode):
        if mode == "bg":
            current_color = self.config.get(
                "settings",
                "background_color",
                fallback="#f0f0f0",
            )
        else:
            current_color = self.config.get(
                "settings",
                "foreground_color",
                fallback="#000000",
            )

        color = QColorDialog.getColor(
            QColor(current_color),
            self,
            "Выберите цвет",
        )

        if not color.isValid():
            return

        if mode == "bg":
            self.config.set(
                "settings",
                "background_color",
                color.name(),
            )
        else:
            self.config.set(
                "settings",
                "foreground_color",
                color.name(),
            )

        self.apply_dynamic_style()

    def apply_dynamic_style(self):
        bg_hex = self.config.get(
            "settings",
            "background_color",
            fallback="#f0f0f0",
        )
        fg_hex = self.config.get(
            "settings",
            "foreground_color",
            fallback="#000000",
        )

        self.setStyleSheet(
            f"background-color: {bg_hex}; color: {fg_hex};"
        )

        for button in (
            self.btn_bg_color,
            self.btn_fg_color,
            self.btn_tutorial,
            self.btn_hint,
            self.btn_layout_hint,
            self.btn_save,
        ):
            self._apply_button_style(button)

        self._apply_slider_style(self.slider_trans)

        radio_style = self._get_radio_style()
        for radio_button in self.radio_buttons:
            radio_button.setStyleSheet(radio_style)

        checkbox_style = self._get_checkbox_style()
        for checkbox in (
            self.check_start_show,
            self.check_a,
            self.check_b,
        ):
            checkbox.setStyleSheet(checkbox_style)

    def run_tutorial(self):
        try:
            subprocess.Popen([sys.executable, "tutorial.pyw"])
        except Exception as error:
            print(f"Ошибка при запуске tutorial.pyw: {error}")

    def update_window_opacity(self, value):
        if value < 30:
            value = 30
            self.slider_trans.blockSignals(True)
            self.slider_trans.setValue(value)
            self.slider_trans.blockSignals(False)

        self.setWindowOpacity(value / 255.0)

    def save_settings(self):
        tryClose_path = os.path.join(os.path.dirname(__file__), "tryCloseScripts.pyw")

        result = subprocess.run(
            [sys.executable, tryClose_path],  # Использует тот же интерпретатор.
            timeout=30                      # Защита от торможения/фриза (в секундах)
        )

        last_run_is_compiled = self.config.get(
            "Script",
            "lastRunIsCompiled",
            fallback=".exe"  # значение по умолчанию, если ключа нет
        )

        if last_run_is_compiled == ".exe":
            exe_path = os.path.join(os.path.dirname(__file__), "Colemak-and-more.exe")
            os.startfile(exe_path)
        else:
            ahk_path = os.path.join(os.path.dirname(__file__), "Colemak-and-more.ahk")
            os.startfile(ahk_path)

        if not self.config.has_section("settings"):
            self.config.add_section("settings")

        self.config.set(
            "settings",
            "start_show_settings",
            str(self.check_start_show.isChecked()),
        )
        self.config.set(
            "settings",
            "CapsLock-eq-Escape",
            str(self.check_a.isChecked()),
        )
        self.config.set(
            "settings",
            "Alt+Apostrophe-eq-Enter",
            str(self.check_b.isChecked()),
        )

        selected_type = "Classic"
        for radio_button in self.radio_buttons:
            if radio_button.isChecked():
                selected_type = radio_button.text()
                break

        self.config.set(
            "settings",
            "Colemak_type",
            selected_type,
        )
        self.config.set(
            "settings",
            "background_color",
            self.config.get(
                "settings",
                "background_color",
                fallback="#f0f0f0",
            ),
        )
        self.config.set(
            "settings",
            "foreground_color",
            self.config.get(
                "settings",
                "foreground_color",
                fallback="#000000",
            ),
        )
        self.config.set(
            "settings",
            "background_transparency",
            str(self.slider_trans.value()),
        )

        with open("config.ini", "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

        print("Настройки сохранены!")
        
        QApplication.instance().quit()


    def show_hint_window(self):
        hint_text = (
            "Mouseless-подобный режим: Alt+,\n"
            "\n"
            "Двигать курсор — j, k, l и ;\n"
            "Колёсико мыши — w/e\n"
            "Левая и правая кнопки мыши — f и d\n"
            "Замедлить движение — a\n"
            "Прекратить управление курсором — s\n"
            "Эмуляция нажатия на колёсико мыши — v\n"
            "\n"
            "Alt+j — выбор из 16 положений курсора + дальнейшее "
            "уточнение в Mouseless-подобном режиме."
        )
        QMessageBox.information(
            self,
            "Подсказка по управлению",
            hint_text,
        )

    def show_layout_help(self):
        fg = self.config.get(
            "settings",
            "foreground_color",
            fallback="#000000",
        )
        bg = self.config.get(
            "settings",
            "background_color",
            fallback="#f0f0f0",
        )

        dialog = KeyboardHelpDialog(
            fg=fg,
            bg=bg,
            parent=self,
        )
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(
        "QToolTip { "
        "background-color: #ffe6b8; "
        "color: #000; "
        "border: 1px solid #cc9933; "
        "padding: 5px; "
        "border-radius: 4px; "
        "}"
    )

    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
