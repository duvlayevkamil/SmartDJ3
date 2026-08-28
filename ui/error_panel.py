"""
Xatoliklar paneli — SanPIN xatolari va ogohlantirishlari.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

PERIODS_PER_DAY = 6  # Kuniga maksimal 6 dars (7-dars yo'q)


class ErrorItem(QWidget):
    """Bitta xatolik yoki ogohlantirish elementi."""

    clicked = pyqtSignal(dict)

    def __init__(self, error_data, parent=None):
        super().__init__(parent)
        self.error_data = error_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        self.setLayout(layout)

        is_error = self.error_data.get('is_error', True)

        # Icon
        icon = "❌" if is_error else "⚠️"
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Xabar
        msg = self.error_data.get('message', '')
        msg_label = QLabel(msg)
        msg_label.setStyleSheet(f"""
            font-size: 12px;
            color: {"#E74C3C" if is_error else "#F39C12"};
            font-weight: {"bold" if is_error else "normal"};
        """)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label, 1)

        # Sinf
        cls_name = self.error_data.get('class_name', '')
        if cls_name:
            cls_label = QLabel(cls_name)
            cls_label.setStyleSheet("font-size: 11px; color: #7F8C8D; font-weight: bold;")
            cls_label.setFixedWidth(50)
            cls_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(cls_label)

        # Tugma
        go_btn = QPushButton("→")
        go_btn.setFixedSize(24, 24)
        go_btn.setStyleSheet(f"""
            QPushButton {{
                background: {"#E74C3C" if is_error else "#F39C12"};
                color: white; border: none; border-radius: 12px;
                font-weight: bold; font-size: 12px;
            }}
            QPushButton:hover {{ background: {"#C0392B" if is_error else "#E67E22"}; }}
        """)
        go_btn.clicked.connect(lambda: self.clicked.emit(self.error_data))
        layout.addWidget(go_btn)

    def enterEvent(self, event):
        self.setStyleSheet("background: #F8F9FA; border-radius: 4px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("")
        super().leaveEvent(event)


class ErrorPanel(QWidget):
    """SanPIN xatolari va ogohlantirishlari paneli."""

    error_clicked = pyqtSignal(int, int, int)  # class_id, day, period

    def __init__(self, parent=None):
        super().__init__(parent)
        self.errors = []
        self.warnings = []
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            ErrorPanel {
                background: #FDF2E9;
                border: 1px solid #E67E22;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        self.setLayout(layout)

        # Sarlavha
        header = QHBoxLayout()
        self.title_label = QLabel("📋 SanPIN hisoboti")
        self.title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2C3E50;")
        header.addWidget(self.title_label)

        self.count_label = QLabel("0 xatolik, 0 ogohlantirish")
        self.count_label.setStyleSheet("font-size: 11px; color: #7F8C8D;")
        header.addWidget(self.count_label)
        header.addStretch()

        clear_btn = QPushButton("🗑️")
        clear_btn.setFixedSize(24, 24)
        clear_btn.setStyleSheet("""
            QPushButton { background: #E74C3C; color: white; border: none; border-radius: 12px; }
            QPushButton:hover { background: #C0392B; }
        """)
        clear_btn.clicked.connect(self.clear)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)
        self.content_widget.setLayout(self.content_layout)

        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll, 1)

    def update_errors(self, timetable_data, classes, db_manager):
        """Xatolarni yangilash."""
        from core.sanpin import SanPINChecker

        self.clear()

        checker = SanPINChecker()

        for cls in classes:
            cls_id, cls_name = cls[0], cls[1]
            cls_level = cls[2] if len(cls) > 2 else 1

            # Sinf uchun jadval ma'lumotlarini yig'ish
            # 7x6 list formatiga aylantirish
            class_tt = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
            for key, info in timetable_data.items():
                if key[0] == cls_id:
                    day, period = key[1], key[2]
                    if period < PERIODS_PER_DAY and day < 6:
                        subj = info.get('subject_name', '') if isinstance(info, dict) else ''
                        class_tt[period][day] = subj

            # Bo'sh jadvalni tekshirmaslik
            has_lessons = any(class_tt[p][d] for p in range(PERIODS_PER_DAY) for d in range(6))
            if not has_lessons:
                continue

            # SanPIN tekshiruvi
            result = checker.check_timetable(class_tt, cls_level)

            # Xatoliklarni qo'shish
            for err in result.get('errors', []):
                # err string yoki dict bo'lishi mumkin
                if isinstance(err, dict):
                    msg = err.get('message', str(err))
                    day = err.get('day', 0)
                    period = err.get('period', 0)
                    rule = err.get('rule', '')
                else:
                    msg = str(err)
                    day = 0
                    period = 0
                    rule = ''

                error_data = {
                    'message': msg,
                    'class_id': cls_id,
                    'class_name': cls_name,
                    'day': day,
                    'period': period,
                    'is_error': True,
                    'rule': rule,
                }
                item = ErrorItem(error_data)
                item.clicked.connect(self._on_error_clicked)
                self.content_layout.addWidget(item)
                self.errors.append(error_data)

            # Ogohlantirishlarni qo'shish
            for warn in result.get('warnings', []):
                if isinstance(warn, dict):
                    wmsg = warn.get('message', str(warn))
                    wday = warn.get('day', 0)
                    wperiod = warn.get('period', 0)
                    wrule = warn.get('rule', '')
                else:
                    wmsg = str(warn)
                    wday = 0
                    wperiod = 0
                    wrule = ''

                warn_data = {
                    'message': wmsg,
                    'class_id': cls_id,
                    'class_name': cls_name,
                    'day': wday,
                    'period': wperiod,
                    'is_error': False,
                    'rule': wrule,
                }
                item = ErrorItem(warn_data)
                item.clicked.connect(self._on_error_clicked)
                self.content_layout.addWidget(item)
                self.warnings.append(warn_data)

        self.content_layout.addStretch()
        self._update_count()

    def _update_count(self):
        n_errors = len(self.errors)
        n_warnings = len(self.warnings)

        self.count_label.setText(f"{n_errors} xatolik, {n_warnings} ogohlantirish")

        if n_errors == 0 and n_warnings == 0:
            self.title_label.setText("✅ SanPIN qoidalariga rioya qilindi!")
            self.setStyleSheet("""
                ErrorPanel {
                    background: #D5F5E3;
                    border: 1px solid #27AE60;
                    border-radius: 8px;
                }
            """)
        elif n_errors == 0:
            self.title_label.setText("⚠️ Faqat ogohlantirishlar")
            self.setStyleSheet("""
                ErrorPanel {
                    background: #FEF9E7;
                    border: 1px solid #F39C12;
                    border-radius: 8px;
                }
            """)
        else:
            self.title_label.setText("❌ SanPIN xatolari mavjud")
            self.setStyleSheet("""
                ErrorPanel {
                    background: #FDF2E9;
                    border: 1px solid #E74C3C;
                    border-radius: 8px;
                }
            """)

    def _on_error_clicked(self, error_data):
        """Xatolik bosilganda."""
        self.error_clicked.emit(
            error_data.get('class_id', 0),
            error_data.get('day', 0),
            error_data.get('period', 0)
        )

    def clear(self):
        """Panelni tozalash."""
        self.errors.clear()
        self.warnings.clear()

        # Barcha child widgetlarni o'chirish
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self._update_count()

    def get_summary(self):
        """Xulosa ma'lumotlarini qaytarish."""
        return {
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'details': self.errors + self.warnings,
        }
