from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QLabel, QMessageBox, QSpinBox,
                             QComboBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class ClassroomWindow(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self.db = db_manager
        self.editing_id = None

        self.setWindowTitle("🚪 Xonalar boshqaruvi")
        self.setGeometry(200, 150, 900, 650)

        self.init_ui()
        self.load_classrooms()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # SARLAVHA
        title = QLabel("🚪 XONALAR BOSHQARUVI")
        title.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: white;
            background-color: #F39C12; padding: 15px; border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # QO'SHISH/TAHRIRLASH QISMI
        self.add_group = QGroupBox("➕ Yangi xona qo'shish")
        self.add_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold;
                border: 2px solid #F39C12; border-radius: 8px;
                margin-top: 10px; padding-top: 15px;
            }
        """)
        add_layout = QHBoxLayout()
        self.add_group.setLayout(add_layout)

        # Xona raqami
        add_layout.addWidget(QLabel("🚪 Xona raqami:"))
        self.input_number = QLineEdit()
        self.input_number.setPlaceholderText("201, 305, Lab-1...")
        self.input_number.setStyleSheet(self._input_style())
        self.input_number.setMaximumWidth(150)
        add_layout.addWidget(self.input_number)

        # Sig'imi
        add_layout.addWidget(QLabel("👥 Sig'imi:"))
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 100)
        self.capacity_spin.setValue(30)
        self.capacity_spin.setStyleSheet(self._input_style())
        self.capacity_spin.setMaximumWidth(80)
        add_layout.addWidget(self.capacity_spin)

        # Xona turi
        add_layout.addWidget(QLabel("🏷️ Turi:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Oddiy",
            "Fizika laboratoriyasi",
            "Kimyo laboratoriyasi",
            "Biologiya laboratoriyasi",
            "Informatika xonasi",
            "Til xonasi",
            "Sport zali",
            "San'at xonasi",
            "Mehnat xonasi",
            "Musiqa xonasi",
            "Kutubxona",
            "Boshqa"
        ])
        self.type_combo.setStyleSheet(self._input_style())
        self.type_combo.setMinimumWidth(200)
        add_layout.addWidget(self.type_combo)

        # Saqlash tugmasi
        self.btn_save = QPushButton("➕ Qo'shish")
        self.btn_save.clicked.connect(self.save_classroom)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        add_layout.addWidget(self.btn_save)

        # Bekor qilish (tahrirlashda)
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

        layout.addWidget(self.add_group)

        # STATISTIKA
        self.stats_label = QLabel("📊 Jami xonalar: 0 | Umumiy sig'imi: 0 o'rin")
        self.stats_label.setStyleSheet("""
            font-size: 13px; font-weight: bold;
            color: white; background-color: #2C3E50;
            padding: 10px; border-radius: 5px;
        """)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)

        # JADVAL
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Xona raqami", "Sig'imi", "Turi", "Holat"
        ])

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 250)
        self.table.setColumnWidth(4, 200)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; gridline-color: #ddd;
                font-size: 13px; color: #000000;
            }
            QTableWidget::item { padding: 10px; }
            QTableWidget::item:selected {
                background-color: #F39C12; color: white;
            }
            QHeaderView::section {
                background-color: #2C3E50; color: white;
                padding: 10px; font-weight: bold; border: none;
            }
        """)

        # Double-click bilan tahrirlash
        self.table.itemDoubleClicked.connect(self.edit_classroom)

        layout.addWidget(self.table)

        # TUGMALAR
        btn_layout = QHBoxLayout()

        btn_edit = QPushButton("✏️ Tahrirlash")
        btn_edit.clicked.connect(self.edit_classroom)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        btn_layout.addWidget(btn_edit)

        btn_delete = QPushButton("🗑️ O'chirish")
        btn_delete.clicked.connect(self.delete_classroom)
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
        btn_refresh.clicked.connect(self.load_classrooms)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #16A085; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #138D75; }
        """)
        btn_layout.addWidget(btn_refresh)

        btn_clear_all = QPushButton("🗑️ Tozalash")
        btn_clear_all.clicked.connect(self.clear_all_classrooms)
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

        # Info
        info = QLabel("💡 Tahrirlash uchun ikki marta bosing")
        info.setStyleSheet("font-size: 12px; color: #7F8C8D; font-style: italic;")
        btn_layout.addWidget(info)

        layout.addLayout(btn_layout)

    def _input_style(self):
        return """
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px; font-size: 13px;
                border: 2px solid #bdc3c7; border-radius: 5px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #F39C12;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #F39C12;
                selection-color: white;
            }
        """

    # ============ SAQLASH ============

    def save_classroom(self):
        """Xona qo'shish yoki yangilash"""
        room_number = self.input_number.text().strip()
        capacity = self.capacity_spin.value()
        room_type = self.type_combo.currentText()

        if not room_number:
            QMessageBox.warning(self, "Xatolik", "Xona raqamini kiriting!")
            return

        if self.editing_id:
            # TAHRIRLASH
            try:
                self.db.update_classroom(self.editing_id, room_number, capacity, room_type)

                QMessageBox.information(
                    self, "Muvaffaqiyat",
                    f"Xona yangilandi! ✅\n\n"
                    f"Xona: {room_number}\n"
                    f"Sig'imi: {capacity}\n"
                    f"Turi: {room_type}"
                )
                self.cancel_edit()
                self.load_classrooms()
            except Exception as e:
                QMessageBox.critical(
                    self, "Xatolik",
                    f"Yangilashda xatolik:\n{str(e)}"
                )
        else:
            # YANGI
            result = self.db.add_classroom(room_number, capacity, room_type)
            
            if result:
                QMessageBox.information(
                    self, "Muvaffaqiyat",
                    f"Xona qo'shildi! ✅\n\n"
                    f"Xona: {room_number}\n"
                    f"Sig'imi: {capacity}\n"
                    f"Turi: {room_type}"
                )
                self.clear_form()
                self.load_classrooms()
            else:
                QMessageBox.warning(
                    self, "Xatolik",
                    f"Xona qo'shilmadi!\nEhtimol bu xona allaqachon mavjud: {room_number}"
                )

    def clear_form(self):
        """Formani tozalash"""
        self.input_number.clear()
        self.capacity_spin.setValue(30)
        self.type_combo.setCurrentIndex(0)

    # ============ YUKLASH ============

    def load_classrooms(self):
        """Xonalarni yuklash"""
        classrooms = self.db.get_all_classrooms()
        self.table.setRowCount(0)

        total_capacity = 0

        for row_num, room in enumerate(classrooms):
            # room = (id, room_number, capacity, room_type)
            self.table.insertRow(row_num)

            # ID
            self.table.setItem(row_num, 0, QTableWidgetItem(str(room[0])))

            # Xona raqami
            number_item = QTableWidgetItem(room[1])
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = number_item.font()
            font.setBold(True)
            number_item.setFont(font)
            number_item.setForeground(QColor("#2C3E50"))
            self.table.setItem(row_num, 1, number_item)

            # Sig'imi
            capacity = room[2] if room[2] else 0
            capacity_item = QTableWidgetItem(f"{capacity} o'rin")
            capacity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if capacity >= 35:
                capacity_item.setForeground(QColor("#27AE60"))
            elif capacity >= 25:
                capacity_item.setForeground(QColor("#3498DB"))
            else:
                capacity_item.setForeground(QColor("#F39C12"))
            self.table.setItem(row_num, 2, capacity_item)

            # Turi (rang bilan)
            room_type = room[3] if room[3] else "Oddiy"
            type_item = QTableWidgetItem(self._get_type_icon(room_type))
            
            # Turiga qarab rang
            type_color = self._get_type_color(room_type)
            type_item.setForeground(QColor(type_color))
            self.table.setItem(row_num, 3, type_item)

            # Holat
            status_item = QTableWidgetItem("✅ Mavjud")
            status_item.setForeground(QColor("#27AE60"))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_num, 4, status_item)

            total_capacity += capacity

        # Statistika
        self.stats_label.setText(
            f"📊 Jami xonalar: {len(classrooms)} ta | "
            f"Umumiy sig'imi: {total_capacity} o'rin"
        )

    def _get_type_icon(self, room_type):
        """Xona turiga ikonka qo'shish"""
        icons = {
            "Oddiy": "🏫",
            "Fizika laboratoriyasi": "⚛️",
            "Kimyo laboratoriyasi": "🧪",
            "Biologiya laboratoriyasi": "🔬",
            "Informatika xonasi": "💻",
            "Til xonasi": "🗣️",
            "Sport zali": "🏃",
            "San'at xonasi": "🎨",
            "Mehnat xonasi": "🔨",
            "Musiqa xonasi": "🎵",
            "Kutubxona": "📚",
            "Boshqa": "📋"
        }
        icon = icons.get(room_type, "🏫")
        return f"{icon} {room_type}"

    def _get_type_color(self, room_type):
        """Xona turiga rang"""
        colors = {
            "Oddiy": "#2C3E50",
            "Fizika laboratoriyasi": "#3498DB",
            "Kimyo laboratoriyasi": "#9B59B6",
            "Biologiya laboratoriyasi": "#27AE60",
            "Informatika xonasi": "#16A085",
            "Til xonasi": "#E67E22",
            "Sport zali": "#E74C3C",
            "San'at xonasi": "#F39C12",
            "Mehnat xonasi": "#7F8C8D",
            "Musiqa xonasi": "#8E44AD",
            "Kutubxona": "#34495E",
            "Boshqa": "#95A5A6"
        }
        return colors.get(room_type, "#2C3E50")

    # ============ TAHRIRLASH ============

    def edit_classroom(self):
        """Xonani tahrirlash"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval xonani tanlang!")
            return

        classroom_id = int(self.table.item(current_row, 0).text())
        room_number = self.table.item(current_row, 1).text()
        capacity_text = self.table.item(current_row, 2).text()
        capacity = int(capacity_text.split()[0])
        type_text = self.table.item(current_row, 3).text()
        
        # Ikonkani olib tashlash
        room_type = type_text.split(" ", 1)[1] if " " in type_text else type_text

        # Formani to'ldirish
        self.input_number.setText(room_number)
        self.capacity_spin.setValue(capacity)
        
        # Turi combobox da topish
        for i in range(self.type_combo.count()):
            if self.type_combo.itemText(i) == room_type:
                self.type_combo.setCurrentIndex(i)
                break

        # Tahrirlash rejimi
        self.editing_id = classroom_id
        self.btn_save.setText("💾 Yangilash")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        self.btn_cancel.setVisible(True)
        self.add_group.setTitle("✏️ Xonani tahrirlash")

    def cancel_edit(self):
        """Tahrirlashni bekor qilish"""
        self.editing_id = None
        self.btn_save.setText("➕ Qo'shish")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        self.btn_cancel.setVisible(False)
        self.add_group.setTitle("➕ Yangi xona qo'shish")
        self.clear_form()

    # ============ O'CHIRISH ============

    def delete_classroom(self):
        """Xonani o'chirish"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval xonani tanlang!")
            return

        classroom_id = int(self.table.item(current_row, 0).text())
        room_number = self.table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"Xonani o'chirmoqchimisiz?\n\n"
            f"Xona: {room_number}\n\n"
            f"⚠️ Bu xonaga biriktirilgan darslar xona belgisi yo'qoladi!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_classroom(classroom_id)
            QMessageBox.information(self, "Muvaffaqiyat", "Xona o'chirildi! ✅")
            self.load_classrooms()

    def clear_all_classrooms(self):
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "Barcha xonalar o'chiriladi! Davom etasizmi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_classrooms()
            QMessageBox.information(self, "Muvaffaqiyat", "Barcha xonalar o'chirildi! ✅")
            self.load_classrooms()