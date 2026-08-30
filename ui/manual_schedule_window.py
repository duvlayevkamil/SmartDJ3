from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QMessageBox, QComboBox, QSplitter,
                             QWidget, QHeaderView, QMenu,
                             QScrollArea, QFrame, QGroupBox,
                             QApplication, QAbstractItemView, QProgressBar,
                             QTextEdit, QFileDialog)
from PyQt6.QtCore import Qt, QMimeData, QSize, QTimer, QThread, pyqtSignal, QPoint, QRect
from PyQt6.QtWidgets import QLayout, QLayoutItem, QSizePolicy
from PyQt6.QtGui import QColor, QDrag, QFont, QAction, QPixmap, QPainter, QBrush, QPen
from datetime import datetime
import logging


class MethodicDayWarningDialog(QDialog):
    """Metodik kun ogohlantirishi — kuchli, ajralib turadigan dialog"""

    def __init__(self, teacher_name, day_name, lesson_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔴 METODIK KUN OGOGHLANTIRISHI")
        self.setMinimumWidth(520)
        self.result = False
        self.teacher_name = teacher_name
        self.day_name = day_name
        self.lesson_info = lesson_info
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        self.setLayout(layout)

        header = QLabel("🔴 DIQQAT! METODIK KUN")
        header.setStyleSheet("""
            font-size: 22px; font-weight: bold; color: white;
            background-color: #C0392B; padding: 20px;
            border-radius: 10px; border: 3px solid #922B21;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        warning = QLabel(
            f"O'qituvchi {self.teacher_name} ning\n"
            f"METODIK KUNI — {self.day_name}!\n\n"
            f"Metodik kunda o'qituvchi maktabda bo'lishi shart emas.\n"
            f"Dars qo'yilsa, o'qituvchi yo'q bo'lishi mumkin!"
        )
        warning.setStyleSheet("""
            font-size: 14px; color: #922B21; padding: 15px;
            background-color: #FADBD8; border-radius: 8px;
            border: 2px solid #E74C3C; font-weight: bold;
        """)
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning)

        info = self.lesson_info
        info_text = (
            f"📚 {info.get('subject_name', '?')} → "
            f"🏫 {info.get('class_name', '?')} | "
            f"📅 {self.day_name} {info.get('period', '?')}-dars"
        )
        info_label = QLabel(info_text)
        info_label.setStyleSheet("""
            font-size: 14px; color: #2C3E50; padding: 12px;
            background: #EBF5FB; border-radius: 6px; font-weight: bold;
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        question = QLabel("Darsni qo'ysakmi?")
        question.setStyleSheet("font-size: 16px; font-weight: bold; color: #C0392B;")
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(question)

        btn_layout = QHBoxLayout()

        yes_btn = QPushButton("✅ Ha, qo'yish")
        yes_btn.setStyleSheet("""
            QPushButton { background: #27AE60; color: white; padding: 14px 30px;
                font-size: 15px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #229954; }
        """)
        yes_btn.clicked.connect(self.accept)
        btn_layout.addWidget(yes_btn)

        no_btn = QPushButton("❌ Yo'q, bekor qilish")
        no_btn.setStyleSheet("""
            QPushButton { background: #E74C3C; color: white; padding: 14px 30px;
                font-size: 15px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #C0392B; }
        """)
        no_btn.clicked.connect(self.reject)
        btn_layout.addWidget(no_btn)

        layout.addLayout(btn_layout)

    def accept(self):
        self.result = True
        super().accept()

    def reject(self):
        self.result = False
        super().reject()


class StrictUnavailableWarningDialog(QDialog):
    """Qat'iy band soat ogohlantirishi — kuchli, ajralib turadigan dialog"""

    def __init__(self, teacher_name, day_name, period, lesson_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔴 QAT'IY BAND SOAT OGOGHLANTIRISHI")
        self.setMinimumWidth(520)
        self.result = False
        self.teacher_name = teacher_name
        self.day_name = day_name
        self.period = period
        self.lesson_info = lesson_info
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        self.setLayout(layout)

        header = QLabel("🔴 DIQQAT! QAT'IY BAND SOAT")
        header.setStyleSheet("""
            font-size: 22px; font-weight: bold; color: white;
            background-color: #D35400; padding: 20px;
            border-radius: 10px; border: 3px solid #BA4A00;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        warning = QLabel(
            f"O'qituvchi {self.teacher_name} ning\n"
            f"{self.day_name} {self.period}-darsda qat'iy bandligi belgilangan!\n\n"
            f"O'qituvchi ushbu vaqtda boshqa ish bilan band bo'lishi mumkin.\n"
            f"Dars qo'yilsa, ziddiyat yuzaga kelishi mumkin!"
        )
        warning.setStyleSheet("""
            font-size: 14px; color: #935116; padding: 15px;
            background-color: #FDEBD0; border-radius: 8px;
            border: 2px solid #E67E22; font-weight: bold;
        """)
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning)

        info = self.lesson_info
        info_text = (
            f"📚 {info.get('subject_name', '?')} → "
            f"🏫 {info.get('class_name', '?')} | "
            f"📅 {self.day_name} {info.get('period', '?')}-dars"
        )
        info_label = QLabel(info_text)
        info_label.setStyleSheet("""
            font-size: 14px; color: #2C3E50; padding: 12px;
            background: #EBF5FB; border-radius: 6px; font-weight: bold;
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        question = QLabel("Darsni qo'ysakmi?")
        question.setStyleSheet("font-size: 16px; font-weight: bold; color: #D35400;")
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(question)

        btn_layout = QHBoxLayout()

        yes_btn = QPushButton("✅ Ha, qo'yish")
        yes_btn.setStyleSheet("""
            QPushButton { background: #27AE60; color: white; padding: 14px 30px;
                font-size: 15px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #229954; }
        """)
        yes_btn.clicked.connect(self.accept)
        btn_layout.addWidget(yes_btn)

        no_btn = QPushButton("❌ Yo'q, bekor qilish")
        no_btn.setStyleSheet("""
            QPushButton { background: #E74C3C; color: white; padding: 14px 30px;
                font-size: 15px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #C0392B; }
        """)
        no_btn.clicked.connect(self.reject)
        btn_layout.addWidget(no_btn)

        layout.addLayout(btn_layout)

    def accept(self):
        self.result = True
        super().accept()

    def reject(self):
        self.result = False
        super().reject()


class SanPINWarningDialog(QDialog):
    """SanPIN buzilishi haqida ogohlantirish va tasdiqlash dialogi"""

    def __init__(self, violations, lesson_info, parent=None):
        """
        violations: list of {'type': 'hard'|'soft', 'message': str}
        lesson_info: dict — qo'yilayotgan dars haqida ma'lumot
        """
        super().__init__(parent)
        self.setWindowTitle("⚠️ SanPIN ogohlantirishi")
        self.setMinimumWidth(480)
        self.result = False  # True = qo'ysin, False = qo'ymasin
        self.violations = violations
        self.lesson_info = lesson_info
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        self.setLayout(layout)

        # Sarlavha
        hard = [v for v in self.violations if v['type'] == 'hard']
        soft = [v for v in self.violations if v['type'] == 'soft']

        if hard:
            header_text = f"❌ {len(hard)} ta jiddiy buzilish"
            header_bg = "#E74C3C"
        else:
            header_text = f"⚠️ {len(soft)} ta chetlanish"
            header_bg = "#F39C12"

        header = QLabel(header_text)
        header.setStyleSheet(f"""
            font-size: 18px; font-weight: bold; color: white;
            background-color: {header_bg}; padding: 14px;
            border-radius: 8px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Dars ma'lumoti
        info = self.lesson_info
        info_label = QLabel(
            f"📚 {info.get('subject_name', '?')} → "
            f"🏫 {info.get('class_name', '?')} | "
            f"📅 {info.get('day_name', '?')} {info.get('period', '?')}-dars"
        )
        info_label.setStyleSheet("""
            font-size: 14px; color: #2C3E50; padding: 10px;
            background: #EBF5FB; border-radius: 6px; font-weight: bold;
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Buzilishlar ro'yxati
        details = QTextEdit()
        details.setReadOnly(True)
        html = "<style>body{font-family:Arial;font-size:13px;} li{margin:4px 0;}</style>"

        if hard:
            html += "<h3 style='color:#E74C3C;'>❌ Jiddiy buzilishlar:</h3><ul>"
            for v in hard:
                html += f"<li style='color:#C0392B;'>{v['message']}</li>"
            html += "</ul>"

        if soft:
            html += "<h3 style='color:#F39C12;'>⚠️ Chetlanishlar:</h3><ul>"
            for v in soft:
                html += f"<li style='color:#E67E22;'>{v['message']}</li>"
            html += "</ul>"

        details.setHtml(html)
        details.setMaximumHeight(200)
        details.setStyleSheet("QTextEdit { background: white; border: 1px solid #ddd; border-radius: 6px; padding: 8px; color: #000000; }")
        layout.addWidget(details)

        # Savol
        question = QLabel("Darsni qo'ysakmi?")
        question.setStyleSheet("font-size: 15px; font-weight: bold; color: #2C3E50; text-align: center;")
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(question)

        # Tugmalar
        btn_layout = QHBoxLayout()

        yes_btn = QPushButton("✅ Ha, qo'yish")
        yes_btn.setStyleSheet("""
            QPushButton { background: #27AE60; color: white; padding: 12px 25px;
                font-size: 14px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #229954; }
        """)
        yes_btn.clicked.connect(self.accept)
        btn_layout.addWidget(yes_btn)

        no_btn = QPushButton("❌ Yo'q, bekor")
        no_btn.setStyleSheet("""
            QPushButton { background: #E74C3C; color: white; padding: 12px 25px;
                font-size: 14px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #C0392B; }
        """)
        no_btn.clicked.connect(self.reject)
        btn_layout.addWidget(no_btn)

        layout.addLayout(btn_layout)

    def accept(self):
        self.result = True
        super().accept()

    def reject(self):
        self.result = False
        super().reject()


class ProgressDialog(QDialog):
    """Avtomatik jadval tuzish jarayoni dialogi — progress + to'xtatish"""

    def __init__(self, total_classes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚡ Avtomatik jadval tuzilmoqda...")
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        self.setModal(True)
        self.cancelled = False

        self.total_classes = total_classes
        self.current_class = 0
        self.results = []

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Sarlavha + miltillaydigan nuqta
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        header = QLabel("⚡ Dars jadvali tuzilmoqda...")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")
        header_layout.addWidget(header)

        # Matn animatsiyasi — nuqtalar siljishi
        self._anim_dots = 0
        self._anim_label = QLabel("⚡")
        self._anim_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498DB;")
        self._anim_label.setFixedWidth(30)
        header_layout.addWidget(self._anim_label)

        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animate_text)
        self._anim_timer.start(400)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_classes)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                text-align: center;
                font-size: 12px;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Holat matni
        self.status_label = QLabel("Tayyorlanmoqda...")
        self.status_label.setStyleSheet("font-size: 13px; color: #7F8C8D;")
        layout.addWidget(self.status_label)

        # Ball
        self.score_label = QLabel("")
        self.score_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #27AE60;")
        layout.addWidget(self.score_label)

        # Vaqt
        self.time_label = QLabel("")
        self.time_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        layout.addWidget(self.time_label)

        # Natijalar jadvali
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(300)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #DEE2E6;
                border-radius: 5px;
                font-size: 11px;
                font-family: Consolas, monospace;
                color: #000000;
            }
        """)
        layout.addWidget(self.results_text)

        # To'xtatish tugmasi
        self.cancel_btn = QPushButton("⏹ To'xtatish")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white;
                padding: 10px 20px; font-size: 14px;
                font-weight: bold; border-radius: 5px;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)

    def _blink_dot(self):
        """Nuqta rangini almashitirish (eski usul — ishlatilmaydi)"""
        pass

    def _on_cancel(self):
        self.cancelled = True
        self.cancel_btn.setText("To'xtatilmoqda...")
        self.cancel_btn.setEnabled(False)
        self.status_label.setText("⏹ Jarayon to'xtatilmoqda...")

    def _animate_text(self):
        """Matn animatsiyasi — ⚡ → 💫 → ⚙️ → 🔄 → ⚡"""
        symbols = ["⚡", "💫", "⚙️", "🔄"]
        self._anim_dots = (self._anim_dots + 1) % len(symbols)
        self._anim_label.setText(symbols[self._anim_dots])

    def update_progress(self, class_name, class_num, score, elapsed, total_elapsed):
        """Progress ni yangilash"""
        self.current_class = class_num
        self.progress_bar.setValue(class_num)

        self.status_label.setText(
            f"📊 {class_name} tayyor ({class_num}/{self.total_classes})"
        )

        # Ball faqat haqiqiy ball bo'lsa ko'rsatiladi (-1 = oxirgi xabar)
        if score >= 0:
            self.score_label.setText(
                f"Ball: {score}/100 {'✅' if score >= 70 else '⚠️' if score >= 50 else '❌'}"
            )

        remaining = (total_elapsed / max(class_num, 1)) * (self.total_classes - class_num)
        self.time_label.setText(
            f"Vaqt: {self._format_time(total_elapsed)} / ~{self._format_time(total_elapsed + remaining)}"
        )

        # Natijani qo'shish — faqat sinf tugaganda
        if score >= 0:
            marker = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
            self.results.append(f"{marker} {class_name}: {score} ball")
            self.results_text.setText("\n".join(self.results))

    def finish(self, success=True, message=""):
        """Dialogni tugatish"""
        self._anim_timer.stop()

        self.progress_bar.setValue(self.total_classes)
        self.cancel_btn.setVisible(False)

        if success:
            self._anim_label.setText("✅")
            self._anim_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #27AE60;")
            self.status_label.setText(f"✅ {message}")
            self.score_label.setText("Barcha sinflar tayyor!")
        else:
            self._anim_label.setText("⏹")
            self._anim_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #E74C3C;")
            self.status_label.setText(f"⏹ {message}")

        # Yopish tugmasi
        close_btn = QPushButton("Yopish")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 10px 20px; font-size: 14px;
                font-weight: bold; border-radius: 5px;
            }
            QPushButton:hover { background-color: #219A52; }
        """)
        close_btn.clicked.connect(self.accept)
        self.layout().addWidget(close_btn)

    def _format_time(self, seconds):
        """Soniyalarni MM:SS formatiga o'tkazish"""
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"


class ScheduleWorker(QThread):
    """
    Background thread — avtomatik jadval tuzish.
    UI bloklanmasin, progress signal orqali yangilansin.
    """
    progress = pyqtSignal(str, int, int, float)  # class_name, idx, score, elapsed
    finished = pyqtSignal(dict, list, int)  # all_data, conflicts, placed_count
    error = pyqtSignal(str)

    def __init__(self, classes, db, parent=None):
        super().__init__(parent)
        self.classes = classes
        self.db = db
        self.cancel_flag = False

    def cancel(self):
        self.cancel_flag = True

    def run(self):
        db = None
        try:
            import time
            from core.scheduler import TimetableScheduler
            from database.db_manager import DatabaseManager

            db = DatabaseManager()
            db.initialize()

            scheduler = TimetableScheduler(db_manager=db)
            start_time = time.time()

            self.progress.emit("Jadval tuzilmoqda...", 0, 0, 0)

            def on_progress(class_name, class_idx, total_classes, score):
                elapsed = time.time() - start_time
                self.progress.emit(
                    f"{class_name} tayyor ({class_idx}/{total_classes})",
                    class_idx, score, elapsed
                )

            all_data, conflicts = scheduler.generate_all_class_timetables(
                self.classes, db,
                cancel_flag=lambda: self.cancel_flag,
                progress_callback=on_progress
            )

            placed = len(all_data)
            elapsed = time.time() - start_time
            self.progress.emit(
                f"Tamom! {placed} ta dars ({elapsed:.0f}s)",
                len(self.classes), -1, elapsed
            )

            self.finished.emit(all_data, conflicts, placed)

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"ScheduleWorker xatolik: {e}\n{error_detail}")
            logging.error(f"ScheduleWorker: {e}\n{error_detail}")
            self.error.emit(f"{type(e).__name__}: {e}")
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass


def normalize_color(color_value, fallback="#3498DB"):
    """Return a valid QColor for hex strings, including legacy values without leading '#'."""
    color_str = str(color_value).strip()
    if not color_str:
        return QColor(fallback)
    if not color_str.startswith("#"):
        color_str = "#" + color_str
    qcolor = QColor(color_str)
    return qcolor if qcolor.isValid() else QColor(fallback)


class FlowGridLayout(QLayout):
    """Gorizontal oqimli tartib — elementlar yonma-yon joylashadi, to'lganda keyingi qatorga o'tadi"""

    def __init__(self, parent=None, spacing=8):
        super().__init__(parent)
        self._spacing = spacing
        self._items = []

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    def _do_layout(self, rect, test_only):
        m = self.contentsMargins()
        effective = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x = effective.x()
        y = effective.y()
        line_height = 0

        for item in self._items:
            wid = item.widget()
            space_x = self._spacing
            space_y = self._spacing
            next_x = x + item.sizeHint().width() + space_x
            next_y = y + item.sizeHint().height() + space_y

            if next_x - space_x > effective.right() and line_height > 0:
                x = effective.x()
                y = next_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = item.sizeHint().height()

            if not test_only:
                item.setGeometry(QRect(x, y, item.sizeHint().width(), item.sizeHint().height()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + m.bottom()


class DraggableLessonButton(QPushButton):
    """Sudrash mumkin bo'lgan dars tugmasi (kartochka)"""

    def __init__(self, lesson_data, count=1, parent=None):
        super().__init__(parent)
        self.lesson_data = lesson_data
        self.count = count

        subject = lesson_data['subject_short'] or lesson_data['subject_name'][:3]

        self.setText(subject)
        self.setFixedSize(40, 30)
        self.setCheckable(True)

        tooltip_html = f"""
        <div style='background-color: #2C3E50; color: white; padding: 8px; border-radius: 5px;'>
            <b style='font-size: 12px; color: #F1C40F;'>📚 {lesson_data['subject_name']}</b><br>
            <span style='font-size: 11px;'>👨‍🏫 {lesson_data['teacher_name']}</span><br>
            <span style='font-size: 11px;'>🏫 {lesson_data.get('class_name', '?')}</span><br>
            <span style='font-size: 10px; color: #2ECC71;'>
                ⏱️ {lesson_data['remaining']}/{lesson_data['weekly_hours']} soat qoldi
            </span>
        </div>
        """
        self.setToolTip(tooltip_html)

        color = normalize_color(lesson_data['color']).name()
        self.setStyleSheet(self._get_card_style(color, count))

    def _get_card_style(self, color, count):
        selected_css = "QPushButton:checked { border: 3px solid #2980B9; }"
        if count > 1:
            return f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: 2px solid #2C3E50;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                    border-right: 4px solid #2C3E50;
                    border-bottom: 4px solid #2C3E50;
                }}
                QPushButton:hover {{
                    border: 3px solid #E74C3C;
                }}
                {selected_css}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: 2px solid #2C3E50;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 3px solid #E74C3C;
                }}
                {selected_css}
            """

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            main_window = self._get_main_window()
            if main_window is not None:
                main_window.select_unplaced_lesson(self.lesson_data, self)
        super().mousePressEvent(event)

    def _get_main_window(self):
        parent = self.parent()
        from ui.manual_schedule_window import ManualScheduleWindow
        while parent is not None and not isinstance(parent, ManualScheduleWindow):
            parent = parent.parent()
        return parent

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        # start_pos mavjud emasligini tekshirish
        if not hasattr(self, 'start_pos'):
            return

        drag = QDrag(self)
        mime_data = QMimeData()

        data_str = (
            f"{self.lesson_data.get('lesson_id', '')}|"
            f"{self.lesson_data.get('class_id', '')}|"
            f"{self.lesson_data.get('class_name', '')}|"
            f"{self.lesson_data.get('subject_name', '')}|"
            f"{self.lesson_data.get('subject_short', '')}|"
            f"{self.lesson_data['teacher_name']}|"
            f"{self.lesson_data['color']}|"
            f"{self.lesson_data['teacher_id']}|"
            f"{self.lesson_data['subject_id']}|"
            f"{self.lesson_data['weekly_hours']}"
        )
        mime_data.setText(data_str)
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        main_window = self._get_main_window()
        if main_window is not None:
            main_window.current_drag_source_widget = self

        try:
            drag.exec(Qt.DropAction.MoveAction)
        finally:
            if main_window is not None and main_window.current_drag_source_widget is self:
                main_window.current_drag_source_widget = None


class ScheduledLessonCard(QWidget):
    """Jadval ichidagi dars kartochkasi — fon rangi paintEvent orqali chiziladi"""

    def __init__(self, lesson_data, parent=None):
        super().__init__(parent)
        self.lesson_data = lesson_data
        self._bg_color = normalize_color(lesson_data.get('color', '#3498DB'))
        self.setAutoFillBackground(False)
        self.drag_start_pos = None  # Sichqoncha bosilgan joy

        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        subject_text = lesson_data.get('subject_short') or lesson_data['subject_name']
        self.subject_label = QLabel(subject_text)
        self.subject_label.setStyleSheet(
            "color: white; font-weight: bold; font-size: 10px;"
            " background: transparent; border: none; margin: 0px; padding: 0px;"
            " line-height: 1;"
        )
        self.subject_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        self.subject_label.setWordWrap(True)
        self.subject_label.setFixedHeight(14)
        self.subject_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.subject_label)

        # Qisqa nomni ishlatish (bazada bo'lsa)
        teacher_short = lesson_data.get('teacher_short', '')
        if not teacher_short:
            teacher_short = self._short_name(lesson_data['teacher_name'])
        self.teacher_label = QLabel(teacher_short)
        self.teacher_label.setStyleSheet(
            "color: rgba(255,255,255,210); font-size: 9px;"
            " background: transparent; border: none; margin: 0px; padding: 0px;"
            " line-height: 1;"
        )
        self.teacher_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.teacher_label.setFixedHeight(12)
        self.teacher_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.teacher_label)

        self.setToolTip(
            f"📚 {lesson_data.get('subject_name', '?')}\n"
            f"👨‍🏫 {lesson_data.get('teacher_name', '?')}\n"
            f"🏫 {lesson_data.get('class_name', '?')}"
        )

    def _short_name(self, full_name):
        """Ismni qisqartirish: 'Karimov Akmal' -> 'Karimov A.'"""
        parts = str(full_name).split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1][0]}."
        return full_name

    def paintEvent(self, event):
        """
        QPainter orqali to'g'ridan-to'g'ri rang chizish.
        Bu Qt stylesheet va QPalette tizimlarini butunlay chetlab o'tadi.
        Shuning uchun QTableWidget ichida ham to'g'ri rang ko'rinadi.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Marginsiz to'liq widget maydoni
        rect = self.rect().adjusted(1, 1, -1, -1)

        # 1) Fon: o'qituvchi rangi bilan to'ldirish
        painter.setBrush(QBrush(self._bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 5, 5)

        # 2) Chegara: biroz to'qroq rang
        border_color = self._bg_color.darker(140)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(rect, 5, 5)

        painter.end()
        # super().paintEvent() chaqirmaymiz — u fon rangini oqlaydi

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def _get_main_window(self):
        parent = self.parent()
        from ui.manual_schedule_window import ManualScheduleWindow
        while parent is not None and not isinstance(parent, ManualScheduleWindow):
            parent = parent.parent()
        return parent

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if self.drag_start_pos is None:
            return

        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        parent_table = self.parent()
        row = -1
        col = -1
        while parent_table is not None and not isinstance(parent_table, QTableWidget):
            parent_table = parent_table.parent()
        if parent_table is not None:
            viewport_pos = self.mapTo(parent_table.viewport(), self.drag_start_pos)
            row = parent_table.rowAt(viewport_pos.y())
            col = parent_table.columnAt(viewport_pos.x())

        drag = QDrag(self)
        mime_data = QMimeData()

        data_values = [
            str(self.lesson_data.get('lesson_id', '')),
            str(self.lesson_data.get('class_id', '')),
            self.lesson_data.get('class_name', ''),
            self.lesson_data.get('subject_name', ''),
            self.lesson_data.get('subject_short', ''),
            self.lesson_data.get('teacher_name', ''),
            self.lesson_data.get('color', ''),
            str(self.lesson_data.get('teacher_id', '')),
            str(self.lesson_data.get('subject_id', '')),
            str(self.lesson_data.get('weekly_hours', '')),
            str(row),
            str(col)
        ]
        mime_data.setText("|".join(data_values))
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        main_window = self._get_main_window()
        if main_window is not None:
            main_window.current_drag_source_widget = self

        try:
            drag.exec(Qt.DropAction.MoveAction)
        finally:
            if main_window is not None and main_window.current_drag_source_widget is self:
                main_window.current_drag_source_widget = None


class LessonCardStack(QWidget):
    """Karta kolodkasi"""

    def __init__(self, lesson_data, count, parent=None):
        super().__init__(parent)
        self.lesson_data = lesson_data
        self.count = count

        self.setFixedSize(50, 40)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.card = DraggableLessonButton(lesson_data, count)
        layout.addWidget(self.card)

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.count <= 1:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = normalize_color(self.lesson_data['color'])

        visible_count = int(min(self.count - 1, 3))

        for i in range(visible_count, 0, -1):
            offset_x = i * 3
            offset_y = i * 3

            shadow_color = color.darker(110 + i * 10)

            painter.setPen(QColor("#2C3E50"))
            painter.setBrush(shadow_color)
            painter.drawRoundedRect(
                offset_x, offset_y,
                55, 45,
                4, 4
            )

        painter.end()

    def update_count(self, count):
        self.count = count
        self.card.count = count
        self.card.setStyleSheet(
            self.card._get_card_style(normalize_color(self.lesson_data['color']).name(), count)
        )

        if count > 1:
            text = f"{self.lesson_data['subject_short'] or self.lesson_data['subject_name'][:3]}\n×{count}"
            self.card.setText(text)
        else:
            text = self.lesson_data['subject_short'] or self.lesson_data['subject_name'][:3]
            self.card.setText(text)

        self.update()


class UnplacedDropWidget(QWidget):
    """Sizilmagan darslar uchun qabul qiluvchi hudud"""

    def __init__(self, parent_window, parent=None):
        super().__init__(parent)
        self.parent_window = parent_window
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasText():
            event.ignore()
            return

        parts = event.mimeData().text().split("|")
        if len(parts) < 12:
            event.ignore()
            return

        lesson_data = self.parent_window.timetable._parse_lesson_data(parts)

        # Kelajak soatini o'rnidan olishga ogohlantirish
        if lesson_data.get('subject_name', '').lower() == 'kelajak soati':
            reply = QMessageBox.question(
                None, "⚠️ Kelajak soati",
                "Kelajak soatini jadvaldan olib tashlamoqchimisiz?\n\n"
                "Bu dars avtomatik ravishda sinf rahbariga\n"
                "belgilangan kunda 1-darsga qo'yilgan.\n\n"
                "Davom etasizmi?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

        src_row = lesson_data.get('src_row')
        src_col = lesson_data.get('src_col')
        if src_row is None or src_col is None:
            event.ignore()
            return

        source_class_id = self.parent_window.classes[src_row][0] if 0 <= src_row < len(self.parent_window.classes) else None
        if source_class_id is None:
            event.ignore()
            return

        src_key = (source_class_id, src_col // self.parent_window.PERIODS_PER_DAY, src_col % self.parent_window.PERIODS_PER_DAY)
        if src_key not in self.parent_window.timetable_data:
            event.ignore()
            return

        self.parent_window.unplace_lesson(src_key)
        self.parent_window.clear_highlights()
        event.acceptProposedAction()


class TimetableGrid(QTableWidget):
    """Drop qabul qiladigan jadval"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setAcceptDrops(True)
        self.setDragEnabled(False)  # Maxsus DnD ishlatamiz, table DnD emas
        self.drag_start_position = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            # ⭐ Highlight rejimini boshlash
            text = event.mimeData().text()
            parts = text.split("|")
            
            if len(parts) >= 10:
                lesson_data = self._parse_lesson_data(parts)
                self.parent_window.highlight_all_cells(lesson_data)
            
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            super().mouseMoveEvent(event)
            return

        if self.drag_start_position is None:
            super().mouseMoveEvent(event)
            return

        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            super().mouseMoveEvent(event)
            return

        item = self.itemAt(self.drag_start_position)
        if item is None:
            super().mouseMoveEvent(event)
            return

        row = self.rowAt(self.drag_start_position.y())
        col = self.columnAt(self.drag_start_position.x())
        widget = self.cellWidget(row, col) if row >= 0 and col >= 0 else None

        lesson_data = None
        if widget is not None and hasattr(widget, 'lesson_data'):
            lesson_data = widget.lesson_data
        else:
            lesson_data = item.data(Qt.ItemDataRole.UserRole)

        if not lesson_data:
            super().mouseMoveEvent(event)
            return

        # Kelajak soatini sudrashga ogohlantirish
        if lesson_data.get('subject_name', '').lower() == 'kelajak soati':
            reply = QMessageBox.question(
                None, "⚠️ Kelajak soati",
                "Kelajak soatini sudrash tavsiya etilmaydi!\n\n"
                "Bu dars avtomatik ravishda sinf rahbariga\n"
                "belgilangan kunda 1-darsga qo'yilgan.\n\n"
                "Davom etasizmi?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        drag = QDrag(widget if isinstance(widget, ScheduledLessonCard) else self)
        mime_data = QMimeData()

        data_values = [
            str(lesson_data.get('lesson_id', '')),
            str(lesson_data.get('class_id', '')),
            lesson_data.get('class_name', ''),
            lesson_data.get('subject_name', ''),
            lesson_data.get('subject_short', ''),
            lesson_data['teacher_name'],
            lesson_data['color'],
            str(lesson_data['teacher_id']),
            str(lesson_data['subject_id']),
            str(lesson_data['weekly_hours']),
            str(row),
            str(col)
        ]
        mime_data.setText("|".join(data_values))
        drag.setMimeData(mime_data)

        if widget is not None:
            pixmap = QPixmap(widget.size())
            pixmap.fill(Qt.GlobalColor.transparent)
            widget.render(pixmap)
        else:
            pixmap = QPixmap(120, 40)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            brush = QBrush(item.background().color())
            painter.fillRect(pixmap.rect(), brush)
            painter.setPen(item.foreground().color())
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pixmap.rect().adjusted(4, 4, -4, -4), Qt.AlignmentFlag.AlignCenter, item.text())
            painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - self.drag_start_position)

        if isinstance(widget, ScheduledLessonCard):
            self.parent_window.current_drag_source_widget = widget
        try:
            drag.exec(Qt.DropAction.MoveAction)
        finally:
            if isinstance(widget, ScheduledLessonCard) and self.parent_window.current_drag_source_widget is widget:
                self.parent_window.current_drag_source_widget = None

    def dragLeaveEvent(self, event):
        # ⭐ Highlightlarni tozalash
        self.parent_window.clear_highlights()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        pos = event.position().toPoint()
        row = self.rowAt(pos.y())
        col = self.columnAt(pos.x())

        if row < 0 or col < 0:
            self.parent_window.clear_highlights()
            event.ignore()
            return

        text = event.mimeData().text()
        parts = text.split("|")

        if len(parts) >= 10:
            lesson_data = self._parse_lesson_data(parts)

            # Kelajak soatini tashlashga ogohlantirish
            if lesson_data.get('subject_name', '').lower() == 'kelajak soati':
                reply = QMessageBox.question(
                    None, "⚠️ Kelajak soati",
                    "Kelajak soatini o'rnidan sudrash tavsiya etilmaydi!\n\n"
                    "Bu dars avtomatik ravishda sinf rahbariga\n"
                    "belgilangan kunda 1-darsga qo'yilgan.\n\n"
                    "Davom etasizmi?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    self.parent_window.clear_highlights()
                    event.ignore()
                    return

            src_key = None
            src_widget = None
            if 'src_row' in lesson_data and 'src_col' in lesson_data:
                src_row = lesson_data.pop('src_row')
                src_col = lesson_data.pop('src_col')
                if 0 <= src_row < len(self.parent_window.classes):
                    src_class_id = self.parent_window.classes[src_row][0]
                    src_day = src_col // self.parent_window.PERIODS_PER_DAY
                    src_period = src_col % self.parent_window.PERIODS_PER_DAY
                    src_key = (src_class_id, src_day, src_period)

            target_day = col // self.parent_window.PERIODS_PER_DAY
            target_period = col % self.parent_window.PERIODS_PER_DAY
            if src_key == (self.parent_window.classes[row][0], target_day, target_period):
                # O'ziga qaytish - hech qanday o'zgarish qilinmaydi
                self.parent_window.clear_highlights()
                event.acceptProposedAction()
                return

            if hasattr(event, 'source'):
                source_widget = event.source()
                if isinstance(source_widget, ScheduledLessonCard):
                    src_widget = source_widget

            if src_widget is None:
                src_widget = self.parent_window.current_drag_source_widget

            if src_widget is None and src_key is not None:
                source_row = next(
                    (idx for idx, cls in enumerate(self.parent_window.classes) if cls[0] == src_key[0]),
                    None
                )
                if source_row is not None:
                    source_col = src_key[1] * self.parent_window.PERIODS_PER_DAY + src_key[2]
                    candidate = self.cellWidget(source_row, source_col)
                    if isinstance(candidate, ScheduledLessonCard):
                        src_widget = candidate

            # Agar src_widget hali None bo'lsa — xavfsiz qilib qo'yamiz
            if src_widget is None:
                self.parent_window.place_lesson(row, col, lesson_data, src_key, src_widget=None)
            else:
                self.parent_window.place_lesson(row, col, lesson_data, src_key, src_widget=src_widget)

        event.acceptProposedAction()
    
    def _parse_lesson_data(self, parts):
        """Mime data ni parse qilish"""
        lesson_data = {
            'lesson_id': int(parts[0]),
            'class_id': int(parts[1]),
            'class_name': parts[2],
            'subject_name': parts[3],
            'subject_short': parts[4],
            'teacher_name': parts[5],
            'color': parts[6],
            'teacher_id': int(parts[7]) if parts[7] else 0,
            'subject_id': int(parts[8]) if parts[8] else 0,
            'weekly_hours': float(parts[9]) if parts[9] else 0
        }
        if len(parts) >= 12:
            lesson_data['src_row'] = int(parts[10])
            lesson_data['src_col'] = int(parts[11])
        return lesson_data


class ManualScheduleWindow(QWidget):
    
    # Konstantalar
    PERIODS_PER_DAY = 6      # Kuniga 6 dars (7-dars yo'q)
    DAYS_PER_WEEK = 6        # Haftada 6 kun
    MIN_COL_WIDTH = 22       # Minimal ustun kengligi (A4 ga sig'ish uchun)
    MAX_COL_WIDTH = 50       # Maksimal ustun kengligi
    MIN_ROW_HEIGHT = 35      # Minimal qator balandligi
    MAX_ROW_HEIGHT = 120     # Maksimal qator balandligi
    VERTICAL_HEADER_WIDTH = 35  # Sinf nomlari ustuni
    DAYS_HEADER_HEIGHT = 35  # Kunlar header balandligi
    
    KUN_RANGLARI = [
        "#3498DB",  # Dushanba
        "#9B59B6",  # Seshanba
        "#E74C3C",  # Chorshanba
        "#F39C12",  # Payshanba
        "#1ABC9C",  # Juma
        "#7F8C8D",  # Shanba
    ]
    
    KUNLAR = ["Dushanba", "Seshanba", "Chorshanba",
              "Payshanba", "Juma", "Shanba"]


    # KONFLIKT RANGLARI
    COLOR_FREE = QColor(46, 204, 113, 120)      # Yashil - bo'sh
    COLOR_BLOCKED = QColor(231, 76, 60, 180)    # Qizil - qat'iy band
    COLOR_SANPIN = QColor(52, 152, 219, 180)    # Ko'k - SanPIN ogohlantirish
    COLOR_SOFT = QColor(241, 196, 15, 180)      # Sariq - yumshoq band
    COLOR_SWAP = QColor(144, 238, 144, 180)      # Och yashil - almashtirish

    def check_prerequisites(self):
        """Oyna ochilishidan oldin oldingi qadamlarni tekshirish"""
        classes = self.db.get_all_classes()
        if not classes:
            QMessageBox.warning(self, "Xatolik",
                "Sinflar yo'q!\n\nAvval sinflarni qo'shing.")
            return False

        teachers = self.db.get_all_teachers()
        if not teachers:
            QMessageBox.warning(self, "Xatolik",
                "O'qituvchilar yo'q!\n\nAvval o'qituvchilarni qo'shing.")
            return False

        subjects = self.db.get_all_subjects()
        if not subjects:
            QMessageBox.warning(self, "Xatolik",
                "Fanlar yo'q!\n\nAvval fanlarni qo'shing.")
            return False

        # Dars biriktirish tekshirish
        has_assignments = False
        for cls in classes:
            assignments = self.db.get_class_assignments(cls[0])
            if assignments:
                has_assignments = True
                break

        if not has_assignments:
            QMessageBox.warning(self, "Xatolik",
                "Hech qanday dars biriktirilmagan!\n\n"
                "Avval '📝 Dars biriktirish' oynasidan\n"
                "har bir sinfga darslarni biriktiring.")
            return False

        return True


    def __init__(self, db_manager, empty=False):
        super().__init__()
        self.db = db_manager
        self.empty_mode = empty

        # Oldingi qadam tekshiruvi
        if not self.check_prerequisites():
            return

        self.classes = []
        self.timetable_data = {}
        
        self.placed_counts = {}
        self.filter_type = "subject"
        self.current_col_width = 30
        self.current_row_height = 40
        self.current_drag_lesson = None
        self.current_drag_source_widget = None
        self.highlight_active = False
        self.original_colors = {}
        self.selected_unplaced_lesson = None
        self.selected_unplaced_button = None
        self.teacher_unavailable_cache = {}
        
        self._drag_indexes = None
        self._sanpin_checker = None

        self.setWindowTitle("📅 Dars jadvali")
        self.resize(1200, 800)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(3)
        self.setLayout(main_layout)

        # Tugmalar paneli
        top_panel = QWidget()
        top_panel.setStyleSheet("background-color: #2C3E50; border-radius: 5px;")
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 5, 10, 5)
        top_panel.setLayout(top_layout)

        header = QLabel("📅 DARS JADVALI")
        header.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        top_layout.addWidget(header)

        top_layout.addStretch()

        btn_auto = QPushButton("⚡ Avtomatik jadval")
        btn_auto.setStyleSheet("background: #8E44AD; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        btn_auto.clicked.connect(self._on_auto)
        top_layout.addWidget(btn_auto)

        btn_save = QPushButton("💾 Saqlash")
        btn_save.setStyleSheet("background: #27AE60; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        btn_save.clicked.connect(self._on_save)
        top_layout.addWidget(btn_save)

        btn_open = QPushButton("📂 Ochish")
        btn_open.setStyleSheet("background: #3498DB; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        btn_open.clicked.connect(self._on_open)
        top_layout.addWidget(btn_open)

        btn_clear = QPushButton("🗑️ Tozalash")
        btn_clear.setStyleSheet("background: #E74C3C; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        btn_clear.clicked.connect(self._on_clear)
        top_layout.addWidget(btn_clear)

        main_layout.addWidget(top_panel)

        # Sinf tanlash paneli — katta hajm uchun qidiruv va filter
        class_selector_panel = QWidget()
        class_selector_panel.setStyleSheet("background: #ECF0F1; border-radius: 3px; padding: 2px;")
        cs_layout = QHBoxLayout()
        cs_layout.setContentsMargins(10, 2, 10, 2)
        class_selector_panel.setLayout(cs_layout)

        cs_label = QLabel("🏫 Sinf:")
        cs_label.setStyleSheet("color: #2C3E50; font-size: 11px; font-weight: bold;")
        cs_layout.addWidget(cs_label)

        self.class_search = QComboBox()
        self.class_search.setStyleSheet("padding: 3px; font-size: 11px; min-width: 150px; background: white; color: #2C3E50;")
        self.class_search.currentIndexChanged.connect(self._on_class_selected)
        cs_layout.addWidget(self.class_search)

        # Daraja filteri
        level_label = QLabel("📊 Daraja:")
        level_label.setStyleSheet("color: #2C3E50; font-size: 11px; font-weight: bold; padding-left: 10px;")
        cs_layout.addWidget(level_label)

        self.level_filter = QComboBox()
        self.level_filter.addItems(["Barchasi", "1-4 sinflar", "5-9 sinflar", "10-11 sinflar"])
        self.level_filter.setStyleSheet("padding: 3px; font-size: 11px; min-width: 100px; background: white; color: #2C3E50;")
        self.level_filter.currentIndexChanged.connect(self._on_level_filter_changed)
        cs_layout.addWidget(self.level_filter)

        # Sinf soni
        self.class_count_label = QLabel("")
        self.class_count_label.setStyleSheet("color: #7F8C8D; font-size: 10px; padding-left: 10px;")
        cs_layout.addWidget(self.class_count_label)

        cs_layout.addStretch()

        main_layout.addWidget(class_selector_panel)

                # Jadval — TimetableGrid (drag-drop qo'llab-quvvatlash bilan)
        self.timetable = TimetableGrid(self)
        self.timetable.setColumnCount(42)
        self.timetable.setRowCount(16)

        # Header ranglarini o'rnatish
        self.setup_timetable()

        self.timetable.setStyleSheet("""
            QTableWidget { background: white; gridline-color: #E8E8E8; border: 1px solid #BDC3C7; }
            QTableWidget::item { padding: 2px; }
            QTableWidget::item:selected { background-color: transparent; }
        """)

        main_layout.addWidget(self.timetable, 3)

        # Joylashtirilmagan darslar paneli
        bottom_panel = QWidget()
        bottom_panel.setStyleSheet("background: #ECF0F1; border-radius: 5px;")
        bottom_main_layout = QVBoxLayout()
        bottom_main_layout.setContentsMargins(5, 5, 5, 5)
        bottom_panel.setLayout(bottom_main_layout)

        # Sarlavha qatori — bitta satrda
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        bottom_title = QLabel("📦 JOYLASHTIRILMAGAN DARSLAR")
        bottom_title.setStyleSheet("background: #2C3E50; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;")
        title_row.addWidget(bottom_title)

        self.unplaced_stats = QLabel("Jami: 0 ta dars qoldi")
        self.unplaced_stats.setStyleSheet("background: #E74C3C; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        title_row.addWidget(self.unplaced_stats)

        # Guruhlash combo — joylashtirilmaganlar paneliga
        filter_label = QLabel("Guruhlash:")
        filter_label.setStyleSheet("color: #2C3E50; font-size: 11px; font-weight: bold; padding-left: 10px;")
        title_row.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["📚 Fan bo'yicha", "👨‍🏫 O'qituvchi bo'yicha", "🏫 Sinf bo'yicha"])
        self.filter_combo.setStyleSheet("padding: 4px; font-size: 11px; min-width: 120px; background: white; color: #2C3E50;")
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        title_row.addWidget(self.filter_combo)

        title_row.addStretch()
        bottom_main_layout.addLayout(title_row)

        self.unplaced_scroll = QScrollArea()
        self.unplaced_scroll.setWidgetResizable(True)
        self.unplaced_container = UnplacedDropWidget(self)
        self.unplaced_container.setStyleSheet("background-color: white;")
        self.unplaced_layout = FlowGridLayout()
        self.unplaced_container.setLayout(self.unplaced_layout)
        self.unplaced_scroll.setWidget(self.unplaced_container)
        bottom_main_layout.addWidget(self.unplaced_scroll)

        main_layout.addWidget(bottom_panel, 1)

        # Status
        self.status_label = QLabel("✅ Tayyor")
        self.status_label.setStyleSheet("background: white; color: #27AE60; padding: 5px; font-size: 11px; border-radius: 3px;")
        main_layout.addWidget(self.status_label)

        self._load_data_sync()

        # Kontekst menyusini ulash (o'ng tugma)
        self.timetable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.timetable.customContextMenuRequested.connect(self.show_context_menu)

    def setup_timetable(self):
        """Jadval ustunlarini kunlar va soatlar bilan to'ldirish"""
        total_cols = self.DAYS_PER_WEEK * self.PERIODS_PER_DAY
        self.timetable.setColumnCount(total_cols)

        kunlar_qisqa = ["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan"]
        headers = []
        for kun in kunlar_qisqa:
            for p in range(1, self.PERIODS_PER_DAY + 1):
                headers.append(f"{kun}{p}")
        self.timetable.setHorizontalHeaderLabels(headers)

        for kun_idx in range(self.DAYS_PER_WEEK):
            for p in range(self.PERIODS_PER_DAY):
                col = kun_idx * self.PERIODS_PER_DAY + p
                rang = self.KUN_RANGLARI[kun_idx]

                header_item = QTableWidgetItem(f"{kunlar_qisqa[kun_idx]}{p+1}")
                header_item.setBackground(QColor(rang))
                header_item.setForeground(QColor("white"))
                header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                font = header_item.font()
                font.setBold(True)
                font.setPointSize(10)
                header_item.setFont(font)

                header_item.setToolTip(f"{self.KUNLAR[kun_idx]} - {p+1}-dars")
                self.timetable.setHorizontalHeaderItem(col, header_item)

        self.timetable.horizontalHeader().setFixedHeight(30)
        self.timetable.verticalHeader().setDefaultSectionSize(self.MIN_ROW_HEIGHT)
        self.timetable.verticalHeader().setFixedWidth(self.VERTICAL_HEADER_WIDTH)
        self.timetable.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Fixed
        )
        self.timetable.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.timetable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.timetable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.timetable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Kontekst menusi allaqachon ulangan (line 1592-1593)

    def _save_current_week_data(self):
        """Joriy haftaning ma'lumotlarini saqlash"""
        self.timetable_data = self._get_grid_data()

    def _get_grid_data(self):
        """Joriy haftaning timetable_data dan olish"""
        return dict(self.timetable_data)

    def _get_grid_data_from_grid(self):
        """Jadval widgetidan to'g'ridan-to'g'ri ma'lumot olish"""
        data = {}
        for row in range(self.timetable.rowCount()):
            for col in range(self.timetable.columnCount()):
                item = self.timetable.item(row, col)
                widget = self.timetable.cellWidget(row, col)
                if widget and hasattr(widget, 'lesson_data'):
                    lesson_data = widget.lesson_data
                    class_id = lesson_data.get('class_id')
                    day = col // self.PERIODS_PER_DAY
                    period = col % self.PERIODS_PER_DAY
                    if class_id:
                        data[(class_id, day, period)] = lesson_data
        return data
        """Oldingi qadamlar mavjudligini tekshirish"""
        missing = []
        buttons = []

        classes = self.db.get_all_classes()
        assignments = []
        for cls in classes:
            cls_assignments = self.db.get_class_assignments(cls[0])
            if cls_assignments:
                assignments.extend(cls_assignments)

        if not classes:
            missing.append("🏫 Sinflar")
            buttons.append(("Sinflar qo'shish", "classes"))
        if not assignments:
            missing.append("📝 Dars biriktirishlar")
            buttons.append(("Dars biriktirish", "assignments"))

        if not missing:
            return True

        # Ogohlantirish oynasi
        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️ Ma'lumot yetarli emas")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("Dars jadvalini tuzish uchun quyidagi ma'lumotlar kerak:")
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
        elif entity == "assignments":
            from ui.assignment_window import AssignmentWindow
            win = AssignmentWindow(self.db)
            win.exec()

    def _load_data_sync(self):
        """Ma'lumotlarni yuklash — sinflar + saqlangan jadval"""
        try:
            self.classes = self.db.get_all_classes()
            self._class_row_map = {cls[0]: i for i, cls in enumerate(self.classes)}
            self.timetable.setRowCount(len(self.classes))

            for i, cls in enumerate(self.classes):
                self.timetable.setVerticalHeaderItem(i, QTableWidgetItem(cls[1]))

            # Class selector ni to'ldirish
            self._populate_class_selector()

            # Bo'sh rejimda: tekshiruv + Kelajak qo'yish + unplaced yuklash
            if self.empty_mode:
                self._init_manual_mode()
                return

            # Bazadan saqlangan jadvalni yuklash — 1-hafta va 2-hafta
            saved_w1 = self.db.load_scheduled_lessons()

            if saved_w1:
                self.timetable_data = saved_w1
                
                # Widgetlarni qayta yaratish
                for (class_id, day, period), info in saved_w1.items():
                    row = None
                    for i, cls in enumerate(self.classes):
                        if cls[0] == class_id:
                            row = i
                            break
                    if row is None:
                        continue
                    col = day * self.PERIODS_PER_DAY + period
                    if col >= self.timetable.columnCount():
                        continue

                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setData(Qt.ItemDataRole.UserRole, info)
                    item.setBackground(QColor("transparent"))
                    self.timetable.setItem(row, col, item)

                    card = ScheduledLessonCard(info)
                    self.timetable.setCellWidget(row, col, card)

                    # Placed counts
                    lesson_id = info.get('lesson_id')
                    if lesson_id:
                        placed_key = (class_id, lesson_id)
                        self.placed_counts[placed_key] = self.placed_counts.get(placed_key, 0) + 1

                self.status_label.setText(
                    f"✅ Yuklandi: {len(self.classes)} sinf | {len(saved_w1)} dars"
                )
            else:
                self.status_label.setText(f"✅ Yuklandi: {len(self.classes)} ta sinf")
        except Exception as e:
            self.status_label.setText(f"❌ Xatolik: {str(e)}")

    def _init_manual_mode(self):
        """Qo'lda jadval rejimi — tekshiruv + Kelajak qo'yish + unplaced yuklash"""
        self.classes = self.db.get_all_classes()
        self._class_row_map = {cls[0]: i for i, cls in enumerate(self.classes)}
        self.timetable.setRowCount(len(self.classes))

        for i, cls in enumerate(self.classes):
            self.timetable.setVerticalHeaderItem(i, QTableWidgetItem(cls[1]))

        # O'qituvchi bandlik cache ni yuklash (ranglarsiz tekshiruv uchun kerak)
        self.load_teacher_unavailable_cache()

        # 1. O'qituvchi yuklanishini tekshirish
        overflow_teachers = self._check_teacher_workload()
        if overflow_teachers:
            msg_lines = ["Quyidagi o'qituvchilarning dars yuklasi limitdan oshib ketdi:\n"]
            for t_name, total, limit, overflow in overflow_teachers:
                msg_lines.append(f"• {t_name}: {total} soat (limit: {limit}) — +{overflow} soat ortiqcha")
            msg_lines.append(f"\nDavom etilsinmi?")
            reply = QMessageBox.question(
                self, "O'qituvchi yuklanishi ortiqcha",
                "\n".join(msg_lines),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.status_label.setText("❌ Bekor qilindi")
                return

        # 2. Kelajak soatini sinf rahbarlariga avtomatik qo'yish
        kelajak_day_str = self.db.get_setting("kelajak_day", "4")
        try:
            kelajak_day = int(kelajak_day_str)
        except (ValueError, TypeError):
            kelajak_day = 4
        if kelajak_day < 0 or kelajak_day > 5:
            kelajak_day = 4

        kunlar = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]
        kelajak_placed_count = 0

        all_teachers = self.db.get_all_teachers()
        for t in all_teachers:
            t_id = t[0]
            t_name = t[1]
            class_teacher_of = t[4]
            if not class_teacher_of:
                continue
            # Sinf rahbarining darslarini tekshirish
            assignments = self.db.get_class_assignments(class_teacher_of)
            for a in assignments:
                subj_name = a[1]
                if subj_name and 'kelajak' in subj_name.lower():
                    # Kelajak soatini jadvalga qo'yish
                    lesson_info = {
                        'lesson_id': a[0],
                        'subject_name': a[1],
                        'teacher_name': a[2],
                        'color': a[3],
                        'weekly_hours': a[4],
                        'subject_id': a[5],
                        'teacher_id': a[6],
                        'teacher_short': a[7] if len(a) > 7 else '',
                        'class_id': class_teacher_of,
                        'class_name': next((c[1] for c in self.classes if c[0] == class_teacher_of), ''),
                    }
                    key = (class_teacher_of, kelajak_day, 0)
                    self.timetable_data[key] = lesson_info
                    # placed_counts ni yangilash
                    placed_key = (class_teacher_of, a[0])
                    self.placed_counts[placed_key] = self.placed_counts.get(placed_key, 0) + 1
                    kelajak_placed_count += 1
                    break

        # 3. Jadvalga Kelajak kartochkalarini chizish
        for (cid, day, period), info in self.timetable_data.items():
            row = self._class_row_map.get(cid)
            if row is None:
                continue
            col = day * self.PERIODS_PER_DAY + period
            if col >= self.timetable.columnCount():
                continue
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setData(Qt.ItemDataRole.UserRole, info)
            item.setBackground(QColor("transparent"))
            self.timetable.setItem(row, col, item)
            card = ScheduledLessonCard(info)
            self.timetable.setCellWidget(row, col, card)

        # 4. Qolgan darslarni unplaced paneliga yuklash
        self.load_unplaced_lessons()

        day_name = kunlar[kelajak_day] if kelajak_day < len(kunlar) else "?"
        self.status_label.setText(
            f"✅ Bo'sh rejim: {len(self.classes)} sinf | "
            f"Kelajak soati: {kelajak_placed_count} ta ({day_name} 1-dars)"
        )

    def _auto_save(self):
        """Jadval o'zgarganda avtomatik saqlash"""
        try:
            self.db.save_scheduled_lessons(self.timetable_data)
        except Exception as e:
            print(f"Avtomatik saqlash xatolik: {e}")

    def _on_auto(self):
        """Avtomatik jadval tuzish — soatlarni tekshirish"""
        # Avval soatlarni tekshirish
        if not self._check_hours_match():
            return

        # Vakantlarni tekshirish — o'qituvchi yetishmayotgan fanlar
        if not self._check_vacants():
            return

        self.auto_generate_all()

    def _check_vacants(self):
        """Vakant darslarni aniqlash — o'qituvchi yetishmayotgan fanlar.
        Dialog ko'rsatadi, foydalanuvchi davom etish/bekor qilish tanlaydi.
        True = davom etish mumkin.
        """
        tayanch = self.db.load_tayanch_reja()
        if not tayanch:
            return True

        # Tayanch bo'yicha fan soatlari
        tayanch_by_level = {}
        for item in tayanch:
            lv = item['class_level']
            subj = item['subject_name']
            hours = item['weekly_hours']
            if lv not in tayanch_by_level:
                tayanch_by_level[lv] = {}
            tayanch_by_level[lv][subj] = tayanch_by_level[lv].get(subj, 0) + hours

        # Vakantlarni topish
        vakants = []
        for cls in self.classes:
            class_id = cls[0]
            class_name = cls[1]
            level = cls[2]

            assignments = self.db.get_class_assignments(class_id)
            assigned_subjects = set()
            for a in assignments:
                assigned_subjects.add(a[1])

            tayanch_subs = tayanch_by_level.get(level, {})
            for subj, hours in tayanch_subs.items():
                if subj not in assigned_subjects:
                    vakants.append((class_name, subj, hours))

        if not vakants:
            return True  # Vakant yo'q — davom etish mumkin

        # Vakant dialogi — oddiy matn shaklida
        lines = []
        for cn, subj, hours in vakants:
            lines.append(f"  • {cn}: {subj} — {hours} soat")

        dialog = QMessageBox(self)
        dialog.setWindowTitle("⚠️ Vakant darslar mavjud!")
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setText(f"Jami {len(vakants)} ta vakant dars bor (o'qituvchi yetishmayapti).")
        dialog.setInformativeText(
            "Vakant darslar jadvalda bo'sh qoldiriladi.\n\n" + "\n".join(lines)
        )

        yes_btn = dialog.addButton("Ha, davom etish", QMessageBox.ButtonRole.AcceptRole)
        dialog.addButton("Bekor qilish", QMessageBox.ButtonRole.RejectRole)
        dialog.exec()

        return dialog.clickedButton() == yes_btn

    def _check_hours_match(self):
        """Tayanch reja bilan soatlarni solishtirish. True = davom etish mumkin."""
        tayanch = self.db.load_tayanch_reja()
        if not tayanch:
            return True  # Tayanch reja yo'q — tekshirmaslik

        # Tayanch reja bo'yicha fan soatlari (daraja → fan → soat)
        tayanch_by_level = {}
        for item in tayanch:
            lv = item['class_level']
            subj = item['subject_name']
            hours = item['weekly_hours']
            if lv not in tayanch_by_level:
                tayanch_by_level[lv] = {}
            tayanch_by_level[lv][subj] = tayanch_by_level[lv].get(subj, 0) + hours

        mismatches = []
        for cls in self.classes:
            class_id = cls[0]
            class_name = cls[1]
            level = cls[2]

            # Bazadagi biriktirilgan fan soatlari
            assignments = self.db.get_class_assignments(class_id)
            assigned_by_subject = {}
            for a in assignments:
                subj = a[1]
                hours = a[4]
                assigned_by_subject[subj] = assigned_by_subject.get(subj, 0) + hours

            assigned = sum(assigned_by_subject.values())

            # Tayanch rejadagi kutilgan soatlar
            tayanch_subs = tayanch_by_level.get(level, {})
            expected = sum(tayanch_subs.values())

            if expected == 0 and assigned == 0:
                continue  # Ikkalasi ham 0 — muammo yo'q

            diff = assigned - expected
            if diff != 0:
                # Fanlar bo'yicha farqlarni topish
                subject_diffs = []
                all_subjects = set(list(tayanch_subs.keys()) + list(assigned_by_subject.keys()))
                for subj in sorted(all_subjects):
                    t_hours = tayanch_subs.get(subj, 0)
                    a_hours = assigned_by_subject.get(subj, 0)
                    if t_hours != a_hours:
                        s_diff = a_hours - t_hours
                        sign = "+" if s_diff > 0 else ""
                        subject_diffs.append(f"{subj} ({sign}{s_diff})")

                mismatches.append({
                    'class_name': class_name,
                    'level': level,
                    'expected': expected,
                    'assigned': assigned,
                    'diff': diff,
                    'subject_diffs': subject_diffs,
                })

        if not mismatches:
            return True  # Hamma mos

        # Ogohlantirish dialogi
        dialog = QMessageBox(self)
        dialog.setWindowTitle("⚠️ Soatlar mos kelmaydi!")
        dialog.setIcon(QMessageBox.Icon.Warning)

        # Jadval shaklida ko'rsatish — 5 ustunli
        table_html = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>"
        table_html += "<tr style='background:#2C3E50; color:white;'>"
        table_html += "<td>Sinf</td><td>Tayanch</td><td>Biriktirilgan</td><td>Farq</td><td>Mos kelmaydigan fanlar</td></tr>"

        for m in mismatches:
            color = "#E74C3C" if m['diff'] > 0 else "#F39C12"
            sign = "+" if m['diff'] > 0 else ""
            table_html += f"<tr>"
            table_html += f"<td><b>{m['class_name']}</b></td>"
            table_html += f"<td>{m['expected']}</td>"
            table_html += f"<td>{m['assigned']}</td>"
            table_html += f"<td style='color:{color}; font-weight:bold;'>{sign}{m['diff']}</td>"
            table_html += f"<td style='font-size:11px;'>{', '.join(m['subject_diffs'])}</td>"
            table_html += f"</tr>"
        table_html += "</table>"

        dialog.setText("Quyidagi sinflarda soatlar mos kelmaydi:")
        dialog.setInformativeText(table_html)

        yes_btn = dialog.addButton("Ha, davom etish", QMessageBox.ButtonRole.AcceptRole)
        dialog.addButton("Bekor qilish", QMessageBox.ButtonRole.RejectRole)
        dialog.exec()

        return dialog.clickedButton() == yes_btn

    def _check_teacher_workload(self):
        """Har bir o'qituvchining dars yuklanishini tekshirish.
        Limit: max_teacher_hours soat (sozlamadan, default 30).
        Sinf rahbarlari uchun +1 qo'shiladi.
        Qaytaradi: overflow_teacherlar ro'yxati yoki bo'sh list.
        """
        # Sozlamadan limitni olish
        try:
            base_limit = int(self.db.get_setting("max_teacher_hours", "30"))
        except (ValueError, TypeError):
            base_limit = 30

        overflow_teachers = []
        all_teachers = self.db.get_all_teachers()
        for t in all_teachers:
            t_id = t[0]
            t_name = t[1]
            class_teacher_of = t[4]  # sinf rahbari bo'lsa, sinf ID; bo'lmasa None
            assignments = self.db.get_teacher_assignments(t_id)
            if not assignments:
                continue
            total_hours = sum(a[3] for a in assignments if a[3])
            # Sinf rahbari bo'lsa +1
            limit = base_limit + 1 if class_teacher_of else base_limit
            if total_hours > limit:
                overflow_teachers.append((t_name, total_hours, limit, total_hours - limit))
        return overflow_teachers

    def _on_save(self):
        """Saqlash — Baza yoki JSON tanlash"""
        if not self.timetable_data:
            QMessageBox.warning(self, "Xatolik", "Jadval bo'sh!")
            return

        # Tanlash dialogi
        msg = QMessageBox(self)
        msg.setWindowTitle("💾 Qayerga saqlash?")
        msg.setText("Qayerga saqlashni xohlaysiz?")
        msg.setInformativeText("Baza — dastur ichidagi xotira\nJSON — faylga qo'lda saqlash")
        msg.setIcon(QMessageBox.Icon.Question)

        db_btn = msg.addButton("💾 Bazaga", QMessageBox.ButtonRole.AcceptRole)
        json_btn = msg.addButton("📄 JSON ga", QMessageBox.ButtonRole.ActionRole)
        both_btn = msg.addButton("💾📄 Ikkalasiga", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)

        msg.exec()
        clicked = msg.clickedButton()

        if clicked == db_btn:
            self._save_to_database()
        elif clicked == json_btn:
            self._save_to_json()
        elif clicked == both_btn:
            self._save_to_database()
            self._save_to_json()

    def _save_to_database(self):
        """Bazaga saqlash"""
        try:
            # Joriy haftaning ma'lumotlarini saqlash
            self._save_current_week_data()

            # 1-haftani saqlash
            self.db.save_scheduled_lessons(self.timetable_data)
            

            total = len(self.timetable_data)
            self.status_label.setText(
                f"💾 Bazaga saqlandi: {total} ta dars (2 hafta)"
            )
            QMessageBox.information(
                self, "Saqlandi",
                f"✅ Jadval bazaga muvaffaqiyatli saqlandi!\n\n"
                f"📊 1-hafta: {len(self.timetable_data)} ta dars\n"
                f"📊 {total} ta dars saqlandi"
            )
        except Exception as e:
            QMessageBox.warning(self, "Xatolik", f"Bazaga saqlash xatolik:\n{str(e)}")

    def _save_to_json(self):
        """JSON faylga saqlash"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Jadvalni JSON ga saqlash",
            f"jadval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON fayllar (*.json)"
        )
        if not filename:
            return

        try:
            import json
            save_data = {
                'version': '1.0',
                'saved_at': datetime.now().isoformat(),
                'classes': [
                    {'id': cls[0], 'name': cls[1], 'level': cls[2],
                     'students_count': cls[3] if len(cls) > 3 else 0,
                     'working_days': cls[4] if len(cls) > 4 else 6}
                    for cls in self.classes
                ],
                'timetable': {
                    f"{k[0]}_{k[1]}_{k[2]}": v
                    for k, v in self.timetable_data.items()
                },
                'placed_counts': {
                    f"{k[0]}_{k[1]}": v
                    for k, v in self.placed_counts.items()
                }
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            self.status_label.setText(
                f"📄 JSON ga saqlandi: {len(self.timetable_data)} ta dars"
            )
            QMessageBox.information(
                self, "Saqlandi",
                f"✅ Jadval JSON faylga muvaffaqiyatli saqlandi!\n\n"
                f"📁 {filename}\n"
                f"📊 {len(self.timetable_data)} ta dars"
            )
        except Exception as e:
            QMessageBox.warning(self, "Xatolik", f"JSON saqlash xatolik:\n{str(e)}")

    def _on_open(self):
        """Ochish — Baza yoki JSON tanlash"""
        if not self.classes:
            QMessageBox.warning(self, "Xatolik", "Sinflar yo'q!")
            return

        # Tanlash dialogi
        msg = QMessageBox(self)
        msg.setWindowTitle("📂 Jadvalni ochish")
        msg.setText("Qayerdan yuklab olishni xohlaysiz?")
        msg.setInformativeText("Baza — oxirgi avtomatik saqlangan jadval\nJSON — fayldan qo'lda yuklash")
        msg.setIcon(QMessageBox.Icon.Question)

        db_btn = msg.addButton("💾 Bazadan", QMessageBox.ButtonRole.AcceptRole)
        json_btn = msg.addButton("📄 JSON dan", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)

        msg.exec()
        clicked = msg.clickedButton()

        if clicked == db_btn:
            self._load_from_database()
        elif clicked == json_btn:
            self.load_all()

    def _load_from_database(self):
        """Bazadan jadvalni yuklash"""
        # Har bir haftani alohida yuklash (kalitlar ustma-ust ketmasligi uchun)
        saved_w1 = self.db.load_scheduled_lessons()
        
        if not saved_w1:
            QMessageBox.information(self, "Ma'lumot", "Bazada saqlangan jadval yo'q!")
            return

        # Jadvalni tozalash
        self.timetable.clearContents()
        for row in range(self.timetable.rowCount()):
            for col in range(self.timetable.columnCount()):
                widget = self.timetable.cellWidget(row, col)
                if widget is not None:
                    self.timetable.removeCellWidget(row, col)
                    widget.deleteLater()
        self.timetable_data = {}
        self.placed_counts = {}

        # 1-haftani yuklash
        for (class_id, day, period), info in saved_w1.items():
            row = None
            class_name = None
            for i, cls in enumerate(self.classes):
                if cls[0] == class_id:
                    row = i
                    class_name = cls[1]
                    break
            if row is None:
                continue
            col = day * self.PERIODS_PER_DAY + period
            if col >= self.timetable.columnCount():
                continue
            info['class_name'] = class_name
            self.timetable_data[(class_id, day, period)] = info
            lesson_id = info.get('lesson_id')
            if lesson_id:
                placed_key = (class_id, lesson_id)
                self.placed_counts[placed_key] = self.placed_counts.get(placed_key, 0) + 1
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setData(Qt.ItemDataRole.UserRole, info)
            item.setBackground(QColor("transparent"))
            self.timetable.setItem(row, col, item)
            card = ScheduledLessonCard(info)
            self.timetable.setCellWidget(row, col, card)



        self.recalculate_table_sizes()
        self.load_unplaced_lessons()

        self.status_label.setText(
            f"💾 Bazadan yuklandi: {len(saved_w1)} ta dars"
        )

    def _on_clear(self):
        """Jadvalni tozalash"""
        if not self.timetable_data:
            return

        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "Barcha darslarni jadvaldan o'chirishni xohlaysizmi?\n\n"
            "Darslar 'Joylashtirilmagan darslar' paneliga qaytadi.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Jadvaldagi barcha widgetlarni o'chirish
        for row in range(self.timetable.rowCount()):
            for col in range(self.timetable.columnCount()):
                widget = self.timetable.cellWidget(row, col)
                if widget is not None:
                    self.timetable.removeCellWidget(row, col)
                    widget.deleteLater()

        # Ma'lumotlarni tozalash
        self.timetable_data = {}
        self.placed_counts = {}

        # Joylashtirilmaganlarni qayta yuklash
        self.load_unplaced_lessons()

        self.status_label.setText("🗑️ Jadval tozalandi — barcha darslar joylashtirilmagan")

    def resizeEvent(self, event):
        """Oyna o'lchami o'zgarganda"""
        super().resizeEvent(event)
        if hasattr(self, 'timetable'):
            QTimer.singleShot(50, self.recalculate_table_sizes)
    
    def recalculate_table_sizes(self):
        """Gorizontal va vertikal o'lchamlarni qayta hisoblash"""
        self.recalculate_column_widths()
        self.recalculate_row_heights()
    
    def recalculate_row_heights(self):
        """SMART AUTO-SIZING: Ekranga moslashtirib qator balandligini hisoblash"""
        if not hasattr(self, 'timetable'):
            return
        
        row_count = self.timetable.rowCount()
        if row_count <= 0:
            return
        
        viewport_height = self.timetable.viewport().height()
        if viewport_height <= 0:
            return
        
        min_total = row_count * self.MIN_ROW_HEIGHT
        
        if min_total <= viewport_height:
            # Barcha sinflar sig'adi — bo'sh joyni teng taqsimlash
            row_height = viewport_height // row_count
            row_height = min(row_height, self.MAX_ROW_HEIGHT)
        else:
            # Ko'p sinf — minimal balandlik, scroll ko'rinadi
            row_height = self.MIN_ROW_HEIGHT
        
        self.current_row_height = row_height
        self.timetable.verticalHeader().setDefaultSectionSize(row_height)
        
        for i in range(row_count):
            self.timetable.setRowHeight(i, row_height)
    
    def recalculate_column_widths(self):
        """SMART AUTO-SIZING: Ekranga moslashtirib ustun kengligini hisoblash"""
        if not hasattr(self, 'timetable'):
            return

        table_width = self.timetable.viewport().width()

        if table_width <= 0:
            return

        total_cols = self.DAYS_PER_WEEK * self.PERIODS_PER_DAY

        col_width = table_width // total_cols
        col_width = max(self.MIN_COL_WIDTH, col_width)

        self.current_col_width = col_width

        # Qoldiq piksellarni oxirgi ustunlarga taqsimlash
        used_width = col_width * total_cols
        remainder = table_width - used_width

        for i in range(total_cols):
            w = col_width + (1 if i < remainder else 0)
            self.timetable.setColumnWidth(i, w)

        self.update_days_header()
    
    def update_days_header(self):
        """Kunlar headerini ustun kengliklariga moslashtirish"""
        if not hasattr(self, 'days_header_labels'):
            return
        
        kun_width = self.PERIODS_PER_DAY * self.current_col_width
        
        for label in self.days_header_labels:
            label.setFixedWidth(kun_width)
    
    def load_teacher_unavailable_cache(self):
        """O'qituvchi unavailable ma'lumotlarini cache qilish"""
        self.teacher_unavailable_cache = {}
        # Teacher ma'lumotlarini ham cache qilish — DB query'larni kamaytirish
        self._teachers_cache = self.db.get_all_teachers()
        
        for teacher in self._teachers_cache:
            teacher_id = teacher[0]
            unavail = self.db.get_teacher_unavailable(teacher_id)
            # {teacher_id: {(day, period): type}}
            self.teacher_unavailable_cache[teacher_id] = {}
            for day, period, avail_type in unavail:
                self.teacher_unavailable_cache[teacher_id][(day, period)] = avail_type
    
    def mark_non_working_days(self):
        """Sinf ishlamaydigan kunlarni kulrang qilish"""
        for row, cls in enumerate(self.classes):
            # cls = (id, name, level, students_count, working_days, created_at)
            working_days = cls[4] if len(cls) > 4 and cls[4] else 6
            
            # FAQAT 5 kun bo'lsa Shanba (5-index) ni kulrang
            if working_days == 5:
                day = 5  # Shanba
                for period in range(self.PERIODS_PER_DAY):
                    col = day * self.PERIODS_PER_DAY + period
                    item = QTableWidgetItem("✕")
                    item.setBackground(QColor("#BDC3C7"))
                    item.setForeground(QColor("#7F8C8D"))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(Qt.ItemFlag.NoItemFlags)  # Tahrirlanmas
                    item.setToolTip(f"{cls[1]} sinfi shanba kuni ishlamaydi")
                    self.timetable.setItem(row, col, item)

    # ============ SANPIN TEKSHIRUVI ============

    def check_sanpin_placement(self, class_id, day, period, lesson_data, exclude_key=None):
        """
        Dars joylashtirishda SanPIN buzilishlarini aniqlash.

        Returns: list of {'type': 'hard'|'soft', 'message': str}
        """
        # SanPINChecker ni cache qilish — har safar yangi yaratmaslik
        if self._sanpin_checker is None:
            from core.sanpin import SanPINChecker
            self._sanpin_checker = SanPINChecker()
        sp = self._sanpin_checker

        # Sinf ma'lumotlari
        class_level = 5
        class_name = ""
        for cls in self.classes:
            if cls[0] == class_id:
                class_level = cls[2] if len(cls) > 2 else 5
                class_name = cls[1]
                break

        max_daily = sp.max_daily_lessons.get(class_level, 6)
        max_weekly = sp.max_weekly_lessons.get(class_level, 34)
        teacher_name = lesson_data.get('teacher_name', '')
        subject_name = lesson_data.get('subject_name', '')
        kunlar = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]

        violations = []

        # 1. Period raqami max_daily dan katta — bu soat umuman yo'q
        if period >= max_daily:
            violations.append({
                'type': 'hard',
                'message': f"{kunlar[day]} kuni {period+1}-dars soati "
                           f"{class_level}-sinf uchun mavjud emas "
                           f"(maksimal {max_daily} dars)"
            })

        # 2. Kunlik dars limiti — darslar soni bo'yicha
        daily_count = sum(
            1 for (cid, d, p), data in self.timetable_data.items()
            if cid == class_id and d == day and (cid, d, p) != exclude_key
        )
        if daily_count >= max_daily:
            violations.append({
                'type': 'hard',
                'message': f"Kunlik limit buzildi: {kunlar[day]} kuni "
                           f"{daily_count}/{max_daily} ta dars bor"
            })

        # 2. Haftalik dars limiti
        weekly_count = sum(
            1 for (cid, d, p), data in self.timetable_data.items()
            if cid == class_id and (cid, d, p) != exclude_key
        )
        if weekly_count >= max_weekly:
            violations.append({
                'type': 'hard',
                'message': f"Haftalik limit buzildi: {weekly_count}/{max_weekly} ta dars bor"
            })

        # 3. Bir kunda bir fan 2 marta (Matematika bundan mustasno)
        if subject_name not in ["Matematika", "Algebra"]:
            same_subject_count = sum(
                1 for (cid, d, p), data in self.timetable_data.items()
                if cid == class_id and d == day
                   and data.get('subject_name') == subject_name
                   and (cid, d, p) != exclude_key
            )
            if same_subject_count >= 1:
                violations.append({
                    'type': 'soft',
                    'message': f"{subject_name} allaqachon {kunlar[day]} kuni "
                               f"{same_subject_count} marta qo'yilgan"
                })

        # 4. Og'ir fan birinchi darsda
        difficulty = sp.get_difficulty(subject_name)
        if period == 0 and difficulty >= 9:
            violations.append({
                'type': 'soft',
                'message': f"1-darsda juda qiyin fan ({subject_name}, "
                           f"qiyinlik={difficulty})"
            })

        # 5. Og'ir fan oxirgi darsda
        if difficulty >= 8:
            # Oxirgi darsni aniqlash
            last_on_day = max(
                (p for (cid, d, p) in self.timetable_data if cid == class_id and d == day),
                default=-1
            )
            if period > last_on_day and period >= 5:
                violations.append({
                    'type': 'soft',
                    'message': f"Oxirgi darsda qiyin fan ({subject_name}, "
                               f"qiyinlik={difficulty})"
                })

        # 6. Ketma-ket qiyin fanlar
        if period > 0 and difficulty >= 7:
            prev_key = (class_id, day, period - 1)
            if prev_key in self.timetable_data:
                prev_subj = self.timetable_data[prev_key].get('subject_name', '')
                prev_diff = sp.get_difficulty(prev_subj)
                if prev_diff >= 7:
                    violations.append({
                        'type': 'soft',
                        'message': f"Ketma-ket qiyin fanlar: {prev_subj} → {subject_name}"
                    })

        # 7. Sportdan keyin qiyin fan
        if period > 0 and difficulty >= 7:
            prev_key = (class_id, day, period - 1)
            if prev_key in self.timetable_data:
                prev_subj = self.timetable_data[prev_key].get('subject_name', '')
                if prev_subj in ["Sport", "Jismoniy tarbiya"]:
                    violations.append({
                        'type': 'soft',
                        'message': f"Sport/JT dan keyin qiyin fan ({subject_name})"
                    })

        return violations

    def get_class_working_days(self, class_id):
        """Sinfning ish kunlarini olish"""
        for cls in self.classes:
            if cls[0] == class_id:
                return cls[4] if len(cls) > 4 and cls[4] else 6
        return 6

    def _build_drag_indexes(self):
        """Drag-and-drop uchun indekslar yaratish — O(1) qidiruv"""
        if self._drag_indexes is not None:
            return self._drag_indexes

        # teacher_idx[(teacher_id, day, period)] = class_id
        teacher_idx = {}
        # daily_count[(class_id, day)] = int
        daily_count = {}
        # weekly_count[(class_id)] = int
        weekly_count = {}
        # subject_day[(class_id, day, lesson_id)] = True
        subject_day = {}

        for (cid, day, period), data in self.timetable_data.items():
            tid = data.get('teacher_id', 0)
            if tid:
                teacher_idx[(tid, day, period)] = cid

            daily_count[(cid, day)] = daily_count.get((cid, day), 0) + 1
            weekly_count[cid] = weekly_count.get(cid, 0) + 1

            lid = data.get('lesson_id', 0)
            if lid:
                subject_day[(cid, day, lid)] = True

        self._drag_indexes = {
            'teacher_idx': teacher_idx,
            'daily_count': daily_count,
            'weekly_count': weekly_count,
            'subject_day': subject_day,
        }
        return self._drag_indexes

    def _invalidate_drag_indexes(self):
        """Indekslarni bekor qilish — timetable_data o'zgarganda"""
        self._drag_indexes = None


    def check_cell_status(self, row, col, lesson_data):
        """
        Katak holatini tekshirish (indekslardan foydalanadi — O(1))

        Returns:
            'free'    - Yashil (bo'sh, qo'yish mumkin)
            'blocked' - Qizil (qat'iy band, metodik kun, boshqa sinfda)
            'sanpin'  - Ko'k (SanPIN ogohlantirish)
            'soft'    - Sariq (yumshoq band soat)
            'swap'    - To'q sariq (katakda dars bor, almashtirish)
            'invalid' - Tekshirilmaydi
        """
        if row >= len(self.classes):
            return 'invalid'

        target_class_id = self.classes[row][0]
        target_class_level = self.classes[row][2] if len(self.classes[row]) > 2 else 5
        day = col // self.PERIODS_PER_DAY
        period = col % self.PERIODS_PER_DAY

        # === 🔴 QIZIL — QAT'IY BLOKLASH (avval tekshiriladi) ===

        # 1. Boshqa sinfning darsi
        if target_class_id != lesson_data['class_id']:
            return 'blocked'

        # 2. Sinf bu kun ishlaydimi?
        working_days = self.get_class_working_days(target_class_id)
        if day >= working_days:
            return 'blocked'

        # SanPINChecker ni bir marta yaratish, keyin keshlash
        if self._sanpin_checker is None:
            from core.sanpin import SanPINChecker
            self._sanpin_checker = SanPINChecker()
        sp = self._sanpin_checker
        max_daily = sp.max_daily_lessons.get(target_class_level, 6)

        # Indekslardan foydalanish (O(1) qidiruv)
        idx = self._drag_indexes or self._build_drag_indexes()
        existing_key = (target_class_id, day, period)

        # 3. Kunlik dars limiti — indeksdan O(1)
        daily_count = idx['daily_count'].get((target_class_id, day), 0)
        if existing_key in self.timetable_data:
            daily_count -= 1

        # 4. Haftalik dars limiti — indeksdan O(1)
        weekly_count = idx['weekly_count'].get(target_class_id, 0)
        if existing_key in self.timetable_data:
            weekly_count -= 1

        # 5. O'qituvchining metodik kuni
        teacher_id = lesson_data.get('teacher_id', 0)
        if not hasattr(self, '_teachers_cache'):
            self._teachers_cache = self.db.get_all_teachers()
        teachers = self._teachers_cache
        for t in teachers:
            if t[0] == teacher_id:
                methodic_day = t[5]
                if methodic_day is not None and methodic_day == day:
                    return 'blocked'
                break

        # 6. O'qituvchining qat'iy band soati
        unavail = self.teacher_unavailable_cache.get(teacher_id, {})
        if (day, period) in unavail:
            if unavail[(day, period)] == 'strict':
                return 'blocked'

        # 7. O'qituvchi shu vaqtda boshqa sinfda — indeksdan O(1)
        if teacher_id:
            blocking_class = idx['teacher_idx'].get((teacher_id, day, period))
            if blocking_class is not None and blocking_class != target_class_id:
                return 'blocked'

        # === 🔵 KO'K — SANPIN OGOGHLANTIRISH ===

        subj_name = lesson_data.get('subject_name', '')
        difficulty = sp.get_difficulty(subj_name)
        is_hard = difficulty >= 7

        # 8. Period raqami max_daily dan katta
        if period >= max_daily:
            return 'sanpin'

        # 9. 1-darsda qiyin fan
        if period == 0 and is_hard:
            return 'sanpin'

        # 10. Oxirgi darsda qiyin fan
        if period == max_daily - 1 and is_hard:
            return 'sanpin'

        # 11. Qiyin fanlar ketma-ket
        if period > 0:
            prev_key = (target_class_id, day, period - 1)
            if prev_key in self.timetable_data:
                prev_subj = self.timetable_data[prev_key].get('subject_name', '')
                prev_diff = sp.get_difficulty(prev_subj)
                if is_hard and prev_diff >= 7:
                    return 'sanpin'

        # 12. Sport darsidan keyin qiyin fan
        if period > 0:
            prev_key = (target_class_id, day, period - 1)
            if prev_key in self.timetable_data:
                prev_subj = self.timetable_data[prev_key].get('subject_name', '')
                prev_lower = prev_subj.lower()
                if is_hard and ('jismoniy' in prev_lower or 'sport' in prev_lower):
                    return 'sanpin'

        # 13. Oyna (bo'sh dars orasida)
        if period > 0:
            prev_key = (target_class_id, day, period - 1)
            if prev_key not in self.timetable_data:
                has_any_before = any(
                    (target_class_id, day, p) in self.timetable_data
                    for p in range(period)
                )
                if has_any_before:
                    return 'sanpin'

        # === 🟡 SARIQ — YUMSHOQ BAND ===

        # 14. Yumshoq band soat
        if (day, period) in unavail:
            if unavail[(day, period)] == 'soft':
                return 'soft'

        # === 🟠 TO'Q SARIQ — ALMASHTIRISH ===

        # 15. Bu katakda allaqachon dars bor
        if existing_key in self.timetable_data:
            existing = self.timetable_data[existing_key]
            if existing['lesson_id'] == lesson_data['lesson_id']:
                return 'blocked'
            return 'swap'

        # 16. Bir kunda shu fan 2 marta — indeksdan O(1)
        lesson_id = lesson_data.get('lesson_id', 0)
        if lesson_id and idx['subject_day'].get((target_class_id, day, lesson_id)):
            return 'swap'

        return 'free'
    
    def highlight_all_cells(self, lesson_data):
        """Barcha kataklarni tekshirib rangini o'zgartirish"""
        if self.highlight_active:
            self.highlight_active = False

        self.highlight_active = True
        self.current_drag_lesson = lesson_data
        self.original_colors = {}
        self._build_drag_indexes()

        total_cols = self.DAYS_PER_WEEK * self.PERIODS_PER_DAY

        for row in range(len(self.classes)):
            for col in range(total_cols):
                item = self.timetable.item(row, col)

                # Asl ranglarni saqlash (dars turgan kataklar uchun)
                has_lesson = (row, col) in self.timetable_data
                if has_lesson and item and (row, col) not in self.original_colors:
                    self.original_colors[(row, col)] = item.background()

                status = self.check_cell_status(row, col, lesson_data)
                if status == 'invalid':
                    continue

                if item is None:
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.timetable.setItem(row, col, item)

                # Rang berish
                if status == 'free':
                    item.setBackground(self.COLOR_FREE)
                elif status == 'blocked':
                    item.setBackground(self.COLOR_BLOCKED)
                elif status == 'sanpin':
                    item.setBackground(self.COLOR_SANPIN)
                elif status == 'soft':
                    item.setBackground(self.COLOR_SOFT)
                elif status == 'swap':
                    item.setBackground(self.COLOR_SWAP)
    
    def clear_highlights(self):
        """Highlightlarni tozalash"""
        if not self.highlight_active:
            return
        
        self.highlight_active = False
        
        total_cols = self.DAYS_PER_WEEK * self.PERIODS_PER_DAY
        
        for row in range(len(self.classes)):
            for col in range(total_cols):
                item = self.timetable.item(row, col)
                
                # Sinf ishlamaydigan kun?
                cls = self.classes[row]
                working_days = cls[4] if len(cls) > 4 and cls[4] else 6
                day = col // self.PERIODS_PER_DAY
                
                if day >= working_days:
                    if item:
                        item.setBackground(QColor("#BDC3C7"))
                    continue
                
                if item is None:
                    continue

                # Agar bu katakda ScheduledLessonCard bo'lsa —
                # rang itemdan emas, carddan keladi, itemni bo'shatamiz
                widget = self.timetable.cellWidget(row, col)
                if isinstance(widget, ScheduledLessonCard):
                    # Widget mavjud — item rangini shaffof/oq qilib qo'yamiz
                    # (rang cardning QPalette'dan keladi)
                    item.setBackground(QColor("transparent"))
                    continue
                
                # Asl rangini qaytarish
                if (row, col) in self.original_colors:
                    item.setBackground(self.original_colors[(row, col)])
                else:
                    item.setBackground(QColor("white"))
                    if not item.text() or item.text() == "":
                        self.timetable.setItem(row, col, QTableWidgetItem(""))
        
        self.original_colors = {}
        self.current_drag_lesson = None
        self.timetable.viewport().update()

    
    def load_unplaced_lessons(self):
        # Clear any stale selected button before rebuilding the list.
        if self.selected_unplaced_button is not None:
            try:
                self.selected_unplaced_button.setChecked(False)
            except Exception:
                pass
            self.selected_unplaced_button = None

        while self.unplaced_layout.count():
            item = self.unplaced_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Subjectlarni bir marta olish (N+1 query tuzatilishi)
        subjects_cache = {}
        for sub in self.db.get_all_subjects():
            subjects_cache[sub[0]] = sub[2] or sub[1][:3]

        lessons_grouped = {}
        total_assignments = 0

        # Haqiqiy jadvaldan placementlarni hisoblash (kasrli fanlar uchun)
        timetable_subject_counts = {}
        for tt_data in [self.timetable_data]:
            for (cid, day, period), ldata in tt_data.items():
                sub_name = ldata.get('subject_name', '')
                key = (cid, sub_name)
                timetable_subject_counts[key] = timetable_subject_counts.get(key, 0) + 1

        for cls in self.classes:
            class_id = cls[0]
            class_name = cls[1]

            assignments = self.db.get_class_assignments(class_id)
            total_assignments += len(assignments)

            for ass in assignments:
                lesson_id = ass[0]
                subject_name = ass[1]
                subject_short = subjects_cache.get(ass[5], subject_name[:3])

                placed = self.placed_counts.get((class_id, lesson_id), 0)
                # Agar placed_counts da topilmasa, jadvaldan tekshirish
                if placed == 0:
                    placed = timetable_subject_counts.get((class_id, subject_name), 0)
                remaining = ass[4] - placed

                if remaining > 0:
                    key = (class_id, lesson_id)
                    lessons_grouped[key] = {
                        'lesson_id': lesson_id,
                        'class_id': class_id,
                        'class_name': class_name,
                        'subject_name': ass[1],
                        'subject_short': subject_short,
                        'teacher_name': ass[2],
                        'teacher_id': ass[6],
                        'subject_id': ass[5],
                        'color': ass[3],
                        'weekly_hours': ass[4],
                        'remaining': remaining,
                        'count': remaining
                    }
        
        # AGAR HECH QANDAY DARS BIRIKTIRILMAGAN BO'LSA
        if total_assignments == 0:
            empty_label = QLabel(
                "⚠️ Hech qanday dars biriktirilmagan!\n\n"
                "Avval '📝 Dars biriktirish' oynasidan\n"
                "har bir sinfga darslarni biriktiring."
            )
            empty_label.setStyleSheet("""
                color: #E74C3C; font-size: 14px; font-weight: bold;
                padding: 30px; background-color: #FADBD8;
                border-radius: 8px;
            """)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.unplaced_layout.addWidget(empty_label)
            self.unplaced_stats.setText("⚠️ Dars biriktirilmagan!")
            return
        
        self.display_grouped_lessons(lessons_grouped)
        
        total = sum(l['count'] for l in lessons_grouped.values())
        self.unplaced_stats.setText(f"Jami: {total} ta dars qoldi")

    def select_unplaced_lesson(self, lesson_data, button):
        if self.selected_unplaced_button is not None and self.selected_unplaced_button is not button:
            self.selected_unplaced_button.setChecked(False)
        self.selected_unplaced_lesson = lesson_data
        self.selected_unplaced_button = button
        if not button.isChecked():
            button.setChecked(True)
    
    def display_grouped_lessons(self, lessons_grouped):
        if not lessons_grouped:
            empty_label = QLabel("✅ Barcha darslar joylashtirildi!")
            empty_label.setStyleSheet("""
                color: #27AE60; font-size: 14px; font-weight: bold;
                padding: 30px;
            """)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.unplaced_layout.addWidget(empty_label)
            return
        
        groups = {}
        
        for key, lesson in lessons_grouped.items():
            if self.filter_type == "subject":
                group_key = lesson['subject_name']
            elif self.filter_type == "teacher":
                group_key = lesson['teacher_name']
            elif self.filter_type == "class":
                group_key = lesson.get('class_name', 'Noma\'lum')
            else:
                group_key = lesson['subject_name']
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(lesson)
        
        for group_name, group_lessons in sorted(groups.items()):
            self.add_lesson_group(group_name, group_lessons)
    
    def add_lesson_group(self, group_name, lessons):
        group_widget = QFrame()
        group_widget.setFrameShape(QFrame.Shape.Box)
        group_widget.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 6px;
                border: 1px solid #BDC3C7;
                padding: 5px;
            }
        """)
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(8, 5, 8, 5)
        group_layout.setSpacing(5)
        group_widget.setLayout(group_layout)
        
        header_layout = QHBoxLayout()
        
        icon = "📚"
        if self.filter_type == "teacher":
            icon = "👨‍🏫"
        elif self.filter_type == "class":
            icon = "🏫"
        
        header = QLabel(f"{icon} {group_name}")
        header.setStyleSheet("""
            font-size: 12px; font-weight: bold;
            color: #2C3E50; background-color: transparent;
            border: none;
        """)
        header_layout.addWidget(header)
        
        total_cards = sum(l['count'] for l in lessons)
        count_label = QLabel(f"{total_cards} ta")
        count_label.setStyleSheet("""
            background-color: #3498DB; color: white;
            padding: 2px 8px; border-radius: 10px;
            font-size: 10px; font-weight: bold;
            border: none;
        """)
        header_layout.addWidget(count_label)
        
        header_layout.addStretch()
        group_layout.addLayout(header_layout)
        
        cards_container = QWidget()
        cards_container.setStyleSheet("background-color: transparent; border: none;")
        cards_layout = QHBoxLayout()
        cards_layout.setContentsMargins(5, 5, 5, 10)
        cards_layout.setSpacing(15)
        cards_container.setLayout(cards_layout)
        
        for lesson in lessons:
            stack = LessonCardStack(lesson, lesson['count'])
            stack.update_count(lesson['count'])
            cards_layout.addWidget(stack)
            if self.selected_unplaced_lesson is not None:
                if (self.selected_unplaced_lesson.get('lesson_id') == lesson['lesson_id']
                        and self.selected_unplaced_lesson.get('class_id') == lesson['class_id']):
                    stack.card.setChecked(True)
                    self.selected_unplaced_button = stack.card
        
        cards_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(cards_container)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(80)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
        """)
        
        group_layout.addWidget(scroll)
        
        self.unplaced_layout.addWidget(group_widget)
    
    def _populate_class_selector(self):
        """Class selector ni to'ldirish — sinflar ro'yxati"""
        self.class_search.clear()
        self.class_search.addItem("📋 Barcha sinflar", -1)

        # Daraja bo'yicha guruhlash
        levels = {}
        for cls in self.classes:
            level = cls[2] if len(cls) > 2 else 0
            if level not in levels:
                levels[level] = []
            levels[level].append(cls)

        for level in sorted(levels.keys()):
            for cls in levels[level]:
                class_id = cls[0]
                class_name = cls[1]
                self.class_search.addItem(f"  {class_name}", class_id)

        # Sinf sonini ko'rsatish
        total = len(self.classes)
        self.class_count_label.setText(f"({total} sinf)")

    def _on_class_selected(self, index):
        """Sinf tanlanganda — faqat shu sinfni ko'rsatish"""
        if index < 0:
            return
        class_id = self.class_search.currentData()
        if class_id is None or class_id == -1:
            # Barcha sinflarni ko'rsatish
            self.timetable.setRowCount(len(self.classes))
            for i, cls in enumerate(self.classes):
                self.timetable.setVerticalHeaderItem(i, QTableWidgetItem(cls[1]))
                self.timetable.setRowHidden(i, False)
        else:
            # Faqat tanlangan sinfni ko'rsatish
            for i, cls in enumerate(self.classes):
                if cls[0] == class_id:
                    self.timetable.setRowHidden(i, False)
                    self.timetable.verticalHeader().resizeSection(i, 50)
                else:
                    self.timetable.setRowHidden(i, True)

    def _on_level_filter_changed(self, index):
        """Daraja filteri o'zgarganda — sinflarni filtrlash"""
        filter_text = self.level_filter.currentText()

        if filter_text == "Barchasi":
            min_level, max_level = 1, 11
        elif filter_text == "1-4 sinflar":
            min_level, max_level = 1, 4
        elif filter_text == "5-9 sinflar":
            min_level, max_level = 5, 9
        elif filter_text == "10-11 sinflar":
            min_level, max_level = 10, 11
        else:
            min_level, max_level = 1, 11

        visible_count = 0
        for i, cls in enumerate(self.classes):
            level = cls[2] if len(cls) > 2 else 0
            if min_level <= level <= max_level:
                self.timetable.setRowHidden(i, False)
                visible_count += 1
            else:
                self.timetable.setRowHidden(i, True)

        self.class_count_label.setText(f"({visible_count}/{len(self.classes)} sinf)")

    def on_filter_changed(self):
        idx = self.filter_combo.currentIndex()
        if idx == 0:
            self.filter_type = "subject"
        elif idx == 1:
            self.filter_type = "teacher"
        else:
            self.filter_type = "class"
        
        self.load_unplaced_lessons()
    
    # ============ JOYLASHTIRISH ============
    
    def place_lesson(self, row, col, lesson_data, src_key=None, src_widget=None):
        self.clear_highlights()

        if row >= len(self.classes):
            return

        target_class_id = self.classes[row][0]
        target_class_name = self.classes[row][1]
        day = col // self.PERIODS_PER_DAY
        period = col % self.PERIODS_PER_DAY
        target_key = (target_class_id, day, period)

        # 1. Boshqa sinfga qo'yish — mumkin emas
        if target_class_id != lesson_data['class_id']:
            QMessageBox.warning(
                self, "Mumkin emas",
                f"Bu dars {lesson_data.get('class_name', '?')} sinfiga tegishli.\n"
                f"Uni boshqa sinfga qo'yib bo'lmaydi!"
            )
            return

        # 1.1. Kelajak soatini ko'chirishga ogohlantirish
        if lesson_data.get('subject_name', '').lower() == 'kelajak soati':
            if src_key is not None:
                reply = QMessageBox.question(
                    self, "⚠️ Kelajak soati",
                    "Kelajak soatini o'rnidan ko'chirmoqchimisiz?\n\n"
                    "Bu dars avtomatik ravishda sinf rahbariga\n"
                    "belgilangan kunda 1-darsga qo'yilgan.\n\n"
                    "Davom etasizmi?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

        # 2. Sinf ishlamaydigan kun — mumkin emas
        working_days = self.get_class_working_days(target_class_id)
        if day >= working_days:
            QMessageBox.warning(
                self, "Mumkin emas",
                f"{target_class_name} sinfi {self.KUNLAR[day]} kuni ishlamaydi!"
            )
            return

        # 3. O'qituvchi metodik kuni — OGOGHLANTIRISH (tasdiqlash bilan)
        teacher_id = lesson_data.get('teacher_id', 0)
        # Teacher ma'lumotlarini cache'dan olish — DB query o'rniga
        if not hasattr(self, '_teachers_cache'):
            self._teachers_cache = self.db.get_all_teachers()
        teachers = self._teachers_cache
        for t in teachers:
            if t[0] == teacher_id:
                if t[5] is not None and t[5] == day:
                    dialog_info = {
                        'subject_name': lesson_data.get('subject_name', ''),
                        'class_name': target_class_name,
                        'period': period + 1,
                    }
                    dialog = MethodicDayWarningDialog(
                        t[1], self.KUNLAR[day], dialog_info, self
                    )
                    dialog.exec()
                    if not dialog.result:
                        return
                    # Tasdiqlansa — davom etish
                break

        # 4. O'qituvchi qat'iy band — OGOGHLANTIRISH (tasdiqlash bilan)
        unavail = self.teacher_unavailable_cache.get(teacher_id, {})
        if (day, period) in unavail and unavail[(day, period)] == 'strict':
            dialog_info = {
                'subject_name': lesson_data.get('subject_name', ''),
                'class_name': target_class_name,
                'period': period + 1,
            }
            dialog = StrictUnavailableWarningDialog(
                lesson_data.get('teacher_name', ''),
                self.KUNLAR[day], period + 1, dialog_info, self
            )
            dialog.exec()
            if not dialog.result:
                return

        # 5. O'qituvchi boshqa sinfda — mumkin emas
        for (cid, d, p), data in self.timetable_data.items():
            if d == day and p == period and cid != target_class_id:
                if data.get('teacher_id') == teacher_id:
                    QMessageBox.warning(
                        self, "Mumkin emas",
                        f"O'qituvchi {lesson_data['teacher_name']} "
                        f"{self.KUNLAR[day]} {period+1}-darsda "
                        f"{data.get('class_name', '?')} sinfida dars o'tkazmoqda!"
                    )
                    return

        # 6. SANPIN TEKSHIRUVI — har qanday holatda (yangi joy, ko'chirish, almashtirish)
        kunlar = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]
        violations = self.check_sanpin_placement(
            target_class_id, day, period, lesson_data,
            exclude_key=src_key if src_key else None
        )

        if violations:
            dialog_info = {
                'subject_name': lesson_data.get('subject_name', ''),
                'class_name': target_class_name,
                'day_name': kunlar[day] if day < 6 else '?',
                'period': period + 1,
            }
            dialog = SanPINWarningDialog(violations, dialog_info, self)
            dialog.exec()
            if not dialog.result:
                return

        # 7. Katakda dars bor — almashtirish logikasi
        if target_key in self.timetable_data:
            existing = self.timetable_data[target_key]
            if existing['lesson_id'] == lesson_data['lesson_id']:
                return

            old_can_place = self._can_place_lesson_at(
                src_key, existing, lesson_data
            )

            if old_can_place:
                reply = QMessageBox.information(
                    self, "Almashtirish",
                    f"✅ Darslar almashadi!\n\n"
                    f"📤 {lesson_data['subject_name']} ({lesson_data['teacher_name']})\n"
                    f"      ↓\n"
                    f"📥 {existing['subject_name']} ({existing['teacher_name']})",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                )
                if reply == QMessageBox.StandardButton.Ok:
                    self._do_swap(target_key, src_key, lesson_data, existing)
                return
            else:
                reply = QMessageBox.question(
                    self, "Almashtirib bo'lmaydi",
                    f"⚠️ Darslar almashib bo'lmaydi!\n\n"
                    f"📥 Joylashtirilayotgan: {lesson_data['subject_name']}\n"
                    f"📍 Mavjud: {existing['subject_name']}\n\n"
                    f"{existing['subject_name']} darsini "
                    f"joylashtirilmaganlarga olib qo'ysak bo'ladimi?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._remove_and_place(target_key, src_key, lesson_data, existing)
                return

        # 8. JOYLASHTIRISH
        self._do_place(row, col, lesson_data, src_key, src_widget)

    # ============ YORDAMCHI METODLAR ============

    def _can_place_lesson_at(self, src_key, existing_lesson, incoming_lesson):
        """
        existing_lesson manbadan kelgan darsning joyiga qo'yilsa bo'ladimi?
        (almashtirish uchun tekshirish)
        """
        src_class_id = src_key[0] if src_key else incoming_lesson['class_id']
        src_day = src_key[1] if src_key else 0
        src_period = src_key[2] if src_key else 0

        # Agar manba joy o'z joyi bo'lsa — almashtirish mumkin (joy almashadi)
        target_class_id = existing_lesson['class_id']
        existing_teacher = existing_lesson.get('teacher_id', 0)

        # O'qituvchi manba joyda bandmi?
        for (cid, d, p), data in self.timetable_data.items():
            if d == src_day and p == src_period and cid == src_class_id:
                if cid != target_class_id:
                    if data.get('teacher_id') == existing_teacher:
                        return False

        # Metodik kun tekshirish
        # Teacher ma'lumotlarini cache'dan olish
        if not hasattr(self, '_teachers_cache'):
            self._teachers_cache = self.db.get_all_teachers()
        teachers = self._teachers_cache
        for t in teachers:
            if t[0] == existing_teacher:
                if t[5] is not None and t[5] == src_day:
                    return False
                break

        # Qat'iy bandlik tekshirish
        unavail = self.teacher_unavailable_cache.get(existing_teacher, {})
        if (src_day, src_period) in unavail:
            if unavail[(src_day, src_period)] == 'strict':
                return False

        # Ish kunlari tekshirish
        working_days = self.get_class_working_days(src_class_id)
        if src_day >= working_days:
            return False

        return True

    def _do_swap(self, target_key, src_key, new_lesson, old_lesson):
        """Ikki dars o'rnini almashadi"""
        target_class_id = target_key[0]
        target_day = target_key[1]
        target_period = target_key[2]

        # 1. Manba darsni o'chirish (agar jadvaldan kelsa)
        if src_key and src_key in self.timetable_data:
            src_row = next(
                (idx for idx, c in enumerate(self.classes) if c[0] == src_key[0]),
                None
            )
            if src_row is not None:
                src_col = src_key[1] * self.PERIODS_PER_DAY + src_key[2]
                self.timetable.removeCellWidget(src_row, src_col)
                self.timetable.setItem(src_row, src_col, QTableWidgetItem(""))
            sk = (new_lesson['class_id'], new_lesson['lesson_id']) if src_key else None
            if sk:
                self.placed_counts[sk] = max(0, self.placed_counts.get(sk, 0) - 1)
            del self.timetable_data[src_key]

        # 2. Yangi darsni maqsad joyiga qo'yish (eski darsni siqib chiqarish)
        old_target_pk = (old_lesson['class_id'], old_lesson['lesson_id'])
        self.placed_counts[old_target_pk] = max(0, self.placed_counts.get(old_target_pk, 0) - 1)
        self.timetable_data[target_key] = new_lesson
        self._invalidate_drag_indexes()
        pk = (target_class_id, new_lesson['lesson_id'])
        self.placed_counts[pk] = self.placed_counts.get(pk, 0) + 1

        # 3. Eski darsni manba joyiga qo'yish (to'liq SWAP)
        if src_key:
            self.timetable_data[src_key] = old_lesson
            old_pk = (old_lesson['class_id'], old_lesson['lesson_id'])
            self.placed_counts[old_pk] = self.placed_counts.get(old_pk, 0) + 1

            # Manba joyini jadvalda yangilash
            src_row = next(
                (idx for idx, c in enumerate(self.classes) if c[0] == src_key[0]),
                None
            )
            if src_row is not None:
                src_col = src_key[1] * self.PERIODS_PER_DAY + src_key[2]
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                item.setData(Qt.ItemDataRole.UserRole, old_lesson)
                item.setBackground(QColor("transparent"))

                existing_widget = self.timetable.cellWidget(src_row, src_col)
                if existing_widget is not None:
                    self.timetable.removeCellWidget(src_row, src_col)
                    existing_widget.deleteLater()

                card = ScheduledLessonCard(old_lesson)
                self.timetable.setItem(src_row, src_col, item)
                self.timetable.setCellWidget(src_row, src_col, card)

        # 4. Jadvalni yangilash
        row = next(
            (idx for idx, c in enumerate(self.classes) if c[0] == target_class_id),
            None
        )
        if row is not None:
            col = target_day * self.PERIODS_PER_DAY + target_period
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setData(Qt.ItemDataRole.UserRole, new_lesson)
            item.setBackground(QColor("transparent"))

            existing_widget = self.timetable.cellWidget(row, col)
            if existing_widget is not None:
                self.timetable.removeCellWidget(row, col)
                existing_widget.deleteLater()

            card = ScheduledLessonCard(new_lesson)
            self.timetable.setItem(row, col, item)
            self.timetable.setCellWidget(row, col, card)

        self.load_unplaced_lessons()
        self.status_label.setText(
            f"🔄 Almashtirildi: {new_lesson['subject_name']} ↔ {old_lesson['subject_name']}"
        )

    def _remove_and_place(self, target_key, src_key, new_lesson, old_lesson):
        """Eski darsni unplaced ga, yangi darsni joyiga qo'yish"""
        target_class_id = target_key[0]
        target_day = target_key[1]
        target_period = target_key[2]

        # 1. Manba darsni o'chirish (agar jadvaldan kelsa)
        if src_key and src_key in self.timetable_data:
            src_row = next(
                (idx for idx, c in enumerate(self.classes) if c[0] == src_key[0]),
                None
            )
            if src_row is not None:
                src_col = src_key[1] * self.PERIODS_PER_DAY + src_key[2]
                self.timetable.removeCellWidget(src_row, src_col)
                self.timetable.setItem(src_row, src_col, QTableWidgetItem(""))
            sk = (new_lesson['class_id'], new_lesson['lesson_id'])
            self.placed_counts[sk] = max(0, self.placed_counts.get(sk, 0) - 1)
            del self.timetable_data[src_key]

        # 2. Yangi darsni joyiga qo'yish
        self.timetable_data[target_key] = new_lesson
        self._invalidate_drag_indexes()
        pk = (target_class_id, new_lesson['lesson_id'])
        self.placed_counts[pk] = self.placed_counts.get(pk, 0) + 1

        # 3. Eski darsni unplaced ga qo'yish
        old_pk = (old_lesson['class_id'], old_lesson['lesson_id'])
        self.placed_counts[old_pk] = max(0, self.placed_counts.get(old_pk, 0) - 1)

        # 4. Jadvalni yangilash
        row = next(
            (idx for idx, c in enumerate(self.classes) if c[0] == target_class_id),
            None
        )
        if row is not None:
            col = target_day * self.PERIODS_PER_DAY + target_period
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setData(Qt.ItemDataRole.UserRole, new_lesson)
            item.setBackground(QColor("transparent"))

            existing_widget = self.timetable.cellWidget(row, col)
            if existing_widget is not None:
                self.timetable.removeCellWidget(row, col)
                existing_widget.deleteLater()

            card = ScheduledLessonCard(new_lesson)
            self.timetable.setItem(row, col, item)
            self.timetable.setCellWidget(row, col, card)

        self.load_unplaced_lessons()
        self.status_label.setText(
            f"📥 {old_lesson['subject_name']} unplaced ga, "
            f"📤 {new_lesson['subject_name']} joylashtirildi"
        )

    def _do_place(self, row, col, lesson_data, src_key, src_widget):
        """Oddiy joylashtirish — bo'sh katakka"""
        target_class_id = self.classes[row][0]
        target_class_name = self.classes[row][1]
        day = col // self.PERIODS_PER_DAY
        period = col % self.PERIODS_PER_DAY
        key = (target_class_id, day, period)

        self.timetable_data[key] = lesson_data
        self._invalidate_drag_indexes()
        placed_key = (target_class_id, lesson_data['lesson_id'])
        self.placed_counts[placed_key] = self.placed_counts.get(placed_key, 0) + 1

        item = QTableWidgetItem("")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        item.setData(Qt.ItemDataRole.UserRole, lesson_data)
        item.setBackground(QColor("transparent"))

        existing_widget = self.timetable.cellWidget(row, col)
        if existing_widget is not None and existing_widget is not src_widget:
            self.timetable.removeCellWidget(row, col)
            existing_widget.deleteLater()

        card = ScheduledLessonCard(lesson_data)

        if isinstance(src_widget, ScheduledLessonCard) and src_key is not None and src_key != key:
            source_row = next(
                (idx for idx, c in enumerate(self.classes) if c[0] == src_key[0]),
                None
            )
            if source_row is not None:
                source_col = src_key[1] * self.PERIODS_PER_DAY + src_key[2]
                self.timetable.removeCellWidget(source_row, source_col)

        self.timetable.setItem(row, col, item)
        self.timetable.setCellWidget(row, col, card)
        self.timetable.viewport().update()

        if src_key is not None and src_key != key:
            self._remove_source_lesson(src_key)

        self.load_unplaced_lessons()
        self.status_label.setText(
            f"✅ Joylashtirildi: {lesson_data['subject_name']} → "
            f"{target_class_name} | {self.KUNLAR[day]} {period+1}-dars"
        )

        # Xatoliklar panelini yangilash (debounced)
        if hasattr(self, '_error_update_timer'):
            self._error_update_timer.stop()
        else:
            from PyQt6.QtCore import QTimer
            self._error_update_timer = QTimer()
            self._error_update_timer.setSingleShot(True)
            self._error_update_timer.timeout.connect(self._update_error_panel)
        self._error_update_timer.start(500)
    
    def _remove_source_lesson(self, src_key):
        if src_key not in self.timetable_data:
            return
        source_lesson = self.timetable_data[src_key]
        source_row = next(
            (idx for idx, cls in enumerate(self.classes) if cls[0] == src_key[0]),
            None
        )
        if source_row is not None:
            source_col = src_key[1] * self.PERIODS_PER_DAY + src_key[2]
            self.timetable.removeCellWidget(source_row, source_col)
            self.timetable.setItem(source_row, source_col, QTableWidgetItem(""))
        removed_key = (source_lesson['class_id'], source_lesson['lesson_id'])
        self.placed_counts[removed_key] = max(
            0, self.placed_counts.get(removed_key, 0) - 1
        )
        del self.timetable_data[src_key]

    def show_context_menu(self, pos):
        item = self.timetable.itemAt(pos)
        if not item:
            return
        
        row = item.row()
        col = item.column()

        day = col // self.PERIODS_PER_DAY
        period = col % self.PERIODS_PER_DAY
        
        if row >= len(self.classes):
            return
        
        class_id = self.classes[row][0]
        key = (class_id, day, period)
        
        if key not in self.timetable_data:
            return
        
        menu = QMenu(self)
        
        delete_action = QAction("🗑️ O'chirish", self)
        delete_action.triggered.connect(
            lambda: self.remove_lesson(row, col, key)
        )
        menu.addAction(delete_action)
        
        info_action = QAction("ℹ️ Ma'lumot", self)
        info_action.triggered.connect(
            lambda: self.show_lesson_info(key)
        )
        menu.addAction(info_action)
        
        menu.exec(self.timetable.viewport().mapToGlobal(pos))
    
    def remove_lesson(self, row, col, key):
        if key not in self.timetable_data:
            return

        lesson_data = self.timetable_data[key]
        placed_key = (lesson_data['class_id'], lesson_data['lesson_id'])

        self.placed_counts[placed_key] = max(
            0, self.placed_counts.get(placed_key, 0) - 1
        )

        if self.timetable.cellWidget(row, col):
            widget = self.timetable.cellWidget(row, col)
            self.timetable.removeCellWidget(row, col)
            widget.deleteLater()

        self.timetable.setItem(row, col, QTableWidgetItem(""))

        del self.timetable_data[key]
        self._invalidate_drag_indexes()

        self.load_unplaced_lessons()
        self.status_label.setText(
            f"🗑️ O'chirildi: {lesson_data['subject_name']}"
        )

    def unplace_lesson(self, src_key):
        if src_key not in self.timetable_data:
            return

        source_row = next(
            (idx for idx, cls in enumerate(self.classes) if cls[0] == src_key[0]),
            None
        )
        if source_row is None:
            return

        source_col = src_key[1] * self.PERIODS_PER_DAY + src_key[2]
        lesson_data = self.timetable_data[src_key]
        self.remove_lesson(source_row, source_col, src_key)
        self.status_label.setText(
            f"↩️ {lesson_data['subject_name']} qaytarildi"
        )

    def show_lesson_info(self, key):
        data = self.timetable_data[key]
        
        class_id, day, period = key
        class_name = ""
        for cls in self.classes:
            if cls[0] == class_id:
                class_name = cls[1]
                break
        
        QMessageBox.information(
            self, "Dars ma'lumoti",
            f"🏫 Sinf: {class_name}\n"
            f"📅 Kun: {self.KUNLAR[day]}\n"
            f"⏰ Dars: {period+1}-dars\n\n"
            f"📚 Fan: {data['subject_name']}\n"
            f"👨‍🏫 O'qituvchi: {data['teacher_name']}"
        )
    
    # ============ TUGMA AMALLAR ============
    
    def clear_all(self):
        if not self.timetable_data:
            return
        
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "BARCHA sinflar uchun jadvalni tozalashni xohlaysizmi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.timetable.clearContents()
            # Widgetlarni ham tozalash
            for row in range(self.timetable.rowCount()):
                for col in range(self.timetable.columnCount()):
                    widget = self.timetable.cellWidget(row, col)
                    if widget is not None:
                        self.timetable.removeCellWidget(row, col)
                        widget.deleteLater()
            self.timetable_data = {}
            self.placed_counts = {}
            self._invalidate_drag_indexes()
            self.load_unplaced_lessons()
            self.status_label.setText("🗑️ Hammasi tozalandi")
    
    def auto_generate_all(self):
        """Barcha sinflar uchun avtomatik jadval generatsiya qilish"""
        try:
            self._do_auto_generate()
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logging.error(f"auto_generate_all: {e}\n{tb}")
            QMessageBox.critical(self, "Xatolik", f"Avtomatik jadval xatolik:\n{str(e)}\n\n{tb[-500:]}")
            self.status_label.setText(f"❌ Xatolik: {str(e)}")

    def _do_auto_generate(self):
        """Asosiy avtomatik jadval logikasi — background thread bilan"""
        if not self.classes:
            QMessageBox.warning(self, "Xatolik", "Sinflar yo'q!")
            return

        # Tekshirish
        has_assignments = False
        for cls in self.classes:
            assignments = self.db.get_class_assignments(cls[0])
            if assignments:
                has_assignments = True
                break

        if not has_assignments:
            QMessageBox.warning(
                self, "Xatolik",
                "Hech qanday dars biriktirilmagan!\n\n"
                "Avval '📝 Dars biriktirish' oynasidan\n"
                "har bir sinfga darslarni biriktiring."
            )
            return

        # O'qituvchi yuklanishini tekshirish (sozlamadan olingan limit bo'yicha)
        overflow_teachers = self._check_teacher_workload()
        if overflow_teachers:
            msg_lines = ["Quyidagi o'qituvchilarning dars yuklasi limitdan oshib ketdi:\n"]
            for t_name, total, limit, overflow in overflow_teachers:
                msg_lines.append(f"• {t_name}: {total} soat (limit: {limit}) — +{overflow} soat ortiqcha")
            msg_lines.append(f"\nJadval tuzilsinmi? (Ba'zi darslar joylashmasligi mumkin)")
            reply = QMessageBox.question(
                self, "O'qituvchi yuklanishi ortiqcha",
                "\n".join(msg_lines),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "Barcha sinflar uchun avtomatik jadval tuzilsinmi?\n\n"
            "⚠️ Mavjud jadval tozalanadi!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Alohida 0,5 soatlik fanlarni aniqlash — kasrli soatlar mavjud bo'lsa
        # Jadvanni tozalash
        self.timetable.clearContents()
        for row in range(self.timetable.rowCount()):
            for col in range(self.timetable.columnCount()):
                widget = self.timetable.cellWidget(row, col)
                if widget is not None:
                    self.timetable.removeCellWidget(row, col)
                    widget.deleteLater()
        self.timetable_data = {}
        self.placed_counts = {}
        self._invalidate_drag_indexes()

        # Progress dialog
        self._progress_dialog = ProgressDialog(len(self.classes), self)

        # Background thread ishga tushirish
        self._schedule_worker = ScheduleWorker(self.classes, self.db)
        self._schedule_worker.progress.connect(self._on_schedule_progress)
        self._schedule_worker.finished.connect(self._on_schedule_finished)
        self._schedule_worker.error.connect(self._on_schedule_error)
        self._schedule_worker.start()

        # Dialogni keyinroq ochish — worker tez tugab qolmasin
        QTimer.singleShot(100, self._show_progress_dialog)

    def _on_schedule_progress(self, class_name, idx, score, elapsed):
        """Worker dan progress signal"""
        if hasattr(self, '_progress_dialog') and self._progress_dialog:
            self._progress_dialog.update_progress(class_name, idx, score, 0, elapsed)
            if self._progress_dialog.cancelled and self._schedule_worker:
                self._schedule_worker.cancel()

    def _show_progress_dialog(self):
        """Progress dialogni ko'rsatish"""
        if hasattr(self, '_progress_dialog') and self._progress_dialog:
            self._progress_dialog.show()
            self._progress_dialog.raise_()
            self._progress_dialog.activateWindow()

    def _on_schedule_finished(self, all_data, conflicts, placed_count):
        """Worker tugadi — natijalarni jadvalga qo'llash"""
        # Jadvalni qo'llash
        for (class_id, day, period), lesson_data in all_data.items():
            row = self._class_row_map.get(class_id)
            if row is None:
                continue

            col = day * self.PERIODS_PER_DAY + period
            key = (class_id, day, period)
            self.timetable_data[key] = lesson_data
            placed_key = (class_id, lesson_data['lesson_id'])
            self.placed_counts[placed_key] = self.placed_counts.get(placed_key, 0) + 1

            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setData(Qt.ItemDataRole.UserRole, lesson_data)
            item.setBackground(QColor("transparent"))
            self.timetable.setItem(row, col, item)
            card = ScheduledLessonCard(lesson_data)
            self.timetable.setCellWidget(row, col, card)

        # Jadval ma'lumotlari
        # Bazaga saqlash
        try:
            self.db.save_scheduled_lessons(self.timetable_data)
        except Exception as e:
            print(f"Avtomatik saqlash xatolik: {e}")

        # SanPIN hisoboti
        from core.sanpin import SanPINChecker
        sp = SanPINChecker()
        sanpin_results = []
        tayanch_data = self.db.load_tayanch_reja()
        for cls in self.classes:
            cid = cls[0]
            cname = cls[1]
            level = cls[2] if len(cls) > 2 else 5
            grid = [["" for _ in range(6)] for _ in range(self.PERIODS_PER_DAY)]
            for (class_id, day, period), info in self.timetable_data.items():
                if class_id == cid and day < 6 and period < self.PERIODS_PER_DAY:
                    grid[period][day] = info['subject_name']
            # Tayanch soatlarni to'plash (sinf darajasiga qarab)
            tayanch_hours = {}
            for t in tayanch_data:
                if t['class_level'] == level:
                    tayanch_hours[t['subject_name']] = t['weekly_hours']
            res = sp.check_timetable(grid, level, tayanch_hours)
            res['class_name'] = cname
            res['total_lessons'] = sum(1 for v in self.timetable_data.values() if v['class_id'] == cid)
            sanpin_results.append(res)

        if sanpin_results:
            avg_score = sum(r.get('score', 0) for r in sanpin_results) // max(len(sanpin_results), 1)
            total_errors = sum(len(r.get('errors', [])) for r in sanpin_results)
            total_warnings = sum(len(r.get('warnings', [])) for r in sanpin_results)
            algo_name = "Greedy + Backtracking"
            self.status_label.setText(
                f"⚡ {algo_name} | {placed_count} ta dars | "
                f"SanPIN: {avg_score}% | Xatolar: {total_errors} | Ogohlantirishlar: {total_warnings}"
            )
            msg = f"{placed_count} ta dars joylashtirildi | SanPIN: {avg_score}%"
        else:
            algo_name = "Greedy + Backtracking"
            self.status_label.setText(f"⚡ {algo_name} | {placed_count} ta dars")
            msg = f"{placed_count} ta dars joylashtirildi"

        if hasattr(self, '_progress_dialog') and self._progress_dialog:
            self._progress_dialog.finish(True, msg)

        # Xatoliklar panelini yangilash
        self._update_error_panel()

    def _on_error_clicked(self, class_id, day, period):
        """Xatolik bosilganda — jadvalga o'tish"""
        row = self._class_row_map.get(class_id)
        if row is None:
            return

        col = day * self.PERIODS_PER_DAY + period
        self.timetable.scrollToItem(
            self.timetable.item(row, col),
            QAbstractItemView.ScrollHint.EnsureVisible
        )
        self.timetable.setCurrentCell(row, col)

    def _update_error_panel(self):
        """Xatoliklar panelini yangilash"""
        if hasattr(self, 'error_panel') and self.error_panel:
            self.error_panel.update_errors(
                self.timetable_data, self.classes, self.db
            )

    def _on_schedule_error(self, error_msg):
        """Worker xatolik"""
        import traceback as tb
        logging.error(f"_on_schedule_error: {error_msg}")
        if hasattr(self, '_progress_dialog') and self._progress_dialog:
            self._progress_dialog.finish(False, f"Xatolik: {error_msg}")
        QMessageBox.critical(self, "Xatolik", f"Avtomatik jadval xatolik:\n{error_msg}")
        self.status_label.setText(f"❌ Xatolik: {error_msg}")

    def save_all(self):
        """Dars jadvalini JSON faylga saqlash"""
        # Joriy haftaning ma'lumotlarini saqlash
        self._save_current_week_data()

        if not self.timetable_data:
            QMessageBox.warning(self, "Xatolik", "Jadval bo'sh!")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Jadvalni saqlash",
            f"jadval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON fayllar (*.json)"
        )
        if not filename:
            return

        try:
            import json

            # Ma'lumotlarni tayyorlash
            save_data = {
                'version': '2.0',
                'saved_at': datetime.now().isoformat(),
                'classes': [],
                'timetable_week1': {},
                # week2 removed
            }

            # Sinflar
            for cls in self.classes:
                save_data['classes'].append({
                    'id': cls[0],
                    'name': cls[1],
                    'level': cls[2],
                    'students_count': cls[3] if len(cls) > 3 else 0,
                    'working_days': cls[4] if len(cls) > 4 else 6,
                })

            # 1-hafta jadvali
            for (class_id, day, period), info in self.timetable_data.items():
                key = f"{class_id}_{day}_{period}"
                save_data['timetable_week1'][key] = {
                    'lesson_id': info.get('lesson_id'),
                    'subject_name': info.get('subject_name'),
                    'subject_short': info.get('subject_short'),
                    'subject_id': info.get('subject_id'),
                    'teacher_name': info.get('teacher_name'),
                    'teacher_id': info.get('teacher_id'),
                    'class_id': info.get('class_id'),
                    'class_name': info.get('class_name'),
                    'color': info.get('color'),
                    'weekly_hours': info.get('weekly_hours'),
                }



            # Joylashtirilgan darslar soni
            save_data['placed_counts'] = {}
            for (class_id, lesson_id), count in self.placed_counts.items():
                save_data['placed_counts'][f"{class_id}_{lesson_id}"] = count

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            total = len(self.timetable_data)
            self.status_label.setText(f"💾 Saqlandi: {total} ta dars → {filename}")
            QMessageBox.information(
                self, "Saqlandi",
                f"Jadval muvaffaqiyatli saqlandi!\n\n"
                f"📁 {filename}\n"
                f"📊 {total} ta dars, {len(self.classes)} sinf"
            )

        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Saqlash xatolik:\n{str(e)}")

    def load_all(self):
        """Saqlangan dars jadvalini yuklab olish"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Jadvalni ochish",
            "",
            "JSON fayllar (*.json);",  # Barcha fayllar (*.*)",
        )
        if not filename:
            return

        try:
            import json

            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # Jadvalni tozalash
            self.timetable.clearContents()
            for row in range(self.timetable.rowCount()):
                for col in range(self.timetable.columnCount()):
                    widget = self.timetable.cellWidget(row, col)
                    if widget is not None:
                        self.timetable.removeCellWidget(row, col)
                        widget.deleteLater()
            self.timetable_data = {}
            self.placed_counts = {}
            self._invalidate_drag_indexes()

            # Jadval ma'lumotlarini yuklash
            timetable = save_data.get('timetable', {})
            placed = 0

            for key_str, info in timetable.items():
                parts = key_str.split('_')
                if len(parts) != 3:
                    continue

                class_id = int(parts[0])
                day = int(parts[1])
                period = int(parts[2])

                # Sinf qatorini topish
                row = None
                for i, cls in enumerate(self.classes):
                    if cls[0] == class_id:
                        row = i
                        break

                if row is None:
                    continue

                col = day * self.PERIODS_PER_DAY + period
                if col >= self.timetable.columnCount():
                    continue

                # timetable_data ga qo'shish
                self.timetable_data[(class_id, day, period)] = info

                # Placed counts
                lesson_id = info.get('lesson_id')
                if lesson_id:
                    placed_key = (class_id, lesson_id)
                    self.placed_counts[placed_key] = self.placed_counts.get(placed_key, 0) + 1

                # Jadvalga widget qo'yish
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                item.setData(Qt.ItemDataRole.UserRole, info)
                item.setBackground(QColor("transparent"))
                self.timetable.setItem(row, col, item)

                card = ScheduledLessonCard(info)
                self.timetable.setCellWidget(row, col, card)
                placed += 1

            self.recalculate_table_sizes()
            self.load_unplaced_lessons()

            self.status_label.setText(
                f"📂 Yuklandi: {placed} ta dars ← {filename.split('/')[-1].split('\\\\')[-1]}"
            )
            QMessageBox.information(
                self, "Yuklandi",
                f"Jadval muvaffaqiyatli yuklandi!\n\n"
                f"📁 {filename}\n"
                f"📊 {placed} ta dars joylashtirildi"
            )

        except json.JSONDecodeError:
            QMessageBox.critical(self, "Xatolik", "Fayl formati noto'g'ri!\nFaqat JSON fayllar qabul qilinadi.")
        except Exception as e:
            QMessageBox.critical(self, "Xatolik", f"Yuklash xatolik:\n{str(e)}")

