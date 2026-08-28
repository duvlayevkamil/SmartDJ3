"""Detailed SanPIN test"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler
from core.sanpin import SanPINChecker

PERIODS_PER_DAY = 6

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()
scheduler = TimetableScheduler(algorithm="brkga")

all_data, conflicts, week2_data = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False
)

sanpin = SanPINChecker()

print("📊 SANPIN TEKSHIRUVI:")
print("=" * 60)

total_score = 0
total_errors = 0
total_warnings = 0

for cls in classes:
    class_id = cls[0]
    class_name = cls[1]
    class_level = cls[2]

    # Jadval yaratish
    timetable = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
    for key, info in all_data.items():
        if key[0] == class_id:
            day, period = key[1], key[2]
            if day < 6 and period < PERIODS_PER_DAY:
                timetable[period][day] = info.get('subject_name', '')

    # SanPIN tekshiruvi
    result = sanpin.check_timetable(timetable, class_level)
    score = result['score']
    errors = result.get('errors', [])
    warnings = result.get('warnings', [])

    total_score += score
    total_errors += len(errors)
    total_warnings += len(warnings)

    # Kunlik taqsimot
    day_counts = []
    for day in range(6):
        count = sum(1 for p in range(PERIODS_PER_DAY)
                   if timetable[p][day] and timetable[p][day].strip())
        day_counts.append(count)

    max_diff = max(day_counts) - min([c for c in day_counts if c > 0]) if any(c > 0 for c in day_counts) else 0

    status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
    print(f"{status} {class_name}: Ball={score}, Xatoliklar={len(errors)}, Ogohlantirishlar={len(warnings)}, Kunlar={day_counts}, Farq={max_diff}")

    if errors:
        for err in errors[:2]:
            print(f"   ❌ {err}")

print(f"\n{'=' * 60}")
print(f"📊 UMUMIY NATIJA:")
print(f"   O'rtacha ball: {total_score / len(classes):.1f}")
print(f"   Jami xatoliklar: {total_errors}")
print(f"   Jami ogohlantirishlar: {total_warnings}")
print(f"{'=' * 60}")

# 2-hafta ma'lumotlari
if week2_data:
    print(f"\n📅 2-HAFTA: {len(week2_data)} ta dars")
else:
    print(f"\n📅 2-HAFTA: bo'sh")

db.close()