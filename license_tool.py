"""
SmartDJ3 Litsenziya Generator — Muallif uchun mustaqil dastur
"""
import sys
import os

# Resource path — PyInstaller bundle uchun
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Core modulni import qilish
sys.path.insert(0, resource_path('.'))
from core.license import generate_activation_code, verify_activation_code

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QClipboard


class LicenseGenerator(QMainWindow):
    """Litsenziya generator oynasi — muallif uchun"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartDJ3 — Litsenziya Generator")
        self.setFixedSize(520, 420)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        central.setLayout(layout)

        # Sarlavha
        title = QLabel("SMARTDJ3 LITSENZIYA GENERATOR")
        title.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: white;
            background-color: #2C3E50; padding: 15px;
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Muallif
        author = QLabel("Duvlayev Kamil Abdurashidovich")
        author.setStyleSheet("font-size: 11px; color: #7F8C8D; text-align: center;")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author)

        # Foydalanuvchi kodi
        user_group = QGroupBox("1. Foydalanuvchi kodini kiriting")
        user_group.setStyleSheet("""
            QGroupBox {
                font-size: 12px; font-weight: bold; color: #2C3E50;
                border: 1px solid #BDC3C7; border-radius: 6px;
                margin-top: 10px; padding-top: 15px;
            }
        """)
        user_layout = QVBoxLayout()
        user_group.setLayout(user_layout)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("ABCD-1234-EFGH-5678")
        self.user_input.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: #2C3E50;
            background-color: white; padding: 12px;
            border: 2px solid #3498DB; border-radius: 6px;
            font-family: Consolas, monospace;
        """)
        self.user_input.textChanged.connect(self._on_user_code_changed)
        user_layout.addWidget(self.user_input)

        layout.addWidget(user_group)

        # Tasdiqlash kodi
        result_group = QGroupBox("2. Tasdiqlash kodi (Foydalanuvchiga bering)")
        result_group.setStyleSheet("""
            QGroupBox {
                font-size: 12px; font-weight: bold; color: #2C3E50;
                border: 1px solid #27AE60; border-radius: 6px;
                margin-top: 10px; padding-top: 15px;
            }
        """)
        result_layout = QVBoxLayout()
        result_group.setLayout(result_layout)

        self.result_display = QLineEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_display.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: #27AE60;
            background-color: #EAFAF1; padding: 12px;
            border: 2px solid #27AE60; border-radius: 6px;
            font-family: Consolas, monospace;
        """)
        result_layout.addWidget(self.result_display)

        layout.addWidget(result_group)

        # Tugmalar
        btn_layout = QHBoxLayout()

        btn_generate = QPushButton("GENERATSIYA QILISH")
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 12px 25px; font-size: 14px;
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        btn_generate.clicked.connect(self._on_generate)
        btn_layout.addWidget(btn_generate)

        btn_copy = QPushButton("NUSXA OLISH")
        btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; color: white;
                padding: 12px 25px; font-size: 14px;
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        btn_copy.clicked.connect(self._on_copy)
        btn_layout.addWidget(btn_copy)

        layout.addLayout(btn_layout)

        # Footer
        footer = QLabel("Telegram: @DUVLAYEV_KAMI | Tel: +998 77-500-04-69")
        footer.setStyleSheet("font-size: 10px; color: #95A5A6; text-align: center;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def _on_user_code_changed(self, text):
        """Foydalanuvchi kodi o'zgarganda — avtomatik generatsiya"""
        clean = text.replace("-", "").replace(" ", "")
        if len(clean) == 16:
            self._on_generate()

    def _on_generate(self):
        """Tasdiqlash kodini generatsiya qilish"""
        user_code = self.user_input.text().strip()
        if not user_code:
            return

        activation_code = generate_activation_code(user_code)
        self.result_display.setText(activation_code)

        # Tekshirish
        is_valid = verify_activation_code(user_code, activation_code)
        if is_valid:
            self.result_display.setStyleSheet("""
                font-size: 20px; font-weight: bold; color: #27AE60;
                background-color: #EAFAF1; padding: 12px;
                border: 2px solid #27AE60; border-radius: 6px;
                font-family: Consolas, monospace;
            """)
        else:
            self.result_display.setStyleSheet("""
                font-size: 20px; font-weight: bold; color: #E74C3C;
                background-color: #FDEDEC; padding: 12px;
                border: 2px solid #E74C3C; border-radius: 6px;
                font-family: Consolas, monospace;
            """)

    def _on_copy(self):
        """Tasdiqlash kodini clipboardga nusxalash"""
        code = self.result_display.text()
        if code:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(code)
                QMessageBox.information(self, "Nusxalandi",
                    f"Tasdiqlash kodi nusxalandi:\n\n{code}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Yorug' tema
    from PyQt6.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    app.setPalette(palette)

    window = LicenseGenerator()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
