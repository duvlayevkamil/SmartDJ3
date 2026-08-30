"""
Heuristic Backtracking dars jadvali tuzish algoritmi
"""
import random
import os
from core.sanpin import SanPINChecker

# Fan nomlari konfiguratsiyasi — qattiq kod o'rniga
DAILY_OCCURRENCE_OVERRIDES = {
    "Matematika": 2,
    "Algebra": 2,
    "Sport": 2,
    "Jismoniy tarbiya": 2,
}

SPORT_SUBJECTS = {"Sport", "Jismoniy tarbiya"}
PERIODS_PER_DAY = 6  # Kuniga maksimal 6 dars (7-dars yo'q)


class TimetableScheduler:
    def __init__(self, algorithm="brkga", db_manager=None):
        """
        algorithm: "backtracking" yoki "brkga"
        db_manager: DatabaseManager instansiyasi (2-hafta generatsiya uchun)
        """
        self.sanpin = SanPINChecker()
        self.kunlar = ["Dushanba", "Seshanba", "Chorshanba",
                       "Payshanba", "Juma", "Shanba"]
        self.base_max_states = 50000
        self.algorithm = algorithm
        self.cancel_flag = False  # To'xtatish flagi
        self.db = db_manager  # 2-hafta generatsiya uchun

    def cancel(self):
        """Jarayonni to'xtatish"""
        self.cancel_flag = True

    def reset_cancel(self):
        """To'xtatish flagini tiklash"""
        self.cancel_flag = False

    def _get_brkga_scheduler(self, class_level=5, total_lessons=20):
        """BRKGA scheduler ni yaratish — sinf darajasiga qarab adaptive"""
        from core.brkga import BRKGAScheduler

        # Adaptive: katta sinf va ko'p dars = kamroq avlod, tezroq stop
        if total_lessons > 30 or class_level >= 10:
            population_size = 60    # 80 → 60 (tezroq)
            generations = 120      # 200 → 120 (tezroq)
            patience = 25          # 40 → 25 (tezroq)
        elif total_lessons > 20 or class_level >= 6:
            population_size = 50   # 60 → 50 (tezroq)
            generations = 100      # 150 → 100 (tezroq)
            patience = 20          # 30 → 20 (tezroq)
        else:
            population_size = 30   # 40 → 30 (tezroq)
            generations = 80       # 100 → 80 (tezroq)
            patience = 15          # 20 → 15 (tezroq)

        return BRKGAScheduler(
            population_size=population_size,
            generations=generations,
            early_stop_score=85,   # 95 → 85 (tezroq tugallash)
            early_stop_patience=patience
        )

    def generate_timetable(self, subjects_hours, class_level,
                           teachers=None, max_daily=None, working_days=6,
                           teacher_constraints=None, subject_teacher_map=None,
                           tayanch_hours=None):
        """
        Avtomatik dars jadvalini tuzish — HYBRID yondashuv

        subjects_hours: {"Matematika": 5, "Fizika": 3, ...}
        class_level: int - sinf darajasi
        max_daily: int - kuniga max dars (ixtiyoriy)
        working_days: int - haftada ish kunlari (5 yoki 6)
        teacher_constraints: set of (teacher_id, day, period) - band vaqtlar
        subject_teacher_map: {subject_name: teacher_id} - fan → o'qituvchi xaritasi
        tayanch_hours: dict - tayanch rejadagi soatlar (SanPIN ustunligi uchun)

        Qaytaradi: 7x6 jadval (list of lists) va to'plangan SanPIN balli (int)
        """
        total_lessons = sum(subjects_hours.values())

        # HYBRID: kam dars = Backtracking, ko'p dars = BRKGA
        use_brkga = self.algorithm == "brkga" and total_lessons >= 20

        if use_brkga:
            brkga = self._get_brkga_scheduler(class_level, total_lessons)
            brkga.cancel_flag = self.cancel_flag
            timetable, score = brkga.generate_timetable(
                subjects_hours, class_level,
                max_daily=max_daily, working_days=working_days,
                teacher_constraints=teacher_constraints,
                subject_teacher_map=subject_teacher_map,
                tayanch_hours=tayanch_hours
            )
            # REPAIR dan oldin cancel tekshirish — BRKGA to'xtatilgan bo'lsa
            if self.cancel_flag:
                return timetable, score
            self.cancel_flag = False

            # BRKGA dan keyin qoldiq darslarni tuzatish
            # To'liq subjects_hours ni beramiz — _repair_unplaced o'zi qoldiqni hisoblaydi
            timetable = self._repair_unplaced(
                timetable, subjects_hours, class_level,
                max_daily, working_days, teacher_constraints, subject_teacher_map
            )

            # Yakuniy ball
            res = self.sanpin.check_timetable(timetable, class_level, tayanch_hours)
            return timetable, res['score']

        # Backtracking algoritmi
        if max_daily is None:
            max_daily = self.sanpin.max_daily_lessons.get(class_level, 7)

        # Barcha darslar ro'yxatini yaratish
        import math
        lessons = []
        for subject, hours in subjects_hours.items():
            h = math.ceil(hours) if hours != int(hours) else int(hours)
            for _ in range(h):
                lessons.append(subject)

        # Haftalik jami darslar
        total = len(lessons)
        if total == 0:
            return [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)], 0

        # TENG TAQSIMOT — har bir kun uchun aniq darslar soni
        daily_target = total // working_days
        extra = total % working_days

        daily_limits = []
        for i in range(6):
            if i < working_days:
                # Qoldiq darslar birinchi kunlarga taqsimlanadi
                if i < extra:
                    daily_limits.append(daily_target + 1)
                else:
                    daily_limits.append(daily_target)
            else:
                daily_limits.append(0)

        # SanPIN max_daily dan oshmaslik
        for i in range(6):
            if daily_limits[i] > max_daily + 1:
                daily_limits[i] = max_daily + 1

        # Slotlar ro'yxati
        slots = []
        for day in range(6):
            for period in range(daily_limits[day]):
                slots.append((day, period))

        # Maksimal qidiruv holatlarini slotlar soniga qarab moslashtirish
        self.max_states = max(self.base_max_states, len(slots) * 500)

        # Fanlar chastotasini olish
        subjects_counts = {}
        for sub in lessons:
            subjects_counts[sub] = subjects_counts.get(sub, 0) + 1

        # Har bir kun uchun fanning maksimal takrorlanish soni
        # Haftada >5 soat bo'lgan fanlar kuniga 2 marta mumkin
        max_daily_occurrences = {}
        for sub, count in subjects_counts.items():
            if sub in DAILY_OCCURRENCE_OVERRIDES or count > 5:
                max_daily_occurrences[sub] = DAILY_OCCURRENCE_OVERRIDES.get(sub, 2)
            else:
                max_daily_occurrences[sub] = 1

        # Hozirgi joylashtirilgan fanlarni saqlash
        day_subjects = {day: [] for day in range(6)}
        best_timetable_grid = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        best_score = 0
        best_filled = 0
        state_count = 0
        filled_count = [0]  # Nechta dars joylashtirildi

        # Backtracking DFS qidiruv
        def backtrack(slot_idx, current_counts, current_timetable):
            nonlocal best_score, best_timetable_grid, best_filled, state_count
            state_count += 1

            all_placed = all(c == 0 for c in current_counts.values())

            if all_placed:
                res = self.sanpin.check_timetable(current_timetable, class_level, tayanch_hours)
                score = res['score']
                if score > best_score:
                    best_score = score
                    best_timetable_grid = [row.copy() for row in current_timetable]
                    best_filled = slot_idx
                return score >= 90

            if slot_idx >= len(slots):
                return False

            if state_count > self.max_states:
                if filled_count[0] > best_filled:
                    best_filled = filled_count[0]
                    best_timetable_grid = [row.copy() for row in current_timetable]
                elif filled_count[0] == best_filled and best_score == 0:
                    best_timetable_grid = [row.copy() for row in current_timetable]
                return False

            day, period = slots[slot_idx]

            # "OYNA" oldini olish — avvalgi slot to'ldirilganmi?
            if period > 0:
                prev_filled = current_timetable[period - 1][day]
                # Agar avvalgi slot bo'sh va hali darslar qoldi — bu slotni to'ldirish shart
                if not prev_filled and any(c > 0 for c in current_counts.values()):
                    # Faqat shu slotni to'ldirishga harakat qilish
                    pass

            candidates = []
            for sub, count in current_counts.items():
                if count > 0:
                    if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                        continue

                    if teacher_constraints and subject_teacher_map:
                        tid = subject_teacher_map.get(sub)
                        if tid and (tid, day, period) in teacher_constraints:
                            continue

                    penalty = 0
                    diff = self.sanpin.get_difficulty(sub)
                    optimal_periods = self.sanpin.get_optimal_period(sub)

                    # 1-4 sinflarda ketma-ket bir xil fan taqiqlanadi
                    if class_level <= 4 and period > 0:
                        prev_sub = current_timetable[period - 1][day]
                        if prev_sub == sub:
                            penalty += 50  # Qat'iy taqiqlangan

                    # Ketma-ket qiyin fanlar (Toifa A — ball >= 11)
                    if period > 0:
                        prev_sub = current_timetable[period - 1][day]
                        if prev_sub:
                            prev_diff = self.sanpin.get_difficulty(prev_sub)
                            if diff >= 11 and prev_diff >= 11:
                                penalty += 15

                    # 1-darsda juda qiyin fan
                    if period == 0 and diff >= 13:
                        penalty += 5

                    # Oxirgi darsda qiyin fan
                    if period == daily_limits[day] - 1 and diff >= 11:
                        penalty += 5

                    # Sportdan keyin qiyin fan
                    if period > 0:
                        prev_sub = current_timetable[period - 1][day]
                        if prev_sub in SPORT_SUBJECTS and diff >= 11:
                            penalty += 10

                    # Optimal soatda emas
                    if (period + 1) not in optimal_periods:
                        penalty += 2

                    day_difficulty = sum(
                        self.sanpin.get_difficulty(current_timetable[p][day])
                        for p in range(PERIODS_PER_DAY) if current_timetable[p][day]
                    ) + diff
                    if day_difficulty > 65:  # Yangi shkala (1-13) uchun
                        penalty += 3

                    # Kunlik taqsimot — ortiqcha darsli kunga katta jazo
                    day_count = sum(1 for p in range(PERIODS_PER_DAY)
                                   if current_timetable[p][day] and current_timetable[p][day].strip())
                    day_limit = daily_limits[day] if daily_limits else PERIODS_PER_DAY
                    if day_count >= day_limit:
                        penalty += 50  # Kun to'ldi — boshqa joyga qo'yish shart
                    elif day_count > daily_target:
                        penalty += (day_count - daily_target) * 10  # Ortiqcha dars — jazo

                    candidates.append((sub, penalty))

            # Agar nomzod yo'q — keyingi slotga o'tish
            if not candidates:
                return backtrack(slot_idx + 1, current_counts, current_timetable)

            candidates.sort(key=lambda x: (x[1], random.random()))

            for sub, _ in candidates:
                current_timetable[period][day] = sub
                current_counts[sub] -= 1
                day_subjects[day].append(sub)
                filled_count[0] += 1

                if backtrack(slot_idx + 1, current_counts, current_timetable):
                    return True

                current_timetable[period][day] = ""
                current_counts[sub] += 1
                day_subjects[day].pop()
                filled_count[0] -= 1

            return False

        # Qidiruvni initsializatsiya qilish
        init_counts = subjects_counts.copy()
        init_timetable = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]

        backtrack(0, init_counts, init_timetable)

        # REPAIR: qoldiq darslarni joylashtirish
        # best_timetable_grid dagi haqiqiy darslar sonini hisoblash
        actual_counts = {}
        for day in range(6):
            for period in range(PERIODS_PER_DAY):
                sub = best_timetable_grid[period][day]
                if sub and sub.strip():
                    actual_counts[sub] = actual_counts.get(sub, 0) + 1

        # subjects_counts ni actual ga moslashtirish
        corrected_counts = {}
        for sub, count in subjects_counts.items():
            corrected_counts[sub] = count

        best_timetable_grid = self._repair_unplaced(
            best_timetable_grid, corrected_counts, class_level,
            max_daily, working_days, teacher_constraints, subject_teacher_map,
            daily_limits=daily_limits
        )

        # Yakuniy ball
        res = self.sanpin.check_timetable(best_timetable_grid, class_level, tayanch_hours)
        best_score = res['score']

        return best_timetable_grid, best_score

    def _can_place_subject(self, timetable, sub, day, period, max_daily,
                           teacher_constraints, subject_teacher_map,
                           max_daily_occurrences=None):
        """Darsni berilgan slotga qo'yish mumkinligini tekshirish"""
        # Slot to'ldirilganmi?
        if timetable[period][day] and timetable[period][day].strip():
            return False
        # O'qituvchi bandligi
        if teacher_constraints and subject_teacher_map:
            tid = subject_teacher_map.get(sub)
            if tid and (tid, day, period) in teacher_constraints:
                return False
        # Takrorlanish — fan turiga qarab cheklov
        max_per_day = 1
        if max_daily_occurrences and sub in max_daily_occurrences:
            max_per_day = max_daily_occurrences[sub]
        elif sub in DAILY_OCCURRENCE_OVERRIDES:
            max_per_day = DAILY_OCCURRENCE_OVERRIDES[sub]
        day_subs = [timetable[p][day] for p in range(PERIODS_PER_DAY)
                    if timetable[p][day] and timetable[p][day].strip()]
        if day_subs.count(sub) >= max_per_day:
            return False
        return True

    def _repair_unplaced(self, timetable, subjects_counts, class_level,
                         max_daily, working_days, teacher_constraints, subject_teacher_map,
                         daily_limits=None):
        """Qoldiq darslarni joylashtirish — oyna va takrorlanishni tuzatish"""
        if max_daily is None:
            max_daily = self.sanpin.max_daily_lessons.get(class_level, 7)

        # Kunlik takrorlanish cheklovlari
        max_daily_occurrences = {}
        for sub, count in subjects_counts.items():
            if sub in DAILY_OCCURRENCE_OVERRIDES or count > 5:
                max_daily_occurrences[sub] = DAILY_OCCURRENCE_OVERRIDES.get(sub, 2)
            else:
                max_daily_occurrences[sub] = 1

        # Qoldiq darslarni aniqlash — Counter ishlatish (xavfsiz)
        from collections import Counter
        placed = {}
        for day in range(6):
            for period in range(PERIODS_PER_DAY):
                sub = timetable[period][day]
                if sub and sub.strip():
                    placed[sub] = placed.get(sub, 0) + 1

        unplaced_counter = Counter()
        for sub, count in subjects_counts.items():
            placed_count = placed.get(sub, 0)
            remaining = int(count - placed_count)
            if remaining > 0:
                unplaced_counter[sub] = remaining

        if not unplaced_counter:
            return timetable

        # 1-QADAM: Bo'sh slotlarga to'g'ridan-to'g'ri qo'yish — kun limitini hisobga olgan holda
        # Avval kam darsli kunlardan boshlash
        for sub in list(unplaced_counter.keys()):
            # Kunlarni darslar soni bo'yicha tartiblash — eng kam darsli birinchi
            day_loads = []
            for day in range(working_days):
                day_count = sum(1 for p in range(PERIODS_PER_DAY)
                               if timetable[p][day] and timetable[p][day].strip())
                day_loads.append((day_count, day))
            day_loads.sort()

            for _, day in day_loads:
                max_period = daily_limits[day] if daily_limits else PERIODS_PER_DAY
                # Kun to'ldi — o'tkazib yuborish
                day_count = sum(1 for p in range(PERIODS_PER_DAY)
                               if timetable[p][day] and timetable[p][day].strip())
                if day_count >= max_period:
                    continue
                for period in range(max_period):
                    if not self._can_place_subject(timetable, sub, day, period,
                                                   max_daily, teacher_constraints,
                                                   subject_teacher_map,
                                                   max_daily_occurrences):
                        continue
                    timetable[period][day] = sub
                    unplaced_counter[sub] -= 1
                    if unplaced_counter[sub] <= 0:
                        del unplaced_counter[sub]
                    break
                if sub not in unplaced_counter:
                    break

        if not unplaced_counter:
            # Hali ham oyna bo'lishi mumkin — tuzatish kerak
            for day in range(working_days):
                self._fix_gaps(timetable, day, max_daily, class_level)
            return timetable

        # 2-QADAM: "OYNA" tuzatish — bo'sh slotlarni siljitib to'ldirish
        for day in range(working_days):
            self._fix_gaps(timetable, day, max_daily, class_level)

        # 3-QADAM: Swop — mavjud darsni boshqa slotga ko'chirib
        for sub in list(unplaced_counter.keys()):
            if not (teacher_constraints and subject_teacher_map):
                continue
            tid = subject_teacher_map.get(sub)
            if not tid:
                continue
            occupied_slots = []
            for day in range(working_days):
                max_period = daily_limits[day] if daily_limits else PERIODS_PER_DAY
                for period in range(max_period):
                    if (tid, day, period) in teacher_constraints:
                        if timetable[period][day] and timetable[period][day].strip():
                            occupied_slots.append((day, period, timetable[period][day]))

            for day, period, existing_sub in occupied_slots:
                max_per_day = max_daily_occurrences.get(existing_sub, 1)
                for new_day in range(working_days):
                    new_max_period = daily_limits[new_day] if daily_limits else PERIODS_PER_DAY
                    for new_period in range(new_max_period):
                        if new_day == day and new_period == period:
                            continue
                        if timetable[new_period][new_day] and timetable[new_period][new_day].strip():
                            continue
                        if (tid, new_day, new_period) in teacher_constraints:
                            continue
                        day_subs = [timetable[p][new_day] for p in range(PERIODS_PER_DAY)
                                    if timetable[p][new_day] and timetable[p][new_day].strip()]
                        if day_subs.count(existing_sub) >= max_per_day:
                            continue
                        timetable[new_period][new_day] = existing_sub
                        timetable[period][day] = sub
                        unplaced_counter[sub] -= 1
                        if unplaced_counter[sub] <= 0:
                            del unplaced_counter[sub]
                        break
                    if sub not in unplaced_counter:
                        break
                if sub not in unplaced_counter:
                    break

        # 4-QADAM: Majburiy qo'yish — avval takrorlanishni saqlab, keyin buzoq
        for sub in list(unplaced_counter.keys()):
            # Avval takrorlanishni SAQLAB qo'yadigan joy topish
            placed = False
            for day in range(working_days):
                max_period = daily_limits[day] if daily_limits else PERIODS_PER_DAY
                for period in range(max_period):
                    if timetable[period][day] and timetable[period][day].strip():
                        continue
                    if teacher_constraints and subject_teacher_map:
                        tid = subject_teacher_map.get(sub)
                        if tid and (tid, day, period) in teacher_constraints:
                            continue
                    # Kunlik takrorlanishni tekshirish
                    day_subs = [timetable[p][day] for p in range(PERIODS_PER_DAY)
                                if timetable[p][day] and timetable[p][day].strip()]
                    max_per_day = max_daily_occurrences.get(sub, 1) if max_daily_occurrences else 1
                    if day_subs.count(sub) < max_per_day:
                        timetable[period][day] = sub
                        unplaced_counter[sub] -= 1
                        if unplaced_counter[sub] <= 0:
                            del unplaced_counter[sub]
                        placed = True
                        break
                if placed:
                    break

            # Agar takrorlanishni saqlab bo'lmasa — majburiy qo'yish
            if sub in unplaced_counter:
                for day in range(working_days):
                    max_period = daily_limits[day] if daily_limits else PERIODS_PER_DAY
                    for period in range(max_period):
                        if timetable[period][day] and timetable[period][day].strip():
                            continue
                        if teacher_constraints and subject_teacher_map:
                            tid = subject_teacher_map.get(sub)
                            if tid and (tid, day, period) in teacher_constraints:
                                continue
                        timetable[period][day] = sub
                        unplaced_counter[sub] -= 1
                        if unplaced_counter[sub] <= 0:
                            del unplaced_counter[sub]
                        placed = True
                        break
                    if placed:
                        break

        # Yakuniy "oyna" tuzatish
        for day in range(working_days):
            self._fix_gaps(timetable, day, max_daily, class_level)

        return timetable

    def _fix_gaps(self, timetable, day, max_daily, class_level=None):
        """Bir kundagi bo'sh slotlarni tuzatish — SanPIN tartibini saqlab"""
        lessons = []
        for period in range(PERIODS_PER_DAY):
            sub = timetable[period][day]
            if sub and sub.strip():
                lessons.append(sub)
            else:
                lessons.append("")

        gaps = [i for i, s in enumerate(lessons) if not s]
        filled = [i for i, s in enumerate(lessons) if s]

        if not gaps or not filled:
            return

        # Compaction: darslarni tepaga siljitish
        new_lessons = [""] * PERIODS_PER_DAY
        idx = 0
        for sub in lessons:
            if sub:
                while idx < PERIODS_PER_DAY and new_lessons[idx]:
                    idx += 1
                if idx < PERIODS_PER_DAY:
                    new_lessons[idx] = sub
                    idx += 1

        # SanPIN tartibini tuzatish: ketma-ket tekshirish
        self._reorder_for_sanpin(new_lessons, day, class_level)

        for period in range(PERIODS_PER_DAY):
            timetable[period][day] = new_lessons[period]

        return timetable

    def _reorder_for_sanpin(self, lessons, day, class_level=None):
        """SanPIN qoidalariga mos tartib — takroriy yaxshilash"""
        if not lessons or all(not s for s in lessons):
            return

        filled_indices = [i for i, s in enumerate(lessons) if s]
        filled_subs = [lessons[i] for i in filled_indices]

        if len(filled_subs) <= 1:
            return

        # Takroriy yaxshilash — barcha qoidalarni bir vaqtda tekshirish
        for _ in range(3):
            improved = False
            for i in range(len(filled_subs) - 1):
                # 1-4 sinflarda bir xil fanlar ketma-ket kelmasin
                if class_level is not None and class_level <= 4:
                    if filled_subs[i] == filled_subs[i + 1]:
                        for j in range(i + 2, len(filled_subs)):
                            if filled_subs[j] != filled_subs[i]:
                                filled_subs[i + 1], filled_subs[j] = filled_subs[j], filled_subs[i + 1]
                                improved = True
                                break

                # Qiyin fanlar ketma-ket kelmasin
                d1 = self.sanpin.get_difficulty(filled_subs[i])
                d2 = self.sanpin.get_difficulty(filled_subs[i + 1])
                if d1 >= 11 and d2 >= 11:
                    for j in range(i + 2, len(filled_subs)):
                        if self.sanpin.get_difficulty(filled_subs[j]) <= 5:
                            filled_subs[i + 1], filled_subs[j] = filled_subs[j], filled_subs[i + 1]
                            improved = True
                            break

                # Sportdan keyin qiyin fan kelmasin
                if filled_subs[i] in SPORT_SUBJECTS:
                    if self.sanpin.get_difficulty(filled_subs[i + 1]) >= 11:
                        for j in range(i + 2, len(filled_subs)):
                            if self.sanpin.get_difficulty(filled_subs[j]) <= 5:
                                filled_subs[i + 1], filled_subs[j] = filled_subs[j], filled_subs[i + 1]
                                improved = True
                                break

            if not improved:
                break

        # Natijani qayta yozish
        for idx, sub in zip(filled_indices, filled_subs):
            lessons[idx] = sub

    def _enforce_even(self, timetable, working_days, teacher_constraints, subject_teacher_map, class_level):
        """Teng taqsimotni ta'minlash — oynasiz, swap orqali"""
        import math

        # Har bir kun uchun darslar sonini oldindan hisoblash
        day_counts = []
        for day in range(working_days):
            count = sum(1 for p in range(PERIODS_PER_DAY)
                        if timetable[p][day] and timetable[p][day].strip())
            day_counts.append(count)

        total = sum(day_counts)
        if total == 0:
            return

        target = total // working_days
        extra = total % working_days

        # 1-QADAM: Ortiqchalarni kam darsli kunlarga siljitish
        for _ in range(15):
            moved_any = False
            for day in range(working_days):
                limit = target + 1 if day < extra else target
                if day_counts[day] <= limit:
                    continue

                underfilled = []
                for td in range(working_days):
                    t_limit = target + 1 if td < extra else target
                    if day_counts[td] < t_limit:
                        underfilled.append((day_counts[td], td))
                underfilled.sort()

                if not underfilled:
                    continue

                # Barcha periodlardan siljitishga harakat qilish
                for period in range(PERIODS_PER_DAY - 1, -1, -1):
                    sub = timetable[period][day]
                    if not sub or not sub.strip():
                        continue

                    for _, td in underfilled:
                        for t_period in range(PERIODS_PER_DAY):
                            if timetable[t_period][td] and timetable[t_period][td].strip():
                                continue
                            if teacher_constraints and subject_teacher_map:
                                tid = subject_teacher_map.get(sub)
                                if tid and (tid, td, t_period) in teacher_constraints:
                                    continue
                            # Kunlik takrorlanish tekshirish
                            td_subs = [timetable[p][td] for p in range(PERIODS_PER_DAY)
                                       if timetable[p][td] and timetable[p][td].strip()]
                            max_per_day = DAILY_OCCURRENCE_OVERRIDES.get(sub, 1)
                            if td_subs.count(sub) >= max_per_day:
                                continue  # Bu kun allaqachon shu dars yetarli

                            timetable[t_period][td] = sub
                            timetable[period][day] = ""
                            day_counts[day] -= 1
                            day_counts[td] += 1
                            moved_any = True
                            break
                        if moved_any:
                            break
                    if moved_any:
                        break

            if not moved_any:
                break

        # 2-QADAM: SWAP — ortiqcha kunlardagi darsni kam kunlardagi dars bilan almashish
        for _ in range(10):
            moved_any = False
            for day in range(working_days):
                limit = target + 1 if day < extra else target
                if day_counts[day] <= limit:
                    continue

                underfilled = []
                for td in range(working_days):
                    t_limit = target + 1 if td < extra else target
                    if day_counts[td] < t_limit:
                        underfilled.append((day_counts[td], td))
                underfilled.sort()

                if not underfilled:
                    continue

                # Ortiqucha kunning darslarini tekshirish
                for period in range(PERIODS_PER_DAY):
                    sub = timetable[period][day]
                    if not sub or not sub.strip():
                        continue

                    for _, td in underfilled:
                        # Kam kunning darslarini topish — almashtirish uchun
                        for t_period in range(PERIODS_PER_DAY):
                            t_sub = timetable[t_period][td]
                            if not t_sub or not t_sub.strip():
                                continue

                            # SWAP: ikkala darsni almashish
                            # Teacher constraints tekshirish
                            if teacher_constraints and subject_teacher_map:
                                tid1 = subject_teacher_map.get(sub)
                                tid2 = subject_teacher_map.get(t_sub)
                                if tid1 and (tid1, td, t_period) in teacher_constraints:
                                    continue
                                if tid2 and (tid2, day, period) in teacher_constraints:
                                    continue

                            # Kunlik takrorlanish tekshirish
                            day_subs_day = [timetable[p][day] for p in range(PERIODS_PER_DAY)
                                           if timetable[p][day] and timetable[p][day].strip()]
                            day_subs_td = [timetable[p][td] for p in range(PERIODS_PER_DAY)
                                          if timetable[p][td] and timetable[p][td].strip()]

                            if day_subs_day.count(t_sub) >= 1:
                                continue
                            if day_subs_td.count(sub) >= 1:
                                continue

                            # SWAP bajarish
                            timetable[period][day] = t_sub
                            timetable[t_period][td] = sub
                            day_counts[day] -= 1
                            day_counts[td] += 1
                            moved_any = True
                            break
                        if moved_any:
                            break
                    if moved_any:
                        break
                if moved_any:
                    break

            if not moved_any:
                break

        # 3-QADAM: Compaction — barcha kunlarni tekshirish
        for day in range(working_days):
            filled = []
            for period in range(PERIODS_PER_DAY):
                sub = timetable[period][day]
                if sub and sub.strip():
                    filled.append(sub)
            for period in range(PERIODS_PER_DAY):
                timetable[period][day] = ""
            for i, sub in enumerate(filled):
                timetable[i][day] = sub

    def _redistribute_all_data(self, all_data, sorted_classes, teacher_schedule):
        """ALL_DATA da kunlar orasida teng taqsimotni ta'minlash"""
        for cls in sorted_classes:
            class_id = cls[0]
            working_days = cls[4] if len(cls) > 4 and cls[4] else 6

            # Har bir kun uchun darslar sonini hisoblash
            day_counts = {}
            for day in range(6):
                day_counts[day] = 0
                for period in range(PERIODS_PER_DAY):
                    key = (class_id, day, period)
                    if key in all_data and all_data[key].get('subject_name', '').strip():
                        day_counts[day] += 1

            total = sum(day_counts.values())
            if total == 0:
                continue

            target = total // working_days
            extra = total % working_days

            # Ish kunlaridan tashqari kunlardagi darslarni ish kunlariga ko'chirish
            for day in range(working_days, 6):
                for period in range(PERIODS_PER_DAY):
                    key = (class_id, day, period)
                    if key not in all_data:
                        continue
                    entry = all_data[key]
                    if not entry.get('subject_name', '').strip():
                        continue

                    teacher_id = entry.get('teacher_id', 0)

                    # Bo'sh slot topish — ish kunlarida
                    moved = False
                    for td in range(working_days):
                        if day_counts[td] >= target + 1:
                            continue
                        # Kunlik takrorlanish tekshirish
                        td_subs = [all_data[(class_id, td, p)].get('subject_name', '')
                                   for p in range(PERIODS_PER_DAY)
                                   if (class_id, td, p) in all_data and all_data[(class_id, td, p)].get('subject_name', '').strip()]
                        sub_name = entry.get('subject_name', '')
                        max_per_day = DAILY_OCCURRENCE_OVERRIDES.get(sub_name, 1)
                        if td_subs.count(sub_name) >= max_per_day:
                            continue
                        for t_period in range(PERIODS_PER_DAY):
                            t_key = (class_id, td, t_period)
                            if t_key in all_data and all_data[t_key].get('subject_name', '').strip():
                                continue
                            if teacher_id and (teacher_id, td, t_period) in teacher_schedule:
                                continue

                            all_data[t_key] = entry
                            del all_data[key]
                            day_counts[day] -= 1
                            day_counts[td] += 1
                            moved = True
                            break
                        if moved:
                            break
                    if not moved:
                        # Agar barcha ish kunlari to'lib bo'lsa — eng kam darsli kun
                        min_day = min(range(working_days), key=lambda d: day_counts[d])
                        for t_period in range(PERIODS_PER_DAY):
                            t_key = (class_id, min_day, t_period)
                            if t_key in all_data and all_data[t_key].get('subject_name', '').strip():
                                continue
                            if teacher_id and (teacher_id, min_day, t_period) in teacher_schedule:
                                continue

                            all_data[t_key] = entry
                            del all_data[key]
                            day_counts[day] -= 1
                            day_counts[min_day] += 1
                            moved = True
                            break

            # Ortiqucha kunlardan kam kunlarga siljitish
            for _ in range(15):
                moved_any = False
                for day in range(working_days):
                    limit = target + 1 if day < extra else target
                    if day_counts[day] <= limit:
                        continue

                    underfilled = []
                    for td in range(working_days):
                        t_limit = target + 1 if td < extra else target
                        if day_counts[td] < t_limit:
                            underfilled.append((day_counts[td], td))
                    underfilled.sort()

                    if not underfilled:
                        continue

                    for period in range(PERIODS_PER_DAY - 1, -1, -1):
                        key = (class_id, day, period)
                        if key not in all_data:
                            continue
                        entry = all_data[key]
                        if not entry.get('subject_name', '').strip():
                            continue

                        sub = entry['subject_name']
                        teacher_id = entry.get('teacher_id', 0)

                        for _, td in underfilled:
                            # Kunlik takrorlanish tekshirish
                            td_subs = [all_data[(class_id, td, p)].get('subject_name', '')
                                       for p in range(PERIODS_PER_DAY)
                                       if (class_id, td, p) in all_data and all_data[(class_id, td, p)].get('subject_name', '').strip()]
                            max_per_day = DAILY_OCCURRENCE_OVERRIDES.get(sub, 1)
                            if td_subs.count(sub) >= max_per_day:
                                continue
                            for t_period in range(PERIODS_PER_DAY):
                                t_key = (class_id, td, t_period)
                                if t_key in all_data and all_data[t_key].get('subject_name', '').strip():
                                    continue
                                if teacher_id and (teacher_id, td, t_period) in teacher_schedule:
                                    continue

                                all_data[t_key] = entry
                                del all_data[key]
                                day_counts[day] -= 1
                                day_counts[td] += 1
                                moved_any = True
                                break
                            if moved_any:
                                break
                        if moved_any:
                            break

                if not moved_any:
                    break

            # Compaction — kun ichida siljitish + TAKRORLANISHLARNI TUXATISH
            for day in range(6):
                entries = []
                seen = {}
                for period in range(PERIODS_PER_DAY):
                    key = (class_id, day, period)
                    if key in all_data and all_data[key].get('subject_name', '').strip():
                        sub = all_data[key]['subject_name']
                        max_per_day = 2 if sub in DAILY_OCCURRENCE_OVERRIDES else 1
                        count = seen.get(sub, 0)
                        if count < max_per_day:
                            entries.append(all_data[key])
                            seen[sub] = count + 1

                for period in range(PERIODS_PER_DAY):
                    key = (class_id, day, period)
                    if key in all_data:
                        del all_data[key]

                # Darslarni 0..N-1 ga siljitish — O'QITUVCHI BANDLIGINI TEKSHIRISH
                placed = []
                skipped = []
                for entry in entries:
                    teacher_id = entry.get('teacher_id', 0)
                    target_slot = len(placed)
                    if teacher_id and (teacher_id, day, target_slot) in teacher_schedule:
                        skipped.append(entry)
                    else:
                        placed.append(entry)
                for entry in skipped:
                    teacher_id = entry.get('teacher_id', 0)
                    found = False
                    for p in range(PERIODS_PER_DAY):
                        if p < len(placed):
                            continue
                        if teacher_id and (teacher_id, day, p) in teacher_schedule:
                            continue
                        placed.append(entry)
                        found = True
                        break
                    if not found:
                        placed.append(entry)
                for i, entry in enumerate(placed):
                    all_data[(class_id, day, i)] = entry

    def generate_all_class_timetables(self, classes, db_manager, cancel_flag=None, progress_callback=None):
        """
        Barcha sinflar uchun avtomatik jadval tuzish (PARALLEL).
        Katta hajm uchun tezlashtirilgan: ThreadPoolExecutor ishlatiladi.

        classes: db.get_all_classes() natijasi
        db_manager: DatabaseManager instansiyasi
        cancel_flag: callable — True qaytarsa to'xtatiladi
        progress_callback: callable(class_name, idx, total, score) — har sinf tugagandan keyin

        Qaytaradi:
            timetable_data: {(class_id, day, period): lesson_data}
            conflicts: [(teacher_name, class1, class2, day, period), ...]
        """
        all_data = {}
        conflicts = []

        # CPU yadrolar soni — parallellik darajasi
        max_workers = min(8, os.cpu_count() or 4)

        # Kelajak soati kunini olish
        kelajak_day_str = db_manager.get_setting("kelajak_day", "4") if hasattr(db_manager, 'get_setting') else "4"
        try:
            kelajak_day = int(kelajak_day_str)
        except (ValueError, TypeError):
            kelajak_day = 4
        if kelajak_day < 0 or kelajak_day > 5:
            kelajak_day = 4

        # O'qituvchilarning metodik kunlari va band soatlarini oldindan qo'shish
        teacher_schedule = {}  # {(teacher_id, day, period): class_name}
        all_teachers = db_manager.get_all_teachers()
        kelajak_map = {}  # {class_id: {'subject': ..., 'teacher_id': ...}}

        for t in all_teachers:
            t_id = t[0]
            methodic_day = t[5]
            if methodic_day is not None and methodic_day != '':
                try:
                    methodic_day = int(methodic_day)
                except (ValueError, TypeError):
                    methodic_day = None
            if methodic_day is not None and 0 <= methodic_day < 6:
                for p in range(PERIODS_PER_DAY):
                    teacher_schedule[(t_id, methodic_day, p)] = "methodic_day"

            unavail = db_manager.get_teacher_unavailable(t_id)
            for (day, period, avail_type) in unavail:
                if 0 <= day < 6 and 0 <= period < PERIODS_PER_DAY:
                    if avail_type == 'strict':
                        teacher_schedule[(t_id, day, period)] = "unavailable"

            class_teacher_of = t[4] if len(t) > 4 else None
            if class_teacher_of:
                t_assignments = db_manager.get_class_assignments(class_teacher_of)
                for a in t_assignments:
                    if 'kelajak' in (a[1] or '').lower():
                        kelajak_map[class_teacher_of] = {
                            'subject': a[1], 'teacher_id': t_id,
                            'lesson_id': a[0], 'subject_id': a[5],
                            'teacher_name': a[2], 'teacher_color': a[3],
                            'teacher_short': a[7] if len(a) > 7 else '',
                            'weekly_hours': a[4],
                        }
                        break

        # Sinf → biriktirilgan darslar xaritasi
        class_assignments = {}
        for cls in classes:
            class_id = cls[0]
            class_name = cls[1]
            working_days = cls[4] if len(cls) > 4 and cls[4] else 6

            assignments = db_manager.get_class_assignments(class_id)
            if not assignments:
                continue

            subjects_hours = {}
            lesson_info = {}
            subject_teacher_map = {}

            for assignment in assignments:
                lesson_id = assignment[0]
                subject_name = assignment[1]
                teacher_name = assignment[2]
                teacher_color = assignment[3]
                weekly_hours = assignment[4]
                subject_id = assignment[5]
                teacher_id = assignment[6]

                if subject_name in subjects_hours:
                    subjects_hours[subject_name] += weekly_hours
                else:
                    subjects_hours[subject_name] = weekly_hours

                lesson_info[subject_name] = {
                    'lesson_id': lesson_id,
                    'subject_name': subject_name,
                    'subject_short': subject_name[:3],
                    'subject_id': subject_id,
                    'teacher_name': teacher_name,
                    'teacher_short': assignment[7] if len(assignment) > 7 else '',
                    'teacher_id': teacher_id,
                    'class_id': class_id,
                    'class_name': class_name,
                    'color': teacher_color,
                    'weekly_hours': weekly_hours,
                }
                subject_teacher_map[subject_name] = teacher_id

            class_assignments[class_id] = {
                'class_name': class_name,
                'working_days': working_days,
                'subjects_hours': subjects_hours,
                'lesson_info': lesson_info,
                'subject_teacher_map': subject_teacher_map,
            }

        # O'qituvchi bandligini hisoblash
        teacher_class_count = {}
        for cid, ca in class_assignments.items():
            for sub, tid in ca['subject_teacher_map'].items():
                teacher_class_count[tid] = teacher_class_count.get(tid, 0) + 1

        # Sinflarni tartibga solish — eng og'ir o'qituvchi yuklamasi birinchi
        def class_priority(cls):
            cid = cls[0]
            if cid not in class_assignments:
                return (999, 0)
            ca = class_assignments[cid]
            scarce_teachers = 0
            for sub, tid in ca['subject_teacher_map'].items():
                if teacher_class_count.get(tid, 0) <= 3:
                    scarce_teachers += 1
            total_hours = sum(ca['subjects_hours'].values())
            return (-scarce_teachers, -total_hours)

        sorted_classes = sorted(
            [cls for cls in classes if cls[0] in class_assignments],
            key=class_priority
        )

        # ============================================================
        # BATCH SCHEDULING — sinflarni guruhlarda jadval tuzish
        # ============================================================
        # Kelajak soatini aniqlash
        for cls in sorted_classes:
            class_id = cls[0]
            if class_id in kelajak_map:
                k_info = kelajak_map[class_id]
                class_assignments[class_id]['kelajak_subject'] = k_info['subject']
                class_assignments[class_id]['kelajak_info'] = k_info

        total_classes = len(sorted_classes)
        results = [None] * total_classes
        processed_count = 0

        # ============================================================
        # SEQUENTIAL SCHEDULING — sinflarni birma-bir jadval tuzish
        # + ALL_DATA COMPACTION — oynalarni tuzatish
        # ============================================================
        # Har sinf oldingi sinflarning teacher_schedule ni ko'radi
        # Ziddiyatlar kam bo'ladi, compaction oynalarni tuzatadi

        for idx, cls in enumerate(sorted_classes):
            if cancel_flag and cancel_flag():
                break

            class_id = cls[0]
            class_name = cls[1]
            working_days = cls[4] if len(cls) > 4 and cls[4] else 6

            ca = class_assignments[class_id]
            subjects_hours = dict(ca['subjects_hours'])
            lesson_info = ca['lesson_info']
            stm = dict(ca['subject_teacher_map'])
            class_level = cls[2] if len(cls) > 2 else 5

            # TO'LIQ teacher_schedule — oldingi barcha sinflarning natijalari
            teacher_constraints = dict(teacher_schedule)

            scheduler = TimetableScheduler(algorithm=self.algorithm, db_manager=self.db)
            timetable, score = scheduler.generate_timetable(
                subjects_hours, class_level, working_days=working_days,
                teacher_constraints=teacher_constraints,
                subject_teacher_map=stm
            )

            result = {
                'class_id': class_id,
                'class_name': class_name,
                'class_level': class_level,
                'working_days': working_days,
                'timetable': timetable,
                'score': score,
                'lesson_info': lesson_info,
                'subject_teacher_map': stm,
                'kelajak_subject': class_assignments[class_id].get('kelajak_subject'),
                'kelajak_info': class_assignments[class_id].get('kelajak_info'),
            }

            results[idx] = result
            processed_count += 1

            # Teacher_schedule ga qo'shish — keyingi sinf shu ma'lumotdan foydalanadi
            self._add_result_to_teacher_schedule(result, teacher_schedule)

            if progress_callback:
                progress_callback(class_name, processed_count, total_classes, score)

        # ============================================================
        # NATIJALARNI QAYTA ISHLASH — all_data ni to'ldirish
        # ============================================================
        for result in results:
            if result is None:
                continue

            class_id = result['class_id']
            class_name = result['class_name']
            timetable = result['timetable']
            lesson_info = result['lesson_info']
            stm = result['subject_teacher_map']
            working_days = result['working_days']

            # Kelajak soatini siljitish
            kelajak_subject = class_assignments[class_id].get('kelajak_subject')
            kelajak_info = class_assignments[class_id].get('kelajak_info')

            if kelajak_subject and kelajak_info:
                target_day = kelajak_day
                target_period = 0

                kelajak_old_day = None
                kelajak_old_period = None
                for day in range(6):
                    for period in range(PERIODS_PER_DAY):
                        if timetable[period][day] == kelajak_subject:
                            kelajak_old_day = day
                            kelajak_old_period = period
                            break
                    if kelajak_old_day is not None:
                        break

                if kelajak_old_day is not None:
                    old_key = (kelajak_info['teacher_id'], kelajak_old_day, kelajak_old_period)
                    if old_key in teacher_schedule:
                        del teacher_schedule[old_key]

                    if kelajak_old_day == target_day and kelajak_old_period == target_period:
                        pass
                    elif timetable[target_period][target_day] and timetable[target_period][target_day].strip():
                        swap_subject = timetable[target_period][target_day]
                        timetable[kelajak_old_period][kelajak_old_day] = swap_subject
                        timetable[target_period][target_day] = kelajak_subject
                    else:
                        timetable[kelajak_old_period][kelajak_old_day] = ""
                        timetable[target_period][target_day] = kelajak_subject

                all_data[(class_id, target_day, target_period)] = {
                    'lesson_id': kelajak_info['lesson_id'],
                    'subject_name': kelajak_subject,
                    'subject_short': kelajak_subject[:3],
                    'subject_id': kelajak_info['subject_id'],
                    'teacher_name': kelajak_info['teacher_name'],
                    'teacher_short': kelajak_info['teacher_short'],
                    'teacher_id': kelajak_info['teacher_id'],
                    'class_id': class_id,
                    'class_name': class_name,
                    'color': kelajak_info['teacher_color'],
                    'weekly_hours': kelajak_info['weekly_hours'],
                }

            # Teng taqsimotni tiklash
            self._enforce_even(timetable, working_days, teacher_schedule, stm, result['class_level'])

            # Oynalarni tuzatish + TAKRORLANISHLARNI TUXATISH — _enforce_even dan keyin
            for day in range(working_days):
                day_lessons = [timetable[p][day] for p in range(PERIODS_PER_DAY)]
                filled = [s for s in day_lessons if s and s.strip()]

                # Takrorlanishlarni tuzatish — bir xil fan 1 marta (Matematika/Algebra/Sport istisno)
                deduped = []
                seen = {}
                for sub in filled:
                    max_per_day = 2 if sub in DAILY_OCCURRENCE_OVERRIDES else 1
                    count = seen.get(sub, 0)
                    if count < max_per_day:
                        deduped.append(sub)
                        seen[sub] = count + 1

                # Barcha bo'sh slotlarni to'ldirish — darslarni tepaga siljitish
                for period in range(PERIODS_PER_DAY):
                    timetable[period][day] = ""
                for i, sub in enumerate(deduped):
                    timetable[i][day] = sub

            # Ballni qayta hisoblash
            res = self.sanpin.check_timetable(timetable, result['class_level'])
            score = res['score']

            # all_data va teacher_schedule ni to'ldirish
            # To'g'ridan-to'g'ri timetable dan — barcha slotlar
            for period in range(len(timetable)):
                for day in range(len(timetable[period]) if timetable[period] else 0):
                    subject_name = timetable[period][day]
                    if subject_name and subject_name.strip():
                            # lesson_info dan topish — asosiy key yoki takroriy
                            info = lesson_info.get(subject_name)
                            if not info:
                                # Takroriy fan — "_2", "_3" ... sinash
                                for suffix in range(2, 20):
                                    info = lesson_info.get(f"{subject_name}_{suffix}")
                                    if info:
                                        break
                            if info:
                                teacher_id = info['teacher_id']
                                t_key = (teacher_id, day, period)
                                teacher_schedule[t_key] = class_name
                                all_data[(class_id, day, period)] = info.copy()
                            else:
                                # lesson_info da topilmadi — placeholder
                                all_data[(class_id, day, period)] = {
                                    'subject_name': subject_name,
                                    'subject_short': subject_name[:3],
                                    'teacher_name': '',
                                    'teacher_id': 0,
                                    'class_id': class_id,
                                    'class_name': class_name,
                                    'color': '#999999',
                                }

        # ============================================================
        # O'QITUVCHI ZIDDYIYATLARINI ANIQLASH VA HAL QILISH
        # ============================================================
        conflicts = self._detect_teacher_conflicts(all_data)

        # Ziddiyatlarni avtomatik hal qilish — swap orqali (ko'proq iteratsiya)
        for _ in range(10):
            if not conflicts:
                break
            self._resolve_conflicts(all_data)
            conflicts = self._detect_teacher_conflicts(all_data)

        # ============================================================
        # ALL_DATA COMPACTION — oynalarni tuzatish + TAKRORLANISHLARNI TUXATISH
        # Har bir sinfning kunlari bo'yicha darslarni 0..N-1 ga siljitish
        # ============================================================
        for cls in sorted_classes:
            class_id = cls[0]
            for day in range(6):
                # Kun ichidagi darslarni yig'ish — TAKRORLANISHLARNI FILTRLASH
                day_entries = []
                seen = {}
                for period in range(PERIODS_PER_DAY):
                    key = (class_id, day, period)
                    if key in all_data and all_data[key].get('subject_name', '').strip():
                        sub = all_data[key]['subject_name']
                        max_per_day = 2 if sub in DAILY_OCCURRENCE_OVERRIDES else 1
                        count = seen.get(sub, 0)
                        if count < max_per_day:
                            day_entries.append((period, all_data[key]))
                            seen[sub] = count + 1

                # Doimo kompaktlash — takrorlanishlarni tuzatish uchun
                for period in range(PERIODS_PER_DAY):
                    key = (class_id, day, period)
                    if key in all_data:
                        del all_data[key]
