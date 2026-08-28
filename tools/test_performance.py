"""
Performance test — moslashtirilgan hajm bilan sinov.
Vaqt, xotira va natijalarni o'lchaydi.

Ishlatish:
    python tools/test_performance.py [sinflar_soni]

Misol:
    python tools/test_performance.py 50
    python tools/test_performance.py 100
    python tools/test_performance.py 250
"""
import sys
import os
import time
import tracemalloc

# Loyiha papkasini path ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from core.scheduler import TimetableScheduler


def test_performance(num_classes=None):
    """Moslashtirilgan hajm bilan scheduler testi"""
    print("=" * 60)
    print("SMARTDJ3 — PERFORMANCE TEST")
    print("=" * 60)

    # Test bazasini yuklash
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
    if not os.path.exists(db_path):
        print("❌ Test baza topilmadi!")
        print("   Avval: python tools/generate_test_data.py")
        return

    db = DatabaseManager()
    db.db_name = db_path
    db.initialize()

    all_classes = db.get_all_classes()
    print(f"\n📊 Bazada: {len(all_classes)} sinf")

    # Sinf sonini cheklash (agar berilgan bo'lsa)
    if num_classes and num_classes < len(all_classes):
        classes = all_classes[:num_classes]
        print(f"   Test uchun: {len(classes)} sinf tanlandi")
    else:
        classes = all_classes
        print(f"   Barcha sinflar: {len(classes)}")

    # Xotira o'lchashni boshlash
    tracemalloc.start()
    mem_before = tracemalloc.get_traced_memory()

    # Scheduler yaratish
    scheduler = TimetableScheduler(algorithm="brkga")

    # Progress callback
    progress_data = {"count": 0, "scores": [], "last_time": time.time()}

    def on_progress(class_name, idx, total, score):
        progress_data["count"] = idx
        if score > 0:
            progress_data["scores"].append(score)

        now = time.time()
        # Har 10 sinfda yoki oxirgida
        if idx % 10 == 0 or idx == total:
            elapsed = now - start_time
            avg_score = sum(progress_data["scores"]) / len(progress_data["scores"]) if progress_data["scores"] else 0
            speed = idx / elapsed if elapsed > 0 else 0
            eta = (total - idx) / speed if speed > 0 else 0
            print(f"   ⏱️ {idx}/{total} — {elapsed:.1f}s — ball: {avg_score:.1f} — tezlik: {speed:.1f} sinf/s — ETA: {eta:.0f}s")

    # Scheduler ni ishga tushirish
    print("\n🚀 Scheduler boshlandi...")
    start_time = time.time()

    try:
        all_data, conflicts = scheduler.generate_all_class_timetables(
            classes, db,
            cancel_flag=lambda: False,
            progress_callback=on_progress
        )
    except Exception as e:
        import traceback
        print(f"\n❌ Xatolik: {e}")
        traceback.print_exc()
        return

    end_time = time.time()
    elapsed = end_time - start_time

    # Xotira natijalari
    mem_after = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Natijalarni hisoblash
    placed = len(all_data)
    total_possible = 0
    for cls in classes:
        assignments = db.get_class_assignments(cls[0])
        if assignments:
            total_possible += sum(a[4] for a in assignments)

    placement_rate = (placed / total_possible * 100) if total_possible > 0 else 0

    # Ball statistikasi
    scores = progress_data["scores"]
    avg_score = sum(scores) / len(scores) if scores else 0
    min_score = min(scores) if scores else 0
    max_score = max(scores) if scores else 0

    # Ziddiyatlar
    num_conflicts = len(conflicts)

    # Natijalarni chiqarish
    print("\n" + "=" * 60)
    print("📊 NATIJALAR:")
    print(f"   ⏱️ Vaqt: {elapsed:.1f} soniya ({elapsed/60:.1f} daqiqa)")
    print(f"   📏 Tezlik: {len(classes)/elapsed:.2f} sinf/soniya")
    print(f"   📝 Joylashtirilgan: {placed}/{total_possible} ({placement_rate:.1f}%)")
    print(f"   ⚠️ Ziddiyatlar: {num_conflicts}")
    print(f"   📈 Ball: o'rtacha={avg_score:.1f}, min={min_score}, max={max_score}")
    print(f"   💾 Xotira: {mem_after[0]/1024/1024:.1f} MB (boshlanish: {mem_before[0]/1024/1024:.1f} MB)")

    # ProRector bilan taqqoslash
    print("\n" + "=" * 60)
    print("⚔️ PRORECTOR BILAN TAQQOSLASH:")
    # ProRector 1-2 daqiqada 250 sinf — ya'ni ~0.5-1s/sinf
    pr_per_class = 0.5  # soniya/sinf (taxminiy)
    pr_estimated = pr_per_class * len(classes)
    speedup = pr_estimated / elapsed if elapsed > 0 else 0
    print(f"   ProRector (taxminiy): ~{pr_estimated:.0f}s ({pr_per_class}s/sinf)")
    print(f"   SmartDJ3: {elapsed:.1f}s ({elapsed/len(classes):.2f}s/sinf)")
    if speedup > 1:
        print(f"   🏆 SmartDJ3 {speedup:.1f}x TEZROQ!")
    else:
        print(f"   ⏳ ProRector {(1/speedup):.1f}x tezroq")

    # Masshtab
    print("\n" + "=" * 60)
    print("📐 MASSHTAB PROGNOZI:")
    for target in [50, 100, 150, 200, 250]:
        if target <= len(classes):
            continue
        est_time = (elapsed / len(classes)) * target
        est_min = est_time / 60
        print(f"   {target} sinf: ~{est_time:.0f}s ({est_min:.1f} daqiqa)")

    db.close()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    test_performance(num)
