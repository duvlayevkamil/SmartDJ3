from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                             QPushButton, QVBoxLayout, QWidget,
                             QTableWidgetItem, QHBoxLayout, QLabel,
                             QComboBox, QDialog, QTextEdit, QMessageBox,
                             QFileDialog, QProgressBar, QSpinBox,
                             QGridLayout, QScrollArea, QGroupBox, QFrame,
                             QLineEdit)
from PyQt6.QtGui import QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, QTimer
import sys
import os
import json
import logging
import traceback
from datetime import datetime


def resource_path(relative_path):
    """PyInstaller bundle va ishlab chiqish muhitida fayl yo'lini qaytaradi"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


from database.db_manager import DatabaseManager
from ui.teacher_window import TeacherWindow
from ui.class_window import ClassWindow
from ui.subject_window import SubjectWindow
from ui.assignment_window import AssignmentWindow
from core.sanpin import SanPINChecker
from core.scheduler import TimetableScheduler
from ui.classroom_window import ClassroomWindow
from ui.manual_schedule_window import ManualScheduleWindow
from ui.monitoring_window import MonitoringWindow


# ================================================================
# SanPIN TEKSHIRUV DIALOG — CHIROYLI HISOBOT
# ================================================================
class SanPINDialog(QDialog):
    def __init__(self, results, parent=None):
        """
        results: list of dict — har bir sinf uchun natija:
        [{'class_name': '1-A', 'score': 85, 'errors': [...], 'warnings': [...], 'details': [...], 'total_lessons': 20}, ...]
        """
        super().__init__(parent)
        self.setWindowTitle("📋 SanPIN tekshiruv natijasi")

        # Ekran o'lchamiga moslashtirish
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.setMinimumSize(800, int(geo.height() * 0.85))
            self.resize(900, int(geo.height() * 0.85))
        else:
            self.setMinimumSize(800, 650)

        self.results = results
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        # Umumiy ball
        scores = [r['score'] for r in self.results]
        avg_score = sum(scores) // len(scores) if scores else 0
        total_errors = sum(len(r['errors']) for r in self.results)
        total_warnings = sum(len(r['warnings']) for r in self.results)

        if avg_score >= 90:
            bg, txt, emoji = "#27AE60", "A'lo", "🟢"
        elif avg_score >= 70:
            bg, txt, emoji = "#F39C12", "Yaxshi", "🟡"
        elif avg_score >= 50:
            bg, txt, emoji = "#E67E22", "Qoniqarli", "🟠"
        else:
            bg, txt, emoji = "#E74C3C", "Qoniqarsiz", "🔴"

        header = QLabel(f"{emoji} SanPIN mosligi: {avg_score}% — {txt}")
        header.setStyleSheet(f"""
            font-size: 20px; font-weight: bold; color: white;
            background-color: {bg}; padding: 16px; border-radius: 10px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Statistika — gorizontal qatorda
        stats_widget = QWidget()
        stats_widget.setStyleSheet("background: white; border-radius: 8px; padding: 8px;")
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_widget.setLayout(stats_layout)

        stats_data = [
            (str(len(self.results)), "Sinf", "#2980B9", "#EBF5FB"),
            (f"{avg_score}%", "Moslik", "#27AE60", "#EAFAF1"),
            (str(total_errors), "Buzilish", "#E74C3C", "#FDEDEC"),
            (str(total_warnings), "Chetlanish", "#F39C12", "#FEF9E7"),
        ]

        for val, label, color, bg in stats_data:
            item = QLabel(f"<div style='font-size:24px; font-weight:bold; color:{color};'>{val}</div>"
                          f"<div style='font-size:11px; color:#5D6D7E;'>{label}</div>")
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setStyleSheet(f"background: {bg}; padding: 8px 20px; border-radius: 6px;")
            stats_layout.addWidget(item)

        layout.addWidget(stats_widget)

        # === YONMA-YON LAYOUT: chap = jadval, o'ng = hisobot ===
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        content_widget.setLayout(content_layout)

        # CHAP TOMON — Ball jadvali
        table_html = "<style>body{font-family:Arial;font-size:13px;margin:0;} table{width:100%;border-collapse:collapse;} td{padding:6px 10px;}</style>"
        table_html += "<h3 style='color:#2C3E50;'>📊 Sinflar bo'yicha ball</h3>"
        table_html += "<table style='border:1px solid #ddd; border-radius:6px;'>"
        table_html += "<tr style='background:#2C3E50; color:white;'><td>Sinf</td><td>Ball</td><td>Darslar</td><td>Holat</td></tr>"
        for r in self.results:
            s = r['score']
            if s >= 90:
                sc, st, ec = "#27AE60", "A'lo", "✅"
            elif s >= 70:
                sc, st, ec = "#F39C12", "Yaxshi", "🟡"
            elif s >= 50:
                sc, st, ec = "#E67E22", "Qoniqarli", "🟠"
            else:
                sc, st, ec = "#E74C3C", "Qoniqarsiz", "❌"
            table_html += f"<tr style='background:#F8F9FA;'><td><b>{r['class_name']}</b></td>"
            table_html += f"<td style='color:{sc}; font-weight:bold;'>{s}%</td>"
            table_html += f"<td>{r.get('total_lessons', '?')}</td>"
            table_html += f"<td>{ec} {st}</td></tr>"
        table_html += "</table>"

        table_view = QTextEdit()
        table_view.setReadOnly(True)
        table_view.setHtml(table_html)
        table_view.setStyleSheet("QTextEdit { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 8px; }")
        content_layout.addWidget(table_view, 1)

        # O'NG TOMON — Xatolar, ogohlantirishlar, tavsiyalar
        report_html = "<style>body{font-family:Arial;font-size:13px;margin:0;} ul{margin:4px 0;}</style>"

        # Xatolar
        if total_errors > 0:
            report_html += f"<h3 style='color:#E74C3C;'>❌ Qo'pol buzilishlar ({total_errors} ta):</h3><ul>"
            for r in self.results:
                if r['errors']:
                    report_html += f"<li style='color:#C0392B;'><b>{r['class_name']}:</b>"
                    report_html += "<ul>"
                    for e in r['errors']:
                        report_html += f"<li>{e}</li>"
                    report_html += "</ul></li>"
            report_html += "</ul>"
        else:
            report_html += "<h3 style='color:#27AE60;'>✅ Qo'pol buzilishlar yo'q!</h3>"

        # Ogohlantirishlar
        if total_warnings > 0:
            report_html += f"<h3 style='color:#F39C12;'>⚠️ Chetlanishlar ({total_warnings} ta):</h3><ul>"
            for r in self.results:
                if r['warnings']:
                    report_html += f"<li style='color:#E67E22;'><b>{r['class_name']}:</b>"
                    report_html += "<ul>"
                    for w in r['warnings']:
                        report_html += f"<li>{w}</li>"
                    report_html += "</ul></li>"
            report_html += "</ul>"
        else:
            report_html += "<h3 style='color:#27AE60;'>✅ Chetlanishlar yo'q!</h3>"

        # Tavsiyalar
        report_html += "<h3 style='color:#8E44AD;'>💡 Tavsiyalar:</h3><ul>"
        if total_errors > 0:
            report_html += "<li style='color:#6C3483;'>Qo'pol buzilishlarni bartaraf eting — ular o'quvchilar salomatligiga ta'sir qiladi</li>"
        if total_warnings > 0:
            report_html += "<li style='color:#6C3483;'>Chetlanishlarni kamaytiring — dars sifatini oshiradi</li>"
        if avg_score < 70:
            report_html += "<li style='color:#6C3483;'>Dars jadvalini qayta tuzing — ko'proq optimallashtiring</li>"
        if avg_score >= 90:
            report_html += "<li style='color:#6C3483;'>Jadval a'lo darajada tuzilgan! Davom eting</li>"
        report_html += "</ul>"

        report_view = QTextEdit()
        report_view.setReadOnly(True)
        report_view.setHtml(report_html)
        report_view.setStyleSheet("QTextEdit { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 8px; }")
        content_layout.addWidget(report_view, 1)

        layout.addWidget(content_widget, 1)

        # Yopish tugmasi (bitta)
        close_btn = QPushButton("Yopish")
        close_btn.setStyleSheet("""
            QPushButton { background: #2C3E50; color: white; padding: 10px 30px;
                font-size: 14px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #1A252F; }
        """)
        close_btn.clicked.connect(self.close)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

