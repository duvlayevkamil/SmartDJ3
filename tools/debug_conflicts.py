"""Ziddiyatlar manbasini aniqlash"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()[:30]
print(f"Test: {len(classes)} sinf")

scheduler = TimetableScheduler(algorithm="brkga")
start = time.time()

all_data, conflicts = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False,
    progress_callback=lambda cn, i, t, s: None
)
elapsed = time.time() - start

print(f"\nVaqt: {elapsed:.1f}s, Joylashtirilgan: {len(all_data)}, Ziddiyatlar: {len(conflicts)}")

# Ziddiyatlarni tahlil qilish
if conflicts:
    print("\nZiddiyatlar tahlili:")
    teacher_conflicts = {}
    for teacher_name, class1, class2, day, period in conflicts:
        key = teacher_name
        if key not in teacher_conflicts:
            teacher_conflicts[key] = []
        teacher_conflicts[key].append((class1, class2, day, period))

    for teacher, items in sorted(teacher_conflicts.items(), key=lambda x: -len(x[1])):
        print(f"  {teacher}: {len(items)} ziddiyat")
        for c1, c2, d, p in items[:3]:
            print(f"    {c1} vs {c2} — kun {d}, dars {p+1}")

db.close()
