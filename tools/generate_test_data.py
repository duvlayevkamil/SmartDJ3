"""
Test data generator — 250 sinf, 500 o'qituvchi, ~3750 dars biriktirish.
SmartDJ3 katta hajm sinovi uchun.

Ishlatish:
    python tools/generate_test_data.py

Natija: smartdj_test.db fayli yaratiladi.
"""
import sys
import os
import random

# Loyiha papkasini path ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager

# Konfiguratsiya
NUM_CLASSES = 250
NUM_TEACHERS = 750  # Kamroq yuklanish uchun ko'proq o'qituvchi
LETTERS = ["A", "B", "V", "G", "D", "E", "K", "N", "M", "P", "R", "S",
           "T", "U", "F", "X", "Y", "Z", "O", "I", "J", "L", "Q", "W"]

# Fanlar ro'yxati — qiyinlik darajasi bilan
SUBJECTS = [
    # Toifa A — Eng qiyin (11-13)
    ("Matematika", "Mat", 12),
    ("Algebra", "Alg", 13),
    ("Geometriya", "Geo", 11),
    ("Fizika", "Fiz", 13),
    ("Kimyo", "Kim", 12),
    ("Informatika", "Inf", 11),
    ("Chet tili", "ChT", 11),
    ("Ingliz tili", "Ing", 11),
    ("Rus tili", "Rus", 11),

    # Toifa B — O'rtacha (8-10)
    ("Ona tili", "OT", 9),
    ("Adabiyot", "Adb", 9),
    ("Biologiya", "Bio", 8),
    ("Geografiya", "Geog", 8),
    ("Tarix", "Tar", 9),
    ("Huquq", "Huq", 8),
    ("Iqtisodiyot", "Iqt", 8),

    # Toifa C — Yengil (3-5)
    ("Tarbiya", "Trb", 3),
    ("Jismoniy tarbiya", "JT", 4),
    ("Sport", "Spo", 4),
    ("Texnologiya", "Tex", 5),
    ("Tasviriy san'at", "Tsv", 3),
    ("Musiqa", "Mus", 3),
    ("San'at", "San", 3),
    ("Mehnat", "Meh", 5),
    ("Chaqiriqqacha harbiy tayyorgarlik", "CHHT", 5),
]

# Tayanch reja — sinf darajasiga qarab haftalik soatlar
# Format: {daraja: {fan_nomi: soat}}
TAYANCH_REJA = {
    1: {"Ona tili": 5, "Matematika": 5, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Musiqa": 1, "Tasviriy san'at": 1, "Texnologiya": 1, "Chet tili": 2,
        "Sport": 2, "San'at": 1, "Mehnat": 1},
    2: {"Ona tili": 5, "Matematika": 5, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Musiqa": 1, "Tasviriy san'at": 1, "Texnologiya": 1, "Chet tili": 2,
        "Sport": 2, "San'at": 1, "Mehnat": 1},
    3: {"Ona tili": 5, "Matematika": 5, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Musiqa": 1, "Tasviriy san'at": 1, "Texnologiya": 1, "Chet tili": 2,
        "Sport": 2, "San'at": 1, "Mehnat": 1},
    4: {"Ona tili": 5, "Matematika": 5, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Musiqa": 1, "Tasviriy san'at": 1, "Texnologiya": 1, "Chet tili": 2,
        "Sport": 2, "San'at": 1, "Mehnat": 1},
    5: {"Ona tili": 4, "Adabiyot": 2, "Matematika": 5, "Algebra": 2,
        "Geometriya": 1, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Chet tili": 3, "Biologiya": 1, "Geografiya": 1, "Tarix": 1,
        "Texnologiya": 1, "Informatika": 1, "Sport": 2, "Musiqa": 1},
    6: {"Ona tili": 4, "Adabiyot": 2, "Matematika": 5, "Algebra": 2,
        "Geometriya": 1, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Chet tili": 3, "Biologiya": 1, "Geografiya": 2, "Tarix": 2,
        "Texnologiya": 1, "Informatika": 1, "Sport": 2, "Musiqa": 1},
    7: {"Ona tili": 3, "Adabiyot": 2, "Matematika": 5, "Algebra": 2,
        "Geometriya": 2, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Chet tili": 3, "Biologiya": 2, "Geografiya": 2, "Tarix": 2,
        "Texnologiya": 1, "Informatika": 1, "Fizika": 2, "Kimyo": 1,
        "Sport": 2, "Musiqa": 1},
    8: {"Ona tili": 3, "Adabiyot": 2, "Matematika": 5, "Algebra": 2,
        "Geometriya": 2, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Chet tili": 3, "Biologiya": 2, "Geografiya": 2, "Tarix": 2,
        "Texnologiya": 1, "Informatika": 1, "Fizika": 2, "Kimyo": 2,
        "Sport": 2, "Musiqa": 1},
    9: {"Ona tili": 3, "Adabiyot": 2, "Matematika": 5, "Algebra": 3,
        "Geometriya": 2, "Tarbiya": 1, "Jismoniy tarbiya": 2,
        "Chet tili": 3, "Biologiya": 2, "Geografiya": 2, "Tarix": 2,
        "Texnologiya": 1, "Informatika": 1, "Fizika": 2, "Kimyo": 2,
        "Huquq": 1, "Iqtisodiyot": 1, "Sport": 2},
    10: {"Ona tili": 3, "Adabiyot": 2, "Algebra": 3, "Geometriya": 2,
         "Chet tili": 3, "Biologiya": 2, "Geografiya": 2, "Tarix": 2,
         "Fizika": 3, "Kimyo": 2, "Informatika": 2, "Jismoniy tarbiya": 2,
         "Texnologiya": 2, "Huquq": 1, "Iqtisodiyot": 1, "Sport": 2},
    11: {"Ona tili": 3, "Adabiyot": 2, "Algebra": 3, "Geometriya": 2,
         "Chet tili": 3, "Biologiya": 2, "Geografiya": 2, "Tarix": 2,
         "Fizika": 3, "Kimyo": 2, "Informatika": 2, "Jismoniy tarbiya": 2,
         "Texnologiya": 2, "Huquq": 1, "Iqtisodiyot": 1, "Sport": 2},
}

