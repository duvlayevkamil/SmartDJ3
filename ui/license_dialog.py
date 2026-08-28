"""
Litsenziya dialogi — SmartDJ3
Foydalanuvchiga litsenziya holatini ko'rsatish va kod kiritish.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QFrame,
    QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class LicenseDialog(QDialog):
    """Litsenziya ogohlantirish va faollashtirish dialogi"""

    def __init__(self, status, message, parent=None):
        super().__init__(parent)
        self.status = status
        self.message = message
        self.activated = False

        self.setWindowTitle("Litsenziya")
        self.setFixedSize(520, 420)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Sarlavha
        if self.status == "expired":
            header_text = "Litsenziya muddati tugadi"
            header_bg = "#E74C3C"
        else:
            header_text = "Sinov muddati tugadi"
            header_bg = "#F39C12"

        header = QLabel(header_text)
        header.setStyleSheet(f"""
            font-size: 18px; font-weight: bold; color: white;
            background-color: {header_bg}; padding: 14px;
            border-radius: 8px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Xabar
        msg = QLabel(self.message)
        msg.setStyleSheet("font-size: 12px; color: #2C3E50; padding: 4px;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)

        # Ajratuvchi chiziq
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #BDC3C7;")
        layout.addWidget(line)

        # Foydalanuvchi kodi
        from core.license import get_machine_id, generate_user_code
        machine_id = get_machine_id()
        user_code = generate_user_code(machine_id)

        code_label = QLabel("Sizning kodingiz (Muallifga yuboring):")
        code_label.setStyleSheet("font-size: 11px; color: #7F8C8D; font-weight: bold;")
        layout.addWidget(code_label)

        code_display = QLineEdit(user_code)
        code_display.setReadOnly(True)
        code_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_display.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: #2C3E50;
            background-color: #ECF0F1; padding: 10px;
            border: 2px solid #BDC3C7; border-radius: 6px;
            font-family: Consolas, monospace;
        """)
        layout.addWidget(code_display)

        # Nusxa olish tugmasi
        btn_copy = QPushButton("Nusxa olish")
        btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; color: white;
                padding: 6px 16px; font-size: 11px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        btn_copy.clicked.connect(lambda: self._copy_code(user_code))
        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        copy_layout.addWidget(btn_copy)
        copy_layout.addStretch()
        layout.addLayout(copy_layout)

        # Tasdiqlash kodi
        confirm_label = QLabel("Tasdiqlash kodini kiriting:")
        confirm_label.setStyleSheet("font-size: 11px; color: #7F8C8D; font-weight: bold; margin-top: 8px;")
        layout.addWidget(confirm_label)

        self.activation_input = QLineEdit()
        self.activation_input.setPlaceholderText("ACTV-XXXX-XXXX-XXXX")
        self.activation_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.activation_input.setStyleSheet("""
            font-size: 16px; font-weight: bold; color: #2C3E50;
            background-color: white; padding: 10px;
            border: 2px solid #3498DB; border-radius: 6px;
            font-family: Consolas, monospace;
        """)
        layout.addWidget(self.activation_input)

        # Tugmalar
        btn_layout = QHBoxLayout()

        btn_activate = QPushButton("Tasdiqlash")
        btn_activate.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 10px 30px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        btn_activate.clicked.connect(self._on_activate)
        btn_layout.addWidget(btn_activate)

        btn_close = QPushButton("Yopish")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6; color: white;
                padding: 10px 30px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7F8C8D; }
        """)
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _copy_code(self, code):
        """Foydalanuvchi kodini clipboardga nusxalash"""
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(code)

    def _on_activate(self):
        """Tasdiqlash kodini tekshirish"""
        code = self.activation_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Xatolik", "Tasdiqlash kodini kiriting!")
            return

        from core.license import activate
        success, msg = activate(code)

        if success:
            QMessageBox.information(self, "Muvaffaqiyat", msg)
            self.activated = True
            self.accept()
        else:
            QMessageBox.warning(self, "Xatolik", msg)
