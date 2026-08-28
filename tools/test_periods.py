"""Test — period 7 ishlatilganini tekshirish"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()
scheduler = TimetableScheduler(algorithm="brkga")

all_data, conflicts, week2_data = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False
)

# Period 7 tekshirish
period7_count = 0
period_max = 0
for key, data in all_data.items():
    class_id, day, period = key
    if period >= 6:
        period7_count += 1
        print(f"⚠️ Period {period+1}: Sinf {class_id}, Kun {day} — {data.get('subject_name', '?')}")
    period_max = max(period_max, period)

# Kunlik taqsimot
print(f"\n📊 NATIJA:")
print(f"   Darslar: {len(all_data)}")
print(f"   Period 7+ soni: {period7_count}")
print(f"   Eng oxirgi period: {period_max + 1}")

# Har sinfning kunlik taqsimoti
print(f"\n📅 KUNLIK TAQSIMOT:")
class_data = {}
for key, data in all_data.items():
    class_id, day, period = key
    if class_id not in class_data:
        class_data[class_id] = {}
    if day not in class_data[class_id]:
        class_data[class_id][day] = 0
    class_data[class_id][day] += 1

for cid in sorted(class_data.keys()):
    days = class_data[cid]
    day_str = ", ".join([f"K{d}:{n}" for d, n in sorted(days.items())])
    print(f"   Sinf {cid}: {day_str}")

db.close()