# O'qituvchi ismlari
FIRST_NAMES = [
    "Abdurashid", "Alisher", "Botir", "Davron", "Eldor", "Farrux", "Gafur",
    "Hamid", "Ilhom", "Javlon", "Kamoliddin", "Laziz", "Mirzohid", "Nodir",
    "Otabek", "Paul", "Rustam", "Sardor", "Timur", "Ulug'bek", "Vohid",
    "Yulduz", "Zafar", "Alisher", "Bahrom", "Davron", "Erkin", "Farruh",
    "G'anisher", "Hikmat", "Igor", "Jasur", "Kamol", "Laziz", "Masud",
    "Nodirjon", "Oybek", "Pyotr", "Rahim", "Sarvar", "Toshmat", "Umid",
    "Viktor", "Xurshid", "Yorqin", "Zakir", "Aleksey", "Boris", "Valeriy",
    "Gennadiy", "Viktor", "Oleg", "Sergey", "Nikolay", "Andrey", "Dmitriy",
]

LAST_NAMES = [
    "Duvlayev", "Toshmatov", "Karimov", "Rahimov", "Qosimov", "Ergashev",
    "Mirzaev", "Xolmatov", "Abdullayev", "Nazarov", "Sultanov", "Turgunov",
    "Yuldashev", "Ismoilov", "G'aniyev", "Sharipov", "Ismoilov", "Umarov",
    "Ruziyev", "Botirova", "Azizova", "Nizomova", "Karimova", "Rahimova",
    "Qosimova", "Ergasheva", "Mirzaeva", "Xolmatova", "Abdullayeva",
    "Nazarova", "Sultanova", "Turgunova", "Yuldasheva", "Ismoilova",
]

# ranglar
COLORS = [
    "#3498DB", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6",
    "#1ABC9C", "#E67E22", "#2980B9", "#C0392B", "#27AE60",
    "#8E44AD", "#D35400", "#16A085", "#F1C40F", "#7F8C8D",
    "#2C3E50", "#95A5A6", "#BDC3C7", "#34495E", "#ECF0F1",
]


