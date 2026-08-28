"""
BRKGAScheduler unit testlari
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brkga import BRKGAScheduler, PERIODS_PER_DAY


class TestBRKGAScheduler:
    """BRKGAScheduler sinfining testlari"""

    def setup_method(self):
        self.scheduler = BRKGAScheduler(
            population_size=10,
            generations=5,
            early_stop_score=85,
            early_stop_patience=3
        )

    # ================================================================
    # INITSIALIZATSIYA
    # ================================================================

    def test_init_default(self):
        """Default qiymatlar"""
        s = BRKGAScheduler()
        assert s.population_size == 60
        assert s.generations == 150
        assert s.early_stop_score == 95

    def test_init_custom(self):
        """Maxsus qiymatlar"""
        s = BRKGAScheduler(population_size=20, generations=10)
        assert s.population_size == 20
        assert s.generations == 10

    def test_cancel_flag(self):
        """Cancel flag"""
        assert self.scheduler.cancel_flag is False
        self.scheduler.cancel_flag = True
        assert self.scheduler.cancel_flag is True

    # ================================================================
    # FAST GREEDY
    # ================================================================

    def test_fast_greedy_empty(self):
        """Bo'sh fanlar — bo'sh jadval"""
        timetable, score = self.scheduler._fast_greedy(
            {}, 5, 6, 6, None, None
        )
        assert all(all(cell == "" for cell in row) for row in timetable)

    def test_fast_greedy_single_subject(self):
        """Bitta fan — jadvalga joylashtiriladi"""
        timetable, score = self.scheduler._fast_greedy(
            {"Matematika": 3}, 5, 6, 6, None, None
        )
        count = sum(1 for row in timetable for cell in row if cell == "Matematika")
        assert count >= 3

    def test_fast_greedy_score(self):
        """Fast greedy balli 0-100 oralig'ida"""
        timetable, score = self.scheduler._fast_greedy(
            {"Matematika": 5, "Fizika": 3}, 8, 6, 6, None, None
        )
        assert 0 <= score <= 100

    # ================================================================
    # GENERATE TIMETABLE
    # ================================================================

    def test_generate_empty(self):
        """Bo'sh fanlar — bo'sh jadval"""
        timetable, score = self.scheduler.generate_timetable({}, 5)
        assert timetable is not None
        assert all(all(cell == "" for cell in row) for row in timetable)

    def test_generate_single_subject(self):
        """Bitta fan"""
        timetable, score = self.scheduler.generate_timetable(
            {"Matematika": 3}, 5, working_days=6
        )
        count = sum(1 for row in timetable for cell in row if cell == "Matematika")
        assert count >= 3

    def test_generate_multiple_subjects(self):
        """Bir nechta fan"""
        timetable, score = self.scheduler.generate_timetable(
            {"Matematika": 5, "Fizika": 3, "Ingliz tili": 3}, 8, working_days=6
        )
        assert timetable is not None
        # Har bir fan kamida 1 marta bo'lishi kerak
        for sub in ["Matematika", "Fizika", "Ingliz tili"]:
            count = sum(1 for row in timetable for cell in row if cell == sub)
            assert count >= 1

    def test_generate_score_range(self):
        """Ball 0-100 oralig'ida"""
        timetable, score = self.scheduler.generate_timetable(
            {"Matematika": 5, "Fizika": 3}, 8
        )
        assert 0 <= score <= 100

    def test_generate_working_days(self):
        """5 ish kuni — Shanba bo'sh"""
        timetable, score = self.scheduler.generate_timetable(
            {"Matematika": 5}, 5, working_days=5
        )
        for period in range(PERIODS_PER_DAY):
            assert timetable[period][5] == ""

    def test_generate_6_working_days(self):
        """6 ish kuni — Shanba to'ldiriladi"""
        timetable, score = self.scheduler.generate_timetable(
            {"Matematika": 6}, 5, working_days=6
        )
        count = sum(1 for row in timetable for cell in row if cell == "Matematika")
        assert count == 6

    # ================================================================
    # TEACHER CONSTRAINTS
    # ================================================================

    def test_teacher_constraints(self):
        """O'qituvchi band soati — algoritm xatosiz ishlaydi"""
        timetable, score = self.scheduler.generate_timetable(
            {"Matematika": 3}, 5, working_days=6,
            teacher_constraints={(1, 0, 0), (1, 1, 0)},
            subject_teacher_map={"Matematika": 1}
        )
        # Algoritm xatosiz tugadi
        assert timetable is not None
        assert score >= 0

    # ================================================================
    # CONSTANTS
    # ================================================================

    def test_periods_per_day(self):
        """PERIODS_PER_DAY = 6"""
        assert PERIODS_PER_DAY == 6


# ================================================================
# Pytest uchun
# ================================================================
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
