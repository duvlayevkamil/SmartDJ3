"""
MUALLIF UCHUN LITSENZIYA GENERATOR — QT GUI
Foydalanuvchi kodini kiritish → Tasdiqlash kodini olish

Ishlatish:
  python tools/activate_gui_qt.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from core.license import generate_activation_code, verify_activation_code


class LicenseGenerator(QMainWindow):
    """Litsenziya generator oynasi — muallif uchun"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartDJ3 — Litsenziya Generator")
        self.setFixedSize(500, 350)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        central.setLayout(layout)

        # Sarlavha
        title = QLabel("🔑 SMARTDJ3 LITSENZIYA GENERATOR")
        title.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: white;
            background-color: #2C3E50; padding: 15px;
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Foydalanuvchi kodi
        user_label = QLabel("Foydalanuvchi kodini kiriting:")
        user_label.setStyleSheet("font-size: 12px; color: #7F8C8D; font-weight: bold;")
        layout.addWidget(user_label)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("ABCD-1234-EFGH-5678")
        self.user_input.setStyleSheet("""
            font-size: 16px; font-weight: bold; color: #2C3E50;
            background-color: white; padding: 10px;
            border: 2px solid #3498DB; border-radius: 6px;
            font-family: Consolas, monospace;
        """)
        self.user_input.textChanged.connect(self._on_user_code_changed)
        layout.addWidget(self.user_input)

        # Ajratuvchi
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #BDC3C7;")
        layout.addWidget(line)

        # Tasdiqlash kodi
        result_label = QLabel("Tasdiqlash kodi:")
        result_label.setStyleSheet("font-size: 12px; color: #7F8C8D; font-weight: bold;")
        layout.addWidget(result_label)

        self.result_display = QLineEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_display.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: #27AE60;
            background-color: #EAFAF1; padding: 10px;
            border: 2px solid #27AE60; border-radius: 6px;
            font-family: Consolas, monospace;
        """)
        layout.addWidget(self.result_display)

        # Tugmalar
        btn_layout = QHBoxLayout()

        btn_generate = QPushButton("⚡ Generatsiya qilish")
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        btn_generate.clicked.connect(self._on_generate)
        btn_layout.addWidget(btn_generate)

        btn_copy = QPushButton("📋 Nusxa olish")
        btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        btn_copy.clicked.connect(self._on_copy)
        btn_layout.addWidget(btn_copy)

        layout.addLayout(btn_layout)

    def _on_user_code_changed(self, text):
        """Foydalanuvchi kodi o'zgarganda — avtomatik generatsiya"""
        if len(text.replace("-", "").replace(" ", "")) == 16:
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
                font-size: 18px; font-weight: bold; color: #27AE60;
                background-color: #EAFAF1; padding: 10px;
                border: 2px solid #27AE60; border-radius: 6px;
                font-family: Consolas, monospace;
            """)
        else:
            self.result_display.setStyleSheet("""
                font-size: 18px; font-weight: bold; color: #E74C3C;
                background-color: #FDEDEC; padding: 10px;
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

    window = LicenseGenerator()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