# Darslarni 0..N-1 ga siljitish — O'QITUVCHI BANDLIGINI TEKSHIRISH
                placed_entries = []
                skip_entries = []
                for i, (old_period, entry) in enumerate(day_entries):
                    teacher_id = entry.get('teacher_id', 0)
                    if teacher_id and (teacher_id, day, i) in teacher_schedule:
                        skip_entries.append(entry)
                    else:
                        placed_entries.append(entry)
                for entry in skip_entries:
                    teacher_id = entry.get('teacher_id', 0)
                    placed = False
                    for p in range(PERIODS_PER_DAY):
                        if (class_id, day, p) in all_data:
                            continue
                        if teacher_id and (teacher_id, day, p) in teacher_schedule:
                            continue
                        placed_entries.append(entry)
                        placed = True
                        break
                    if not placed:
                        placed_entries.append(entry)
                for i, entry in enumerate(placed_entries):
                    all_data[(class_id, day, i)] = entry

        # ============================================================
        # ALL_DATA REDISTRIBUTION — kunlar orasida teng taqsimot
        # ============================================================
        self._redistribute_all_data(all_data, sorted_classes, teacher_schedule)

        # ============================================================
        # 2-HAFTA GENERATSIYA — kasrli soatlar uchun almashtirish
        # ============================================================
        week2_data = self._generate_week2(all_data, sorted_classes, class_assignments)

        # ============================================================
        # WEEK2 COMPACTION — _generate_week2 dan keyin oynalarni tuzatish
        # ============================================================
        for cls in sorted_classes:
            class_id = cls[0]
            for day in range(6):
                day_entries = []
                for period in range(PERIODS_PER_DAY):
                    key = (class_id, day, period)
                    if key in week2_data and week2_data[key].get('subject_name', '').strip():
                        day_entries.append((period, week2_data[key]))

                if len(day_entries) >= PERIODS_PER_DAY:
                    continue

                for period in range(PERIODS_PER_DAY):
                    key = (class_id, day, period)
                    if key in week2_data:
                        del week2_data[key]

                for i, (old_period, entry) in enumerate(day_entries):
                    week2_data[(class_id, day, i)] = entry

        return all_data, conflicts, week2_data

    def _generate_week2(self, week1_data, sorted_classes, class_assignments):
        """
        2-haftani 1-hafta asosida generatsiya qilish.
        - 1-hafta: ceil(hours) bilan jadval tuziladi (0,5 → 1 soat, 1,5 → 2 soat)
        - 2-hafta: 1-hafta nusxasi + kasrli fanlarni almashtirish

        Muhim: 0,5 soatlik fanlar 2 xil bo'ladi:
        1. Juftlik (Geografiya 1,5 + Iqtisodiy 0,5) — 2-haftada almashtiriladi
        2. Alohida (Musiqa 0,5) — 1-haftada qo'yiladi, 2-haftada YO'Q
        """
        import math

        # 2-hafta = 1-hafta nusxasi
        week2 = {k: v.copy() for k, v in week1_data.items()}

        # Har bir sinf uchun kasrli soatli fanlarni topish
        for cls in sorted_classes:
            class_id = cls[0]

            # Kasrli soatli fanlarni ajratish
            half_subjects = []      # 0,5 soatliklar (alohida yoki juftlik)
            bigger_subjects = []    # 1,5+ soatliklar

            for subject, hours in class_assignments.get(class_id, {}).get('subjects_hours', {}).items():
                if hours == int(hours):
                    continue  # Butun sonli — qiziqmaslik
                if hours < 1:
                    half_subjects.append((subject, hours))
                else:
                    bigger_subjects.append((subject, hours))

            if not half_subjects:
                continue

            # Cache: alohida 0,5 soatlik fanlarni bir marta yuklash
            standalone_subjects = self.db.get_standalone_half_subjects(class_id)
            standalone_names = set(standalone_subjects.values())

            # 1. Alohida 0,5 soatlik fanlar — 2-haftadan o'chirish
            # (1-haftada allaqachon qo'yilgan, 2-haftada kerak emas)
            for subject, hours in half_subjects:
                if subject in standalone_names:
                    # 2-haftadan o'chirish
                    for k in list(week2.keys()):
                        if k[0] == class_id and week2[k].get('subject_name') == subject:
                            del week2[k]
                            break

            # 2. Juftlikdagi 0,5 soatlik fanlar — 2-haftada katta fan bilan almashtirish
            for sub_small, hours_small in half_subjects:
                # Alohida emasligini tekshirish
                if sub_small in standalone_names:
                    continue

                # Faqat 2-haftadan o'chirish (1-haftada qoldiramiz — oyna yaratmaslik uchun)
                for k in list(week2.keys()):
                    if k[0] == class_id and week2[k].get('subject_name') == sub_small:
                        del week2[k]
                        break

                # Juftlikdagi katta fanni topish (1,5+ soatlik)
                for sub_big, hours_big in bigger_subjects:
                    if hours_big < 1:
                        continue

                    # 2-haftada sub_big dan bittasini sub_small ga almashtirish
                    big_in_week2 = [(k, v) for k, v in week2.items()
                                    if k[0] == class_id and v.get('subject_name') == sub_big]

                    if big_in_week2:
                        key_to_replace, entry_to_replace = big_in_week2[0]
                        new_entry = entry_to_replace.copy()
                        new_entry['subject_name'] = sub_small
                        new_entry['subject_short'] = sub_small[:3]
                        week2[key_to_replace] = new_entry
                    break  # Faqat bitta juftlik bilan ishlash

        return week2

    def _add_result_to_teacher_schedule(self, result, teacher_schedule):
        """
        Scheduler natijasini teacher_schedule ga qo'shish.
        Keyingi batch shu ma'lumotlardan foydalanadi.
        """
        timetable = result['timetable']
        lesson_info = result['lesson_info']
        working_days = result['working_days']

        for day in range(6):
            if day >= working_days:
                continue
            for period in range(PERIODS_PER_DAY):
                if period < len(timetable) and day < len(timetable[period]):
                    subject_name = timetable[period][day]
                    if subject_name and subject_name.strip() and subject_name in lesson_info:
                        info = lesson_info[subject_name]
                        teacher_id = info['teacher_id']
                        t_key = (teacher_id, day, period)
                        if t_key not in teacher_schedule:
                            teacher_schedule[t_key] = result['class_name']

    def _detect_teacher_conflicts(self, all_data):
        """
        O'qituvchi ziddiyatlarini aniqlash.
        Bir xil o'qituvchi bir vaqtda 2 ta sinfda bo'lsa — ziddiyat.

        Qaytaradi: [(teacher_name, class1, class2, day, period), ...]
        """
        conflicts = []
        # teacher_id → {(day, period): class_name}
        teacher_cells = {}
        for (class_id, day, period), info in all_data.items():
            teacher_id = info.get('teacher_id')
            if teacher_id:
                key = (day, period)
                if teacher_id not in teacher_cells:
                    teacher_cells[teacher_id] = {}
                if key in teacher_cells[teacher_id]:
                    existing_class = teacher_cells[teacher_id][key]
                    class_name = info.get('class_name', f'Sinf {class_id}')
                    teacher_name = info.get('teacher_name', f'ID {teacher_id}')
                    conflicts.append((
                        teacher_name,
                        existing_class,
                        class_name,
                        day,
                        period
                    ))
                else:
                    teacher_cells[teacher_id][key] = info.get('class_name', f'Sinf {class_id}')

        return conflicts

    def _resolve_conflicts(self, all_data, max_iterations=20):
        """
        O'qituvchi ziddiyatlarini avtomatik hal qilish.
        Har iteratsiyada BARCHA ziddiyatlarni hal qilishga harakat qiladi.
        """
        for iteration in range(max_iterations):
            conflicts = self._detect_teacher_conflicts(all_data)
            if not conflicts:
                break

            resolved_any = False
            for teacher_name, class1, class2, day, period in conflicts:
                # class2 ning darsini topish
                key2 = None
                info2 = None
                for k, v in all_data.items():
                    if v.get('class_name') == class2 and k[1] == day and k[2] == period:
                        key2 = k
                        info2 = v
                        break

                if not key2 or not info2:
                    continue

                teacher_id = info2.get('teacher_id')
                class_id2 = key2[0]

                # class2 darsini bo'sh joyga ko'chirish
                moved = False
                sub_name = info2.get('subject_name', '')
                # Avval bir xil kun ichida (oyna yaratmaslik)
                for new_period in range(PERIODS_PER_DAY):
                    if new_period == period:
                        continue
                    # class2 ning yangi joyda mavjudligini tekshirish
                    c2_occupied = any(
                        vv.get('class_name') == class2 and kk[1] == day and kk[2] == new_period
                        for kk, vv in all_data.items()
                    )
                    if c2_occupied:
                        continue
                    occupied = any(
                        vv.get('teacher_id') == teacher_id and kk[1] == day and kk[2] == new_period
                        for kk, vv in all_data.items()
                    )
                    if occupied:
                        continue
                    # Kunlik takrorlanish tekshirish
                    day_subs = [vv.get('subject_name', '') for kk, vv in all_data.items()
                                if vv.get('class_name') == class2 and kk[1] == day]
                    max_per_day = DAILY_OCCURRENCE_OVERRIDES.get(sub_name, 1)
                    if day_subs.count(sub_name) >= max_per_day:
                        continue
                    all_data[(class_id2, day, new_period)] = info2.copy()
                    del all_data[key2]
                    resolved_any = True
                    moved = True
                    break

                if not moved:
                    # Boshqa kunlarga ko'chirish
                    for new_day in range(6):
                        if new_day == day:
                            continue
                        for new_period in range(PERIODS_PER_DAY):
                            # class2 ning yangi joyda mavjudligini tekshirish
                            c2_occupied = any(
                                vv.get('class_name') == class2 and kk[1] == new_day and kk[2] == new_period
                                for kk, vv in all_data.items()
                            )
                            if c2_occupied:
                                continue
                            occupied = any(
                                vv.get('teacher_id') == teacher_id and kk[1] == new_day and kk[2] == new_period
                                for kk, vv in all_data.items()
                            )
                            if occupied:
                                continue
                            # Kunlik takrorlanish tekshirish
                            day_subs = [vv.get('subject_name', '') for kk, vv in all_data.items()
                                        if vv.get('class_name') == class2 and kk[1] == new_day]
                            max_per_day = DAILY_OCCURRENCE_OVERRIDES.get(sub_name, 1)
                            if day_subs.count(sub_name) >= max_per_day:
                                continue
                            all_data[(class_id2, new_day, new_period)] = info2.copy()
                            del all_data[key2]
                            resolved_any = True
                            moved = True
                            break
                        if moved:
                            break

            if not resolved_any:
                break