def generate_test_data():
    """Test ma'lumotlarini yaratish"""
    print("=" * 60)
    print("SMARTDJ3 — TEST DATA GENERATOR")
    print(f"目標: {NUM_CLASSES} sinf, {NUM_TEACHERS} o'qituvchi")
    print("=" * 60)

    # Test bazasini yaratish
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smartdj_test.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Eski test baza o'chirildi: {db_path}")

    db = DatabaseManager()
    db.db_name = db_path
    db.initialize()
    print(f"✅ Test baza yaratildi: {db_path}")

    # 1. FANLARNI QO'SHISH
    print("\n📚 Fanlar qo'shildi...")
    subject_ids = {}
    for name, short, diff in SUBJECTS:
        sid = db.add_subject(name, short, diff)
        if sid:
            subject_ids[name] = sid
    print(f"   {len(subject_ids)} ta fan qo'shildi")

    # 2. SINFLARNI YARATISH
    print(f"\n🏫 {NUM_CLASSES} sinf yaratilmoqda...")
    class_ids = []
    for i in range(NUM_CLASSES):
        level = (i % 11) + 1  # 1-11 daraja
        letter_idx = (i // 11) % len(LETTERS)
        letter = LETTERS[letter_idx]
        class_name = f"{level}-{letter}"
        working_days = 5 if level <= 4 else 6
        students = random.randint(20, 40)

        cid = db.add_class(class_name, level, students, working_days)
        if cid:
            class_ids.append((cid, class_name, level, working_days))

    print(f"   {len(class_ids)} sinf yaratildi")

    # 3. O'QITUVCHILARNI YARATISH
    print(f"\n👨‍🏫 {NUM_TEACHERS} o'qituvchi yaratilmoqda...")
    teacher_ids = []
    used_names = set()

    for i in range(NUM_TEACHERS):
        # Unikal ism yaratish
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full_name = f"{last} {first}"
            if full_name not in used_names:
                used_names.add(full_name)
                break

        short_name = f"{first[0]}.{last[0]}."
        color = COLORS[i % len(COLORS)]
        methodic_day = random.randint(0, 5)  # 0-5 (Dush-Shan)
        phone = f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}"

        tid = db.add_teacher(full_name, phone, color, None, methodic_day, short_name)
        if tid:
            teacher_ids.append((tid, full_name))

    print(f"   {len(teacher_ids)} o'qituvchi yaratildi")

    # 4. DARS BIRIKTIRISH — realistik o'qituvchi yuklanishi
    print(f"\n📝 Darslar biriktirilmoqda...")
    total_assignments = 0

    # Har o'qituvchining yuklanishi: {teacher_id: sinflar_soni}
    teacher_load = {tid: 0 for tid, _ in teacher_ids}
    MAX_CLASSES_PER_TEACHER = 2  # Har o'qituvchi maksimum 2 sinfga dars bersin

    # Har fan uchun o'qituvchilar ro'yxati: {subject_name: [(tid, tname), ...]}
    subject_teachers = {}
    for subject_name in SUBJECTS:
        name = subject_name[0]
        subject_teachers[name] = []

    # O'qituvchalarni fanlar bo'yicha tasniflash — ko'proq o'qituvchi, kamroq sinf
    for tid, tname in teacher_ids:
        # Har o'qituvchi 1-2 fandan dars bersin
        num_subjects = random.randint(1, 2)
        assigned_subjects = random.sample(list(SUBJECTS), min(num_subjects, len(SUBJECTS)))
        for subj in assigned_subjects:
            subject_teachers[subj[0]].append((tid, tname))

    # Har sinf uchun darslarni biriktirish
    for class_id, class_name, level, working_days in class_ids:
        tayanch = TAYANCH_REJA.get(level, {})
        if not tayanch:
            continue

        for subject_name, weekly_hours in tayanch.items():
            if subject_name not in subject_ids:
                continue

            subject_id = subject_ids[subject_name]

            # Shu fan uchun mos o'qituvchi topish
            available = subject_teachers.get(subject_name, [])

            # Eng kam yuklangan o'qituvchini tanlash
            best_teacher = None
            best_load = float('inf')

            for tid, tname in available:
                load = teacher_load.get(tid, 0)
                if load < MAX_CLASSES_PER_TEACHER and load < best_load:
                    best_load = load
                    best_teacher = (tid, tname)

            # Agar mos o'qituvchi topilmasa — tasodifiy (kam yuklangan)
            if best_teacher is None:
                for tid, tname in teacher_ids:
                    load = teacher_load.get(tid, 0)
                    if load < MAX_CLASSES_PER_TEACHER:
                        best_teacher = (tid, tname)
                        break

            # Oxirgi umid — har qanday o'qituvchi
            if best_teacher is None:
                best_teacher = random.choice(teacher_ids)

            tid, tname = best_teacher
            teacher_load[tid] = teacher_load.get(tid, 0) + 1

            success = db.add_lesson_assignment(
                class_id, subject_id, tid, weekly_hours, None
            )
            if success:
                total_assignments += 1

    print(f"   {total_assignments} ta dars biriktirildi")

    # 5. STATISTIKA
    print("\n" + "=" * 60)
    print("📊 STATISTIKA:")
    print(f"   Sinf: {len(class_ids)}")
    print(f"   O'qituvchi: {len(teacher_ids)}")
    print(f"   Fan: {len(subject_ids)}")
    print(f"   Dars biriktirish: {total_assignments}")

    # O'qituvchi yuklanishi
    teacher_load = {}
    for (cid, cname, lvl, wd) in class_ids:
        assignments = db.get_class_assignments(cid)
        for a in assignments:
            tid = a[6]
            hours = a[4]
            teacher_load[tid] = teacher_load.get(tid, 0) + hours

    max_load = max(teacher_load.values()) if teacher_load else 0
    avg_load = sum(teacher_load.values()) / len(teacher_load) if teacher_load else 0
    print(f"   O'qituvchi yuklanishi: max={max_load} soat, o'rtacha={avg_load:.1f} soat")

    # Har sinf uchun jami soatlar
    class_hours = []
    for cid, cname, lvl, wd in class_ids:
        assignments = db.get_class_assignments(cid)
        total = sum(a[4] for a in assignments) if assignments else 0
        class_hours.append((cname, lvl, total))

    avg_hours = sum(h for _, _, h in class_hours) / len(class_hours) if class_hours else 0
    print(f"   Sinf soatlari: o'rtacha={avg_hours:.1f} soat/sinf")

    db.close()
    print(f"\n✅ Test baza tayyor: {db_path}")
    print("=" * 60)

    return db_path


if __name__ == "__main__":
    generate_test_data()
