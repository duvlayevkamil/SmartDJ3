"""
Exporter unit testlari
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exporter import build_html, KUNLAR, KUN_QISQA, PERIODS_PER_DAY


class TestExporter:
    """Exporter funksiyalarining testlari"""

    def setup_method(self):
        """Test data"""
        self.classes = [
            (1, "1-A", 1, 30, 6),
            (2, "1-B", 1, 28, 6),
            (3, "2-A", 2, 30, 6),
        ]
        self.timetable = {}
        # 1-A sinfi uchun darslar
        for day in range(6):
            for period in range(PERIODS_PER_DAY):
                key = (1, day, period)
                self.timetable[key] = {
                    'subject_name': 'Matematika',
                    'subject_short': 'Mat',
                    'teacher_name': 'Karimov A',
                    'teacher_short': 'KA',
                    'class_name': '1-A',
                    'color': '#3498DB',
                }

    # ================================================================
    # BUILD HTML
    # ================================================================

    def test_build_html_returns_string(self):
        """HTML qaytaradi"""
        html = build_html(self.timetable, self.classes)
        assert isinstance(html, str)

    def test_build_html_containsDOCTYPE(self):
        """HTML DOCTYPE mavjud"""
        html = build_html(self.timetable, self.classes)
        assert "<!DOCTYPE html>" in html

    def test_build_html_contains_title(self):
        """HTML sarlavha mavjud"""
        html = build_html(self.timetable, self.classes)
        assert "DARS JADVALI" in html

    def test_build_html_contains_class_names(self):
        """HTML sinf nomlarini o'z ichiga oladi"""
        html = build_html(self.timetable, self.classes)
        assert "1-A" in html

    def test_build_html_umumiy(self):
        """Umumiy jadval"""
        html = build_html(self.timetable, self.classes, etype='umumiy')
        assert "1-A" in html

    def test_build_html_sinf(self):
        """Sinf bo'yicha jadval"""
        html = build_html(self.timetable, self.classes, etype='sinf', eid=1, ename="1-A")
        assert "1-A" in html

    def test_build_html_with_school(self):
        """Maktab nomi bilan"""
        html = build_html(self.timetable, self.classes, school="Test Maktab")
        assert "Test Maktab" in html

    def test_build_html_font_size(self):
        """Shrift o'lchami"""
        html = build_html(self.timetable, self.classes, fs=10)
        assert "10pt" in html

    # ================================================================
    # CONSTANTS
    # ================================================================

    def test_kunlar(self):
        """Kunlar ro'yxati"""
        assert len(KUNLAR) == 6
        assert "Dushanba" in KUNLAR

    def test_kun_qisqa(self):
        """Qisqa kunlar"""
        assert len(KUN_QISQA) == 6

    def test_periods_per_day(self):
        """PERIODS_PER_DAY = 6"""
        assert PERIODS_PER_DAY == 6


# ================================================================
# Pytest uchun
# ================================================================
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
