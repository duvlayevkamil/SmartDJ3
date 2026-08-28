"""
DatabaseManager unit testlari
"""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager


class TestDatabaseManager:
    """DatabaseManager sinfining testlari"""

    def setup_method(self):
        """Har bir testdan oldin yangi vaqtinchalik baza"""
        self.db = DatabaseManager()
        # Vaqtinchalik baza fayli
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db.db_name = self.temp_db.name
        self.db.connection = None
        self.db.initialize()

    def teardown_method(self):
        """Testdan keyin tozalash"""
        try:
            if self.db.connection:
                self.db.connection.close()
                self.db.connection = None
            import time
            time.sleep(0.1)  # Windows uchun kutish
            if os.path.exists(self.temp_db.name):
                os.unlink(self.temp_db.name)
        except Exception:
            pass

    # ================================================================
    # SINFLAR
    # ================================================================

    def test_add_class(self):
        """Sinf qo'shish"""
        result = self.db.add_class("1-A", 1, 30)
        assert result is not None

    def test_get_all_classes(self):
        """Barcha sinflar"""
        self.db.add_class("1-A", 1, 30)
        self.db.add_class("2-A", 2, 28)
        classes = self.db.get_all_classes()
        assert len(classes) == 2

    def test_update_class(self):
        """Sinfni yangilash"""
        cid = self.db.add_class("1-A", 1, 30)
        self.db.update_class(cid, "1-B", 1, 25)
        classes = self.db.get_all_classes()
        assert classes[0][1] == "1-B"

    def test_delete_class(self):
        """Sinfni o'chirish"""
        cid = self.db.add_class("1-A", 1, 30)
        self.db.delete_class(cid)
        classes = self.db.get_all_classes()
        assert len(classes) == 0

    # ================================================================
    # FANLAR
    # ================================================================

    def test_add_subject(self):
        """Fan qo'shish"""
        result = self.db.add_subject("Matematika", "Mat", 5)
        assert result is not None

    def test_get_all_subjects(self):
        """Barcha fanlar"""
        self.db.add_subject("Matematika", "Mat", 5)
        self.db.add_subject("Fizika", "Fiz", 8)
        subjects = self.db.get_all_subjects()
        assert len(subjects) == 2

    def test_update_subject(self):
        """Fanni yangilash"""
        sid = self.db.add_subject("Matematika", "Mat", 5)
        self.db.update_subject(sid, "Algebra", "Alg", 9)
        subjects = self.db.get_all_subjects()
        assert subjects[0][1] == "Algebra"

    def test_delete_subject(self):
        """Fanni o'chirish"""
        sid = self.db.add_subject("Matematika", "Mat", 5)
        self.db.delete_subject(sid)
        subjects = self.db.get_all_subjects()
        assert len(subjects) == 0

    # ================================================================
    # O'QITUVCHILAR
    # ================================================================

    def test_add_teacher(self):
        """O'qituvchi qo'shish"""
        result = self.db.add_teacher("Karimov A", "123456789", "#3498DB")
        assert result is not None

    def test_get_all_teachers(self):
        """Barcha o'qituvchilar"""
        self.db.add_teacher("Karimov A")
        self.db.add_teacher("Aliyev B")
        teachers = self.db.get_all_teachers()
        assert len(teachers) == 2

    def test_update_teacher(self):
        """O'qituvchini yangilash"""
        tid = self.db.add_teacher("Karimov A")
        self.db.update_teacher(tid, "Karimov A.", "123", "#FF0000", None, None)
        teachers = self.db.get_all_teachers()
        assert teachers[0][1] == "Karimov A."

    def test_delete_teacher(self):
        """O'qituvchini o'chirish"""
        tid = self.db.add_teacher("Karimov A")
        self.db.delete_teacher(tid)
        teachers = self.db.get_all_teachers()
        assert len(teachers) == 0

    # ================================================================
    # XONALAR
    # ================================================================

    def test_add_classroom(self):
        """Xona qo'shish"""
        result = self.db.add_classroom("101", 30, "Oddiy")
        assert result is not None

    def test_get_all_classrooms(self):
        """Barcha xonalar"""
        self.db.add_classroom("101")
        self.db.add_classroom("102")
        classrooms = self.db.get_all_classrooms()
        assert len(classrooms) == 2

    def test_update_classroom(self):
        """Xonani yangilash"""
        rid = self.db.add_classroom("101", 30, "Oddiy")
        self.db.update_classroom(rid, "102", 35, "Laboratoriya")
        classrooms = self.db.get_all_classrooms()
        assert classrooms[0][1] == "102"

    def test_delete_classroom(self):
        """Xonani o'chirish"""
        rid = self.db.add_classroom("101")
        self.db.delete_classroom(rid)
        classrooms = self.db.get_all_classrooms()
        assert len(classrooms) == 0

    # ================================================================
    # DARS BIRIKTIRISH
    # ================================================================

    def test_add_lesson_assignment(self):
        """Dars biriktirish"""
        cid = self.db.add_class("1-A", 1, 30)
        sid = self.db.add_subject("Matematika", "Mat", 5)
        tid = self.db.add_teacher("Karimov A")
        result = self.db.add_lesson_assignment(cid, sid, tid, 5)
        assert result is True

    def test_get_class_assignments(self):
        """Sinfning darslari"""
        cid = self.db.add_class("1-A", 1, 30)
        sid = self.db.add_subject("Matematika", "Mat", 5)
        tid = self.db.add_teacher("Karimov A")
        self.db.add_lesson_assignment(cid, sid, tid, 5)
        assignments = self.db.get_class_assignments(cid)
        assert len(assignments) == 1

    def test_delete_lesson_assignment(self):
        """Dars biriktirishni o'chirish"""
        cid = self.db.add_class("1-A", 1, 30)
        sid = self.db.add_subject("Matematika", "Mat", 5)
        tid = self.db.add_teacher("Karimov A")
        self.db.add_lesson_assignment(cid, sid, tid, 5)
        assignments = self.db.get_class_assignments(cid)
        aid = assignments[0][0]
        self.db.delete_lesson_assignment(aid)
        assignments = self.db.get_class_assignments(cid)
        assert len(assignments) == 0

    # ================================================================
    # SOZLAMALAR
    # ================================================================

    def test_set_setting(self):
        """Sozlama saqlash"""
        self.db.set_setting("test_key", "test_value")
        value = self.db.get_setting("test_key")
        assert value == "test_value"

    def test_get_setting_default(self):
        """Default qiymat"""
        value = self.db.get_setting("nonexistent", "default")
        assert value == "default"

    # ================================================================
    # TOZALASH
    # ================================================================

    def test_clear_all(self):
        """Barcha jadvallarni tozalash"""
        self.db.add_class("1-A", 1, 30)
        self.db.add_subject("Matematika")
        self.db.add_teacher("Karimov A")
        self.db.clear_all()
        assert len(self.db.get_all_classes()) == 0
        assert len(self.db.get_all_subjects()) == 0
        assert len(self.db.get_all_teachers()) == 0

    # ================================================================
    # BAND SOATLAR
    # ================================================================

    def test_set_teacher_unavailable(self):
        """O'qituvchi band soati"""
        tid = self.db.add_teacher("Karimov A")
        self.db.set_teacher_unavailable(tid, 0, 0, 'strict')
        unavailable = self.db.get_teacher_unavailable(tid)
        assert len(unavailable) == 1

    def test_clear_teacher_unavailable(self):
        """Band soatlarni tozalash"""
        tid = self.db.add_teacher("Karimov A")
        self.db.set_teacher_unavailable(tid, 0, 0, 'strict')
        self.db.clear_teacher_unavailable(tid)
        unavailable = self.db.get_teacher_unavailable(tid)
        assert len(unavailable) == 0


# ================================================================
# Pytest uchun
# ================================================================
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
