"""
Monitoring rejimi — Real vaqtda dars jadvalini kuzatish.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFrame, QGridLayout, QScrollArea, QPushButton, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from datetime import datetime


KUNLAR = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]
KUN_QISQA = ["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan"]

# Dars vaqtlari (taxminiy)
DARS_VAQTLARI = [
    ("08:00", "08:45"),
    ("08:55", "09:40"),
    ("09:50", "10:35"),
    ("10:45", "11:30"),
    ("11:40", "12:25"),
    ("12:35", "13:20"),
    ("13:30", "14:15"),
]


class MonitoringWindow(QWidget):
    """Real vaqtda dars jadvalini kuzatish oynasi."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager

        self.setWindowTitle("📊 Monitoring — Real vaqt kuzatish")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 800)

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self._setup_ui()
        self._load_data()
        self._update_display()

        # Har 60 sekundda yangilash
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_display)
        self.timer.start(60000)

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.setLayout(layout)

        # Sarlavha
        header = QHBoxLayout()
        title = QLabel("📊 MONITORING REJIMI")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50;")
        header.addWidget(title)

        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 14px; color: #7F8C8D; font-weight: bold;")
        header.addWidget(self.time_label)
        header.addStretch()

        refresh_btn = QPushButton("🔄 Yangilash")
        refresh_btn.setStyleSheet(
            "QPushButton { background: #3498DB; color: white; padding: 8px 16px; "
            "border-radius: 5px; font-weight: bold; border: none; }"
            "QPushButton:hover { background: #2980B9; }"
        )
        refresh_btn.clicked.connect(self._update_display)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Demo rejim paneli
        demo_layout = QHBoxLayout()
        demo_layout.setSpacing(8)

        self.demo_check = QCheckBox("🎮 Demo rejim")
        self.demo_check.setStyleSheet("""
            QCheckBox {
                font-size: 12px; font-weight: bold; color: #2C3E50;
                background: #ECF0F1; padding: 6px 12px; border-radius: 5px;
                border: 2px solid #BDC3C7;
            }
            QCheckBox:hover { background: #D5DBDB; border-color: #95A5A6; }
            QCheckBox:checked { background: #8E44AD; color: white; border-color: #8E44AD; }
            QCheckBox::indicator { width: 16px; height: 16px; }
        """)
        self.demo_check.toggled.connect(self._on_demo_toggled)
        demo_layout.addWidget(self.demo_check)

        demo_day_label = QLabel("Kun:")
        demo_day_label.setStyleSheet("font-size: 11px; color: #7F8C8D;")
        demo_layout.addWidget(demo_day_label)

        self.demo_day_combo = QComboBox()
        self.demo_day_combo.addItems(KUNLAR)
        self.demo_day_combo.setStyleSheet("padding: 4px; font-size: 11px; min-width: 120px;")
        self.demo_day_combo.currentIndexChanged.connect(self._on_demo_changed)
        demo_layout.addWidget(self.demo_day_combo)

        demo_period_label = QLabel("Dars:")
        demo_period_label.setStyleSheet("font-size: 11px; color: #7F8C8D;")
        demo_layout.addWidget(demo_period_label)

        self.demo_period_combo = QComboBox()
        for i, (start, end) in enumerate(DARS_VAQTLARI):
            self.demo_period_combo.addItem(f"{i+1}-dars ({start}-{end})")
        self.demo_period_combo.setStyleSheet("padding: 4px; font-size: 11px; min-width: 150px;")
        self.demo_period_combo.currentIndexChanged.connect(self._on_demo_changed)
        demo_layout.addWidget(self.demo_period_combo)

        demo_layout.addStretch()

        # Demo rejim default: o'chirilgan
        self.demo_check.setChecked(False)
        self.demo_day_combo.setEnabled(False)
        self.demo_period_combo.setEnabled(False)

        layout.addLayout(demo_layout)

        # Hozirgi dars ma'lumoti
        self.current_info = QLabel()
        self.current_info.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: white; "
            "background: #27AE60; padding: 12px; border-radius: 8px;"
        )
        self.current_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.current_info)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #BDC3C7; border-radius: 5px; }
            QTabBar::tab { background: #ECF0F1; padding: 10px 20px; font-weight: bold; }
            QTabBar::tab:selected { background: #3498DB; color: white; }
        """)

        # Tab 1: Sinf bo'yicha
        self.class_tab = self._create_class_tab()
        self.tabs.addTab(self.class_tab, "🏫 Sinflar")

        # Tab 2: O'qituvchilar
        self.teacher_tab = self._create_teacher_tab()
        self.tabs.addTab(self.teacher_tab, "👨‍🏫 O'qituvchilar")

        # Tab 3: Xonalar
        self.room_tab = self._create_room_tab()
        self.tabs.addTab(self.room_tab, "🚪 Xonalar")

        layout.addWidget(self.tabs, 1)

    def _create_class_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        widget.setLayout(layout)

        self.class_table = QTableWidget()
        self.class_table.setAlternatingRowColors(True)
        self.class_table.setStyleSheet("""
            QTableWidget { background: white; gridline-color: #BDC3C7; font-size: 12px; color: #000000; }
            QHeaderView::section { background: #2C3E50; color: white; padding: 8px; font-weight: bold; }
        """)
        self.class_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.class_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.class_table.verticalHeader().setVisible(False)
        layout.addWidget(self.class_table)

        return widget

    def _create_teacher_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        widget.setLayout(layout)

        self.teacher_table = QTableWidget()
        self.teacher_table.setAlternatingRowColors(True)
        self.teacher_table.setStyleSheet("""
            QTableWidget { background: white; gridline-color: #BDC3C7; font-size: 12px; color: #000000; }
            QHeaderView::section { background: #2C3E50; color: white; padding: 8px; font-weight: bold; }
        """)
        self.teacher_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.teacher_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.teacher_table.verticalHeader().setVisible(False)
        layout.addWidget(self.teacher_table)

        return widget

    def _create_room_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        widget.setLayout(layout)

        self.room_table = QTableWidget()
        self.room_table.setAlternatingRowColors(True)
        self.room_table.setStyleSheet("""
            QTableWidget { background: white; gridline-color: #BDC3C7; font-size: 12px; color: #000000; }
            QHeaderView::section { background: #2C3E50; color: white; padding: 8px; font-weight: bold; }
        """)
        self.room_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.room_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.room_table.verticalHeader().setVisible(False)
        layout.addWidget(self.room_table)

        return widget

    def _load_data(self):
        """Ma'lumotlarni bazadan yuklash."""
        self.classes = self.db.get_all_classes()
        self.teachers = self.db.get_all_teachers()
        self.classrooms = self.db.get_all_classrooms()
        self.scheduled = self.db.load_scheduled_lessons()

    def _on_demo_toggled(self, checked):
        """Demo rejim yoqish/o'chirish."""
        self.demo_day_combo.setEnabled(checked)
        self.demo_period_combo.setEnabled(checked)
        self._update_display()

    def _on_demo_changed(self):
        """Demo rejimda kun/dars o'zgarganda."""
        if self.demo_check.isChecked():
            self._update_display()

    def _get_current_period(self):
        """Hozirgi kun va dars vaqtini aniqlash."""
        # Demo rejimda tanlangan kun/dars ishlatiladi
        if self.demo_check.isChecked():
            day_idx = self.demo_day_combo.currentIndex()
            period_idx = self.demo_period_combo.currentIndex()
            return day_idx, period_idx

        now = datetime.now()
        weekday = now.weekday()  # 0=Dushanba, 6=Yakshanba

        if weekday >= 6:  # Yakshanba
            return None, None

        current_time = now.strftime("%H:%M")

        for i, (start, end) in enumerate(DARS_VAQTLARI):
            if start <= current_time <= end:
                return weekday, i

        # Dars vaqti tugagan yoki hali boshlanmagan
        return weekday, None

    def _update_display(self):
        """Display ni yangilash."""
        now = datetime.now()
        self.time_label.setText(f"🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}")

        day_idx, period_idx = self._get_current_period()

        if self.demo_check.isChecked():
            # Demo rejimda
            self.current_info.setText(
                f"🎮 DEMO — {KUNLAR[day_idx]} — {period_idx + 1}-dars "
                f"({DARS_VAQTLARI[period_idx][0]}-{DARS_VAQTLARI[period_idx][1]})"
            )
            self.current_info.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: white; "
                "background: #8E44AD; padding: 12px; border-radius: 8px;"
            )
        elif day_idx is None:
            self.current_info.setText("📅 Hozir dars vaqti emas")
            self.current_info.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: white; "
                "background: #95A5A6; padding: 12px; border-radius: 8px;"
            )
        elif period_idx is None:
            self.current_info.setText(f"📅 {KUNLAR[day_idx]} — Darslar tugagan yoki hali boshlanmagan")
            self.current_info.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: white; "
                "background: #F39C12; padding: 12px; border-radius: 8px;"
            )
        else:
            self.current_info.setText(
                f"📅 {KUNLAR[day_idx]} — {period_idx + 1}-dars "
                f"({DARS_VAQTLARI[period_idx][0]}-{DARS_VAQTLARI[period_idx][1]})"
            )
            self.current_info.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: white; "
                "background: #27AE60; padding: 12px; border-radius: 8px;"
            )

        self._update_class_table(day_idx, period_idx)
        self._update_teacher_table(day_idx, period_idx)
        self._update_room_table(day_idx, period_idx)

    def _update_class_table(self, day_idx, period_idx):
        """Sinf jadvalini yangilash."""
        self.class_table.clearContents()

        headers = ["Sinf", "Hozirgi dars", "O'qituvchi", "Xona", "Holat"]
        self.class_table.setColumnCount(len(headers))
        self.class_table.setHorizontalHeaderLabels(headers)
        self.class_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.class_table.setRowCount(len(self.classes))

        for row, cls in enumerate(self.classes):
            cls_id, cls_name = cls[0], cls[1]

            # Sinf nomi
            name_item = QTableWidgetItem(cls_name)
            name_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.class_table.setItem(row, 0, name_item)

            if day_idx is not None and period_idx is not None:
                # Hozirgi darsni topish
                lesson = self.scheduled.get((cls_id, day_idx, period_idx))
                if lesson:
                    subject_item = QTableWidgetItem(lesson.get('subject_name', ''))
                    teacher_item = QTableWidgetItem(lesson.get('teacher_name', ''))
                    self.class_table.setItem(row, 1, subject_item)
                    self.class_table.setItem(row, 2, teacher_item)

                    # Xona (hozircha bo'sh)
                    self.class_table.setItem(row, 3, QTableWidgetItem("-"))

                    # Holat
                    status_item = QTableWidgetItem("✅ O'tmoqda")
                    status_item.setForeground(QColor("#27AE60"))
                    self.class_table.setItem(row, 4, status_item)
                else:
                    self.class_table.setItem(row, 1, QTableWidgetItem("-"))
                    self.class_table.setItem(row, 2, QTableWidgetItem("-"))
                    self.class_table.setItem(row, 3, QTableWidgetItem("-"))
                    status_item = QTableWidgetItem("⏸️ Tanaffus")
                    status_item.setForeground(QColor("#F39C12"))
                    self.class_table.setItem(row, 4, status_item)
            else:
                for col in range(1, 5):
                    self.class_table.setItem(row, col, QTableWidgetItem("-"))
                status_item = QTableWidgetItem("⏹️ Kutilmoqda")
                status_item.setForeground(QColor("#95A5A6"))
                self.class_table.setItem(row, 4, status_item)

    def _update_teacher_table(self, day_idx, period_idx):
        """O'qituvchi jadvalini yangilash."""
        self.teacher_table.clearContents()

        headers = ["O'qituvchi", "Hozirgi dars", "Sinf", "Xona", "Holat"]
        self.teacher_table.setColumnCount(len(headers))
        self.teacher_table.setHorizontalHeaderLabels(headers)
        self.teacher_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.teacher_table.setRowCount(len(self.teachers))

        for row, teacher in enumerate(self.teachers):
            t_id, t_name = teacher[0], teacher[1]

            name_item = QTableWidgetItem(t_name)
            name_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.teacher_table.setItem(row, 0, name_item)

            if day_idx is not None and period_idx is not None:
                # O'qituvchining hozirgi darsini topish
                found = False
                for key, lesson in self.scheduled.items():
                    if (lesson.get('teacher_id') == t_id and
                        key[1] == day_idx and key[2] == period_idx):
                        self.teacher_table.setItem(row, 1, QTableWidgetItem(lesson.get('subject_name', '')))
                        self.teacher_table.setItem(row, 2, QTableWidgetItem(lesson.get('class_name', '')))
                        self.teacher_table.setItem(row, 3, QTableWidgetItem("-"))
                        status_item = QTableWidgetItem("✅ Dars o'tmoqda")
                        status_item.setForeground(QColor("#27AE60"))
                        self.teacher_table.setItem(row, 4, status_item)
                        found = True
                        break

                if not found:
                    for col in range(1, 4):
                        self.teacher_table.setItem(row, col, QTableWidgetItem("-"))
                    status_item = QTableWidgetItem("⏸️ Bo'sh")
                    status_item.setForeground(QColor("#F39C12"))
                    self.teacher_table.setItem(row, 4, status_item)
            else:
                for col in range(1, 5):
                    self.teacher_table.setItem(row, col, QTableWidgetItem("-"))
                status_item = QTableWidgetItem("⏹️ Kutilmoqda")
                status_item.setForeground(QColor("#95A5A6"))
                self.teacher_table.setItem(row, 4, status_item)

    def _update_room_table(self, day_idx, period_idx):
        """Xona jadvalini yangilash."""
        self.room_table.clearContents()

        headers = ["Xona", "Turi", "Sig'im", "Hozirgi dars", "Holat"]
        self.room_table.setColumnCount(len(headers))
        self.room_table.setHorizontalHeaderLabels(headers)
        self.room_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.room_table.setRowCount(len(self.classrooms))

        for row, room in enumerate(self.classrooms):
            r_id, r_number, r_capacity, r_type = room[0], room[1], room[2], room[3]

            self.room_table.setItem(row, 0, QTableWidgetItem(str(r_number)))
            self.room_table.setItem(row, 1, QTableWidgetItem(r_type or "-"))
            self.room_table.setItem(row, 2, QTableWidgetItem(str(r_capacity)))

            if day_idx is not None and period_idx is not None:
                # Xonada hozir dars o'tayotganini tekshirish
                occupied = False
                for key, lesson in self.scheduled.items():
                    if key[1] == day_idx and key[2] == period_idx:
                        # Xona hali integration qilinmagan
                        pass

                if not occupied:
                    self.room_table.setItem(row, 3, QTableWidgetItem("-"))
                    status_item = QTableWidgetItem("✅ Bo'sh")
                    status_item.setForeground(QColor("#27AE60"))
                    self.room_table.setItem(row, 4, status_item)
            else:
                self.room_table.setItem(row, 3, QTableWidgetItem("-"))
                status_item = QTableWidgetItem("⏹️ Kutilmoqda")
                status_item.setForeground(QColor("#95A5A6"))
                self.room_table.setItem(row, 4, status_item)

    def bring_to_front(self):
        """Oynani oldingi planiga chiqarish."""
        self.setWindowState(Qt.WindowState.WindowNoState)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
