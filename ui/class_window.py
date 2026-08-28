from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QLabel, QMessageBox, QSpinBox,
                             QComboBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import math


class ClassWindow(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self.db = db_manager
        self.editing_id = None  # Tahrirlash uchun

        self.setWindowTitle("🏫 Sinflar boshqaruvi")
        self.setGeometry(200, 150, 800, 600)

        self.init_ui()
        self.load_classes()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Sarlavha
        title = QLabel("🏫 SINFLAR BOSHQARUVI")
        title.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: white;
            background-color: #3498DB; padding: 15px; border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Qo'shish qismi
        add_group = QGroupBox("➕ Yangi sinf qo'shish")
        add_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold;
                border: 2px solid #3498DB; border-radius: 8px;
                margin-top: 10px; padding-top: 15px;
            }
        """)
        add_layout = QHBoxLayout()
        add_group.setLayout(add_layout)

        # Sinf darajasi
        add_layout.addWidget(QLabel("Sinf:"))
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 11)
        self.level_spin.setValue(1)
        self.level_spin.setStyleSheet(self._input_style())
        add_layout.addWidget(self.level_spin)

        # Harf
        add_layout.addWidget(QLabel("Harf:"))
        self.letter_combo = QComboBox()
        self.letter_combo.addItems(["A", "B", "V", "G", "D", "E"])
        self.letter_combo.setStyleSheet(self._input_style())
        add_layout.addWidget(self.letter_combo)

        # O'quvchilar soni
        add_layout.addWidget(QLabel("O'quvchilar:"))
        self.students_spin = QSpinBox()
        self.students_spin.setRange(1, 50)
        self.students_spin.setValue(25)
        self.students_spin.setStyleSheet(self._input_style())
        add_layout.addWidget(self.students_spin)

        # Ish kunlari
        add_layout.addWidget(QLabel("📅 Hafta kunlari:"))
        self.days_combo = QComboBox()
        self.days_combo.addItems(["5 kun (Dush-Juma)", "6 kun (Dush-Sha)"])
        self.days_combo.setCurrentIndex(1)  # 6 kun default
        self.days_combo.setStyleSheet(self._input_style())
        add_layout.addWidget(self.days_combo)

        # Tugmalar
        self.btn_add = QPushButton("➕ Qo'shish")
        self.btn_add.clicked.connect(self.save_class)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        add_layout.addWidget(self.btn_add)

        self.btn_cancel = QPushButton("✖ Bekor")
        self.btn_cancel.clicked.connect(self.cancel_edit)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7F8C8D; }
        """)
        self.btn_cancel.setVisible(False)
        add_layout.addWidget(self.btn_cancel)

        add_layout.addStretch()
        layout.addWidget(add_group)

        # Jadval
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["", "Sinf nomi", "Daraja", "O'quvchilar soni", "Kunlar", "Jami soatlar"]
        )

        self.table.setColumnHidden(0, True)  # ID ustuni yashirilgan
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 120)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; gridline-color: #ddd;
                font-size: 13px; color: #000000;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected {
                background-color: #3498DB; color: white;
            }
            QHeaderView::section {
                background-color: #2C3E50; color: white;
                padding: 10px; font-weight: bold; border: none;
            }
        """)

        layout.addWidget(self.table)

        # Double-click bilan tahrirlash
        self.table.itemDoubleClicked.connect(self.edit_class)

        # Tugmalar
        btn_layout = QHBoxLayout()

        btn_edit = QPushButton("✏️ Tahrirlash")
        btn_edit.clicked.connect(self.edit_class)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #F39C12; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E67E22; }
        """)
        btn_layout.addWidget(btn_edit)

        btn_delete = QPushButton("🗑️ O'chirish")
        btn_delete.clicked.connect(self.delete_class)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        btn_layout.addWidget(btn_delete)

        btn_refresh = QPushButton("🔄 Yangilash")
        btn_refresh.clicked.connect(self.load_classes)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        btn_layout.addWidget(btn_refresh)

        btn_clear_all = QPushButton("🗑️ Tozalash")
        btn_clear_all.clicked.connect(self.clear_all_classes)
        btn_clear_all.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        btn_layout.addWidget(btn_clear_all)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _input_style(self):
        return """
            QSpinBox, QComboBox {
                padding: 8px; font-size: 13px;
                border: 2px solid #bdc3c7; border-radius: 5px;
                min-width: 80px;
            }
            QSpinBox:focus, QComboBox:focus {
                border: 2px solid #3498DB;
            }
        """

    def add_class(self):
        """Sinf qo'shish (yangi)"""
        level = self.level_spin.value()
        letter = self.letter_combo.currentText()
        students = self.students_spin.value()

        days_idx = self.days_combo.currentIndex()
        working_days = 5 if days_idx == 0 else 6

        if level <= 4 and working_days == 6:
            reply = QMessageBox.question(
                self, "Tavsiya",
                f"{level}-sinf boshlang'ich sinf hisoblanadi.\n"
                f"Odatda 5 kun ishlaydi.\n\n"
                f"Baribir 6 kun qilinsinmi?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                working_days = 5

        name = f"{level}-{letter}"
        result = self.db.add_class(name, level, students, working_days)

        if result:
            QMessageBox.information(
                self, "Muvaffaqiyat",
                f"Sinf qo'shildi: {name} ✅\n"
                f"O'quvchilar: {students}\n"
                f"Hafta kunlari: {working_days}"
            )
            self.load_classes()
        else:
            QMessageBox.warning(
                self, "Xatolik",
                f"Bu sinf allaqachon mavjud: {name}"
            )

    def save_class(self):
        """Saqlash — yangi yoki tahrirlash"""
        if self.editing_id:
            self._update_class()
        else:
            self.add_class()

    def _update_class(self):
        """Sinfni yangilash"""
        level = self.level_spin.value()
        letter = self.letter_combo.currentText()
        students = self.students_spin.value()
        days_idx = self.days_combo.currentIndex()
        working_days = 5 if days_idx == 0 else 6

        name = f"{level}-{letter}"
        self.db.update_class(self.editing_id, name, level, students, working_days)

        QMessageBox.information(
            self, "Muvaffaqiyat",
            f"Sinf yangilandi: {name} ✅"
        )
        self.cancel_edit()
        self.load_classes()

    def edit_class(self):
        """Sinfni tahrirlash"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval sinfni tanlang!")
            return

        class_id = int(self.table.item(current_row, 0).text())
        class_name = self.table.item(current_row, 1).text()
        students_text = self.table.item(current_row, 3).text()

        # Sinf nomidan darajani ajratish: "5-A" → level=5, letter="A"
        parts = class_name.split("-")
        level = int(parts[0]) if parts else 1
        letter = parts[1] if len(parts) > 1 else "A"

        # Kunlarni aniqlash
        days_text = self.table.item(current_row, 4).text()
        working_days = 5 if "5" in days_text else 6

        # Formani to'ldirish
        self.level_spin.setValue(level)
        idx = self.letter_combo.findText(letter)
        if idx >= 0:
            self.letter_combo.setCurrentIndex(idx)
        self.students_spin.setValue(int(students_text))
        self.days_combo.setCurrentIndex(0 if working_days == 5 else 1)

        # Tahrirlash rejimi
        self.editing_id = class_id
        self.btn_add.setText("💾 Yangilash")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #F39C12; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E67E22; }
        """)
        self.btn_cancel.setVisible(True)

    def cancel_edit(self):
        """Tahrirlashni bekor qilish"""
        self.editing_id = None
        self.btn_add.setText("➕ Qo'shish")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        self.btn_cancel.setVisible(False)
        self.level_spin.setValue(1)
        self.letter_combo.setCurrentIndex(0)
        self.students_spin.setValue(25)
        self.days_combo.setCurrentIndex(1)

    def load_classes(self):
        classes = self.db.get_all_classes()
        self.table.setRowCount(0)

        # Tayanch rejadagi ma'lumotlarni oldindan yuklash
        tayanch = self.db.load_tayanch_reja()
        tayanch_by_level = {}
        for item in tayanch:
            level = item['class_level']
            tayanch_by_level[level] = tayanch_by_level.get(level, 0) + item['weekly_hours']

        for row_num, cls in enumerate(classes):
            self.table.insertRow(row_num)
            # cls = (id, name, level, students_count, working_days, created_at)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(cls[0])))
            self.table.setItem(row_num, 1, QTableWidgetItem(cls[1]))
            self.table.setItem(row_num, 2, QTableWidgetItem(f"{cls[2]}-sinf"))
            self.table.setItem(row_num, 3, QTableWidgetItem(str(cls[3])))

            working_days = cls[4] if len(cls) > 4 and cls[4] else 6
            days_item = QTableWidgetItem(f"{working_days} kun")
            if working_days == 5:
                days_item.setForeground(QColor("#27AE60"))
            else:
                days_item.setForeground(QColor("#3498DB"))
            self.table.setItem(row_num, 4, days_item)

            # Jami soatlar — tayanch rejadan
            level = cls[2]
            total = tayanch_by_level.get(level, 0)
            if total > 0:
                hours_item = QTableWidgetItem(str(total))
                hours_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                hours_item.setForeground(QColor("#2C3E50"))
            else:
                hours_item = QTableWidgetItem("")
            self.table.setItem(row_num, 5, hours_item)

    def delete_class(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval sinfni tanlang!")
            return

        class_id = int(self.table.item(current_row, 0).text())
        class_name = self.table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"{class_name} ni o'chirmoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_class(class_id)
            QMessageBox.information(self, "Muvaffaqiyat", "Sinf o'chirildi! ✅")
            self.load_classes()

    def clear_all_classes(self):
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "Barcha sinflar o'chiriladi! Davom etasizmi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_classes()
            QMessageBox.information(self, "Muvaffaqiyat", "Barcha sinflar o'chirildi! ✅")
            self.load_classes()