"""
Tayanch Reja — MTT tomonidan chiqarilgan yillik dars rejasini ko'rish va boshqarish.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QHeaderView, QAbstractItemView, QFrame, QGroupBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont


import math


class TayanchRejaWindow(QDialog):
    """Tayanch reja oynasi — PDF import, ko'rish, tahrirlash, saqlash."""

    CLASS_LEVELS = list(range(1, 12))  # 1-11 sinflar

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.pdf_source = None
        self.is_editing = False

        self.setWindowTitle("📋 Tayanch reja — MTT standarti")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        # Window flags: allow minimization but keep non-modal
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.init_ui()
        self.load_from_db()

    def bring_to_front(self):
        """Oynani oldingi planiga chiqarish"""
        self.setWindowState(Qt.WindowState.WindowNoState)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    # ================================================================
    # UI
    # ================================================================

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.setLayout(layout)

        # ---- Sarlavha ----
        header = QLabel("📋 TAYANCH REJA — O'zbekiston Respublikasi Xalq ta'limi vazirligi")
        header.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2C3E50; "
            "background: #ECF0F1; padding: 12px; border-radius: 8px;"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # ---- PDF manba ----
        self.source_label = QLabel("PDF manba: — (bazadan yuklandi)" if not self.pdf_source
                                   else f"PDF manba: {self.pdf_source}")
        self.source_label.setStyleSheet(
            "font-size: 11px; color: #7F8C8D; padding: 2px 8px; background: transparent;"
        )
        layout.addWidget(self.source_label)

        # ---- Tugmalar paneli ----
        btn_panel = QWidget()
        btn_panel.setStyleSheet("background: #2C3E50; border-radius: 6px;")
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(10, 6, 10, 6)
        btn_layout.setSpacing(8)
        btn_panel.setLayout(btn_layout)

        btn_import = QPushButton("📥 PDF import")
        btn_import.setStyleSheet(self._btn_style("#3498DB"))
        btn_import.clicked.connect(self.import_pdf)
        btn_layout.addWidget(btn_import)

        btn_import_excel = QPushButton("📊 Excel import")
        btn_import_excel.setStyleSheet(self._btn_style("#27AE60"))
        btn_import_excel.clicked.connect(self.import_excel)
        btn_layout.addWidget(btn_import_excel)

        self.btn_edit = QPushButton("✏️ Tahrirlash")
        self.btn_edit.setStyleSheet(self._btn_style("#F39C12"))
        self.btn_edit.clicked.connect(self.toggle_edit)
        btn_layout.addWidget(self.btn_edit)

        btn_refresh = QPushButton("🔄 Yangilash")
        btn_refresh.setStyleSheet(self._btn_style("#9B59B6"))
        btn_refresh.clicked.connect(self.refresh)
        btn_layout.addWidget(btn_refresh)

        btn_save = QPushButton("💾 Saqlash")
        btn_save.setStyleSheet(self._btn_style("#27AE60"))
        btn_save.clicked.connect(self.save)
        btn_layout.addWidget(btn_save)

        btn_clear = QPushButton("🗑️ Tozalash")
        btn_clear.setStyleSheet(self._btn_style("#E74C3C"))
        btn_clear.clicked.connect(self.clear_all)
        btn_layout.addWidget(btn_clear)

        btn_layout.addStretch()

        btn_close = QPushButton("❌ Yopish")
        btn_close.setStyleSheet(self._btn_style("#E74C3C"))
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        layout.addWidget(btn_panel)

        # ---- Jadval ----
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white; gridline-color: #BDC3C7;
                font-size: 12px; color: #000000;
            }
            QTableWidget::item { padding: 4px 8px; }
            QTableWidget::item:selected { background: #D5F5E3; color: #2C3E50; }
            QHeaderView::section {
                background: #2C3E50; color: white; padding: 6px;
                font-weight: bold; font-size: 12px; border: none;
            }
        """)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, 1)

        # ---- Pastki ma'lumot ----
        self.info_label = QLabel("Ma'lumot: —")
        self.info_label.setStyleSheet(
            "font-size: 11px; color: #5D6D7E; padding: 4px 8px; background: transparent;"
        )
        layout.addWidget(self.info_label)

    def _btn_style(self, color):
        return f"""
            QPushButton {{
                background: {color}; color: white;
                padding: 8px 16px; font-size: 12px; font-weight: bold;
                border-radius: 5px; border: none;
            }}
            QPushButton:hover {{ background: {color}DD; }}
            QPushButton:pressed {{ background: {color}BB; }}
        """

    # ================================================================
    # PDF IMPORT
    # ================================================================

    def import_pdf(self):
        """PDF faylni tanlash va parse qilish."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Tayanch reja PDF faylini tanlang", "",
            "PDF fayllar (*.pdf);;Barcha fayllar (*.*)"
        )
        if not path:
            return

        from core.tayanch_reja_parser import TayanchRejaParser
        parser = TayanchRejaParser()
        data = parser.parse_for_display(path)

        if not data:
            QMessageBox.warning(
                self, "Xatolik",
                "PDF fayldan jadval topilmadi!\n\n"
                + "\n".join(parser.errors)
            )
            return

        self.pdf_source = path.split("/")[-1].split("\\")[-1]
        self.source_label.setText(f"PDF manba: {self.pdf_source}")

        self._fill_table_from_data(data)
        self.set_editing(True)

        total_hours = sum(d['weekly_hours'] for d in data)
        n_subjects = len(set(d['subject_name'] for d in data))
        n_classes = len(set(d['class_level'] for d in data))
        self.info_label.setText(
            f"📥 PDF dan yuklandi: {n_subjects} fan, {n_classes} sinf darajasi, "
            f"{total_hours} soat/hafta"
        )

    # ================================================================
    # EXCEL IMPORT
    # ================================================================

    def import_excel(self):
        """Excel faylni tanlash va parse qilish."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Tayanch reja Excel faylini tanlang", "",
            "Excel fayllar (*.xlsx *.xls);;Barcha fayllar (*.*)"
        )
        if not path:
            return

        from core.excel_parser import TayanchRejaExcelParser
        parser = TayanchRejaExcelParser()
        data = parser.parse_for_display(path)

        if not data:
            QMessageBox.warning(
                self, "Xatolik",
                "Excel fayldan jadval topilmadi!\n\n"
                + "\n".join(parser.errors)
            )
            return

        self.pdf_source = path.split("/")[-1].split("\\")[-1]
        self.source_label.setText(f"Excel manba: {self.pdf_source}")

        self._fill_table_from_data(data)
        self.set_editing(True)

        total_hours = sum(d['weekly_hours'] for d in data)
        n_subjects = len(set(d['subject_name'] for d in data))
        n_classes = len(set(d['class_level'] for d in data))
        self.info_label.setText(
            f"📥 Excel dan yuklandi: {n_subjects} fan, {n_classes} sinf darajasi, "
            f"{total_hours} soat/hafta"
        )

    # ================================================================
    # TABLE
    # ================================================================

    def _fill_table_from_data(self, data):
        """Parse qilingan ma'lumotdan jadvalni to'ldirish — Jami ustuni va qatori bilan."""
        ordered_subjects = []
        seen_subjects = set()
        for d in data:
            key = (d['subject_name'], d.get('is_group', False))
            if key not in seen_subjects:
                ordered_subjects.append({
                    'name': d['subject_name'],
                    'short': d.get('subject_short', ''),
                    'is_group': d.get('is_group', False),
                })
                seen_subjects.add(key)

        classes = sorted(set(d['class_level'] for d in data))

        lookup = {}
        for d in data:
            lookup[(d['subject_name'], d['class_level'])] = d['weekly_hours']

        n_cols = len(classes) + 2  # Fan nomi + sinflar + Jami
        n_rows = len(ordered_subjects) + 1  # fanlar + Jami qatori

        self.table.clear()
        self.table.setColumnCount(n_cols)
        self.table.setRowCount(n_rows)

        # Ustun nomlari
        headers = ["Fan nomi"] + [f"{c}-sinf" for c in classes] + ["Jami"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, n_cols):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        GROUP_BG = "#D5DBDB"
        GROUP_COLOR = "#2C3E50"
        TOTAL_BG = "#2C3E50"
        TOTAL_FG = "white"

        # Har bir sinf uchun umumiy soat (Jami qatori uchun)
        class_totals = {c: 0 for c in classes}

        # Qatorlarni to'ldirish
        for row, subj in enumerate(ordered_subjects):
            is_group = subj['is_group']

            if is_group:
                name_item = QTableWidgetItem(subj['name'])
                name_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                name_item.setBackground(QColor(GROUP_BG))
                name_item.setForeground(QColor(GROUP_COLOR))
                self.table.setItem(row, 0, name_item)

                for col in range(1, n_cols):
                    cell = QTableWidgetItem("")
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    cell.setBackground(QColor(GROUP_BG))
                    self.table.setItem(row, col, cell)
            else:
                name_item = QTableWidgetItem(subj['name'])
                name_item.setFont(QFont("Arial", 11))
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                name_item.setBackground(QColor("#FFFFFF"))
                self.table.setItem(row, 0, name_item)

                row_total = 0
                for col_idx, cls_level in enumerate(classes):
                    hours = lookup.get((subj['name'], cls_level), 0)
                    display_hours = hours
                    row_total += hours
                    class_totals[cls_level] += hours

                    item = QTableWidgetItem(str(display_hours) if display_hours > 0 else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                    if hours == 0:
                        item.setBackground(QColor("#FDFEFE"))
                    elif hours <= 2:
                        item.setBackground(QColor("#EAFAF1"))
                    elif hours <= 4:
                        item.setBackground(QColor("#FEF9E7"))
                    else:
                        item.setBackground(QColor("#FADBD8"))

                    self.table.setItem(row, col_idx + 1, item)

                # Jami ustuni (oxirgi ustun)
                display_total = row_total
                total_item = QTableWidgetItem(str(display_total) if display_total > 0 else "")
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                total_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                total_item.setBackground(QColor("#EBF5FB"))
                total_item.setForeground(QColor("#2C3E50"))
                self.table.setItem(row, n_cols - 1, total_item)

        # Jami qatori (oxirgi qator)
        jami_row = len(ordered_subjects)
        jami_label = QTableWidgetItem("Jami")
        jami_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        jami_label.setFlags(jami_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        jami_label.setBackground(QColor(TOTAL_BG))
        jami_label.setForeground(QColor(TOTAL_FG))
        self.table.setItem(jami_row, 0, jami_label)

        grand_total = 0
        for col_idx, cls_level in enumerate(classes):
            val = class_totals[cls_level]
            grand_total += val
            display_val = val
            item = QTableWidgetItem(str(display_val) if display_val > 0 else "")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.setBackground(QColor(TOTAL_BG))
            item.setForeground(QColor(TOTAL_FG))
            self.table.setItem(jami_row, col_idx + 1, item)

        # Umumiy jami (pastki o'ng burchak)
        display_grand = grand_total
        grand_item = QTableWidgetItem(str(display_grand))
        grand_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        grand_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        grand_item.setFlags(grand_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        grand_item.setBackground(QColor("#1A252F"))
        grand_item.setForeground(QColor("white"))
        self.table.setItem(jami_row, n_cols - 1, grand_item)

        self.table.resizeRowsToContents()

    def _get_table_data(self):
        """Jadvaldan ma'lumotni qaytarish (Jami ustun/qator tashlab)."""
        data = []
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        if cols < 3:  # Kamida: Fan nomi + 1 sinf + Jami
            return data

        # Sinf ustunlarini olish — oxirgi "Jami" ustunini tashlab
        class_levels = []
        for col in range(1, cols - 1):  # oxirgi ustun = Jami
            header_text = self.table.horizontalHeaderItem(col)
            if header_text:
                import re
                m = re.search(r'(\d+)', header_text.text())
                if m:
                    class_levels.append(int(m.group(1)))

        # Oxirgi qator = Jami qatori, uni tashlab o'tish
        for row in range(rows - 1):
            name_item = self.table.item(row, 0)
            if not name_item:
                continue
            subject_name = name_item.text().strip()
            if not subject_name:
                continue

            # Guruh sarlavhasini tashlab o'tish
            bg = name_item.background()
            if bg.color().name() == "#d5dbdb":
                continue

            words = subject_name.split()
            short = ''.join(w[0].upper() for w in words[:3]) if len(words) > 1 else subject_name[:4].title()

            for col_idx, cls_level in enumerate(class_levels):
                item = self.table.item(row, col_idx + 1)
                hours = 0
                if item and item.text().strip():
                    try:
                        val = float(item.text().strip().replace(',', '.'))
                        hours = int(val) if val == int(val) else val
                    except (ValueError, TypeError):
                        pass

                if hours and hours > 0:
                    data.append({
                        'subject_name': subject_name,
                        'subject_short': short,
                        'class_level': cls_level,
                        'weekly_hours': hours,
                    })

        return data

    # ================================================================
    # TAHRIRLASH
    # ================================================================

    def toggle_edit(self):
        """Tahrirlash tugmasini bosish."""
        self.set_editing(not self.is_editing)

    def set_editing(self, enabled):
        """Tahrirlash rejimini o'zgartirish."""
        self.is_editing = enabled
        if enabled:
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
            self.btn_edit.setText("🔒 Tahrirlashni yakunlash")
            self.btn_edit.setStyleSheet(self._btn_style("#E67E22"))
        else:
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.btn_edit.setText("✏️ Tahrirlash")
            self.btn_edit.setStyleSheet(self._btn_style("#F39C12"))

    # ================================================================
    # SAQLASH / YUKLASH
    # ================================================================

    def save(self):
        """Jadvalni bazaga saqlash."""
        data = self._get_table_data()
        if not data:
            QMessageBox.warning(self, "Xatolik", "Saqlash uchun ma'lumot yo'q!")
            return

        try:
            self.db.save_tayanch_reja(data, pdf_source=self.pdf_source)
            self.set_editing(False)

            total = sum(d['weekly_hours'] for d in data)
            n_subj = len(set(d['subject_name'] for d in data))
            QMessageBox.information(
                self, "Saqlandi",
                f"Tayanch reja muvaffaqiyatli saqlandi!\n\n"
                f"📊 {n_subj} fan, {total} soat/hafta"
            )
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Saqlashda xatolik:\n{str(e)}")

    def clear_all(self):
        """Tayanch rejni tozalash — jadval va bazani tozalash."""
        reply = QMessageBox.question(
            self, "Tozalash",
            "Tayanch reja ma'lumotlarini tozalashni xohlaysizmi?\n\n"
            "Baza ham tozalanadi!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.db.clear_tayanch_reja()
        except Exception:
            pass

        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.pdf_source = None
        self.source_label.setText("PDF manba: —")
        self.info_label.setText("Ma'lumot: Tozalandi")
        self.set_editing(False)

    def load_from_db(self):
        """Bazadan tayanch reja yuklash."""
        data = self.db.load_tayanch_reja()
        if not data:
            self.info_label.setText("Ma'lumot: Bazada tayanch reja yo'q — PDF yuklang")
            return

        self.pdf_source = data[0].get('pdf_source') if data else None
        if self.pdf_source:
            self.source_label.setText(f"PDF manba: {self.pdf_source}")
        else:
            self.source_label.setText("PDF manba: — (qo'lda kiritilgan)")

        self._fill_table_from_data(data)

        total = sum(d['weekly_hours'] for d in data)
        n_subj = len(set(d['subject_name'] for d in data))
        n_classes = len(set(d['class_level'] for d in data))
        self.info_label.setText(
            f"📂 Bazadan yuklandi: {n_subj} fan, {n_classes} sinf darajasi, "
            f"{total} soat/hafta"
        )

    def refresh(self):
        """Qayta yuklash."""
        self.load_from_db()
