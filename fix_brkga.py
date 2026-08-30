import os

# Eski faylni zaxiralash
src = os.path.join('core', 'brkga.py')
bak = os.path.join('core', 'brkga_backup.py')
if os.path.exists(src) and not os.path.exists(bak):
    import shutil
    shutil.copy2(src, bak)
    print(f'Zaxira: {bak}')

# Faylni o'qish
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# 1-TUZATISH: 2-bosqichga teacher tekshiruv qo'shish
old1 = '''            # 2. Bo'sh slot + teacher band (ziddiyat bilan) + kunlik takrorlanish
            if not placed:
                for day in range(working_days):
                    for period in range(daily_limits[day]):
                        if timetable[period][day]:
                            continue
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        timetable[period][day] = sub'''

new1 = '''            # 2. Bo'sh slot + kunlik takrorlanish (TEKSHIRUV BILAN)
            if not placed:
                for day in range(working_days):
                    for period in range(daily_limits[day]):
                        if timetable[period][day]:
                            continue
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        # O'qituvchi bandligini tekshirish
                        if teacher_constraints and subject_teacher_map:
                            tid = subject_teacher_map.get(sub)
                            if tid and (tid, day, period) in teacher_constraints:
                                continue
                        timetable[period][day] = sub'''

# 2-TUZATISH: 3-bosqich (swap) ga teacher tekshiruv qo'shish
old2 = '''                        # Yangi dars kunlik takrorlanishni tekshirish
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        for new_day in range(working_days):'''

new2 = '''                        # Yangi dars kunlik takrorlanishni tekshirish
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        # Yangi dars uchun o'qituvchi bandligini tekshirish
                        if teacher_constraints and subject_teacher_map:
                            tid = subject_teacher_map.get(sub)
                            if tid and (tid, day, period) in teacher_constraints:
                                continue
                        for new_day in range(working_days):'''

# 3-TUZATISH: 3-bosqich swap ichida ko'chirilgan dars tekshiruvi
old3 = '''                                # Ko'chirilgan dars kunlik takrorlanishini tekshirish
                                if day_subjects[new_day].count(existing) >= max_daily_occurrences.get(existing, 1):
                                    continue
                                timetable[new_period][new_day] = existing'''

new3 = '''                                # Ko'chirilgan dars kunlik takrorlanishini tekshirish
                                if day_subjects[new_day].count(existing) >= max_daily_occurrences.get(existing, 1):
                                    continue
                                # Ko'chirilgan dars uchun o'qituvchi bandligini tekshirish
                                if teacher_constraints and subject_teacher_map:
                                    exist_tid = subject_teacher_map.get(existing)
                                    if exist_tid and (exist_tid, new_day, new_period) in teacher_constraints:
                                        continue
                                timetable[new_period][new_day] = existing'''

# 4-TUZATISH: 4-bosqich (oxirgi umid) ga teacher tekshiruv qo'shish
old4 = '''            # 4. OXIRGI UMID — mavjud darsni bosib, qayta joylashtirish
            if not placed:
                for day in range(working_days):
                    for period in range(daily_limits[day]):
                        existing = timetable[period][day]
                        if not existing:
                            continue
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        timetable[period][day] = sub'''

new4 = '''            # 4. OXIRGI UMID — mavjud darsni bosib, qayta joylashtirish
            if not placed:
                for day in range(working_days):
                    for period in range(daily_limits[day]):
                        existing = timetable[period][day]
                        if not existing:
                            continue
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        # O'qituvchi bandligini tekshirish
                        if teacher_constraints and subject_teacher_map:
                            tid = subject_teacher_map.get(sub)
                            if tid and (tid, day, period) in teacher_constraints:
                                continue
                        timetable[period][day] = sub'''

# Tuzatishlarni qo'llash
count = 0
for old, new in [(old1, new1), (old2, new2), (old3, new3), (old4, new4)]:
    if old in code:
        code = code.replace(old, new)
        count += 1
        print(f'  Tuzatildi #{count}')
    else:
        print(f'  Topilmadi (allaqachon tuzatilgan bo''lishi mumkin)')

# Saqlash
with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'\nTayyor! {count} ta tuzatish qo''llanildi')