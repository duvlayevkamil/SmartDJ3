"""5 sinf test — parallel scheduling ishlayaptimi"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()[:5]
print(f"Test: {len(classes)} sinf")

scheduler = TimetableScheduler(algorithm="brkga")

progress_data = {"scores": []}
def on_progress(class_name, idx, total, score):
    if score > 0:
        progress_data["scores"].append(score)
    print(f"   {idx}/{total} {class_name} — ball: {score}")

start = time.time()
all_data, conflicts = scheduler.generate_all_class_timetables(
    classes, db,
    cancel_flag=lambda: False,
    progress_callback=on_progress
)
elapsed = time.time() - start

print(f"\nNatija: {elapsed:.1f}s, joylashtirilgan: {len(all_data)}, ziddiyatlar: {len(conflicts)}")
if progress_data["scores"]:
    avg = sum(progress_data["scores"]) / len(progress_data["scores"])
    print(f"O'rtacha ball: {avg:.1f}")

db.close()