# ================================================================
# AVTOMATIK JADVAL DIALOG
# ================================================================
class AutoScheduleDialog(QDialog):
    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Avtomatik jadval tuzish")
        self.setGeometry(200, 150, 600, 700)
        self.result_timetable = None
        self.result_score = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("⚡ AVTOMATIK JADVAL TUZISH")
        title.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: white;
            background-color: #2C3E50; padding: 15px; border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        class_layout = QHBoxLayout()
        class_label = QLabel("Sinf darajasi:")
        class_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        class_layout.addWidget(class_label)

        self.class_spin = QSpinBox()
        self.class_spin.setRange(1, 11)
        self.class_spin.setValue(5)
        self.class_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px; font-size: 14px;
                border: 2px solid #3498DB; border-radius: 5px;
            }
        """)
        class_layout.addWidget(self.class_spin)
        layout.addLayout(class_layout)

        subjects_group = QGroupBox("Fanlar va haftalik soatlar")
        subjects_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold;
                border: 2px solid #3498DB; border-radius: 8px;
                margin-top: 10px; padding-top: 15px;
            }
        """)
        subjects_layout = QGridLayout()
        subjects_group.setLayout(subjects_layout)

        self.subject_spins = {}

        fanlar = [
            ("Matematika", 5), ("Ona tili", 4), ("Ingliz tili", 3),
            ("Fizika", 3), ("Kimyo", 2), ("Biologiya", 2),
            ("Tarix", 2), ("Geografiya", 2), ("Informatika", 2),
            ("Sport", 2), ("Adabiyot", 2), ("Musiqa", 1),
            ("San'at", 1), ("Texnologiya", 1)
        ]

        for i, (fan, soat) in enumerate(fanlar):
            row = i // 2
            col = (i % 2) * 2

            label = QLabel(fan + ":")
            label.setStyleSheet("font-weight: normal; font-size: 13px;")
            subjects_layout.addWidget(label, row, col)

            spin = QSpinBox()
            spin.setRange(0, 7)
            spin.setValue(soat)
            spin.setStyleSheet("""
                QSpinBox {
                    padding: 5px; font-size: 13px;
                    border: 1px solid #bdc3c7; border-radius: 3px;
                    min-width: 50px;
                }
            """)
            subjects_layout.addWidget(spin, row, col + 1)
            self.subject_spins[fan] = spin

        scroll = QScrollArea()
        scroll.setWidget(subjects_group)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(350)
        layout.addWidget(scroll)

        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498DB; border-radius: 5px;
                text-align: center; font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #27AE60; border-radius: 3px;
            }
        """)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            "font-size: 14px; padding: 10px; color: #2C3E50;"
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()

        btn_generate = QPushButton("⚡ Jadval tuzish")
        btn_generate.clicked.connect(self.generate)
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 15px; font-size: 15px;
                border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        btn_layout.addWidget(btn_generate)

        btn_cancel = QPushButton("Bekor qilish")
        btn_cancel.clicked.connect(self.close)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6; color: white;
                padding: 15px; font-size: 15px;
                border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7F8C8D; }
        """)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def generate(self):
        subjects_hours = {}
        for fan, spin in self.subject_spins.items():
            if spin.value() > 0:
                subjects_hours[fan] = spin.value()

        if not subjects_hours:
            QMessageBox.warning(self, "Xatolik", "Kamida bitta fan tanlang!")
            return

        self.progress.setVisible(True)
        self.progress.setValue(30)
        self.status_label.setText("⏳ Jadval tuzilmoqda...")
        QApplication.processEvents()

        scheduler = TimetableScheduler(db_manager=self.db)
        class_level = self.class_spin.value()

        timetable, score = scheduler.generate_timetable(
            subjects_hours, class_level
        )

        self.progress.setValue(100)

        if timetable:
            self.result_timetable = timetable
            self.result_score = score
            self.status_label.setText(
                f"✅ Jadval tuzildi! SanPIN ball: {score}/100"
            )
            QMessageBox.information(
                self, "Muvaffaqiyat",
                f"Jadval muvaffaqiyatli tuzildi!\n\nSanPIN ball: {score}/100"
            )
            self.accept()
        else:
            self.status_label.setText(
                "❌ Jadval tuzib bo'lmadi. Soatlarni kamaytiring."
            )


