"""50 sinf batch test"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()[:50]
print(f"Test: {len(classes)} sinf")

scheduler = TimetableScheduler(algorithm="brkga")
start = time.time()

def on_progress(class_name, idx, total, score):
    elapsed = time.time() - start
    if idx % 10 == 0 or idx == total:
        print(f"   {idx}/{total} — {elapsed:.1f}s — ball: {score}")

all_data, conflicts = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False, progress_callback=on_progress
)
elapsed = time.time() - start
print(f"\n{len(classes)} sinf = {elapsed:.1f}s ({elapsed/len(classes):.2f}s/sinf)")
print(f"Taxmin 250 sinf: ~{elapsed/len(classes)*250:.0f}s ({elapsed/len(classes)*250/60:.1f} daq)")
print(f"Joylashtirilgan: {len(all_data)}, Ziddiyatlar: {len(conflicts)}")
db.close()
