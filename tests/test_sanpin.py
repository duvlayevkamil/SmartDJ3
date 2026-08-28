"""
SanPINChecker unit testlari
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sanpin import SanPINChecker, PERIODS_PER_DAY


class TestSanPINChecker:
    """SanPINChecker sinfining asosiy testlari"""

    def setup_method(self):
        """Har bir testdan oldin yangi instansiya"""
        self.checker = SanPINChecker()

    # ================================================================
    # INITSIALIZATSIYA
    # ================================================================

    def test_max_daily_lessons_keys(self):
        """max_daily_lessons 1-11 sinflar uchun to'liq"""
        for level in range(1, 12):
            assert level in self.checker.max_daily_lessons

    def test_max_weekly_lessons_keys(self):
        """max_weekly_lessons 1-11 sinflar uchun to'liq"""
        for level in range(1, 12):
            assert level in self.checker.max_weekly_lessons

    def test_difficulty_not_empty(self):
        """difficulty ro'yxati bo'sh emas"""
        assert len(self.checker.difficulty) > 0

    def test_hard_subjects_list(self):
        """Qiyin fanlar ro'yxati mavjud"""
        assert "Matematika" in self.checker.hard_subjects
        assert "Fizika" in self.checker.hard_subjects

    def test_easy_subjects_list(self):
        """Yengil fanlar ro'yxati mavjud"""
        assert "Musiqa" in self.checker.easy_subjects
        assert "Sport" in self.checker.easy_subjects

    # ================================================================
    # GET_DIFFICULTY
    # ================================================================

    def test_get_difficulty_known_subject(self):
        """Ma'lum fan uchun qiyinlik"""
        assert self.checker.get_difficulty("Matematika") == 12
        assert self.checker.get_difficulty("Fizika") == 13

    def test_get_difficulty_unknown_subject(self):
        """Noma'lum fan uchun default qiyinlik"""
        assert self.checker.get_difficulty("Nomalum_fan") == 5

    # ================================================================
    # GET_OPTIMAL_PERIOD
    # ================================================================

    def test_get_optimal_period_hard_subject(self):
        """Qiyin fan uchun optimal davrlar — 2, 3"""
        periods = self.checker.get_optimal_period("Matematika")
        assert 2 in periods
        assert 3 in periods

    def test_get_optimal_period_easy_subject(self):
        """Yengil fan uchun optimal davrlar — oxirgi"""
        periods = self.checker.get_optimal_period("Musiqa")
        assert 5 in periods or 6 in periods

    # ================================================================
    # CHECK_TIMETABLE — MUVAFFAQIYATLI HOLAT
    # ================================================================

    def test_empty_timetable(self):
        """Bo'sh jadval — xato yo'q"""
        timetable = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        result = self.checker.check_timetable(timetable, 5)
        assert result['is_valid'] is True
        assert result['score'] == 100
        assert len(result['errors']) == 0

    def test_valid_timetable(self):
        """To'g'ri jadval — ball yuqori"""
        timetable = [
            ["Ona tili", "Matematika", "Tarix", "Biologiya", "Musiqa", "Sport"],
            ["Matematika", "Tarix", "Ona tili", "Kimyo", "Tarix", "Adabiyot"],
            ["Biologiya", "Ingliz tili", "Matematika", "Tarix", "Biologiya", "Sport"],
            ["Tarix", "Matematika", "Biologiya", "Ingliz tili", "Tarix", "Musiqa"],
            ["Musiqa", "Tarix", "Ingliz tili", "Matematika", "Biologiya", "Sport"],
            ["", "", "", "", "", ""],
        ]
        result = self.checker.check_timetable(timetable, 5)
        assert result['total_lessons'] == 30

    # ================================================================
    # CHECK_TIMETABLE — XATOLAR
    # ================================================================

    def test_too_many_weekly_lessons(self):
        """Haftalik ortiqcha dars — xato"""
        # 5-sinf uchun max 30 soat, lekin 40 qo'yamiz
        timetable = [
            ["Matematika"] * 6,
            ["Fizika"] * 6,
            ["Kimyo"] * 6,
            ["Ingliz tili"] * 6,
            ["Tarix"] * 6,
            ["Biologiya"] * 6,
            ["Geografiya"] * 5,
        ]
        result = self.checker.check_timetable(timetable, 5)
        assert result['is_valid'] is False
        assert any("Haftalik" in e for e in result['errors'])

    def test_too_many_daily_lessons(self):
        """Kunlik ortiqcha dars — xato"""
        timetable = [
            ["Matematika", "Fizika", "Kimyo", "Ingliz tili", "Tarix", "Biologiya"],
            ["Matematika", "Fizika", "Kimyo", "Ingliz tili", "Tarix", "Biologiya"],
            ["Matematika", "Fizika", "Kimyo", "Ingliz tili", "Tarix", "Biologiya"],
            ["Matematika", "Fizika", "Kimyo", "Ingliz tili", "Tarix", "Biologiya"],
            ["Matematika", "Fizika", "Kimyo", "Ingliz tili", "Tarix", "Biologiya"],
            ["Matematika", "Fizika", "Kimyo", "Ingliz tili", "Tarix", "Biologiya"],
            ["Matematika", "Fizika", "Kimyo", "Ingliz tili", "Tarix", "Biologiya"],
        ]
        # 1-sinf uchun max 4 soat/kun
        result = self.checker.check_timetable(timetable, 1)
        assert result['is_valid'] is False

    def test_consecutive_same_subject_grade1(self):
        """1-4 sinflarda ketma-ket bir xil fan — xato"""
        timetable = [
            ["Matematika", "", "", "", "", ""],
            ["Matematika", "", "", "", "", ""],  # ketma-ket
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
        ]
        result = self.checker.check_timetable(timetable, 2)
        assert any("ketma-ket" in e for e in result['errors'])

    def test_gap_detection(self):
        """Oyna (bo'sh dars orasida) — xato"""
        timetable = [
            ["Matematika", "", "", "", "", ""],
            ["", "", "", "", "", ""],  # bo'sh
            ["Fizika", "", "", "", "", ""],  # keyin dars
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
        ]
        result = self.checker.check_timetable(timetable, 5)
        assert any("oyna" in e.lower() for e in result['errors'])

    # ================================================================
    # CHECK_TIMETABLE — OGOHLANTIRISHLAR
    # ================================================================

    def test_consecutive_hard_subjects(self):
        """Ketma-ket qiyin fanlar — ogohlantirish"""
        timetable = [
            ["Matematika", "", "", "", "", ""],
            ["Fizika", "", "", "", "", ""],  # ketma-ket qiyin
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
        ]
        result = self.checker.check_timetable(timetable, 8)
        assert any("ketma-ket qiyin" in w for w in result['warnings'])

    def test_sport_before_hard_subject(self):
        """Sportdan keyin qiyin fan — ogohlantirish"""
        timetable = [
            ["Sport", "", "", "", "", ""],
            ["Matematika", "", "", "", "", ""],  # sportdan keyin qiyin
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
        ]
        result = self.checker.check_timetable(timetable, 8)
        assert any("Sport" in w for w in result['warnings'])

    # ================================================================
    # CHECK_TIMETABLE — TAYANCH REJA BILAN
    # ================================================================

    def test_tayanch_hours_override(self):
        """Tayanch reja bo'yicha limit oshiriladi"""
        timetable = [
            ["Matematika", "Matematika", "Matematika", "Matematika", "Matematika", ""],
            ["Matematika", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
        ]
        # Tayanch reja: Matematika 6 soat/hafta
        tayanch = {"Matematika": 6}
        result = self.checker.check_timetable(timetable, 5, tayanch_hours=tayanch)
        # Tayanch reja bo'yicha 6 soat ruxsat etiladi
        assert result['total_lessons'] == 6

    # ================================================================
    # CACHE
    # ================================================================

    def test_cache_returns_copy(self):
        """Cache dan olingan natija nusxa bo'lishi kerak"""
        timetable = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        r1 = self.checker.check_timetable(timetable, 5)
        r2 = self.checker.check_timetable(timetable, 5)
        # Ikkala natija bir xil, lekin alohida obyektlar
        assert r1['score'] == r2['score']
        r1['errors'].append("test")
        assert "test" not in r2['errors']

    def test_clear_cache(self):
        """Cache tozalash"""
        timetable = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        self.checker.check_timetable(timetable, 5)
        assert len(self.checker._fitness_cache) > 0
        self.checker.clear_cache()
        assert len(self.checker._fitness_cache) == 0

    # ================================================================
    # HELPER METHODS
    # ================================================================

    def test_timetable_hash(self):
        """Hash bir xil jadval uchun bir xil"""
        t1 = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        t2 = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        assert self.checker._timetable_hash(t1, 5) == self.checker._timetable_hash(t2, 5)

    def test_timetable_hash_different(self):
        """Hash farqli jadval uchun farqli"""
        t1 = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        t2 = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        t2[0][0] = "Matematika"
        assert self.checker._timetable_hash(t1, 5) != self.checker._timetable_hash(t2, 5)


# ================================================================
# Pytest uchun
# ================================================================
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
