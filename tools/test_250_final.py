"""250 sinf TO'LIQ SINOV"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()
print(f"📊 {len(classes)} sinf, {len(db.get_all_teachers())} o'qituvchi")

scheduler = TimetableScheduler(algorithm="brkga")
start = time.time()

def on_progress(class_name, idx, total, score):
    elapsed = time.time() - start
    if idx % 50 == 0 or idx == total:
        speed = idx / elapsed if elapsed > 0 else 0
        eta = (total - idx) / speed if speed > 0 else 0
        print(f"   {idx}/{total} — {elapsed:.1f}s — {speed:.1f} sinf/s — ETA: {eta:.0f}s")

all_data, conflicts = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False, progress_callback=on_progress
)
elapsed = time.time() - start

print(f"\n{'='*50}")
print(f"⏱️ {elapsed:.1f}s ({elapsed/60:.1f} daqiqa)")
print(f"📝 {len(all_data)} dars joylashtirildi")
print(f"⚠️ {len(conflicts)} ziddiyat")
print(f"⚔️ ProRector: ~120s | SmartDJ3: {elapsed:.0f}s")
if elapsed < 120:
    print(f"🏆 SMARTDJ3 PRORECTOR DAN TEZROQ!")
else:
    print(f"⏳ ProRector {120/elapsed:.1f}x tezroq")
print(f"{'='*50}")
db.close()