# ================================================================
# ASOSIY OYNA
# ================================================================
class DarsJadvali(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.db.initialize()
        self.sanpin = SanPINChecker()

        self.setWindowTitle("SmartDJ3 - Dars Jadvali Tizimi")

        self.init_ui()

        self.showMaximized()

    def init_ui(self):
        markaziy = QWidget()
        self.setCentralWidget(markaziy)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        markaziy.setLayout(main_layout)

        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)

        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

    # ================================================================
    # CHAP PANEL
    # ================================================================
    def create_left_panel(self):
        widget = QWidget()
        widget.setFixedWidth(260)
        widget.setStyleSheet("QWidget { background-color: #2C3E50; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)

        # Logo
        logo_widget = QWidget()
        logo_widget.setStyleSheet("QWidget { background-color: #1A252F; }")
        logo_layout = QVBoxLayout()
        logo_widget.setLayout(logo_layout)

        title = QLabel("⚡ SmartDJ3")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px; font-weight: bold; color: #3498DB;
            background-color: transparent; padding: 25px 10px;
        """)
        logo_layout.addWidget(title)

        subtitle = QLabel("Dars Jadvali Tizimi")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 12px; color: #7F8C8D;
            background-color: transparent; padding: 0px 10px 15px 10px;
        """)
        logo_layout.addWidget(subtitle)
        layout.addWidget(logo_widget)

        self._add_divider(layout)
        self._add_section_label(layout, "ASOSIY MA'LUMOTLAR")

        # 1. Sinflar
        btn_classes = self._create_menu_button("  🏫   Sinflar", "#3498DB")
        btn_classes.clicked.connect(self.open_classes)
        layout.addWidget(btn_classes)

        # 2. Fanlar
        btn_subjects = self._create_menu_button("  📚   Fanlar", "#9B59B6")
        btn_subjects.clicked.connect(self.open_subjects)
        layout.addWidget(btn_subjects)

        # 3. O'qituvchilar
        btn_teachers = self._create_menu_button("  👨‍🏫   O'qituvchilar", "#4ECDC4")
        btn_teachers.clicked.connect(self.open_teachers)
        layout.addWidget(btn_teachers)

        # 4. Xonalar
        btn_rooms = self._create_menu_button("  🚪   Xonalar", "#F39C12")
        btn_rooms.clicked.connect(self.open_classrooms)  # ← QO'SHILDI
        layout.addWidget(btn_rooms)

        # 5. Dars biriktirish (YANGI!)
        btn_assignments = self._create_menu_button(
            "  📝   Dars biriktirish", "#16A085"
        )
        btn_assignments.clicked.connect(self.open_assignments)
        layout.addWidget(btn_assignments)

        # 6. Tayanch reja
        btn_tayanch = self._create_menu_button(
            "  📋   Tayanch reja", "#D35400"
        )
        btn_tayanch.clicked.connect(self.open_tayanch_reja)
        layout.addWidget(btn_tayanch)

        # 7. DARS JADVALI
        btn_manual = self._create_menu_button(
            "  📅   Dars jadvali", "#8E44AD"
        )
        btn_manual.clicked.connect(self.open_manual_schedule)
        layout.addWidget(btn_manual)

        self._add_divider(layout)
        self._add_section_label(layout, "AMALLAR")

        # SanPIN
        btn_sanpin = self._create_menu_button("  📋   SanPIN tekshiruvi", "#E74C3C")
        btn_sanpin.clicked.connect(self.check_sanpin)
        layout.addWidget(btn_sanpin)

        # Monitoring
        btn_monitoring = self._create_menu_button("  📊   Monitoring", "#3498DB")
        btn_monitoring.clicked.connect(self.open_monitoring)
        layout.addWidget(btn_monitoring)

        # Chop etish
        btn_export = self._create_menu_button("  🖨️   Chop etish", "#1ABC9C")
        btn_export.clicked.connect(self.export_jadval)
        layout.addWidget(btn_export)

        # Qo'llanma
        btn_guide = self._create_menu_button("  📖   Qo'llanma", "#95A5A6")
        btn_guide.clicked.connect(self._open_guide)
        layout.addWidget(btn_guide)

        # Stretch
        stretch_widget = QWidget()
        stretch_widget.setStyleSheet("background-color: #2C3E50;")
        layout.addWidget(stretch_widget, 1)

        self._add_divider(layout)

        # AVTOMATIK JADVAL
        btn_auto = QPushButton("⚡ AVTOMATIK JADVAL")
        btn_auto.clicked.connect(self.auto_schedule)
        btn_auto.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 15px; font-size: 14px; font-weight: bold;
                border-radius: 8px; margin: 8px; border: none;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:pressed { background-color: #1E8449; }
        """)
        layout.addWidget(btn_auto)

        # QO'LDA JADVAL
        btn_manual = QPushButton("📅 QO'LDA JADVAL")
        btn_manual.clicked.connect(self.manual_schedule)
        btn_manual.setStyleSheet("""
            QPushButton {
                background-color: #8E44AD; color: white;
                padding: 15px; font-size: 14px; font-weight: bold;
                border-radius: 8px; margin: 8px; border: none;
            }
            QPushButton:hover { background-color: #7D3C98; }
            QPushButton:pressed { background-color: #6C3483; }
        """)
        layout.addWidget(btn_manual)

        # TO'LIQ TOZALASH
        btn_clear_all = QPushButton("🔥 BAZANI TOZALASH")
        btn_clear_all.clicked.connect(self.clear_all_database)
        btn_clear_all.setStyleSheet("""
            QPushButton {
                background-color: #C0392B; color: white;
                padding: 15px; font-size: 14px; font-weight: bold;
                border-radius: 8px; margin: 8px; border: none;
            }
            QPushButton:hover { background-color: #E74C3C; }
            QPushButton:pressed { background-color: #922B21; }
        """)
        layout.addWidget(btn_clear_all)

        return widget

    def _create_menu_button(self, text, hover_color):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #BDC3C7;
                padding: 15px 20px;
                font-size: 14px;
                border: none;
                border-left: 4px solid transparent;
                text-align: left;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #34495E;
                color: white;
                border-left: 4px solid {hover_color};
            }}
            QPushButton:pressed {{
                background-color: #273746;
            }}
        """)
        return btn

    def _add_divider(self, layout):
        divider = QLabel()
        divider.setFixedHeight(2)
        divider.setStyleSheet("background-color: #34495E;")
        layout.addWidget(divider)

    def _add_section_label(self, layout, text):
        label = QLabel(f"   {text}")
        label.setStyleSheet("""
            font-size: 11px; color: #5D6D7E;
            background-color: transparent;
            padding: 10px 15px 5px 15px;
            font-weight: bold; letter-spacing: 2px;
        """)
        layout.addWidget(label)

    # ================================================================
    # O'NG PANEL
    # ================================================================
    def create_right_panel(self):
        widget = QWidget()
        widget.setStyleSheet("QWidget { background-color: #ECF0F1; }")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)

        # Scroll area ichidagi kontent
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: #ECF0F1;")
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(30, 20, 30, 20)
        inner_layout.setSpacing(15)
        scroll_content.setLayout(inner_layout)

        # ---- LOGO ----
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("logo.png"))
        logo_label.setPixmap(logo_pixmap.scaled(
            250, 250, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")
        inner_layout.addWidget(logo_label)

        # ---- IMKONIYATLAR + STATISTIKA (yonma-yon) ----
        middle_row = QHBoxLayout()
        middle_row.setSpacing(12)

        # Chap: Imkoniyatlar
        features = self._create_features_section()
        middle_row.addWidget(features, 2)

        # O'ng: Statistika (vertikal)
        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout()
        self.stats_layout.setSpacing(6)
        self.stats_container.setLayout(self.stats_layout)
        self._refresh_stats()
        middle_row.addWidget(self.stats_container, 1)

        inner_layout.addLayout(middle_row)

        # ---- LITSENZIYA ----
        license_card = self._create_license_section()
        inner_layout.addWidget(license_card)

        # ---- MUALLIF ----
        author = QLabel("© 2026 Duvlayev Kamil Abdurashidovich\nBarcha huquqlar himoyalangan")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author.setStyleSheet(
            "font-size: 11px; color: #95A5A6; background: transparent; padding: 15px;"
        )
        inner_layout.addWidget(author)

        inner_layout.addStretch()

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #ECF0F1; border: none; }")
        layout.addWidget(scroll)

        return widget

    def _refresh_stats(self):
        """Statistika kartochkalarini yangilash — vertikal"""
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        classes = self.db.get_all_classes()
        teachers = self.db.get_all_teachers()
        subjects = self.db.get_all_subjects()
        total_lessons = sum(
            sum(x[4] for x in (self.db.get_class_assignments(c[0]) or []))
            for c in classes
        )

        self.stats_layout.addWidget(self._stat_card("🏫", str(len(classes)), "Sinf", "#3498DB"))
        self.stats_layout.addWidget(self._stat_card("👨‍🏫", str(len(teachers)), "O'qituvchi", "#9B59B6"))
        self.stats_layout.addWidget(self._stat_card("📚", str(len(subjects)), "Fan", "#E67E22"))
        self.stats_layout.addWidget(self._stat_card("📝", str(total_lessons), "Dars soat", "#1ABC9C"))

    def _stat_card(self, emoji, value, label, color):
        """Bitta statistika kartochkasi"""
        w = QWidget()
        w.setStyleSheet(f"background: {color}15; border-radius: 8px; padding: 3px;")
        v = QVBoxLayout()
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.setSpacing(0)
        w.setLayout(v)

        e = QLabel(emoji)
        e.setStyleSheet("font-size: 18px; background: transparent;")
        e.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(e)

        val = QLabel(value)
        val.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; background: transparent;")
        val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(val)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 9px; color: #7F8C8D; background: transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(lbl)

        return w

    def _create_features_section(self):
        """Dastur imkoniyatlari"""
        card = QWidget()
        card.setStyleSheet("background: white; border-radius: 10px; padding: 8px;")
        v = QVBoxLayout()
        v.setSpacing(1)
        v.setContentsMargins(8, 4, 8, 4)
        card.setLayout(v)

        header = QLabel("✨ Imkoniyatlar")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50; background: transparent;")
        v.addWidget(header)

        features = [
            # 🟢 Algoritmlar
            ("📝 Dars biriktirish", "O'qituvchi-fan-sinf bog'lash, avtomatik soat to'ldirish", "#27AE60"),
            ("📋 Tayanch reja", "MMT o'quv rejasini PDF dan import qilish", "#27AE60"),
            ("⚡ Avtomatik jadval", "Greedy algoritmi, 2-8 soniyada tayyor", "#27AE60"),
            ("🎯 Teng taqsimot", "Kunlar bo'yicha darslarni teng taqsimlash", "#27AE60"),
            # 🔵 Boshqaruv
            ("🖱️ Drag & drop", "Sichqoncha bilan joylashtirish va SWAP almashtirish", "#3498DB"),
            ("🔄 2-haftalik jadval", "Toq/Juft haftalar, kasrli soatlar (0.5, 1.5)", "#3498DB"),
            ("👨‍🏫 O'qituvchi boshq.", "Band soatlar, metodik kun, sinf rahbari", "#3498DB"),
            ("🏫 Sinflar boshqaruvi", "1-11 sinflar, ish kunlari (5/6 kun)", "#3498DB"),
            ("🚪 Xonalar boshqaruvi", "Laboratoriyalar, sport zallari", "#3498DB"),
            # 🟡 Nazorat
            ("📋 SanPIN nazorati", "Kunlik/haftalik limitlar, ogohlantirishlar", "#F39C12"),
            ("📊 Monitoring", "Real vaqtda kuzatish + demo rejim", "#F39C12"),
            # 🔴 Export
            ("🖨️ Export", "Excel, Word, HTML, CSV, PDF formatlari", "#E74C3C"),
        ]

        for emoji_title, desc, color in features:
            row = QHBoxLayout()
            row.setSpacing(8)

            dot = QLabel("●")
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background: {color}; border-radius: 4px;")
            row.addWidget(dot)

            t = QLabel(emoji_title)
            t.setStyleSheet("font-size: 11px; font-weight: bold; color: #2C3E50; background: transparent;")
            row.addWidget(t)

            row.addStretch()

            d = QLabel(desc)
            d.setStyleSheet("font-size: 10px; color: #95A5A6; background: transparent;")
            row.addWidget(d)

            v.addLayout(row)

        return card

    def _create_license_section(self):
        """Litsenziya ma'lumotlari"""
        from core.license import check_license, load_license, TRIAL_DAYS
        from datetime import datetime, timedelta

        card = QWidget()
        card.setStyleSheet("background: white; border-radius: 10px; padding: 15px;")
        v = QVBoxLayout()
        v.setSpacing(6)
        card.setLayout(v)

        header = QLabel("🔑 Litsenziya")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #2C3E50; background: transparent;")
        v.addWidget(header)

        status, message = check_license()
        license_data = load_license()

        trial_row = QHBoxLayout()
        trial_label = QLabel("Holat:")
        trial_label.setStyleSheet("font-size: 13px; color: #5D6D7E; background: transparent;")
        trial_row.addWidget(trial_label)

        if status == "licensed":
            status_text = "🟢 Litsenziya faol"
            status_color = "#27AE60"
        elif status == "trial":
            install_date = datetime.fromisoformat(license_data["install_date"]) if license_data else datetime.now()
            remaining = TRIAL_DAYS - (datetime.now() - install_date).days
            status_text = f"🟡 Bepul sinov ({remaining} kun)"
            status_color = "#F39C12"
        else:
            status_text = "🔴 Litsenziya talab qilinadi"
            status_color = "#E74C3C"

        trial_status = QLabel(status_text)
        trial_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {status_color}; background: transparent;")
        trial_row.addWidget(trial_status)
        trial_row.addStretch()
        v.addLayout(trial_row)

        period_row = QHBoxLayout()
        period_label = QLabel("Muddat:")
        period_label.setStyleSheet("font-size: 13px; color: #5D6D7E; background: transparent;")
        period_row.addWidget(period_label)

        if license_data:
            install_dt = datetime.fromisoformat(license_data["install_date"])
            expiry_dt = install_dt + timedelta(days=TRIAL_DAYS)
            period_text = f"{install_dt.strftime('%d.%m.%Y')} — {expiry_dt.strftime('%d.%m.%Y')}"
        else:
            period_text = "—"

        period_val = QLabel(period_text)
        period_val.setStyleSheet("font-size: 13px; color: #2C3E50; background: transparent;")
        period_row.addWidget(period_val)
        period_row.addStretch()
        v.addLayout(period_row)

        btn_layout = QHBoxLayout()

        btn_activate = QPushButton("🔑 Litsenziya olish")
        btn_activate.setStyleSheet("""
            QPushButton { background: #3498DB; color: white; padding: 8px 16px;
                font-size: 12px; border-radius: 5px; font-weight: bold; border: none; }
            QPushButton:hover { background: #2980B9; }
        """)
        btn_activate.clicked.connect(self._open_license_dialog)
        btn_layout.addWidget(btn_activate)

        btn_terms = QPushButton("📄 Shartlar")
        btn_terms.setStyleSheet("""
            QPushButton { background: #95A5A6; color: white; padding: 8px 16px;
                font-size: 12px; border-radius: 5px; font-weight: bold; border: none; }
            QPushButton:hover { background: #7F8C8D; }
        """)
        btn_terms.clicked.connect(self._open_terms_dialog)
        btn_layout.addWidget(btn_terms)

        btn_layout.addStretch()
        v.addLayout(btn_layout)

        return card

    def _open_license_dialog(self):
        """Litsenziya dialogini ochish"""
        from core.license import check_license
        from ui.license_dialog import LicenseDialog

        status, message = check_license()
        dlg = LicenseDialog(status, message, self)
        dlg.exec()
        # Dialog yopilgandan keyin sahifani yangilash
        self._refresh_stats()

    def _open_terms_dialog(self):
        """Litsenziya shartlari va muallif kontaktlari dialogini ochish"""
        dlg = QDialog(self)
        dlg.setWindowTitle("📜 Litsenziya shartlari")
        dlg.setMinimumSize(600, 550)
        dlg.setMaximumSize(700, 650)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Sarlavha
        title = QLabel("📜 SMARTDJ3 LITSENZIYA SHARTLARI")
        title.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: #2C3E50;
            padding: 12px; background: #EBF5FB; border-radius: 8px;
            text-align: center;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Asosiy matn — scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: 1px solid #BDC3C7; border-radius: 8px; background: white; }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(12)

        terms_text = QLabel(
            "<div style='font-size: 13px; color: #2C3E50; line-height: 1.6;'>"

            "<b style='color: #2980B9;'>1. UMUMIY QOIDALAR</b><br>"
            "• SmartDJ3 dasturi muallif huquqi bilan himoyalangan<br>"
            "• Dasturni faqat shaxsiy maqsadlarda ishlatish mumkin<br>"
            "• Sotish, tarqatish yoki o'zgartirish taqiqlanadi<br><br>"

            "<b style='color: #2980B9;'>2. SINOV MUDDATI</b><br>"
            "• Dastur ishga tushirilgan kundan 7 kun bepul ishlaydi<br>"
            "• Sinov davomida barcha funksiyalar mavjud<br>"
            "• 7 kun o'tgandan keyin faollashtirish kerak<br><br>"

            "<b style='color: #2980B9;'>3. FAOLLASHTIRISH</b><br>"
            "• \"Litsenziya olish\" tugmasini bosing<br>"
            "• Foydalanuvchi kodi avtomatik yaratiladi<br>"
            "• Muallifdan tasdiqlash kodi olish kerak<br>"
            "• Bitta litsenziya bitta kompyuter uchun<br><br>"

            "<b style='color: #2980B9;'>4. MAS'ULIYAT</b><br>"
            "• Dastur natijalari uchun muallif javobgar emas<br>"
            "• Bazani avval saqlab qo'yish tavsiya etiladi<br>"
            "• Texnik nosozliklardan foydalanuvchi o'zi javobgar<br><br>"

            "<b style='color: #2980B9;'>5. QO'SHIMCHA SHARTLAR</b><br>"
            "• Yangilanishlar bepul taqdim etiladi<br>"
            "• Bitta litsenziya cheksiz muddatga amal qiladi<br>"
            "• Litsenziya qayta sotilmaydi yoki o'tkazilmaydi<br>"

            "</div>"
        )
        terms_text.setWordWrap(True)
        terms_text.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(terms_text)

        # Ajratuvchi chiziq
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #BDC3C7; margin: 10px 0;")
        content_layout.addWidget(separator)

        # Muallif kontaktlari
        contact_title = QLabel("📞 MUALLIF BILAN BOG'LANISH")
        contact_title.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #2980B9;
            padding: 8px 0;
        """)
        content_layout.addWidget(contact_title)

        contact_text = QLabel(
            "<div style='font-size: 13px; color: #2C3E50; line-height: 1.8;'>"
            "<b>Muallif:</b> Duvlayev Kamil Abdurashidovich<br>"
            "<b>Telefon:</b> <a href='tel:+998775000469' style='color: #3498DB;'>+998 77-500-04-69</a><br>"
            "<b>Telegram:</b> <a href='https://t.me/DUVLAYEV_KAMI' style='color: #3498DB;'>@DUVLAYEV_KAMI</a>"
            "</div>"
        )
        contact_text.setWordWrap(True)
        contact_text.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(contact_text)

        # Ajratuvchi chiziq
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("color: #BDC3C7; margin: 10px 0;")
        content_layout.addWidget(separator2)

        # Eslatmalar
        notes_title = QLabel("📌 MUHIM ESLATMALAR")
        notes_title.setStyleSheet("""
            font-size: 14px; font-weight: bold; color: #E67E22;
            padding: 8px 0;
        """)
        content_layout.addWidget(notes_title)

        notes_text = QLabel(
            "<div style='font-size: 12px; color: #5D6D7E; line-height: 1.6;'>"
            "• Dasturni ishlatishdan oldin bazani zaxiralab qo'ying<br>"
            "• Litsenziya kodini himoya qiling, boshqa bilan ulashmang<br>"
            "• Muammo chiqsa, muallif bilan bog'laning"
            "</div>"
        )
        notes_text.setWordWrap(True)
        notes_text.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(notes_text)

        # Versiya
        version_label = QLabel("Versiya: SmartDJ3 v1.0")
        version_label.setStyleSheet("font-size: 11px; color: #95A5A6; padding-top: 5px;")
        content_layout.addWidget(version_label)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Yopish tugmasi
        btn_close = QPushButton("✕ Yopish")
        btn_close.setStyleSheet("""
            QPushButton {
                background: #E74C3C; color: white; padding: 10px 30px;
                font-size: 13px; font-weight: bold; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: #C0392B; }
        """)
        btn_close.clicked.connect(dlg.close)
        btn_close_layout = QHBoxLayout()
        btn_close_layout.addStretch()
        btn_close_layout.addWidget(btn_close)
        btn_close_layout.addStretch()
        layout.addLayout(btn_close_layout)

        dlg.setLayout(layout)
        dlg.exec()

    def _open_guide(self):
        """Qo'llanma — foydalanuvchi qo'llanmasi"""
        dlg = QDialog(self)
        dlg.setWindowTitle("📖 SmartDJ3 Qo'llanma")
        dlg.setMinimumSize(650, 600)
        dlg.setMaximumSize(750, 700)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Sarlavha
        title = QLabel("📖 SMARTDJ3 FOYDALANUVCHI QO'LLANMASI")
        title.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: white;
            padding: 14px; background: #2980B9; border-radius: 8px;
            text-align: center;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: 1px solid #BDC3C7; border-radius: 8px; background: white; }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)

        guide_text = QLabel(
            "<div style='font-size: 13px; color: #2C3E50; line-height: 1.7;'>"

            # ===== 1. ISHGA TUSHIRISH =====
            "<b style='color: #E74C3C; font-size: 15px;'>1. DASTURNI ISHGA TUSHIRISH</b><br>"
            "SmartDJ3 ni oching. Agar birinchi marta ishlatayotgan bo'lsangiz, "
            "7 kunlik sinov muddati boshlanadi. Litsenziya olish uchun "
            "\"🔑 Litsenziya olish\" tugmasini bosing.<br><br>"

            # ===== 2. MA'LUMOTLARNI KIRITISH =====
            "<b style='color: #E74C3C; font-size: 15px;'>2. MA'LUMOTLARNI KIRITISH</b><br>"
            "Dars jadvalini yaratishdan oldin quyidagi ma'lumotlarni kiriting. "
            "Har bir bosqichni ketma-ket bajarish tavsiya etiladi.<br><br>"

            "<b style='color: #27AE60; font-size: 14px;'>2.1. 📋 Tayanch o'quv reja (BIRINCHI QADAM)</b><br>"
            "\"📋 Tayanch reja\" tugmasini bosing. Bu yerda MMT standart dars rejasini yuklashingiz mumkin.<br>"
            "&nbsp;&nbsp;&nbsp;• Tayanch reja — har bir sinf uchun fanlar va haftalik soatlar ro'yxati<br>"
            "&nbsp;&nbsp;&nbsp;• Dastur MMT standartlariga asoslangan<br>"
            "&nbsp;&nbsp;&nbsp;• Yuklanganda \"Dars biriktirish\" qismida soatlar avtomatik to'ldiriladi<br>"
            "&nbsp;&nbsp;&nbsp;• Tayanch reja PDF formatidan import qilinadi<br><br>"

            "<b style='color: #27AE60; font-size: 14px;'>2.2. 🏫 Sinflar</b><br>"
            "\"Sinflar\" tugmasini bosing.<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Sinf nomi</b> — masalan: 1-A, 2-B, 5-A<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Sinf darajasi</b> — 1-4 sinf (kichik) yoki 5-11 sinf (katta)<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Ish kunlari</b> — 1-4: Dushanba-Juma (5 kun), 5-11: Dushanba-Shanba (6 kun)<br><br>"

            "<b style='color: #27AE60; font-size: 14px;'>2.3. 📚 Fanlar</b><br>"
            "\"Fanlar\" tugmasini bosing.<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Import:</b> \"📥 Tayanch rejadan import\" — avtomatik qo'shadi<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Qo'lda:</b> Fan nomi + qisqacha nom (masalan: Matematika → Mate)<br>"
            "&nbsp;&nbsp;&nbsp;• Sport fanlarini alohida belgilang (SanPIN qoidalari boshqacha)<br><br>"

            "<b style='color: #27AE60; font-size: 14px;'>2.4. 👨‍🏫 O'qituvchilar</b><br>"
            "\"O'qituvchilar\" tugmasini bosing.<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Ism-familiya</b> — to'liq (masalan: Karimova Nodira)<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Fan</b> — qaysi fan o'qitishini tanlang<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Rang</b> — jadvalda ko'rinishi uchun<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Band soatlar</b> — qaysi kun/soatda dars bermaydi<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Metodik kun</b> — haftada bir kun dars o'tkazmaydi<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Sinf rahbari</b> — qaysi sinfning rahbari<br><br>"

            "<b style='color: #27AE60; font-size: 14px;'>2.5. 🚪 Xonalar</b><br>"
            "\"Xonalar\" tugmasini bosing — laboratoriyalar, sport zallari va boshqalar.<br><br>"

            "<b style='color: #27AE60; font-size: 14px;'>2.6. 📝 Dars biriktirish</b><br>"
            "\"Dars biriktirish\" tugmasini bosing.<br>"
            "&nbsp;&nbsp;&nbsp;• Sinfni tanlang (chap tomonda)<br>"
            "&nbsp;&nbsp;&nbsp;• Fan uchun <b>haftalik soat</b> ni kiriting (kasrli: 0.5, 1.5)<br>"
            "&nbsp;&nbsp;&nbsp;• O'qituvchini tanlang<br>"
            "&nbsp;&nbsp;&nbsp;• Tayanch reja yuklangan bo'lsa, soatlar avtomatik to'ldiriladi<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Kasrli soatlar:</b> 0.5, 1.0, 1.5, 2.0 va boshqa qiymatlar kiritish mumkin<br>"
            "&nbsp;&nbsp;&nbsp;• Ayrim fanlar boshqa fan hisobidan o'qitilishi mumkin (masalan: 1.5 soat Geografiya + 0.5 soat Iqtisodiy bilim)<br><br>"

            # ===== 3. JADVAL YARATISH =====
            "<b style='color: #E74C3C; font-size: 15px;'>3. DARS JADVALINI YARATISH</b><br><br>"

            "<b style='color: #8E44AD; font-size: 14px;'>3.1. ⚡ Avtomatik usul</b><br>"
            "\"⚡ AVTOMATIK JADVAL\" tugmasini bosing.<br>"
            "&nbsp;&nbsp;&nbsp;• Hybrid algoritm: BRKGA (genetik) + Backtracking ishlatiladi<br>"
            "&nbsp;&nbsp;&nbsp;• 2-30 soniyada tayyor (sinflar soniga qarab)<br>"
            "&nbsp;&nbsp;&nbsp;• 2-haftalik jadval avtomatik yaratiladi<br>"
            "&nbsp;&nbsp;&nbsp;• Kelajak soati sinf rahbarlariga <b>Juma kuni, 1-darsda</b> avtomatik qo'yiladi<br><br>"

            "<b style='color: #8E44AD; font-size: 14px;'>3.2. ✋ Qo'lda usul</b><br>"
            "\"📅 QO'LDA JADVAL\" tugmasini bosing.<br>"
            "&nbsp;&nbsp;&nbsp;• Darslarni sichqoncha bilan sudrab joylashtiring<br>"
            "&nbsp;&nbsp;&nbsp;• Mavjud darsning ustiga qo'ysangiz — <b>SWAP</b> (almashtirish) taklif qilinadi<br>"
            "&nbsp;&nbsp;&nbsp;• Bo'sh joyga qo'ysangiz — dars o'rniga qo'yiladi<br>"
            "&nbsp;&nbsp;&nbsp;• O'ng tugma — kontekst menyusi (ko'chirish, o'chirish)<br><br>"

            "<b style='color: #8E44AD; font-size: 14px;'>3.3. 🔄 2-haftalik jadval</b><br>"
            "SmartDJ3 ikki haftalik jadval tuzadi:<br>"
            "&nbsp;&nbsp;&nbsp;• <b>1-hafta (Toq)</b> — toq haftalar uchun (1, 3, 5...)<br>"
            "&nbsp;&nbsp;&nbsp;• <b>2-hafta (Juft)</b> — juft haftalar uchun (2, 4, 6...)<br>"
            "&nbsp;&nbsp;&nbsp;• <b>1.5 soatlik fanlar:</b> 1-haftada 2 dars, 2-haftada 1 dars<br>"
            "&nbsp;&nbsp;&nbsp;• <b>0.5 soatlik fanlar (tarkibida):</b> 1-haftada 0 dars, 2-haftada 1 dars<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Alohida 0.5 soatlik fan:</b> jadval tuzishdan oldin dastur \"0.5 soatlik darslar\" ro'yxatidan belgilashni so'raydi<br><br>"

            "<b style='color: #8E44AD; font-size: 14px;'>3.4. 🎯 Teng taqsimot</b><br>"
            "Dastur kunlar bo'yicha darslarni imkon qadar teng taqsimlaydi.<br>"
            "&nbsp;&nbsp;&nbsp;• 1-sinf: kuniga max 4, 2-4 sinf: max 5, 5-11 sinf: max 6 dars<br>"
            "&nbsp;&nbsp;&nbsp;• SanPIN qoidasiga ko'ra 6 darsdan oshmasligi tavsiya etiladi<br><br>"

            # ===== 4. JADVAL BOSHQARISHI =====
            "<b style='color: #E74C3C; font-size: 15px;'>4. JADVAL BOSHQARISHI</b><br><br>"

            "<b style='color: #3498DB; font-size: 14px;'>4.1. Hafta tanlash</b><br>"
            "\"Hafta:\" dropdownidan 1-hafta yoki 2-haftani tanlang.<br>"
            "&nbsp;&nbsp;&nbsp;• Faqat tanlangan hafta ko'rsatiladi<br>"
            "&nbsp;&nbsp;&nbsp;• Saqlash har ikkala haftani saqlaydi<br><br>"

            "<b style='color: #3498DB; font-size: 14px;'>4.2. SWAP — darslarni almashtirish</b><br>"
            "&nbsp;&nbsp;&nbsp;• Bitta darsni boshqa darsning ustiga sudring<br>"
            "&nbsp;&nbsp;&nbsp;• Tasdiqlash dialogi chiqadi<br>"
            "&nbsp;&nbsp;&nbsp;• Ikkala dars o'rnini almashtiradi<br>"
            "&nbsp;&nbsp;&nbsp;• O'qituvchi ziddiyati tekshiriladi<br><br>"

            "<b style='color: #3498DB; font-size: 14px;'>4.3. Kelajak soati</b><br>"
            "Sinf rahbarlariga Juma kuni 1-darsda \"Kelajak soati\" avtomatik qo'yiladi.<br>"
            "&nbsp;&nbsp;&nbsp;• Bazada \"Kelajak soati\" assignment bo'lishi kerak<br>"
            "&nbsp;&nbsp;&nbsp;• Sinf rahbari tayinlangan bo'lishi kerak<br><br>"

            "<b style='color: #3498DB; font-size: 14px;'>4.4. Joylashtirilmagan darslar</b><br>"
            "Pastki qismdagi panelda joylashtirilmagan darslar ko'rsatiladi.<br>"
            "&nbsp;&nbsp;&nbsp;• \"Guruhlash\" — fan/o'qituvchi/sinf bo'yicha ajratish<br>"
            "&nbsp;&nbsp;&nbsp;• Darsni tanlab jadvalga sudring<br><br>"

            # ===== 5. MONITORING =====
            "<b style='color: #E74C3C; font-size: 15px;'>5. MONITORING</b><br><br>"

            "<b style='color: #F39C12; font-size: 14px;'>5.1. Haqiqiy vaqt</b><br>"
            "\"📊 Monitoring\" tugmasini bosing.<br>"
            "&nbsp;&nbsp;&nbsp;• Har 60 sekundda yangilanadi<br>"
            "&nbsp;&nbsp;&nbsp;• Hozirgi dars, o'qituvchi, xona ko'rsatiladi<br>"
            "&nbsp;&nbsp;&nbsp;• 3 tab: Sinflar, O'qituvchilar, Xonalar<br><br>"

            "<b style='color: #F39C12; font-size: 14px;'>5.2. Demo rejim</b><br>"
            "\"🎮 Demo rejim\" checkboxini yoqing.<br>"
            "&nbsp;&nbsp;&nbsp;• Kun va dars soatini tanlang<br>"
            "&nbsp;&nbsp;&nbsp;• Haqiqiy vaqt o'rniga tanlangan vaqt bo'yicha ko'rsatiladi<br>"
            "&nbsp;&nbsp;&nbsp;• Sinov uchun yoki boshqa kunlarni ko'rish uchun<br><br>"

            # ===== 6. SANPIN =====
            "<b style='color: #E74C3C; font-size: 15px;'>6. SANPIN TEKSHIRISH</b><br>"
            "\"📋 SanPIN tekshiruvi\" tugmasini bosing.<br>"
            "&nbsp;&nbsp;&nbsp;• Kunlik limitlar tekshiriladi: 1-sinf: 4, 2-4: 5, 5-11: 6 dars<br>"
            "&nbsp;&nbsp;&nbsp;• Haftalik limitlar tekshiriladi<br>"
            "&nbsp;&nbsp;&nbsp;• Oyna (bo'sh darslar orasida) aniqlanadi<br>"
            "&nbsp;&nbsp;&nbsp;• Ball va ogohlantirishlar ko'rsatiladi<br>"
            "&nbsp;&nbsp;&nbsp;• Tayanch reja asosiy yo'nalish sifatida ishlatiladi<br><br>"

            # ===== 7. CHOP ETISH =====
            "<b style='color: #E74C3C; font-size: 15px;'>7. CHOP ETISH / EKSPORT</b><br><br>"

            "<b style='color: #1ABC9C; font-size: 14px;'>7.1. Formatlar</b><br>"
            "&nbsp;&nbsp;&nbsp;• 📄 <b>PDF</b> — chop etish uchun eng yaxshi<br>"
            "&nbsp;&nbsp;&nbsp;• 📊 <b>Excel</b> — tahrirlash uchun qulay<br>"
            "&nbsp;&nbsp;&nbsp;• 📝 <b>Word</b> — hujjat sifatida saqlash<br>"
            "&nbsp;&nbsp;&nbsp;• 🌐 <b>HTML</b> — brauzerda ko'rish<br><br>"

            "<b style='color: #1ABC9C; font-size: 14px;'>7.2. Hafta tanlash</b><br>"
            "Export dialogida \"Hafta tanlash\" qismidan tanlang:<br>"
            "&nbsp;&nbsp;&nbsp;• <b>1-hafta</b> — faqat toq haftalar jadvali<br>"
            "&nbsp;&nbsp;&nbsp;• <b>2-hafta</b> — faqat juft haftalar jadvali<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Ikkalasi</b> — ikkala hafta bitta faylda<br><br>"

            "<b style='color: #1ABC9C; font-size: 14px;'>7.3. Sozlamalar</b><br>"
            "&nbsp;&nbsp;&nbsp;• <b>Chop etish turi:</b> Umumiy, Sinf, O'qituvchi, Fan<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Maktab nomi:</b> Sarlavhada ko'rsatiladi<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Shrift:</b> 6-14 pt oralig'ida<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Qog'oz:</b> A4, A3, Letter, Legal<br>"
            "&nbsp;&nbsp;&nbsp;• <b>Yo'nalish:</b> Vertikal yoki Gorizontal<br><br>"

            # ===== 8. MASLAHATLAR =====
            "<b style='color: #E74C3C; font-size: 15px;'>8. MASLAHATLAR</b><br>"
            "&nbsp;&nbsp;&nbsp;• Bazani muntazam zaxiralab turing<br>"
            "&nbsp;&nbsp;&nbsp;• Avtomatik jadvaldan oldin barcha ma'lumotlarni tekshiring<br>"
            "&nbsp;&nbsp;&nbsp;• 0.5 soatlik fanlar uchun \"Dars biriktirish\" da 0.5 kiriting<br>"
            "&nbsp;&nbsp;&nbsp;• Monitoring demo rejimi bilan jadvalni oldindan ko'ring<br>"
            "&nbsp;&nbsp;&nbsp;• Muammo chiqsa, \"📄 Shartlar\" sahifasidan muallif bilan bog'laning<br>"
            "&nbsp;&nbsp;&nbsp;• Export qilishdan oldin hafta tanlaganingizga ishonch hosil qiling<br><br>"

            "<b style='color: #9B59B6;'>📞 Qo'shimcha ma'lumot:</b><br>"
            "&nbsp;&nbsp;&nbsp;• Muallif: Duvlayev Kamil Abdurashidovich<br>"
            "&nbsp;&nbsp;&nbsp;• Versiya: SmartDJ3<br>"
            "&nbsp;&nbsp;&nbsp;• Yil: 2026<br><br>"

            "</div>"
        )
        guide_text.setWordWrap(True)
        guide_text.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(guide_text)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Yopish tugmasi
        btn_close = QPushButton("✕ Yopish")
        btn_close.setStyleSheet("""
            QPushButton {
                background: #3498DB; color: white; padding: 10px 30px;
                font-size: 13px; font-weight: bold; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: #2980B9; }
        """)
        btn_close.clicked.connect(dlg.close)
        btn_close_layout = QHBoxLayout()
        btn_close_layout.addStretch()
        btn_close_layout.addWidget(btn_close)
        btn_close_layout.addStretch()
        layout.addLayout(btn_close_layout)

        dlg.setLayout(layout)
        dlg.exec()

    def open_classes(self):
        """Sinflar oynasi"""
        win = ClassWindow(self.db)
        win.setWindowFlags(Qt.WindowType.Window)
        win.show()
        self._classes_window = win
        self._refresh_stats()

    def open_subjects(self):
        """Fanlar oynasi"""
        win = SubjectWindow(self.db)
        win.setWindowFlags(Qt.WindowType.Window)
        win.show()
        self._subjects_window = win
        self._refresh_stats()

    def open_teachers(self):
        """O'qituvchilar oynasi"""
        win = TeacherWindow(self.db)
        win.setWindowFlags(Qt.WindowType.Window)
        win.show()
        self._teachers_window = win
        self._refresh_stats()

    def open_assignments(self):
        """Dars biriktirish oynasi"""
        win = AssignmentWindow(self.db)
        win.setWindowFlags(Qt.WindowType.Window)
        win.show()
        self._assignments_window = win
        self._refresh_stats()

    def open_classrooms(self):
        """Xonalar oynasi"""
        win = ClassroomWindow(self.db)
        win.setWindowFlags(Qt.WindowType.Window)
        win.show()
        self._classrooms_window = win

    def open_tayanch_reja(self):
        """Tayanch reja oynasi — MTT standart dars rejasini ko'rish"""
        # Agar oyna allaqachon ochiq bo'lsa — oldingi planiga chiqarish
        if hasattr(self, '_tayanch_window') and self._tayanch_window is not None:
            if self._tayanch_window.isVisible():
                self._tayanch_window.bring_to_front()
                return
            else:
                self._tayanch_window = None

        from ui.tayanch_reja_window import TayanchRejaWindow
        # Oynani ochoq (non-modal) qilish — boshqa oynalar bilan ishlash mumkin
        win = TayanchRejaWindow(self.db, self)
        win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        win.show()
        self._tayanch_window = win  # Referensni saqlash (garbage collection dan himoya)

    def open_monitoring(self):
        """Monitoring rejimi — real vaqt kuzatish"""
        # Agar oyna allaqachon ochiq bo'lsa — oldingi planiga chiqarish
        if hasattr(self, '_monitoring_window') and self._monitoring_window is not None:
            if self._monitoring_window.isVisible():
                self._monitoring_window.bring_to_front()
                return
            else:
                self._monitoring_window = None

        win = MonitoringWindow(self.db, self)
        win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        win.show()
        self._monitoring_window = win

    def clear_all_database(self):
        """Bazani to'liq tozalash — 2 bosqichli tasdiqlash + backup"""
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONWARNING)
        except Exception:
            pass
        reply1 = QMessageBox.warning(
            self, "⚠️ OGOHLANTIRISH!",
            "BARCHA MA'LUMOTLAR O'CHIRILADI!\n\n"
            "• Sinflar\n• Fanlar\n• O'qituvchilar\n• Xonalar\n"
            "• Dars biriktirishlar\n• Dars jadvali\n\n"
            "Bu amal qaytarib bo'lmaydi!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply1 != QMessageBox.StandardButton.Yes:
            return

        # 2-BOSQICH: Matn kiriting
        dialog = QDialog(self)
        dialog.setWindowTitle("🔥 TASDIQLASH")
        dialog.setMinimumWidth(400)
        dialog_layout = QVBoxLayout()

        warning = QLabel("⚠️ BAZANI TO'LIQ TOZALASH")
        warning.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #E74C3C; "
            "padding: 15px; background: #FDEDEC; border-radius: 8px;"
        )
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialog_layout.addWidget(warning)

        desc = QLabel(
            "Barcha ma'lumotlar o'chiriladi va qaytarib bo'lmaydi.\n"
            "Davom etish uchun quyidagini kiriting:"
        )
        desc.setStyleSheet("font-size: 13px; color: #2C3E50; padding: 10px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        dialog_layout.addWidget(desc)

        confirm_input = QLineEdit()
        confirm_input.setPlaceholderText("O'CHIRISH deb yozing")
        confirm_input.setStyleSheet(
            "font-size: 14px; padding: 10px; border: 2px solid #E74C3C; "
            "border-radius: 5px; font-weight: bold;"
        )
        confirm_input.setMaxLength(20)
        dialog_layout.addWidget(confirm_input)

        status_label = QLabel("")
        status_label.setStyleSheet("font-size: 12px; color: #E74C3C; padding: 5px;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialog_layout.addWidget(status_label)

        btn_layout = QHBoxLayout()

        yes_btn = QPushButton("🔥 TOZALASH")
        yes_btn.setEnabled(False)
        yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white;
                padding: 12px 25px; font-size: 14px;
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
            QPushButton:disabled { background-color: #BDC3C7; }
        """)
        btn_layout.addWidget(yes_btn)

        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6; color: white;
                padding: 12px 25px; font-size: 14px;
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7F8C8D; }
        """)
        btn_layout.addWidget(cancel_btn)
        dialog_layout.addLayout(btn_layout)

        dialog.setLayout(dialog_layout)

        def on_text_changed(text):
            normalized = text.strip().upper().replace("'", "'").replace("'", "'")
            if normalized == "O'CHIRISH":
                yes_btn.setEnabled(True)
                status_label.setText("✅ Tasdiqlash tayyor")
                status_label.setStyleSheet("font-size: 12px; color: #27AE60; padding: 5px;")
            else:
                yes_btn.setEnabled(False)
                status_label.setText("'O'CHIRISH' deb yozing")
                status_label.setStyleSheet("font-size: 12px; color: #E74C3C; padding: 5px;")

        confirm_input.textChanged.connect(on_text_changed)

        def on_confirm():
            dialog.accept()

        def on_cancel():
            dialog.reject()

        yes_btn.clicked.connect(on_confirm)
        cancel_btn.clicked.connect(on_cancel)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # BACKUP yaratish
        try:
            backup_data = {
                'backup_date': datetime.now().isoformat(),
                'classes': [],
                'subjects': [],
                'teachers': [],
                'classrooms': [],
                'assignments': []
            }

            for cls in self.db.get_all_classes():
                backup_data['classes'].append({
                    'id': cls[0], 'name': cls[1], 'level': cls[2],
                    'students_count': cls[3] if len(cls) > 3 else 0,
                    'working_days': cls[4] if len(cls) > 4 else 6
                })

            for s in self.db.get_all_subjects():
                backup_data['subjects'].append({
                    'id': s[0], 'name': s[1], 'short_name': s[2],
                    'difficulty': s[3] if len(s) > 3 else 5
                })

            for t in self.db.get_all_teachers():
                backup_data['teachers'].append({
                    'id': t[0], 'full_name': t[1], 'phone': t[2],
                    'color': t[3], 'class_teacher_of': t[4],
                    'methodic_day': t[5] if len(t) > 5 else None
                })

            for cr in self.db.get_all_classrooms():
                backup_data['classrooms'].append({
                    'id': cr[0], 'room_number': cr[1],
                    'capacity': cr[2], 'room_type': cr[3]
                })

            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            QMessageBox.warning(self, "Backup xatolik", f"Backup yaratilmadi:\n{str(e)}")
            return

        # TOZALASH
        self.db.clear_all()

        # Statistika yangilash
        self._refresh_stats()

        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
        QMessageBox.information(
            self, "✅ Tozalandi",
            f"Barcha ma'lumotlar o'chirildi!\n\n"
            f"📦 Zaxira: {backup_file}"
        )

    def open_manual_schedule(self):
        """Qo'lda jadval tuzish oynasi"""
        try:
            self._schedule_win = ManualScheduleWindow(self.db)
            # Agar prerequisite bajarilmasa, oyna ko'rsatilmaydi
            if not hasattr(self._schedule_win, 'classes'):
                return
            self._schedule_win.show()
            self._schedule_win.raise_()
        except Exception as e:
            logging.error(traceback.format_exc())
            QMessageBox.warning(self, "Xatolik", f"Oyna ochilmadi:\n{str(e)}")

    def check_sanpin(self):
        """Barcha sinflar uchun SanPIN tekshiruvi"""
        classes = self.db.get_all_classes()
        if not classes:
            QMessageBox.warning(self, "Xatolik", "Sinflar yo'q!")
            return

        # Bazadan mavjud jadvalni yuklash — faqat 1-hafta (week_index=0)
        saved = self.db.load_scheduled_lessons(week_index=0)
        if not saved:
            QMessageBox.warning(
                self, "Xatolik",
                "Tekshirish uchun dars jadvali topilmadi!\n\n"
                "Avval '⚡ Avtomatik jadval' tugmasini bosing."
            )
            return

        results = []
        tayanch_data = self.db.load_tayanch_reja()

        for cls in classes:
            cid = cls[0]
            cname = cls[1]
            level = cls[2] if len(cls) > 2 else 5

            # Bu sinfning darslarini ajratish
            grid = [["" for _ in range(6)] for _ in range(6)]
            for (class_id, day, period), info in saved.items():
                if class_id == cid and day < 6 and period < 6:
                    grid[period][day] = info['subject_name']

            # Bo'sh jadvalni o'tkazib yuborish
            total_lessons = sum(1 for row in grid for cell in row if cell)
            if total_lessons == 0:
                continue

            # Tayanch soatlarni to'plash
            tayanch_hours = {}
            for t in tayanch_data:
                if t['class_level'] == level:
                    tayanch_hours[t['subject_name']] = t['weekly_hours']

            res = self.sanpin.check_timetable(grid, level, tayanch_hours)
            res['class_name'] = cname
            res['total_lessons'] = total_lessons
            results.append(res)

        if not results:
            QMessageBox.warning(
                self, "Xatolik",
                "Tekshirish uchun dars jadvali topilmadi!"
            )
            return

        dialog = SanPINDialog(results, self)
        dialog.exec()

    def auto_schedule(self):
        """Avtomatik jadval tuzish — darhol boshlaydi"""
        try:
            self._schedule_win = ManualScheduleWindow(self.db, empty=True)
            if not hasattr(self._schedule_win, 'classes'):
                return
            self._schedule_win.show()
            self._schedule_win.raise_()
            QTimer.singleShot(500, self._schedule_win._on_auto)
        except Exception as e:
            logging.error(traceback.format_exc())
            QMessageBox.warning(self, "Xatolik", f"Oyna ochilmadi:\n{str(e)}")

    def manual_schedule(self):
        """Qo'lda jadval tuzish — bo'sh jadval"""
        self._schedule_win = ManualScheduleWindow(self.db, empty=True)
        self._schedule_win.show()
        self._schedule_win.raise_()

    # ================================================================
    # CHOP ETISH
    # ================================================================
    def export_jadval(self):
        try:
            from ui.manual_schedule_window import ManualScheduleWindow
            td = None
            td2 = None
            cls = None

            for w in QApplication.topLevelWidgets():
                if isinstance(w, ManualScheduleWindow) and w.isVisible():
                    td = dict(w.timetable_data)
                    td2 = dict(w.timetable_data_week2) if hasattr(w, 'timetable_data_week2') and w.timetable_data_week2 else None
                    cls = list(w.classes)
                    break

            if not td:
                saved_w1 = self.db.load_scheduled_lessons(week_index=0)
                if saved_w1:
                    td = saved_w1
                    cls = self.db.get_all_classes()
                saved_w2 = self.db.load_scheduled_lessons(week_index=1)
                if saved_w2:
                    td2 = saved_w2

            if not td:
                QMessageBox.warning(self, "Xatolik",
                    "Dars jadvali topilmadi!\nAvval jadvalni tuzing.")
                return

            from core.export_dialog import FormatSelectDialog
            dlg = FormatSelectDialog(self)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            from core.export_settings import ExportSettingsDialog
            settings = ExportSettingsDialog(
                self.db, td, cls, self, export_format=dlg.selected_format,
                tt2=td2)
            settings.exec()

        except Exception as e:
            logging.error(f"export_jadval: {e}")
            logging.error(traceback.format_exc())
            QMessageBox.critical(self, "Xatolik", str(e))

    # ================================================================
    # DASTUR YOPISH
    # ================================================================
    def closeEvent(self, event):
        self.db.close()
        event.accept()


# ================================================================
# DASTURNI ISHGA TUSHIRISH
# ================================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Windows qorong'i temasi merosini bekor qilish — doimo yorug' tema
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    # Litsenziya tekshiruvi
    from core.license import check_license
    from ui.license_dialog import LicenseDialog

    status, message = check_license()
    if status in ("expired",):
        from PyQt6.QtWidgets import QDialog
        dlg = LicenseDialog(status, message)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)

    oyna = DarsJadvali()
    oyna.show()

    sys.exit(app.exec())