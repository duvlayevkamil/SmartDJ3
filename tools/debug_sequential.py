"""Sequential scheduling da nima uchun 4 dars qoldiq"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()

# 7-B ni topish va uning indeksini aniqlash
target_idx = None
for i, cls in enumerate(classes):
    if cls[1] == "7-B":
        target_idx = i
        break

print(f"7-B indeksi: {target_idx}")

# Faqat 7-B gacha bo'lgan sinflarni jadval tuzish
test_classes = classes[:target_idx + 1]
print(f"Test: {len(test_classes)} sinf (7-B oxirgi)")

scheduler = TimetableScheduler(algorithm="brkga")
all_data, conflicts = scheduler.generate_all_class_timetables(
    test_classes, db, cancel_flag=lambda: False,
    progress_callback=lambda cn, i, t, s: None
)

# 7-B natijasini tekshirish
target_id = classes[target_idx][0]
placed = {}
for (cid, day, period), info in all_data.items():
    if cid == target_id:
        sub = info.get('subject_name', '')
        placed[sub] = placed.get(sub, 0) + 1

assignments = db.get_class_assignments(target_id)
needed = {}
for a in assignments:
    subj = a[1]
    needed[subj] = needed.get(subj, 0) + a[4]

print(f"\n7-B natijasi:")
for sub, count in sorted(placed.items()):
    n = needed.get(sub, 0)
    status = "✅" if count >= n else f"❌ {count}/{n}"
    print(f"  {sub}: {count} (kerak: {n}) {status}")

# Joylashmaganlar
for sub, n in needed.items():
    p = placed.get(sub, 0)
    if p < n:
        print(f"  ❌ {sub}: {p}/{n} — {n-p} ta qoldiq")

db.close()
