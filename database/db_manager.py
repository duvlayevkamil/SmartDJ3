import sqlite3
import os


class DatabaseManager:
    def __init__(self):
        import sys
        import shutil
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            self.db_name = os.path.join(exe_dir, "smartdj.db")
            if not os.path.exists(self.db_name):
                bundled_db = os.path.join(sys._MEIPASS, "smartdj.db")
                if os.path.exists(bundled_db):
                    shutil.copy2(bundled_db, self.db_name)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_name = os.path.join(base_dir, "smartdj.db")
        self.connection = None

    def initialize(self):
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout=5000")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            level INTEGER NOT NULL,
            students_count INTEGER DEFAULT 0,
            working_days INTEGER DEFAULT 6,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        try:
            self.cursor.execute("ALTER TABLE classes ADD COLUMN working_days INTEGER DEFAULT 6")
        except sqlite3.OperationalError:
            pass
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            short_name TEXT,
            difficulty INTEGER DEFAULT 5
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT,
            color TEXT DEFAULT '#3498DB',
            class_teacher_of INTEGER,
            methodic_day INTEGER,
            short_name TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_teacher_of) REFERENCES classes(id) ON DELETE SET NULL
        )""")
        try:
            self.cursor.execute('ALTER TABLE teachers ADD COLUMN short_name TEXT DEFAULT ""')
        except sqlite3.OperationalError:
            pass
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS teacher_unavailable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            day INTEGER NOT NULL,
            period INTEGER NOT NULL,
            availability_type TEXT DEFAULT 'strict',
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
            UNIQUE(teacher_id, day, period)
        )""")
        try:
            self.cursor.execute("ALTER TABLE teacher_unavailable ADD COLUMN availability_type TEXT DEFAULT 'strict'")
        except sqlite3.OperationalError:
            pass
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS lesson_assignments (
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
        )""")
        try:
            self.cursor.execute("ALTER TABLE lesson_assignments ADD COLUMN classroom_id INTEGER")
        except sqlite3.OperationalError:
            pass
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            capacity INTEGER,
            room_type TEXT
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS scheduled_lessons (
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
        )""")
        try:
            self.cursor.execute("ALTER TABLE scheduled_lessons ADD COLUMN week_index INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tayanch_reja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            subject_short TEXT,
            class_level INTEGER NOT NULL,
            weekly_hours REAL DEFAULT 0,
            pdf_source TEXT,
            order_index INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(subject_name, class_level)
        )""")
        try:
            self.cursor.execute("ALTER TABLE tayanch_reja ADD COLUMN order_index INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS standalone_half_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            UNIQUE(class_id, subject_id)
        )""")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_class ON lesson_assignments(class_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_teacher ON lesson_assignments(teacher_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_class ON scheduled_lessons(class_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_teacher ON scheduled_lessons(teacher_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_week ON scheduled_lessons(week_index)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_unavail_teacher ON teacher_unavailable(teacher_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_tayanch_level ON tayanch_reja(class_level)")
        self.connection.commit()
        print("Ma\'lumotlar bazasi tayyor!")

    def get_setting(self, key, default=None):
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        self.connection.commit()

    def add_class(self, name, level, students_count=0, working_days=6):
        try:
            self.cursor.execute("INSERT INTO classes (name, level, students_count, working_days) VALUES (?, ?, ?, ?)", (name, level, students_count, working_days))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Xatolik: {e}")
            return None

    def update_class(self, class_id, name, level, students_count, working_days):
        self.cursor.execute("UPDATE classes SET name = ?, level = ?, students_count = ?, working_days = ? WHERE id = ?", (name, level, students_count, working_days, class_id))
        self.connection.commit()

    def get_all_classes(self):
        self.cursor.execute("SELECT * FROM classes ORDER BY level, name")
        return self.cursor.fetchall()

    def delete_class(self, class_id):
        self.cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        self.connection.commit()

    def add_subject(self, name, short_name="", difficulty=5):
        try:
            self.cursor.execute("INSERT INTO subjects (name, short_name, difficulty) VALUES (?, ?, ?)", (name, short_name, difficulty))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Xatolik: {e}")
            return None

    def get_all_subjects(self):
        self.cursor.execute("SELECT * FROM subjects ORDER BY name")
        return self.cursor.fetchall()

    def delete_subject(self, subject_id):
        self.cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        self.connection.commit()

    def update_subject(self, subject_id, name, short_name, difficulty):
        self.cursor.execute("UPDATE subjects SET name=?, short_name=?, difficulty=? WHERE id=?", (name, short_name, difficulty, subject_id))
        self.connection.commit()

    def add_teacher(self, full_name, phone="", color="#3498DB", class_teacher_of=None, methodic_day=None, short_name=""):
        try:
            self.cursor.execute("INSERT INTO teachers (full_name, phone, color, class_teacher_of, methodic_day, short_name) VALUES (?, ?, ?, ?, ?, ?)", (full_name, phone, color, class_teacher_of, methodic_day, short_name))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Xatolik: {e}")
            return None

    def get_all_teachers(self):
        self.cursor.execute("SELECT t.*, c.name as class_name FROM teachers t LEFT JOIN classes c ON t.class_teacher_of = c.id ORDER BY t.full_name")
        return self.cursor.fetchall()

    def get_teacher_by_id(self, teacher_id):
        self.cursor.execute("SELECT t.*, c.name as class_name FROM teachers t LEFT JOIN classes c ON t.class_teacher_of = c.id WHERE t.id = ?", (teacher_id,))
        return self.cursor.fetchone()

    def update_teacher(self, teacher_id, full_name, phone, color, class_teacher_of, methodic_day, short_name):
        self.cursor.execute("UPDATE teachers SET full_name = ?, phone = ?, color = ?, class_teacher_of = ?, methodic_day = ?, short_name = ? WHERE id = ?", (full_name, phone, color, class_teacher_of, methodic_day, short_name, teacher_id))
        self.connection.commit()

    def delete_teacher(self, teacher_id):
        self.cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        self.connection.commit()

    def set_teacher_unavailable(self, teacher_id, day, period, availability_type=None):
        try:
            if availability_type is None:
                self.cursor.execute("DELETE FROM teacher_unavailable WHERE teacher_id = ? AND day = ? AND period = ?", (teacher_id, day, period))
            else:
                self.cursor.execute("INSERT OR REPLACE INTO teacher_unavailable (teacher_id, day, period, availability_type) VALUES (?, ?, ?, ?)", (teacher_id, day, period, availability_type))
            self.connection.commit()
        except Exception as e:
            print(f"Xatolik: {e}")

    def get_teacher_unavailable(self, teacher_id):
        self.cursor.execute("SELECT day, period, availability_type FROM teacher_unavailable WHERE teacher_id = ?", (teacher_id,))
        return self.cursor.fetchall()

    def get_teacher_unavailable_count(self, teacher_id):
        self.cursor.execute("SELECT availability_type, COUNT(*) FROM teacher_unavailable WHERE teacher_id = ? GROUP BY availability_type", (teacher_id,))
        results = self.cursor.fetchall()
        counts = {"strict": 0, "soft": 0}
        for row in results:
            counts[row[0]] = row[1]
        return counts

    def clear_teacher_unavailable(self, teacher_id):
        self.cursor.execute("DELETE FROM teacher_unavailable WHERE teacher_id = ?", (teacher_id,))
        self.connection.commit()

    def add_classroom(self, room_number, capacity=None, room_type=None):
        try:
            self.cursor.execute("INSERT INTO classrooms (room_number, capacity, room_type) VALUES (?, ?, ?)", (room_number, capacity, room_type))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Xatolik: {e}")
            return None

    def get_all_classrooms(self):
        self.cursor.execute("SELECT * FROM classrooms ORDER BY room_number")
        return self.cursor.fetchall()

    def delete_classroom(self, classroom_id):
        self.cursor.execute("DELETE FROM classrooms WHERE id = ?", (classroom_id,))
        self.connection.commit()

    def update_classroom(self, classroom_id, room_number, capacity, room_type):
        self.cursor.execute("UPDATE classrooms SET room_number=?, capacity=?, room_type=? WHERE id=?", (room_number, capacity, room_type, classroom_id))
        self.connection.commit()

    def add_lesson_assignment(self, class_id, subject_id, teacher_id, weekly_hours=2, classroom_id=None):
        try:
            self.cursor.execute("INSERT INTO lesson_assignments (class_id, subject_id, teacher_id, weekly_hours, classroom_id) VALUES (?, ?, ?, ?, ?)", (class_id, subject_id, teacher_id, weekly_hours, classroom_id))
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Xatolik: {e}")
            return None

    def update_lesson_assignment(self, assignment_id, class_id, subject_id, teacher_id, weekly_hours, classroom_id=None):
        try:
            self.cursor.execute("UPDATE lesson_assignments SET class_id = ?, subject_id = ?, teacher_id = ?, classroom_id = ?, weekly_hours = ? WHERE id = ?", (class_id, subject_id, teacher_id, classroom_id, weekly_hours, assignment_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Xatolik: {e}")
            return False

    def get_class_assignments(self, class_id):
        self.cursor.execute("SELECT la.id, s.name as subject_name, t.full_name as teacher_name, t.color, la.weekly_hours, s.id as subject_id, t.id as teacher_id, COALESCE(t.short_name, '') as teacher_short FROM lesson_assignments la INNER JOIN subjects s ON la.subject_id = s.id INNER JOIN teachers t ON la.teacher_id = t.id WHERE la.class_id = ? ORDER BY s.name", (class_id,))
        return self.cursor.fetchall()

    def get_teacher_assignments(self, teacher_id):
        self.cursor.execute("SELECT la.id, c.name as class_name, s.name as subject_name, la.weekly_hours, cr.room_number, c.id as class_id, s.id as subject_id, cr.id as classroom_id FROM lesson_assignments la INNER JOIN classes c ON la.class_id = c.id INNER JOIN subjects s ON la.subject_id = s.id LEFT JOIN classrooms cr ON la.classroom_id = cr.id WHERE la.teacher_id = ? ORDER BY c.name, s.name", (teacher_id,))
        return self.cursor.fetchall()

    def get_all_lesson_assignments(self):
        self.cursor.execute("SELECT la.id, c.name as class_name, s.name as subject_name, t.full_name as teacher_name, la.weekly_hours, c.id as class_id, s.id as subject_id, t.id as teacher_id FROM lesson_assignments la INNER JOIN classes c ON la.class_id = c.id INNER JOIN subjects s ON la.subject_id = s.id INNER JOIN teachers t ON la.teacher_id = t.id ORDER BY c.name, s.name")
        return self.cursor.fetchall()

    def delete_lesson_assignment(self, assignment_id):
        self.cursor.execute("DELETE FROM lesson_assignments WHERE id = ?", (assignment_id,))
        self.connection.commit()

    def save_scheduled_lessons(self, timetable_data, week_index=0):
        self.cursor.execute("DELETE FROM scheduled_lessons WHERE week_index = ?", (week_index,))
        for (class_id, day, period), info in timetable_data.items():
            self.cursor.execute("INSERT INTO scheduled_lessons (class_id, day, period, lesson_id, subject_name, teacher_name, teacher_id, color, week_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (class_id, day, period, info.get("lesson_id"), info.get("subject_name"), info.get("teacher_name"), info.get("teacher_id"), info.get("color"), week_index))
        self.connection.commit()

    def load_scheduled_lessons(self, week_index=None):
        if week_index is not None:
            self.cursor.execute("SELECT sl.*, COALESCE(s.short_name, '') as subject_short, COALESCE(t.short_name, '') as teacher_short FROM scheduled_lessons sl LEFT JOIN subjects s ON sl.subject_name = s.name LEFT JOIN teachers t ON sl.teacher_id = t.id WHERE sl.week_index = ?", (week_index,))
        else:
            self.cursor.execute("SELECT sl.*, COALESCE(s.short_name, '') as subject_short, COALESCE(t.short_name, '') as teacher_short FROM scheduled_lessons sl LEFT JOIN subjects s ON sl.subject_name = s.name LEFT JOIN teachers t ON sl.teacher_id = t.id")
        rows = self.cursor.fetchall()
        timetable = {}
        for row in rows:
            key = (row[1], row[2], row[3])
            timetable[key] = {
                "lesson_id": row[4], "subject_name": row[5], "teacher_name": row[6],
                "teacher_id": row[7], "color": row[8], "class_id": row[1],
                "subject_short": row[11] if len(row) > 11 else "",
                "teacher_short": row[12] if len(row) > 12 else "",
                "week_index": row[10] if len(row) > 10 else 0,
            }
        return timetable

    def clear_scheduled_lessons(self):
        self.cursor.execute("DELETE FROM scheduled_lessons")
        self.connection.commit()

    def clear_classes(self):
        self.cursor.execute("DELETE FROM scheduled_lessons")
        self.cursor.execute("DELETE FROM lesson_assignments")
        self.cursor.execute("DELETE FROM classes")
        self.connection.commit()

    def clear_subjects(self):
        self.cursor.execute("PRAGMA foreign_keys = OFF")
        self.cursor.execute("DELETE FROM scheduled_lessons")
        self.cursor.execute("DELETE FROM subjects")
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.connection.commit()

    def clear_subjects_keep_assignments(self):
        self.cursor.execute("DELETE FROM scheduled_lessons")
        self.connection.commit()

    def clear_teachers(self):
        self.cursor.execute("DELETE FROM scheduled_lessons")
        self.cursor.execute("DELETE FROM lesson_assignments")
        self.cursor.execute("DELETE FROM teacher_unavailable")
        self.cursor.execute("DELETE FROM teachers")
        self.connection.commit()

    def clear_classrooms(self):
        self.cursor.execute("DELETE FROM lesson_assignments")
        self.cursor.execute("DELETE FROM classrooms")
        self.connection.commit()

    def clear_lesson_assignments(self):
        self.cursor.execute("DELETE FROM scheduled_lessons")
        self.cursor.execute("DELETE FROM lesson_assignments")
        self.connection.commit()

    def clear_teacher_unavailable_all(self):
        self.cursor.execute("DELETE FROM teacher_unavailable")
        self.connection.commit()

    def save_tayanch_reja(self, data, pdf_source=""):
        self.cursor.execute("DELETE FROM tayanch_reja")
        for idx, item in enumerate(data):
            self.cursor.execute("INSERT INTO tayanch_reja (subject_name, subject_short, class_level, weekly_hours, pdf_source, order_index) VALUES (?, ?, ?, ?, ?, ?)", (item.get("subject_name", ""), item.get("subject_short", ""), item.get("class_level", 0), item.get("weekly_hours", 0), pdf_source, idx))
        self.connection.commit()

    def load_tayanch_reja(self):
        self.cursor.execute("SELECT subject_name, subject_short, class_level, weekly_hours, pdf_source, order_index FROM tayanch_reja ORDER BY order_index, class_level")
        rows = self.cursor.fetchall()
        return [{"subject_name": r[0], "subject_short": r[1], "class_level": r[2], "weekly_hours": r[3], "pdf_source": r[4]} for r in rows]

    def get_tayanch_hours(self, class_level, subject_name):
        self.cursor.execute("SELECT weekly_hours FROM tayanch_reja WHERE class_level = ? AND subject_name = ? LIMIT 1", (class_level, subject_name))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_tayanch_reja_subjects(self):
        self.cursor.execute("SELECT DISTINCT subject_name, subject_short FROM tayanch_reja ORDER BY subject_name")
        return self.cursor.fetchall()

    def clear_tayanch_reja(self):
        self.cursor.execute("DELETE FROM tayanch_reja")
        self.connection.commit()

    def get_standalone_half_subjects(self, class_id):
        self.cursor.execute("SELECT sh.subject_id, s.name FROM standalone_half_subjects sh JOIN subjects s ON sh.subject_id = s.id WHERE sh.class_id = ?", (class_id,))
        return self.cursor.fetchall()

    def save_standalone_half_subjects(self, class_id, subject_ids):
        self.cursor.execute("DELETE FROM standalone_half_subjects WHERE class_id = ?", (class_id,))
        for subject_id in subject_ids:
            self.cursor.execute("INSERT INTO standalone_half_subjects (class_id, subject_id) VALUES (?, ?)", (class_id, subject_id))
        self.connection.commit()

    def get_fractional_subjects(self, class_id):
        assignments = self.get_class_assignments(class_id)
        fractional = []
        for a in assignments:
            subject_id = a[5]
            subject_name = a[1]
            weekly_hours = a[4]
            if weekly_hours != int(weekly_hours):
                fractional.append({"subject_id": subject_id, "subject_name": subject_name, "weekly_hours": weekly_hours, "is_half": weekly_hours < 1})
        return fractional

    def clear_all(self):
        self.cursor.execute("DELETE FROM scheduled_lessons")
        self.cursor.execute("DELETE FROM lesson_assignments")
        self.cursor.execute("DELETE FROM teacher_unavailable")
        self.cursor.execute("DELETE FROM teachers")
        self.cursor.execute("DELETE FROM classrooms")
        self.cursor.execute("DELETE FROM classes")
        self.cursor.execute("DELETE FROM subjects")
        self.cursor.execute("DELETE FROM tayanch_reja")
        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
