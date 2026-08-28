"""Joylashmay qolgan darslarni tahlil qilish"""
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

scheduler = TimetableScheduler(algorithm="brkga")
start = time.time()

all_data, conflicts = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False,
    progress_callback=lambda cn, i, t, s: None
)
elapsed = time.time() - start

# Har sinf uchun joylashtirilgan vs kerakli darslar
print(f"\n⏱️ Vaqt: {elapsed:.1f}s")
print(f"📝 Joylashtirilgan: {len(all_data)} dars")

total_needed = 0
total_placed = 0
unplaced_by_class = []
unplaced_by_subject = {}

for cls in classes:
    class_id = cls[0]
    class_name = cls[1]
    assignments = db.get_class_assignments(class_id)
    if not assignments:
        continue

    needed = sum(a[4] for a in assignments)
    placed = sum(1 for k, v in all_data.items() if k[0] == class_id)

    total_needed += needed
    total_placed += placed
    unplaced = needed - placed

    if unplaced > 0:
        unplaced_by_class.append((class_name, class_id, needed, placed, unplaced))
        # Qaysi fanlar joylashmadi?
        for a in assignments:
            subject_name = a[1]
            weekly_hours = a[4]
            # Shu fandan nechta joylashtirildi?
            placed_for_subject = sum(
                1 for k, v in all_data.items()
                if k[0] == class_id and v.get('subject_name') == subject_name
            )
            if placed_for_subject < weekly_hours:
                missing = weekly_hours - placed_for_subject
                unplaced_by_subject[subject_name] = unplaced_by_subject.get(subject_name, 0) + missing

# Natijalar
print(f"\n{'='*60}")
print(f"📊 NATIJALAR:")
print(f"   Kerakli: {total_needed} dars")
print(f"   Joylashtirilgan: {total_placed} dars")
print(f"   Joylashmay qolgan: {total_needed - total_placed} dars ({(total_needed - total_placed)/total_needed*100:.1f}%)")

if unplaced_by_class:
    print(f"\n🏫 Joylashmay qolgan sinflar ({len(unplaced_by_class)} sinf):")
    for name, cid, needed, placed, unplaced in sorted(unplaced_by_class, key=lambda x: -x[4])[:20]:
        print(f"   {name}: {placed}/{needed} (+{unplaced} qoldiq)")

if unplaced_by_subject:
    print(f"\n📚 Joylashmay qolgan fanlar:")
    for subj, count in sorted(unplaced_by_subject.items(), key=lambda x: -x[1]):
        print(f"   {subj}: {count} soat qoldiq")

db.close()
