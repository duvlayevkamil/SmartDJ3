from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QMessageBox, QComboBox, QSpinBox,
                             QDoubleSpinBox,
                             QGroupBox, QSplitter, QWidget, QListWidget,
                             QListWidgetItem, QInputDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont


class AssignmentWindow(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self.db = db_manager
        self.current_teacher_id = None
        self.current_teacher_name = ""
        self.editing_assignment_id = None  # Tahrirlash uchun

        self.setWindowTitle("📝 O'qituvchilar darslari")
        self.setGeometry(80, 50, 1200, 750)

        # Oldingi qadam tekshiruvi
        if not self.check_prerequisites():
            return

        self.init_ui()
        self.load_teachers()

    def check_prerequisites(self):
        """Oldingi qadamlar mavjudligini tekshirish"""
        missing = []
        buttons = []

        classes = self.db.get_all_classes()
        subjects = self.db.get_all_subjects()
        teachers = self.db.get_all_teachers()

        if not classes:
            missing.append("🏫 Sinflar")
            buttons.append(("Sinflar qo'shish", "classes"))
        if not subjects:
            missing.append("📚 Fanlar")
            buttons.append(("Fanlar qo'shish", "subjects"))
        if not teachers:
            missing.append("👨‍🏫 O'qituvchilar")
            buttons.append(("O'qituvchilar qo'shish", "teachers"))

        if not missing:
            return True

        # Ogohlantirish oynasi
        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️ Ma'lumot yetarli emas")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("Dars biriktirish uchun quyidagi ma'lumotlar kerak:")
        msg.setInformativeText(
            "Quydagilar topilmadi:\n" +
            "\n".join(f"  • {m}" for m in missing) +
            "\n\nAvval ularni qo'shing!"
        )

        for btn_text, entity in buttons:
            msg.addButton(btn_text, QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Close)

        msg.exec()

        # Tugmalar bosilganda oynalarni ochish
        clicked = msg.clickedButton()
        for btn_text, entity in buttons:
            if clicked and clicked.text() == btn_text:
                self._open_missing_window(entity)
                break

        return False

    def _open_missing_window(self, entity):
        """Yetishmayotgan oynani ochish"""
        if entity == "classes":
            from ui.class_window import ClassWindow
            win = ClassWindow(self.db)
            win.exec()
        elif entity == "subjects":
            from ui.subject_window import SubjectWindow
            win = SubjectWindow(self.db)
            win.exec()
        elif entity == "teachers":
            from ui.teacher_window import TeacherWindow
            win = TeacherWindow(self.db)
            win.exec()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        # SARLAVHA (kichikroq)
        title = QLabel("📝 O'QITUVCHILAR DARSLARI")
        title.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: white;
            background-color: #16A085; padding: 12px; border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(50)  # Maksimal balandlik
        layout.addWidget(title)

        # ⏱️ MAKSIMAL SOAT TUGMASI — alohida, ajralib turadigan
        btn_max_hours = QPushButton("👨‍🏫 O'qituvchilarga maksimal dars soatini belgilash")
        btn_max_hours.clicked.connect(self.set_max_hours)
        btn_max_hours.setStyleSheet("""
            QPushButton {
                font-size: 14px; font-weight: bold; color: white;
                background-color: #8E44AD; padding: 12px 20px;
                border-radius: 8px; border: 3px solid #7D3C98;
            }
            QPushButton:hover { background-color: #7D3C98; }
            QPushButton:pressed { background-color: #6C3483; }
        """)
        btn_max_hours.setFixedHeight(45)
        layout.addWidget(btn_max_hours)

        # SPLITTER - 2 ta panel
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # CHAP PANEL - O'qituvchilar ro'yxati
        left_widget = self.create_teachers_panel()
        splitter.addWidget(left_widget)

        # O'NG PANEL - Darslar
        right_widget = self.create_lessons_panel()
        splitter.addWidget(right_widget)

        # Splitter o'lchamlari
        splitter.setSizes([300, 900])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter, 1)  # 1 - stretch factor

    # ============ CHAP PANEL ============

    def create_teachers_panel(self):
        """O'qituvchilar ro'yxati paneli"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        widget.setLayout(layout)

        # Sarlavha
        title = QLabel("👨‍🏫 O'QITUVCHILAR")
        title.setStyleSheet("""
            font-size: 13px; font-weight: bold; color: white;
            background-color: #2C3E50; padding: 10px; border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(40)
        layout.addWidget(title)

        # Info
        info_label = QLabel("💡 O'qituvchini tanlang")
        info_label.setStyleSheet("""
            font-size: 11px; color: #7F8C8D;
            padding: 6px; background-color: #ECF0F1;
            border-radius: 4px;
        """)
        info_label.setFixedHeight(30)
        layout.addWidget(info_label)

        # O'qituvchilar ro'yxati
        self.teachers_list = QListWidget()
        self.teachers_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 12px; color: #000000;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ECF0F1;
            }
            QListWidget::item:hover {
                background-color: #ECF0F1;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
                color: white;
                font-weight: bold;
            }
        """)
        self.teachers_list.itemClicked.connect(self.on_teacher_selected)
        layout.addWidget(self.teachers_list, 1)  # stretch

        # Statistika
        self.teacher_stats = QLabel("Jami: 0 ta o'qituvchi")
        self.teacher_stats.setStyleSheet("""
            font-size: 11px; color: #7F8C8D;
            padding: 6px; background-color: #ECF0F1;
            border-radius: 4px;
        """)
        self.teacher_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.teacher_stats.setFixedHeight(30)
        layout.addWidget(self.teacher_stats)

        # Yangilash tugmasi
        btn_refresh = QPushButton("🔄 Yangilash")
        btn_refresh.clicked.connect(self.load_teachers)
        btn_refresh.setFixedHeight(35)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; color: white;
                padding: 8px; font-size: 12px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        layout.addWidget(btn_refresh)

        return widget

    # ============ O'NG PANEL ============

    def create_lessons_panel(self):
        """O'qituvchining darslari paneli"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        widget.setLayout(layout)

        # Tanlangan o'qituvchi
        self.selected_teacher_label = QLabel(
            "⚠️ Chap tomondan o'qituvchini tanlang"
        )
        self.selected_teacher_label.setStyleSheet("""
            font-size: 14px; font-weight: bold;
            color: white; background-color: #E67E22;
            padding: 12px; border-radius: 6px;
        """)
        self.selected_teacher_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_teacher_label.setFixedHeight(50)
        layout.addWidget(self.selected_teacher_label)

        # YANGI DARS QO'SHISH
        self.add_group = QGroupBox("➕ Yangi dars biriktirish")
        self.add_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px; font-weight: bold;
                border: 2px solid #27AE60; border-radius: 6px;
                margin-top: 8px; padding-top: 12px;
            }
        """)
        self.add_group.setEnabled(False)
        self.add_group.setFixedHeight(85)
        
        add_layout = QHBoxLayout()
        add_layout.setSpacing(5)
        self.add_group.setLayout(add_layout)

        # Sinf
        add_layout.addWidget(QLabel("🏫 Sinf:"))
        self.class_combo = QComboBox()
        self.class_combo.setStyleSheet(self._input_style())
        self.class_combo.setMinimumWidth(110)
        self.class_combo.currentIndexChanged.connect(self._auto_fill_hours)
        add_layout.addWidget(self.class_combo)

        # Fan
        add_layout.addWidget(QLabel("📚 Fan:"))
        self.subject_combo = QComboBox()
        self.subject_combo.setStyleSheet(self._input_style())
        self.subject_combo.setMinimumWidth(140)
        self.subject_combo.currentIndexChanged.connect(self._auto_fill_hours)
        add_layout.addWidget(self.subject_combo)

        # Soat (0.5 qadam bilan)
        add_layout.addWidget(QLabel("⏱️ Soat:"))
        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(0.5, 10)
        self.hours_spin.setSingleStep(0.5)
        self.hours_spin.setDecimals(1)
        self.hours_spin.setValue(2)
        self.hours_spin.setStyleSheet(self._input_style())
        self.hours_spin.setMaximumWidth(60)
        add_layout.addWidget(self.hours_spin)

        # Xona
        add_layout.addWidget(QLabel("🚪 Xona:"))
        self.classroom_combo = QComboBox()
        self.classroom_combo.setStyleSheet(self._input_style())
        self.classroom_combo.setMinimumWidth(110)
        add_layout.addWidget(self.classroom_combo)

        # Saqlash
        self.btn_save = QPushButton("💾 Saqlash")
        self.btn_save.clicked.connect(self.save_assignment)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 8px 15px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        add_layout.addWidget(self.btn_save)

        # Bekor qilish
        self.btn_cancel_edit = QPushButton("✖")
        self.btn_cancel_edit.clicked.connect(self.cancel_edit)
        self.btn_cancel_edit.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6; color: white;
                padding: 8px 12px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7F8C8D; }
        """)
        self.btn_cancel_edit.setVisible(False)
        self.btn_cancel_edit.setMaximumWidth(40)
        add_layout.addWidget(self.btn_cancel_edit)

        layout.addWidget(self.add_group)

        # STATISTIKA
        self.stats_label = QLabel("📊 Darslar: 0 ta | Jami soat: 0")
        self.stats_label.setStyleSheet("""
            font-size: 12px; font-weight: bold;
            color: white; background-color: #2C3E50;
            padding: 8px; border-radius: 5px;
        """)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setFixedHeight(35)
        layout.addWidget(self.stats_label)

        # JADVAL
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Sinf", "Fan", "Soat", "Xona", "Holat"
        ])

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 150)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(35)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; gridline-color: #ddd;
                font-size: 12px; color: #000000;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected {
                background-color: #3498DB; color: white;
            }
            QHeaderView::section {
                background-color: #2C3E50; color: white;
                padding: 8px; font-weight: bold; border: none;
            }
        """)

        self.table.itemDoubleClicked.connect(self.edit_assignment)
        layout.addWidget(self.table, 1)  # stretch

        # TUGMALAR
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        btn_edit = QPushButton("✏️ Tahrirlash")
        btn_edit.clicked.connect(self.edit_assignment)
        btn_edit.setFixedHeight(35)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #F39C12; color: white;
                padding: 8px 15px; font-size: 12px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E67E22; }
        """)
        btn_layout.addWidget(btn_edit)

        btn_delete = QPushButton("🗑️ O'chirish")
        btn_delete.clicked.connect(self.delete_assignment)
        btn_delete.setFixedHeight(35)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white;
                padding: 8px 15px; font-size: 12px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        btn_layout.addWidget(btn_delete)

        btn_clear_all = QPushButton("🗑️ Tozalash")
        btn_clear_all.clicked.connect(self.clear_all_assignments)
        btn_clear_all.setFixedHeight(35)
        btn_clear_all.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white;
                padding: 8px 15px; font-size: 12px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        btn_layout.addWidget(btn_clear_all)

        btn_layout.addStretch()

        info = QLabel("💡 Tahrirlash uchun ikki marta bosing")
        info.setStyleSheet("font-size: 11px; color: #7F8C8D; font-style: italic;")
        btn_layout.addWidget(info)

        layout.addLayout(btn_layout)

        return widget

    # ============ YORDAMCHI ============

    def _input_style(self):
        return """
            QComboBox, QSpinBox {
                padding: 8px; font-size: 13px;
                border: 2px solid #bdc3c7; border-radius: 5px;
            }
            QComboBox:focus, QSpinBox:focus {
                border: 2px solid #3498DB;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #3498DB;
                selection-color: white;
            }
        """

    def _auto_fill_hours(self):
        """Sinf va fan tanlangach Tayanch rejadan soatni avtomatik to'ldirish"""
        class_id = self.class_combo.currentData()
        subject_id = self.subject_combo.currentData()

        if not class_id or not subject_id:
            return

        # Sinf darajasini olish
        classes = self.db.get_all_classes()
        class_level = None
        for cls in classes:
            if cls[0] == class_id:
                class_level = cls[2]  # level ustuni
                break

        if class_level is None:
            return

        # Fan nomini olish
        subjects = self.db.get_all_subjects()
        subject_name = None
        for sub in subjects:
            if sub[0] == subject_id:
                subject_name = sub[1]  # name ustuni
                break

        if not subject_name:
            return

        # Tayanch rejadan soatni qidirish
        hours = self.db.get_tayanch_hours(class_level, subject_name)
        if hours is not None:
            self.hours_spin.setValue(float(hours))

    # ============ YUKLASH ============

    def load_teachers(self):
        """O'qituvchilarni yuklash"""
        self.teachers_list.clear()
        teachers = self.db.get_all_teachers()

        for teacher in teachers:
            # teacher: (id, full_name, phone, color, ...)
            teacher_id = teacher[0]
            full_name = teacher[1]
            color = teacher[3]

            # Darslar sonini olish
            assignments = self.db.get_teacher_assignments(teacher_id)
            lesson_count = len(assignments)
            total_hours = sum(a[3] for a in assignments) if assignments else 0

            # Item yaratish
            display_text = f"  {full_name}\n  📚 {lesson_count} fan | ⏱️ {total_hours} soat"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, teacher_id)

            # Rang
            item.setBackground(QColor(color).lighter(180))

            self.teachers_list.addItem(item)

        self.teacher_stats.setText(f"Jami: {len(teachers)} ta o'qituvchi")

    def load_classes_combo(self):
        """Sinflarni yuklash"""
        self.class_combo.clear()
        self.class_combo.addItem("— Sinf —", None)
        
        classes = self.db.get_all_classes()
        for cls in classes:
            self.class_combo.addItem(cls[1], cls[0])

    def load_subjects_combo(self):
        """Fanlarni yuklash"""
        self.subject_combo.clear()
        self.subject_combo.addItem("— Fan —", None)
        
        subjects = self.db.get_all_subjects()
        for sub in subjects:
            self.subject_combo.addItem(sub[1], sub[0])

    def load_classrooms_combo(self):
        """Xonalarni yuklash"""
        self.classroom_combo.clear()
        self.classroom_combo.addItem("— Xona yo'q —", None)
        
        classrooms = self.db.get_all_classrooms()
        for room in classrooms:
            # room = (id, room_number, capacity, room_type)
            display = f"{room[1]} ({room[3]})" if room[3] else room[1]
            self.classroom_combo.addItem(display, room[0])

    # ============ O'QITUVCHI TANLASH ============

    def on_teacher_selected(self, item):
        """O'qituvchi tanlanganda"""
        teacher_id = item.data(Qt.ItemDataRole.UserRole)
        teacher = self.db.get_teacher_by_id(teacher_id)

        if not teacher:
            return

        self.current_teacher_id = teacher_id
        self.current_teacher_name = teacher[1]

        # Sarlavhani yangilash
        color = teacher[3]
        self.selected_teacher_label.setText(
            f"👨‍🏫 {teacher[1]} ning darslari"
        )
        self.selected_teacher_label.setStyleSheet(f"""
            font-size: 16px; font-weight: bold;
            color: white; background-color: {color};
            padding: 15px; border-radius: 8px;
        """)

        # Comboboxlarni yuklash
        self.load_classes_combo()
        self.load_subjects_combo()
        self.load_classrooms_combo()

        # Dars qo'shish panelini yoqish
        self.add_group.setEnabled(True)

        # Darslarni yuklash
        self.load_assignments()

    def load_assignments(self):
        """O'qituvchining darslarini yuklash"""
        if not self.current_teacher_id:
            return

        assignments = self.db.get_teacher_assignments(self.current_teacher_id)
        self.table.setRowCount(0)

        total_hours = 0

        for row_num, assignment in enumerate(assignments):
            # assignment = (id, class_name, subject_name, weekly_hours, 
            #               room_number, class_id, subject_id, classroom_id)
            self.table.insertRow(row_num)

            # ID
            self.table.setItem(row_num, 0, QTableWidgetItem(str(assignment[0])))

            # Sinf
            class_item = QTableWidgetItem(assignment[1])
            class_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            class_item.setForeground(QColor("#2980B9"))
            self.table.setItem(row_num, 1, class_item)

            # Fan
            subject_item = QTableWidgetItem(assignment[2])
            subject_item.setForeground(QColor("#2C3E50"))
            font = subject_item.font()
            font.setBold(True)
            subject_item.setFont(font)
            self.table.setItem(row_num, 2, subject_item)

            # Soat
            hours = assignment[3]
            hours_item = QTableWidgetItem(f"{hours} soat")
            hours_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if hours >= 5:
                hours_item.setForeground(QColor("#E74C3C"))
            elif hours >= 3:
                hours_item.setForeground(QColor("#F39C12"))
            else:
                hours_item.setForeground(QColor("#27AE60"))
            self.table.setItem(row_num, 3, hours_item)

            # Xona
            room = assignment[4] if assignment[4] else "—"
            room_item = QTableWidgetItem(room)
            room_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_num, 4, room_item)

            # Holat
            status = "✅ Faol"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#27AE60"))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_num, 5, status_item)

            total_hours += hours

        # Statistika
        self.stats_label.setText(
            f"📊 Darslar: {len(assignments)} ta | "
            f"Jami soat: {total_hours} soat/hafta"
        )

    # ============ SAQLASH ============

    def save_assignment(self):
        """Dars biriktirish (yangi yoki tahrirlash)"""
        if not self.current_teacher_id:
            return

        class_id = self.class_combo.currentData()
        subject_id = self.subject_combo.currentData()
        classroom_id = self.classroom_combo.currentData()
        hours = self.hours_spin.value()

        if not class_id:
            QMessageBox.warning(self, "Xatolik", "Sinfni tanlang!")
            return

        if not subject_id:
            QMessageBox.warning(self, "Xatolik", "Fanni tanlang!")
            return

        if self.editing_assignment_id:
            # TAHRIRLASH
            success = self.db.update_lesson_assignment(
                self.editing_assignment_id, class_id, subject_id,
                self.current_teacher_id, hours, classroom_id
            )

            if success:
                QMessageBox.information(
                    self, "Muvaffaqiyat",
                    "Dars yangilandi! ✅"
                )
                self.cancel_edit()
                self.load_assignments()
                self.load_teachers()
            else:
                QMessageBox.critical(
                    self, "Xatolik",
                    "Yangilashda xatolik!"
                )
        else:
            # YANGI
            # 1. Tekshirish: Bir xil o'qituvchi uchun takroriy
            assignments = self.db.get_teacher_assignments(self.current_teacher_id)
            for ass in assignments:
                if ass[5] == class_id and ass[6] == subject_id:
                    QMessageBox.warning(
                        self, "Xatolik",
                        f"Bu dars allaqachon biriktirilgan:\n\n"
                        f"Sinf: {self.class_combo.currentText()}\n"
                        f"Fan: {self.subject_combo.currentText()}\n\n"
                        f"Tahrirlash uchun ro'yxatdan tanlang."
                    )
                    return

            # 2. Tekshirish: Boshqa o'qituvchiga bir xil sinfda bir xil fan
            all_assignments = self.db.get_all_lesson_assignments()
            for ass in all_assignments:
                # ass = (id, class_name, subject_name, teacher_name, weekly_hours,
                #        class_id, subject_id, teacher_id)
                if ass[5] == class_id and ass[6] == subject_id and ass[7] != self.current_teacher_id:
                    QMessageBox.critical(
                        self, "🚫 Xatolik",
                        f"Bu fanni boshqa o'qituvchi allaqachon olmoqda!\n\n"
                        f"Sinf: {self.class_combo.currentText()}\n"
                        f"Fan: {self.subject_combo.currentText()}\n"
                        f"Joriy o'qituvchi: {ass[3]}\n\n"
                        f"Bir sinfda bir fan faqat bitta o'qituvchida bo'lishi kerak!"
                    )
                    return

            # 3. Tekshirish: Tayanch rejada yo'q fan
            classes = self.db.get_all_classes()
            class_level = None
            for cls in classes:
                if cls[0] == class_id:
                    class_level = cls[2]
                    break

            subjects = self.db.get_all_subjects()
            subject_name = None
            for sub in subjects:
                if sub[0] == subject_id:
                    subject_name = sub[1]
                    break

            if class_level is not None and subject_name:
                tayanch_hours = self.db.get_tayanch_hours(class_level, subject_name)
                if tayanch_hours is None:
                    reply = QMessageBox.warning(
                        self, "⚠️ Tayanch rejada yo'q",
                        f"Diqqat! Bu fan Tayanch o'quv rejadagi "
                        f"{class_level}-sinf uchun ko'rsatilmagan.\n\n"
                        f"Sinf: {self.class_combo.currentText()}\n"
                        f"Fan: {self.subject_combo.currentText()}\n\n"
                        f"Davom etasizmi?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return

            success = self.db.add_lesson_assignment(
                class_id, subject_id, self.current_teacher_id, 
                hours, classroom_id
            )

            if success:
                QMessageBox.information(
                    self, "Muvaffaqiyat",
                    f"Dars biriktirildi! ✅\n\n"
                    f"O'qituvchi: {self.current_teacher_name}\n"
                    f"Sinf: {self.class_combo.currentText()}\n"
                    f"Fan: {self.subject_combo.currentText()}\n"
                    f"Soat: {hours}/hafta"
                )
                self.clear_form()
                self.load_assignments()
                self.load_teachers()
            else:
                QMessageBox.critical(
                    self, "Xatolik",
                    "Dars biriktirilmadi!"
                )

    def clear_form(self):
        """Formani tozalash"""
        self.class_combo.setCurrentIndex(0)
        self.subject_combo.setCurrentIndex(0)
        self.classroom_combo.setCurrentIndex(0)
        self.hours_spin.setValue(2)

    # ============ TAHRIRLASH ============

    def edit_assignment(self):
        """Darsni tahrirlash"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Tahrirlash uchun darsni tanlang!")
            return

        assignment_id = int(self.table.item(current_row, 0).text())

        # Assignment ma'lumotlarini olish
        assignments = self.db.get_teacher_assignments(self.current_teacher_id)
        target = None
        for ass in assignments:
            if ass[0] == assignment_id:
                target = ass
                break

        if not target:
            return

        # ass = (id, class_name, subject_name, weekly_hours, 
        #        room_number, class_id, subject_id, classroom_id)

        # Formani to'ldirish
        # Sinf
        for i in range(self.class_combo.count()):
            if self.class_combo.itemData(i) == target[5]:
                self.class_combo.setCurrentIndex(i)
                break

        # Fan
        for i in range(self.subject_combo.count()):
            if self.subject_combo.itemData(i) == target[6]:
                self.subject_combo.setCurrentIndex(i)
                break

        # Xona
        for i in range(self.classroom_combo.count()):
            if self.classroom_combo.itemData(i) == target[7]:
                self.classroom_combo.setCurrentIndex(i)
                break

        # Soat
        self.hours_spin.setValue(target[3])

        # Tahrirlash rejimiga o'tish
        self.editing_assignment_id = assignment_id
        self.btn_save.setText("💾 Yangilash")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #F39C12; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E67E22; }
        """)
        self.btn_cancel_edit.setVisible(True)
        self.add_group.setTitle("✏️ Darsni tahrirlash")

    def cancel_edit(self):
        """Tahrirlashni bekor qilish"""
        self.editing_assignment_id = None
        self.btn_save.setText("💾 Saqlash")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 10px 20px; font-size: 14px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        self.btn_cancel_edit.setVisible(False)
        self.add_group.setTitle("➕ Yangi dars biriktirish")
        self.clear_form()

    # ============ O'CHIRISH ============

    def delete_assignment(self):
        """Darsni o'chirish"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval darsni tanlang!")
            return

        assignment_id = int(self.table.item(current_row, 0).text())
        class_name = self.table.item(current_row, 1).text()
        subject_name = self.table.item(current_row, 2).text()

        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"O'chirmoqchimisiz?\n\n"
            f"O'qituvchi: {self.current_teacher_name}\n"
            f"Sinf: {class_name}\n"
            f"Fan: {subject_name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_lesson_assignment(assignment_id)
            QMessageBox.information(self, "Muvaffaqiyat", "O'chirildi! ✅")
            self.load_assignments()
            self.load_teachers()

    def clear_all_assignments(self):
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "Barcha dars biriktirishlar o'chiriladi! Davom etasizmi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_lesson_assignments()
            QMessageBox.information(self, "Muvaffaqiyat", "Barcha darslar o'chirildi! ✅")
            self.load_teachers()
            self.table.setRowCount(0)
            self.stats_label.setText("📊 Darslar: 0 ta | Jami soat: 0")
            self.selected_teacher_label.setText(
                "⚠️ Chap tomondan o'qituvchini tanlang"
            )
            self.selected_teacher_label.setStyleSheet("""
                font-size: 14px; font-weight: bold;
                color: white; background-color: #E67E22;
                padding: 12px; border-radius: 6px;
            """)
            self.add_group.setEnabled(False)

    def set_max_hours(self):
        """O'zbekistonda qonun bo'yicha maksimal dars soatini o'rnatish"""
        # Joriy qiymatlarni olish
        current_hours = self.db.get_setting("max_teacher_hours", "30")
        current_day = self.db.get_setting("kelajak_day", "4")  # Default: Payshanba (index 4)
        try:
            current_val = int(current_hours)
        except (ValueError, TypeError):
            current_val = 30
        try:
            current_day_val = int(current_day)
        except (ValueError, TypeError):
            current_day_val = 4

        kunlar = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]

        # Maxsus dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("👨‍🏫 O'qituvchilarga maksimal dars soatini belgilash")
        dialog.setMinimumWidth(400)
        dialog_layout = QVBoxLayout()

        # 1. Maksimal dars soati
        lbl_hours = QLabel("O'zbekistonda qonun bo'yicha\nbitta o'qituvchiga maksimal dars soati:")
        lbl_hours.setStyleSheet("font-size: 13px; font-weight: bold;")
        dialog_layout.addWidget(lbl_hours)

        spin_hours = QSpinBox()
        spin_hours.setRange(1, 60)
        spin_hours.setValue(current_val)
        spin_hours.setStyleSheet("font-size: 14px; padding: 5px;")
        dialog_layout.addWidget(spin_hours)

        dialog_layout.addSpacing(15)

        # 2. Kelajak soati kuni
        lbl_day = QLabel("Tarbiyaviy / Kelajak soati haftaning qaysi kuni o'tiladi?")
        lbl_day.setStyleSheet("font-size: 13px; font-weight: bold;")
        dialog_layout.addWidget(lbl_day)

        combo_day = QComboBox()
        combo_day.addItems(kunlar)
        combo_day.setCurrentIndex(current_day_val)
        combo_day.setStyleSheet("font-size: 14px; padding: 5px;")
        dialog_layout.addWidget(combo_day)

        dialog_layout.addSpacing(20)

        # Tugmalar
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(btn_box)

        dialog.setLayout(dialog_layout)

        # Dialogni ishga tushirish
        if dialog.exec() == QDialog.DialogCode.Accepted:
            hours = spin_hours.value()
            day_index = combo_day.currentIndex()
            self.db.set_setting("max_teacher_hours", hours)
            self.db.set_setting("kelajak_day", day_index)
            QMessageBox.information(
                self,
                "✅ Saqlandi",
                f"Maksimal dars soati: {hours} soat/hafta\n\n"
                f"• Oddiy o'qituvchilar: {hours} soat\n"
                f"• Sinf rahbarlari: {hours + 1} soat\n\n"
                f"📅 Kelajak soati: {kunlar[day_index]} kuni"
            )