import sqlite3
import os


class DatabaseManager:
    def __init__(self):
        import sys
        import shutil
        if getattr(sys, 'frozen', False):
            # PyInstaller bundle — exe yonidagi yoziladigan joyda saqlash
            exe_dir = os.path.dirname(sys.executable)
            self.db_name = os.path.join(exe_dir, "smartdj.db")
            # Agar exe yonida baza yo'q bo'lsa — bundle dan ko'chirib olish
            if not os.path.exists(self.db_name):
                bundled_db = os.path.join(sys._MEIPASS, "smartdj.db")
                if os.path.exists(bundled_db):
                    shutil.copy2(bundled_db, self.db_name)
        else:
            # Ishlab chiqish muhiti — loyiha papkasida
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_name = os.path.join(base_dir, "smartdj.db")
        self.connection = None

    def initialize(self):
        """Ma'lumotlar bazasini yaratish"""
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout=5000")
        self.cursor = self.connection.cursor()

        # 1. SINFLAR (haftada kun soni qo'shildi)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                level INTEGER NOT NULL,
                students_count INTEGER DEFAULT 0,
                working_days INTEGER DEFAULT 6,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Eski jadvalga working_days qo'shish
        try:
            self.cursor.execute(
                'ALTER TABLE classes ADD COLUMN working_days INTEGER DEFAULT 6'
            )
        except sqlite3.OperationalError:
            pass

        # 2. FANLAR
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                short_name TEXT,
                difficulty INTEGER DEFAULT 5
            )
        ''')

        # 3. O'QITUVCHILAR
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT,
                color TEXT DEFAULT '#3498DB',
                class_teacher_of INTEGER,
                methodic_day INTEGER,
                short_name TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_teacher_of) REFERENCES classes(id) ON DELETE SET NULL
            )
        ''')

        # Eski jadvalga short_name ustunini qo'shish
        try:
            self.cursor.execute('ALTER TABLE teachers ADD COLUMN short_name TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass

        # 4. O'QITUVCHI BAND SOATLARI (2 xil tur bilan)
        # availability_type: 'strict' (qat'iy-qizil) yoki 'soft' (yumshoq-sariq)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_unavailable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                day INTEGER NOT NULL,
                period INTEGER NOT NULL,
                availability_type TEXT DEFAULT 'strict',
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                UNIQUE(teacher_id, day, period)
            )
        ''')
        
        # Eski jadvalga ustun qo'shish (agar bor bo'lsa)
        try:
            self.cursor.execute(
                'ALTER TABLE teacher_unavailable ADD COLUMN availability_type TEXT DEFAULT "strict"'
            )
        except sqlite3.OperationalError:
            pass

        # 5. DARS BIRIKTIRISH (Sinf + Fan + O'qituvchi + Soat + Xona)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lesson_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                classroom_id INTEGER,
                weekly_hours REAL NOT NULL DEFAULT 2,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                UNIQUE(class_id, subject_id, teacher_id)
            )
        ''')
        
        # Eski jadvalga xona ustuni qo'shish
        try:
            self.cursor.execute(
                'ALTER TABLE lesson_assignments ADD COLUMN classroom_id INTEGER'
            )
        except sqlite3.OperationalError:
            pass

        # 6. XONALAR
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classrooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT NOT NULL UNIQUE,
                capacity INTEGER,
                room_type TEXT
            )
        ''')

        # 7. JADVAL (tayyor dars jadvali)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                day INTEGER NOT NULL,
                period INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                subject_name TEXT,
                teacher_name TEXT,
                teacher_id INTEGER,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lesson_assignments(id) ON DELETE CASCADE
            )
        ''')

        # week_index qo'shish (0=numerator, 1=denominator)
        try:
            self.cursor.execute(
                'ALTER TABLE scheduled_lessons ADD COLUMN week_index INTEGER DEFAULT 0'
            )
        except sqlite3.OperationalError:
            pass

        # 8. TAYANCH REJA (MTT tomonidan chiqarilgan yillik reja)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tayanch_reja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                subject_short TEXT,
                class_level INTEGER NOT NULL,
                weekly_hours REAL DEFAULT 0,
                pdf_source TEXT,
                order_index INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subject_name, class_level)
            )
        ''')

        # Eski jadvalga order_index qo'shish
        try:
            self.cursor.execute(
                'ALTER TABLE tayanch_reja ADD COLUMN order_index INTEGER DEFAULT 0'
            )
        except sqlite3.OperationalError:
            pass

        # 9. SOZLAMALAR (global settings)
        self.cursor.execute('''
            subject_id = a[5]
            subject_name = a[1]
            weekly_hours = a[4]
            if weekly_hours != int(weekly_hours):  # Kasrli soat
                fractional.append({
                    'subject_id': subject_id,
                    'subject_name': subject_name,
                    'weekly_hours': weekly_hours,
                    'is_half': weekly_hours < 1  # 0,5 soatlik
                })
        return fractional

    def close(self):
        if self.connection:
            self.connection.close()