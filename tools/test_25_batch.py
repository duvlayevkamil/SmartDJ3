"""25 sinf batch test"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()[:25]
print(f"Test: {len(classes)} sinf")

scheduler = TimetableScheduler(algorithm="brkga")
scores = []
start = time.time()

def on_progress(class_name, idx, total, score):
    elapsed = time.time() - start
    avg = sum(scores) / len(scores) if scores else 0
    print(f"   {idx}/{total} {class_name} — ball: {score} — {elapsed:.1f}s — o'rtacha: {avg:.1f}")

all_data, conflicts = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False,
    progress_callback=lambda cn, i, t, s: (scores.append(s) if s > 0 else None, print(f"   {i}/{t} {cn} — {s} — {time.time()-start:.1f}s"))
)
elapsed = time.time() - start
print(f"\n{len(classes)} sinf = {elapsed:.1f}s ({elapsed/len(classes):.2f}s/sinf)")
print(f"Taxmin 250 sinf: ~{elapsed/len(classes)*250:.0f}s ({elapsed/len(classes)*250/60:.1f} daq)")
db.close()
