"""ALL_DATA compaction test — real database"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()
print(f"📊 {len(classes)} sinf (haqiqiy maktab)")

scheduler = TimetableScheduler(algorithm="brkga")
start = time.time()

all_data, conflicts, week2_data = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False
)
elapsed = time.time() - start

# Natijalarni tahlil qilish
print(f"\n{'='*60}")
print(f"⏱️ {elapsed:.1f}s")
print(f"📝 {len(all_data)} dars joylashtirildi")

# Har sinfning kunini tekshirish — oyna borligini aniqlash
gaps = 0
gap_details = {}
total_lessons = len(all_data)

for class_id in sorted(set(k[0] for k in all_data.keys())):
    class_gaps = 0
    class_lessons = 0
    for day in range(6):
        day_lessons = []
        for period in range(6):
            key = (class_id, day, period)
            if key in all_data and all_data[key].get('subject_name', '').strip():
                day_lessons.append(period)
        
        if day_lessons:
            # Oxirgi dars periodi
            max_period = max(day_lessons)
            expected_slots = max_period + 1
            actual_lessons = len(day_lessons)
            gap = expected_slots - actual_lessons
            if gap > 0:
                class_gaps += gap
                gap_details[(class_id, day)] = gap
        class_lessons += len(day_lessons)
    
    gaps += class_gaps
    if class_gaps > 0:
        print(f"⚠️ Sinf {class_id}: {class_gaps} oyna")

print(f"\n{'='*60}")
print(f"📊 NATIJA:")
print(f"   Darslar: {total_lessons}")
print(f"   Ziddiyatlar: {len(conflicts)}")
print(f"   Oynalar: {gaps}")
print(f"{'='*60}")

# Oyna tafsilotlari
if gap_details:
    print(f"\n🔍 OYNA TAFSILOTLARI:")
    for (class_id, day), gap in sorted(gap_details.items()):
        print(f"   Sinf {class_id}, Kun {day}: {gap} oyna")

db.close()