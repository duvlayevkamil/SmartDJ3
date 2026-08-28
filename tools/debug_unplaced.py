"""Nima uchun 4 dars joylashmayapti"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.brkga import BRKGAScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()

# 7-B sinfini topish
target_class = None
for cls in classes:
    if cls[1] == "7-B":
        target_class = cls
        break

if not target_class:
    print("7-B topilmadi")
    db.close()
    exit()

class_id = target_class[0]
assignments = db.get_class_assignments(class_id)
print(f"Sinf: {target_class[1]} (daraja {target_class[2]})")
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

# Greedy ni chaqirish
brkga = BRKGAScheduler()
teacher_constraints = {}

timetable, score = brkga._fast_greedy(
    subjects_hours, target_class[2], 6, 6,
    teacher_constraints, subject_teacher_map
)

# Natijani tekshirish
placed = {}
for day in range(6):
    for period in range(6):
        sub = timetable[period][day]
        if sub:
            placed[sub] = placed.get(sub, 0) + 1

print(f"\nJoylashtirilgan:")
for sub, count in sorted(placed.items()):
    needed = subjects_hours.get(sub, 0)
    status = "✅" if count >= needed else f"❌ {count}/{needed}"
    print(f"  {sub}: {count} (kerak: {needed}) {status}")

print(f"\nBall: {score}")

db.close()
