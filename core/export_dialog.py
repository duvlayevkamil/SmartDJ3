"""
Export format tanlash — PDF, Excel, Word, HTML
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QGridLayout, QWidget)
from PyQt6.QtCore import Qt


class FormatSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chop etish")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint
                           | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.selected_format = None

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        self.setLayout(layout)

        h = QLabel("Chop etish formatini tanlang")
        h.setStyleSheet("font-size:18px; font-weight:bold; color:#2C3E50;")
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(h)

        layout.addSpacing(5)

        # Format tugmalari — grid layout
        grid = QGridLayout()
        grid.setSpacing(12)

        formats = [
            ("📄 PDF", "PDF formatda chop etish", "#E74C3C", "#FADBD8", "#C0392B", 'pdf'),
            ("📊 Excel", "Excel formatda chop etish", "#27AE60", "#D5F5E3", "#1E8449", 'excel'),
            ("📝 Word", "Word formatda chop etish", "#2980B9", "#D6EAF8", "#1F618D", 'word'),
            ("🌐 HTML", "HTML formatda saqlash", "#8E44AD", "#E8DAEF", "#6C3483", 'html'),
        ]

        for i, (icon, text, border_color, hover_bg, hover_border, fmt) in enumerate(formats):
            btn = QPushButton(f"{icon}\n{text}")
            btn.setMinimumHeight(70)
            btn.setStyleSheet(f"""
                QPushButton {{ background: white; color: #2C3E50; border: 2px solid {border_color};
                    border-radius: 10px; font-size: 14px; font-weight: bold; }}
                QPushButton:hover {{ background: {hover_bg}; border-color: {hover_border}; }}
            """)
            btn.clicked.connect(lambda checked, f=fmt: self._sel(f))
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)

        layout.addStretch()

        b3 = QPushButton("Bekor")
        b3.setStyleSheet(
            "QPushButton { background: #95A5A6; color: white; padding: 8px; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; border: none; }"
            "QPushButton:hover { background: #7F8C8D; }")
        b3.clicked.connect(self.reject)
        layout.addWidget(b3)

    def _sel(self, fmt):
        self.selected_format = fmt
        self.accept()
