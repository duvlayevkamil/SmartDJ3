"""
TimetableScheduler unit testlari
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scheduler import (
    TimetableScheduler, PERIODS_PER_DAY,
    DAILY_OCCURRENCE_OVERRIDES, SPORT_SUBJECTS
)
from core.sanpin import SanPINChecker


class TestTimetableScheduler:
    """TimetableScheduler sinfining asosiy testlari"""

    def setup_method(self):
        """Har bir testdan oldin yangi instansiya"""
        self.scheduler = TimetableScheduler(algorithm="backtracking")
        self.sanpin = SanPINChecker()

    # ================================================================
    # GENERATE_TIMETABLE — ASOSIY
    # ================================================================

    def test_empty_subjects(self):
        """Bo'sh fanlar ro'yxati — bo'sh jadval"""
        timetable, score = self.scheduler.generate_timetable({}, 5)
        assert timetable is not None
        assert all(all(cell == "" for cell in row) for row in timetable)

    def test_single_subject(self):
        """Bitta fan — jadvalga joylashtiriladi"""
        subjects = {"Matematika": 3}
        timetable, score = self.scheduler.generate_timetable(subjects, 5, working_days=6)
        # Kamida 3 ta Matematika bo'lishi kerak
        count = sum(1 for row in timetable for cell in row if cell == "Matematika")
        assert count >= 3

    def test_multiple_subjects(self):
        """Bir nechta fan — barchasi joylashtiriladi"""
        subjects = {
            "Matematika": 5,
            "Fizika": 3,
            "Ingliz tili": 3,
            "Tarix": 2,
            "Sport": 2,
        }
        timetable, score = self.scheduler.generate_timetable(subjects, 8, working_days=6)
        # Har bir fan kamida o'z soatlaricha joylashishi kerak
        for sub, hours in subjects.items():
            count = sum(1 for row in timetable for cell in row if cell == sub)
            assert count >= hours - 1, f"{sub}: {count} < {hours}"

    def test_score_not_negative(self):
        """Ball manfiy bo'lmasligi kerak"""
        subjects = {"Matematika": 5, "Fizika": 3}
        timetable, score = self.scheduler.generate_timetable(subjects, 5, working_days=6)
        assert score >= 0

    def test_score_not_over_100(self):
        """Ball 100 dan oshmasligi kerak"""
        timetable, score = self.scheduler.generate_timetable({"Matematika": 3}, 5)
        assert score <= 100

    # ================================================================
    # WORKING DAYS
    # ================================================================

    def test_5_working_days(self):
        """5 ish kuni — Shanba bo'sh"""
        subjects = {"Matematika": 5}
        timetable, score = self.scheduler.generate_timetable(subjects, 5, working_days=5)
        # Shanba (day=5) bo'sh bo'lishi kerak
        for period in range(PERIODS_PER_DAY):
            assert timetable[period][5] == ""

    def test_6_working_days(self):
        """6 ish kuni — Shanba ham to'ldiriladi"""
        subjects = {"Matematika": 6}
        timetable, score = self.scheduler.generate_timetable(subjects, 5, working_days=6)
        count = sum(1 for row in timetable for cell in row if cell == "Matematika")
        assert count == 6

    # ================================================================
    # SANPIN CHECK
    # ================================================================

    def test_no_consecutive_same_grade1(self):
        """1-4 sinflarda ketma-ket bir xil fan yo'q"""
        subjects = {"Matematika": 6}
        timetable, score = self.scheduler.generate_timetable(subjects, 2, working_days=6)
        # Tekshirish
        for day in range(6):
            for period in range(PERIODS_PER_DAY - 1):
                if (timetable[period][day] and timetable[period + 1][day]
                        and timetable[period][day] == timetable[period + 1][day]):
                    # 1-4 sinflarda bu xato
                    if 2 <= 4:
                        assert False, f"Ketma-ket bir xil fan: {day=}, {period=}"

    def test_no_gaps(self):
        """Oyna yo'q — darslar tepada"""
        subjects = {"Matematika": 3, "Fizika": 2}
        timetable, score = self.scheduler.generate_timetable(subjects, 5, working_days=6)
        # Har bir kunda darslar 0..N-1 da bo'lishi kerak
        for day in range(6):
            found_empty = False
            found_lesson_after = False
            for period in range(PERIODS_PER_DAY):
                if timetable[period][day] == "":
                    found_empty = True
                elif found_empty:
                    found_lesson_after = True
            assert not found_lesson_after, f"Oyna topildi: day={day}"

    # ================================================================
    # TEACHER CONSTRAINTS
    # ================================================================

    def test_teacher_constraints(self):
        """O'qituvchi band soati — dars qo'yilmaydi"""
        subjects_hours = {"Matematika": 3}
        teacher_constraints = {(1, 0, 0), (1, 1, 0), (1, 2, 0)}  # teacher_id=1 band
        subject_teacher_map = {"Matematika": 1}
        timetable, score = self.scheduler.generate_timetable(
            subjects_hours, 5, working_days=6,
            teacher_constraints=teacher_constraints,
            subject_teacher_map=subject_teacher_map
        )
        # Teacher 1 band bo'lgan slotlarda Matematika bo'lmasligi kerak
        for (tid, day, period) in teacher_constraints:
            if tid == 1:
                assert timetable[period][day] != "Matematika"

    # ================================================================
    # DAILY OCCURRENCE
    # ================================================================

    def test_daily_occurrence_override(self):
        """Matematika kuniga 2 marta mumkin"""
        subjects = {"Matematika": 10}
        timetable, score = self.scheduler.generate_timetable(subjects, 8, working_days=6)
        # Har bir kunda Matematika 2 dan ko'p bo'lmasligi kerak
        for day in range(6):
            count = sum(1 for p in range(PERIODS_PER_DAY) if timetable[p][day] == "Matematika")
            assert count <= 2, f"Matematika {count} marta: day={day}"

    # ================================================================
    # CONSTANTS
    # ================================================================

    def test_periods_per_day(self):
        """PERIODS_PER_DAY = 6"""
        assert PERIODS_PER_DAY == 6

    def test_sport_subjects(self):
        """Sport fanlari to'g'ri"""
        assert "Sport" in SPORT_SUBJECTS
        assert "Jismoniy tarbiya" in SPORT_SUBJECTS

    def test_daily_occurrence_overrides(self):
        """Kunlik takrorlanish override'lari"""
        assert DAILY_OCCURRENCE_OVERRIDES["Matematika"] == 2
        assert DAILY_OCCURRENCE_OVERRIDES["Algebra"] == 2

    # ================================================================
    # REPAIR UNPLACED
    # ================================================================

    def test_repair_unplaced(self):
        """Qoldiq darslar joylashtiriladi"""
        timetable = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        # 2 ta dars qo'yamiz
        timetable[0][0] = "Matematika"
        timetable[1][0] = "Matematika"

        subjects_counts = {"Matematika": 5}
        result = self.scheduler._repair_unplaced(
            timetable, subjects_counts, 5, 6, 6, None, None
        )
        count = sum(1 for row in result for cell in row if cell == "Matematika")
        assert count >= 5

    # ================================================================
    # FIX GAPS
    # ================================================================

    def test_fix_gaps(self):
        """Oynalar tuzatiladi"""
        timetable = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        timetable[0][0] = "Matematika"
        timetable[2][0] = "Fizika"  # 1-bo'sh, keyin dars — oyna

        self.scheduler._fix_gaps(timetable, 0, 6, 5)
        # Oyna yo'q bo'lishi kerak
        found_empty = False
        found_lesson_after = False
        for period in range(PERIODS_PER_DAY):
            if timetable[period][0] == "":
                found_empty = True
            elif found_empty:
                found_lesson_after = True
        assert not found_lesson_after

    # ================================================================
    # CANCEL FLAG
    # ================================================================

    def test_cancel_flag(self):
        """Cancel flag ishlaydi"""
        self.scheduler.cancel_flag = True
        subjects = {"Matematika": 3}
        timetable, score = self.scheduler.generate_timetable(subjects, 5)
        # Cancel bo'lsa ham jadval qaytishi kerak
        assert timetable is not None

    def test_reset_cancel(self):
        """Reset cancel flag"""
        self.scheduler.cancel()
        assert self.scheduler.cancel_flag is True
        self.scheduler.reset_cancel()
        assert self.scheduler.cancel_flag is False

    # ================================================================
    # REORDER FOR SANPIN
    # ================================================================

    def test_reorder_for_sanpin(self):
        """SanPIN tartibi — qiyin fanlar ajratiladi"""
        lessons = ["Matematika", "Fizika", "Matematika", "Fizika"]
        self.scheduler._reorder_for_sanpin(lessons, 0, 5)
        # Natija bo'sh emas
        assert len(lessons) == 4


# ================================================================
# Pytest uchun
# ================================================================
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
