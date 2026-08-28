"""
250 sinf TO'LIQ SINOV — vaqt, xotira, natija o'lchash.
"""
import sys, os, time, tracemalloc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
db = DatabaseManager()
db.db_name = db_path
db.initialize()

classes = db.get_all_classes()
print(f"📊 Bazada: {len(classes)} sinf")
print(f"📊 O'qituvchilar: {len(db.get_all_teachers())}")
print(f"📊 Fanlar: {len(db.get_all_subjects())}")

# Xotira
tracemalloc.start()
mem_before = tracemalloc.get_traced_memory()

scheduler = TimetableScheduler(algorithm="brkga")
scores = []
start = time.time()

def on_progress(class_name, idx, total, score):
    if score > 0:
        scores.append(score)
    elapsed = time.time() - start
    if idx % 25 == 0 or idx == total:
        avg = sum(scores) / len(scores) if scores else 0
        speed = idx / elapsed if elapsed > 0 else 0
        eta = (total - idx) / speed if speed > 0 else 0
        print(f"   ⏱️ {idx}/{total} — {elapsed:.1f}s — ball: {avg:.1f} — {speed:.1f} sinf/s — ETA: {eta:.0f}s")

print(f"\n🚀 Scheduler boshlandi — {time.strftime('%H:%M:%S')}")
all_data, conflicts = scheduler.generate_all_class_timetables(
    classes, db, cancel_flag=lambda: False, progress_callback=on_progress
)
elapsed = time.time() - start

mem_after = tracemalloc.get_traced_memory()
tracemalloc.stop()

placed = len(all_data)
total_possible = sum(sum(a[4] for a in db.get_class_assignments(cls[0])) for cls in classes)
avg_score = sum(scores) / len(scores) if scores else 0

print(f"\n{'='*60}")
print(f"📊 NATIJALAR:")
print(f"   ⏱️ Vaqt: {elapsed:.1f}s ({elapsed/60:.1f} daqiqa)")
print(f"   📏 Tezlik: {len(classes)/elapsed:.2f} sinf/soniya")
print(f"   📝 Joylashtirilgan: {placed}/{total_possible} ({placed/total_possible*100:.1f}%)")
print(f"   ⚠️ Ziddiyatlar: {len(conflicts)}")
print(f"   📈 Ball: o'rtacha={avg_score:.1f}")
print(f"   💾 Xotira: {mem_after[0]/1024/1024:.1f} MB")
print(f"\n⚔️ ProRector: ~120s (2 daq) | SmartDJ3: {elapsed:.0f}s ({elapsed/60:.1f} daq)")
if elapsed < 120:
    print(f"   🏆 SmartDJ3 PRORECTOR DAN TEZROQ!")
else:
    print(f"   ⏳ ProRector {120/elapsed:.1f}x tezroq")
print(f"{'='*60}")

db.close()
