"""Tez sinov — 1 sinf uchun scheduler ishlayaptimi"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()
print(f"Bazada {len(classes)} sinf")

# 1 sinf sinash
cls = classes[0]
class_id = cls[0]
class_name = cls[1]
class_level = cls[2]
working_days = cls[4] if cls[4] else 6

assignments = db.get_class_assignments(class_id)
print(f"\nSinf: {class_name} (daraja {class_level}, {working_days} kun)")
print(f"Darslar: {len(assignments)}")

subjects_hours = {}
subject_teacher_map = {}
for a in assignments:
    subj = a[1]
    hours = a[4]
    tid = a[6]
    subjects_hours[subj] = subjects_hours.get(subj, 0) + hours
    subject_teacher_map[subj] = tid

print(f"Fanlar: {subjects_hours}")

# 1 sinf uchun scheduler
scheduler = TimetableScheduler(algorithm="brkga")
start = time.time()
timetable, score = scheduler.generate_timetable(
    subjects_hours, class_level,
    working_days=working_days,
    teacher_constraints={},
    subject_teacher_map=subject_teacher_map
)
elapsed = time.time() - start
print(f"\nNatija: {elapsed:.1f}s, ball: {score}")
print("Jadval:")
days = ["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan"]
for p in range(6):
    row = []
    for d in range(6):
        cell = timetable[p][d] if timetable[p][d] else "."
        row.append(cell[:4].ljust(4))
    print(f"  {p+1}-dars: {' | '.join(row)}")

db.close()
