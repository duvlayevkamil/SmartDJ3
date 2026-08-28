from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QLabel, QMessageBox, QSpinBox,
                             QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from core.sanpin import SanPINChecker
import math


class SubjectWindow(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self.db = db_manager
        self.editing_id = None

        self.setWindowTitle("📚 Fanlar boshqaruvi")
        self.setGeometry(200, 150, 800, 600)

        self.init_ui()
        self.load_subjects()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("📚 FANLAR BOSHQARUVI")
        title.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: white;
            background-color: #9B59B6; padding: 15px; border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Qo'shish qismi
        add_group = QGroupBox("➕ Yangi fan qo'shish")
        add_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold;
                border: 2px solid #9B59B6; border-radius: 8px;
                margin-top: 10px; padding-top: 15px;
            }
        """)
        add_layout = QHBoxLayout()
        add_group.setLayout(add_layout)

        add_layout.addWidget(QLabel("Fan nomi:"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Masalan: Astronomiya")
        self.input_name.setStyleSheet(self._input_style())
        add_layout.addWidget(self.input_name, 2)

        add_layout.addWidget(QLabel("Qisqartma:"))
        self.input_short = QLineEdit()
        self.input_short.setPlaceholderText("Astr")
        self.input_short.setMaximumWidth(80)
        self.input_short.setStyleSheet(self._input_style())
        add_layout.addWidget(self.input_short)

        add_layout.addWidget(QLabel("Qiyinlik (1-10):"))
        self.difficulty_spin = QSpinBox()
        self.difficulty_spin.setRange(1, 10)
        self.difficulty_spin.setValue(5)
        self.difficulty_spin.setStyleSheet(self._input_style())
        add_layout.addWidget(self.difficulty_spin)

        # Fan nomi o'zgarganda avtomatik qiyinlik aniqlash
        self.sanpin = SanPINChecker()
        self.input_name.textChanged.connect(self._auto_difficulty)

        self.btn_add = QPushButton("➕ Qo'shish")
        self.btn_add.clicked.connect(self.save_subject)
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

        layout.addWidget(add_group)

        # Jadval
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Fan nomi", "Qisqartma", "Qiyinlik darajasi", "Jami soatlar"]
        )

        self.table.setColumnHidden(0, True)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 180)
        self.table.setColumnWidth(4, 120)

        self.table.itemDoubleClicked.connect(self.edit_subject)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; gridline-color: #ddd;
                font-size: 13px; color: #000000;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected {
                background-color: #9B59B6; color: white;
            }
            QHeaderView::section {
                background-color: #2C3E50; color: white;
                padding: 10px; font-weight: bold; border: none;
            }
        """)
        layout.addWidget(self.table)

        # Tugmalar
        btn_layout = QHBoxLayout()

        btn_edit = QPushButton("✏️ Tahrirlash")
        btn_edit.clicked.connect(self.edit_subject)
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
        btn_delete.clicked.connect(self.delete_subject)
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
        btn_refresh.clicked.connect(self.load_subjects)
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
        btn_clear_all.clicked.connect(self.clear_all_subjects)
        btn_clear_all.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        btn_layout.addWidget(btn_clear_all)

        btn_import = QPushButton("📥 Tayanch rejadadan import")
        btn_import.clicked.connect(self.import_from_tayanch)
        btn_import.setStyleSheet("""
            QPushButton {
                background-color: #D35400; color: white;
                padding: 10px 20px; font-size: 13px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E67E22; }
        """)
        btn_layout.addWidget(btn_import)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _input_style(self):
        return """
            QLineEdit, QSpinBox {
                padding: 8px; font-size: 13px;
                border: 2px solid #bdc3c7; border-radius: 5px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #9B59B6;
            }
        """

    def _auto_difficulty(self, text):
        """Fan nomi bo'yicha avtomatik qiyinlik aniqlash."""
        if self.editing_id:
            return  # Tahrirlashda avtomatik o'zgartirmaslik
        text = text.strip()
        if not text:
            return
        # SanPIN ro'yxatidan qidirish
        for subject, diff in self.sanpin.difficulty.items():
            if subject.lower() == text.lower():
                self.difficulty_spin.setValue(diff)
                return
        # Qisman mos kelish (masalan: "Matematika" = "Matematika va Fizika")
        for subject, diff in self.sanpin.difficulty.items():
            if subject.lower() in text.lower() or text.lower() in subject.lower():
                self.difficulty_spin.setValue(diff)
                return

    def add_subject(self):
        name = self.input_name.text().strip()
        short = self.input_short.text().strip()
        diff = self.difficulty_spin.value()

        if not name:
            QMessageBox.warning(self, "Xatolik", "Fan nomini kiriting!")
            return

        result = self.db.add_subject(name, short, diff)

        if result:
            QMessageBox.information(self, "Muvaffaqiyat", f"Fan qo'shildi: {name} ✅")
            self.input_name.clear()
            self.input_short.clear()
            self.load_subjects()
        else:
            QMessageBox.warning(self, "Xatolik", "Bu fan allaqachon mavjud!")

    def save_subject(self):
        if self.editing_id:
            self._update_subject()
        else:
            self.add_subject()

    def _update_subject(self):
        name = self.input_name.text().strip()
        short = self.input_short.text().strip()
        diff = self.difficulty_spin.value()

        if not name:
            QMessageBox.warning(self, "Xatolik", "Fan nomini kiriting!")
            return

        # Takroriy nomni tekshirish (o'zgartirilayotgan fandan tashqari)
        existing = self.db.get_all_subjects()
        for sub in existing:
            if sub[1].lower() == name.lower() and sub[0] != self.editing_id:
                QMessageBox.warning(self, "Xatolik",
                    f"'{name}' nomli fan allaqachon mavjud!\n\n"
                    f"Boshqa nom tanlang.")
                return

        try:
            self.db.update_subject(self.editing_id, name, short, diff)
            QMessageBox.information(self, "Muvaffaqiyat", f"Fan yangilandi: {name} ✅")
            self.cancel_edit()
            self.load_subjects()
        except Exception as e:
            QMessageBox.critical(self, "Xatolik",
                f"Fan yangilashda xatolik yuz berdi:\n\n{str(e)}\n\n"
                f"DB fayl: {self.db.db_name}")

    def edit_subject(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval fan tanlang!")
            return

        subject_id = int(self.table.item(current_row, 0).text())
        subject_name = self.table.item(current_row, 1).text()
        short = self.table.item(current_row, 2).text()

        # Qiyinlik darajasini olish
        diff_text = self.table.item(current_row, 3).text()
        diff = int(diff_text.split("/")[0].strip().split(" ")[-1])

        self.input_name.setText(subject_name)
        self.input_short.setText(short)
        self.difficulty_spin.setValue(diff)

        self.editing_id = subject_id
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
        self.input_name.clear()
        self.input_short.clear()
        self.difficulty_spin.setValue(5)

    def load_subjects(self):
        subjects = self.db.get_all_subjects()
        self.table.setRowCount(0)

        # Tayanch rejadagi soatlarni oldindan yuklash
        tayanch = self.db.load_tayanch_reja()
        hours_by_subject = {}
        for item in tayanch:
            name = item['subject_name']
            hours_by_subject[name] = hours_by_subject.get(name, 0) + item['weekly_hours']

        # "Tarbiyaviy soat" soatlarini "Kelajak soati" ga ko'chirish
        tarbiy_hours = hours_by_subject.pop('Tarbiyaviy soat', 0)
        if tarbiy_hours > 0:
            hours_by_subject['Kelajak soati'] = hours_by_subject.get('Kelajak soati', 0) + tarbiy_hours

        for row_num, sub in enumerate(subjects):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(sub[0])))
            self.table.setItem(row_num, 1, QTableWidgetItem(sub[1]))
            self.table.setItem(row_num, 2, QTableWidgetItem(sub[2] or ""))

            # Qiyinlik darajasini rangli ko'rsatish
            diff = sub[3] if sub[3] else 5
            diff_item = QTableWidgetItem(f"{diff}/10")
            if diff >= 8:
                diff_item.setText(f"🔴 {diff}/10 (Qiyin)")
            elif diff >= 5:
                diff_item.setText(f"🟡 {diff}/10 (O'rtacha)")
            else:
                diff_item.setText(f"🟢 {diff}/10 (Yengil)")
            self.table.setItem(row_num, 3, diff_item)

            # Jami soatlar — tayanch rejadagi yig'indi
            total = hours_by_subject.get(sub[1], 0)
            total = math.ceil(total) if total != int(total) else int(total)
            if total > 0:
                total_item = QTableWidgetItem(str(total))
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                total_item.setForeground(QColor("#2C3E50"))
            else:
                total_item = QTableWidgetItem("—")
                total_item.setForeground(QColor("#BDC3C7"))
            self.table.setItem(row_num, 4, total_item)

    def delete_subject(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval fan tanlang!")
            return

        subject_id = int(self.table.item(current_row, 0).text())
        subject_name = self.table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"{subject_name} ni o'chirmoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_subject(subject_id)
            QMessageBox.information(self, "Muvaffaqiyat", "Fan o'chirildi! ✅")
            self.load_subjects()

    def clear_all_subjects(self):
        # Dars biriktirishlar sonini tekshirish
        all_assignments = self.db.get_all_lesson_assignments()
        assignments_count = len(all_assignments) if all_assignments else 0

        # Agar dars biriktirishlar bo'lsa — tanlov dialogi
        if assignments_count > 0:
            from PyQt6.QtWidgets import QDialog, QDialogButtonBox
            dialog = QDialog(self)
            dialog.setWindowTitle("Fanlarni tozalash")
            dialog.setMinimumWidth(450)
            dialog_layout = QVBoxLayout()
            dialog.setLayout(dialog_layout)

            # Sarlavha
            header = QLabel("⚠️ Barcha fanlar o'chiriladi!")
            header.setStyleSheet("""
                font-size: 16px; font-weight: bold; color: #E74C3C;
                padding: 15px; background: #FDEDEC; border-radius: 8px;
            """)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dialog_layout.addWidget(header)

            # Savol
            question = QLabel(
                "O'qituvchilarga biriktirilgan darslar saqlansinmi?"
            )
            question.setStyleSheet("font-size: 13px; color: #2C3E50; padding: 10px;")
            question.setAlignment(Qt.AlignmentFlag.AlignCenter)
            question.setWordWrap(True)
            dialog_layout.addWidget(question)

            # Tugmalar
            btn_layout = QHBoxLayout()

            btn_keep = QPushButton("✅ SAQLASH\n(Darslar saqlanadi)")
            btn_keep.setStyleSheet("""
                QPushButton { background: #27AE60; color: white; padding: 12px 20px;
                    font-size: 12px; border-radius: 6px; font-weight: bold; }
                QPushButton:hover { background: #229954; }
            """)
            btn_keep.clicked.connect(dialog.accept)
            btn_layout.addWidget(btn_keep)

            btn_delete = QPushButton("❌ O'CHIRISH\n(Darslar ham o'chadi)")
            btn_delete.setStyleSheet("""
                QPushButton { background: #E74C3C; color: white; padding: 12px 20px;
                    font-size: 12px; border-radius: 6px; font-weight: bold; }
                QPushButton:hover { background: #C0392B; }
            """)
            btn_delete.clicked.connect(dialog.reject)
            btn_layout.addWidget(btn_delete)

            dialog_layout.addLayout(btn_layout)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # SAQLASH — faqat jadval tozalanadi, fanlar va darslar saqlanadi
                self.db.clear_subjects_keep_assignments()
                QMessageBox.information(self, "Muvaffaqiyat",
                    "Jadval tozalandi!\n✅ Fanlar va dars biriktirishlar SAQLANDI.")
            else:
                # O'CHIRISH — hammasi o'chiriladi
                self.db.clear_subjects()
                QMessageBox.information(self, "Muvaffaqiyat",
                    "Barcha fanlar va dars biriktirishlar o'chirildi!")
        else:
            # Dars biriktirishlar yo'q — oddiy tozalash
            reply = QMessageBox.question(
                self, "Tasdiqlash",
                "Barcha fanlar o'chiriladi! Davom etasizmi?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.db.clear_subjects()
                QMessageBox.information(self, "Muvaffaqiyat", "Barcha fanlar o'chirildi! ✅")

        self.load_subjects()

    def import_from_tayanch(self):
        """Tayanch rejadagi fanlarni import qilish."""
        tayanch = self.db.load_tayanch_reja()
        if not tayanch:
            QMessageBox.warning(self, "Xatolik",
                "Tayanch reja bazada yo'q!\n\nAvval Tayanch reja oynasidan PDF yuklang.")
            return

        # Noyob fanlarni ajratib olish
        existing = {s[1].lower() for s in self.db.get_all_subjects()}
        new_subjects = []
        seen = set()
        skipped_tarbiyaviy = False

        for item in tayanch:
            name = item['subject_name']

            # "Tarbiyaviy soat" → o'tkazib yuborish (Kelajak soati avtomatik)
            if name.lower() == 'tarbiyaviy soat':
                skipped_tarbiyaviy = True
                continue

            if name.lower() not in existing and name.lower() not in seen:
                seen.add(name.lower())
                diff = self.sanpin.difficulty.get(name, 5)
                short = item.get('subject_short', '')
                new_subjects.append((name, short, diff))

        # "Kelajak soati" mavjudligini tekshirish
        has_kelajak = any(s[1].lower() == 'kelajak soati' for s in self.db.get_all_subjects())
        if not has_kelajak and 'Kelajak soati' not in seen:
            new_subjects.append(('Kelajak soati', 'Ks', 1))

        if not new_subjects:
            QMessageBox.information(self, "Natija",
                "Barcha fanlar allaqachon bazada mavjud.")
            return

        # Import qilish
        added = 0
        for name, short, diff in new_subjects:
            result = self.db.add_subject(name, short, diff)
            if result:
                added += 1

        self.load_subjects()

        # Natija xabari — Tarbiyaviy soat o'tkazib yuborilgani haqida
        msg = f"✅ {added} ta fan import qilindi!\nJami: {len(new_subjects)} ta yangi fan topildi."
        if skipped_tarbiyaviy:
            msg += "\n\n📝 Tarbiyaviy soat → Kelajak soati o'zgartirildi\n(Kelajak soati avtomatik qo'yiladi)"
        QMessageBox.information(self, "Import", msg)