"""Greedy-only test — BRKGA ishlatmasdan"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()
print(f"📊 {len(classes)} sinf")

# BRKGA threshold ni 100 ga oshirish — hech qachon BRKGA ishlamasin
from core import brkga
original_generate = brkga.BRKGAScheduler.generate_timetable

def greedy_only_generate(self, subjects_hours, class_level, max_daily=None,
                         working_days=6, teacher_constraints=None,
                         subject_teacher_map=None, tayanch_hours=None, verbose=False):
    """Faqat greedy — BRKGA ishlatmasdan"""
    self.tayanch_hours = tayanch_hours
    self._teacher_constraints = teacher_constraints
    self._subject_teacher_map = subject_teacher_map
    if max_daily is None:
        max_daily = self.sanpin.max_daily_lessons.get(class_level, 7)

    timetable, score = self._fast_greedy(
        subjects_hours, class_level, max_daily,
        working_days, teacher_constraints, subject_teacher_map
    )
    return timetable, score

brkga.BRKGAScheduler.generate_timetable = greedy_only_generate

scheduler = TimetableScheduler(algorithm="brkga")
start = time.time()

all_data, conflicts = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False,
    progress_callback=lambda cn, i, t, s: None
)
elapsed = time.time() - start

print(f"\n{'='*50}")
print(f"⏱️ Vaqt: {elapsed:.1f}s ({elapsed/60:.1f} daqiqa)")
print(f"📝 Joylashtirilgan: {len(all_data)}")
print(f"⚠️ Ziddiyatlar: {len(conflicts)}")
print(f"📊 Tezlik: {len(classes)/elapsed:.1f} sinf/s")
print(f"{'='*50}")

# Joylashmay qolganlarni hisoblash
total_needed = sum(sum(a[4] for a in db.get_class_assignments(cls[0])) for cls in classes)
total_placed = len(all_data)
print(f"❌ Joylashmay qolgan: {total_needed - total_placed} ({(total_needed - total_placed)/total_needed*100:.1f}%)")

db.close()
