"""
BRKGA — Biased Random-Key Genetic Algorithm
Dars jadvali tuzish uchun genetik algoritm
"""
import random
import math
from core.sanpin import SanPINChecker

PERIODS_PER_DAY = 6  # Kuniga maksimal 6 dars (7-dars yo'q)


class BRKGAScheduler:
    """
    BRKGA asosidagi dars jadvali generatori.

    G'oya:
    1. Har bir yechim "xromosoma" — 0 dan 1 gacha raqamlar ketma-ketligi
    2. Xromosomani dekod qilish → jadvalga aylantirish
    3. SanPIN balli → fitness (qancha yuqori, shuncha yaxshi)
    4. Eng yaxshilarini "ota-ona" deb tanlash
    5. Yangi avlod: crossover + mutatsiya
    6. Takrorlash → yechim yaxshilanadi
    """

    def __init__(self, population_size=60, elite_ratio=0.2,
                 mutant_ratio=0.15, generations=150,
                 early_stop_score=95, early_stop_patience=30):
        """
        population_size: har bir avlodda nechta yechim
        elite_ratio: nechasi "ota-ona" bo'ladi (eng yaxshilari)
        mutant_ratio: nechasi tasodifiy mutatsiya
        generations: maksimal avlodlar soni
        early_stop_score: shu ballga yetilsa to'xtash
        early_stop_patience: shuncha avlod yaxshilanmasa to'xtash
        """
        self.sanpin = SanPINChecker()
        self.population_size = population_size
        self.cancel_flag = False  # To'xtatish flagi
        self.tayanch_hours = None  # Tayanch reja soatlari (SanPIN ustunligi uchun)
        self.elite_count = max(2, int(population_size * elite_ratio))
        self.mutant_count = max(1, int(population_size * mutant_ratio))
        self.offspring_count = population_size - self.elite_count - self.mutant_count
        self.generations = generations
        self.early_stop_score = early_stop_score
        self.early_stop_patience = early_stop_patience
        self.kunlar = ["Dushanba", "Seshanba", "Chorshanba",
                       "Payshanba", "Juma", "Shanba"]
        self._fitness_cache = {}  # {timetable_key: (score, timetable)} — katta hajm uchun
        self._teacher_constraints = None
        self._subject_teacher_map = None

    # ================================================================
    # TEZ GREEDY — BRKGA dan oldin sinab ko'rish
    # ================================================================

    def _fast_greedy(self, subjects_hours, class_level, max_daily,
                     working_days, teacher_constraints, subject_teacher_map):
        """
        Tez greedy algoritm — 0.1-0.5 soniya.
        Qiyin fanlarni 2-3 darsga, yengillarni oxirgi darslarga qo'yadi.
        Agar ball ≥ 85 bo'lsa, BRKGA kerak emas.
        """
        # Darslar ro'yxatini tayyorlash
        lessons = []
        for sub, hours in subjects_hours.items():
            h = math.ceil(hours) if hours != int(hours) else int(hours)
            for _ in range(h):
                lessons.append(sub)

        total = len(lessons)
        if total == 0:
            return [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)], 0

        # Slotlarni hisoblash
        daily_limits = self._compute_daily_limits(total, working_days, max_daily)
        slots = []
        for day in range(6):
            for period in range(daily_limits[day]):
                slots.append((day, period))

        # Fan qiyinlik darajalari — oldindan hisoblash
        subjects_counts = {}
        for sub in lessons:
            subjects_counts[sub] = subjects_counts.get(sub, 0) + 1

        max_daily_occurrences = {}
        for sub, count in subjects_counts.items():
            if sub in ["Matematika", "Algebra"] or count > 5:
                max_daily_occurrences[sub] = 2
            else:
                max_daily_occurrences[sub] = 1

        # Fan qiyinliklari — dictionary (tezroq lookup)
        difficulty_map = {}
        for sub in set(lessons):
            difficulty_map[sub] = self.sanpin.get_difficulty(sub)

        # Greedy placement: har bir slot uchun eng mos fanni tanlash
        timetable = [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)]
        remaining = {}
        for sub in lessons:
            remaining[sub] = remaining.get(sub, 0) + 1

        day_subjects = {d: [] for d in range(6)}

        for day, period in slots:
            best_sub = None
            best_penalty = float('inf')

            for sub in remaining:
                if remaining[sub] <= 0:
                    continue
                # Kunlik takrorlanish
                if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                    continue
                # 1-4 sinflarda ketma-ket bir xil fan — QATTIQ TAQIQLANADI
                if class_level <= 4 and period > 0:
                    prev = timetable[period - 1][day]
                    if prev == sub:
                        continue  # Qo'ymaymiz
                # O'qituvchi bandligi — QATTIQ CHEKLOV
                if teacher_constraints and subject_teacher_map:
                    tid = subject_teacher_map.get(sub)
                    if tid and (tid, day, period) in teacher_constraints:
                        continue  # Ziddiyatli slotga QO'YMAYMIZ

                # Penalty hisoblash
                penalty = 0
                diff = difficulty_map.get(sub, 5)

                # 1-4 sinflarda ketma-ket bir xil fan
                if class_level <= 4 and period > 0:
                    prev = timetable[period - 1][day]
                    if prev == sub:
                        penalty += 50

                # Ketma-ket qiyin fanlar
                if period > 0:
                    prev = timetable[period - 1][day]
                    if prev:
                        prev_diff = difficulty_map.get(prev, 5)
                        if diff >= 11 and prev_diff >= 11:
                            penalty += 15

                # 1-darsda juda qiyin
                if period == 0 and diff >= 13:
                    penalty += 5

                # Oxirgi darsda qiyin
                if period == daily_limits[day] - 1 and diff >= 11:
                    penalty += 5

                # Sportdan keyin qiyin
                if period > 0:
                    prev = timetable[period - 1][day]
                    if prev in ("Sport", "Jismoniy tarbiya") and diff >= 11:
                        penalty += 10

                # Optimal soatda emas
                if diff >= 11 and period + 1 not in [2, 3]:
                    penalty += 3
                elif diff >= 8 and period + 1 not in [1, 2, 3, 4]:
                    penalty += 2
                elif diff <= 5 and period + 1 not in [4, 5, 6, 7]:
                    penalty += 2

                # Kun qiyinligi balansi
                day_diff = sum(difficulty_map.get(timetable[p][day], 0)
                               for p in range(PERIODS_PER_DAY) if timetable[p][day]) + diff
                if day_diff > 65:
                    penalty += 3

                # Kunlik teng taqsimot — kam darsli kunlarni afzal ko'rish
                day_count = len(day_subjects[day])
                avg_per_day = sum(len(v) for v in day_subjects.values()) / max(len([d for d in range(working_days) if day_subjects[d]]), 1)
                day_limit = daily_limits[day] if daily_limits else PERIODS_PER_DAY
                if day_count >= day_limit:
                    penalty += 50  # Kun to'ldi — boshqa joyga qo'yish shart
                elif day_count > avg_per_day + 1:
                    penalty += 10  # O'rtachadan ko'p darsli kun — katta jazo

                # Oyna (gap) — avvalgi slot bo'sh bo'lsa va hali darslar qoldi bo'lsa
                if period > 0 and not timetable[period - 1][day]:
                    has_remaining = any(c > 0 for c in remaining.values())
                    if has_remaining:
                        penalty += 20  # Oyna oldini olish uchun katta jazo

                if penalty < best_penalty:
                    best_penalty = penalty
                    best_sub = sub

            if best_sub:
                timetable[period][day] = best_sub
                remaining[best_sub] -= 1
                day_subjects[day].append(best_sub)

        # ============================================================
        # 2-BOSQICH: MAJBURIY JOYLASHTIRISH — qoldiq darslarni qo'yish
        # ============================================================
        max_iterations = 100
        for _ in range(max_iterations):
            unplaced = [sub for sub, count in remaining.items() if count > 0]
            if not unplaced:
                break
            sub = unplaced[0]
            placed = False
            # 1. Bo'sh slot + teacher band emas + kunlik takrorlanish + kun limiti
            for day in range(working_days):
                if len(day_subjects[day]) >= daily_limits[day]:
                    continue  # Kun to'ldi — boshqa kun tanlash
                for period in range(daily_limits[day]):
                    if timetable[period][day]:
                        continue
                    if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                        continue
                    if teacher_constraints and subject_teacher_map:
                        tid = subject_teacher_map.get(sub)
                        if tid and (tid, day, period) in teacher_constraints:
                            continue
                    timetable[period][day] = sub
                    remaining[sub] -= 1
                    day_subjects[day].append(sub)
                    placed = True
                    break
                if placed:
                    break

            # 2. Bo'sh slot + teacher band (ziddiyat bilan) + kunlik takrorlanish
            if not placed:
                for day in range(working_days):
                    for period in range(daily_limits[day]):
                        if timetable[period][day]:
                            continue
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        timetable[period][day] = sub
                        remaining[sub] -= 1
                        day_subjects[day].append(sub)
                        placed = True
                        break
                    if placed:
                        break

            # 3. Swap — mavjud darsni boshqa joyga ko'chirib, bo'sh slot yaratish
            if not placed:
                for day in range(working_days):
                    for period in range(daily_limits[day]):
                        existing = timetable[period][day]
                        if not existing:
                            continue
                        # Yangi dars kunlik takrorlanishni tekshirish
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        for new_day in range(working_days):
                            for new_period in range(daily_limits[new_day]):
                                if new_day == day and new_period == period:
                                    continue
                                if timetable[new_period][new_day]:
                                    continue
                                # Ko'chirilgan dars kunlik takrorlanishini tekshirish
                                if day_subjects[new_day].count(existing) >= max_daily_occurrences.get(existing, 1):
                                    continue
                                timetable[new_period][new_day] = existing
                                timetable[period][day] = sub
                                remaining[sub] -= 1
                                day_subjects[day].append(sub)
                                day_subjects[new_day].append(existing)
                                placed = True
                                break
                            if placed:
                                break
                        if placed:
                            break
                    if placed:
                        break

            # 4. OXIRGI UMID — mavjud darsni bosib, qayta joylashtirish
            if not placed:
                for day in range(working_days):
                    for period in range(daily_limits[day]):
                        existing = timetable[period][day]
                        if not existing:
                            continue
                        if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                            continue
                        timetable[period][day] = sub
                        remaining[sub] -= 1
                        day_subjects[day].append(sub)
                        remaining[existing] = remaining.get(existing, 0) + 1
                        placed = True
                        break
                    if placed:
                        break

        # ============================================================
        # 3-BOSQICH: OYNA TUZATISH — bo'sh slotlarni to'ldirish
        # ============================================================
        for day in range(working_days):
            # Kun ichidagi darslarni yig'ish
            day_lessons = []
            for period in range(daily_limits[day]):
                sub = timetable[period][day]
                if sub:
                    day_lessons.append(sub)
                else:
                    day_lessons.append("")

            # Oynalarni topish va tuzatish — darslarni tepaga siljitish
            filled = [s for s in day_lessons if s]
            if len(filled) < daily_limits[day]:
                # Bo'sh slotlarni to'ldirish — darslarni tepaga siljitish
                for period in range(daily_limits[day]):
                    timetable[period][day] = ""
                for i, sub in enumerate(filled):
                    timetable[i][day] = sub

        # SWAP — ichki swap, teacher constraints bilan
        best_score = self.sanpin.check_timetable(timetable, class_level, self.tayanch_hours)['score']

        for _ in range(3):
            improved = False
            for day1 in range(working_days):
                for period1 in range(daily_limits[day1]):
                    sub1 = timetable[period1][day1]
                    if not sub1:
                        continue
                    if teacher_constraints and subject_teacher_map:
                        tid = subject_teacher_map.get(sub1)
                        if tid and (tid, day1, period1) in teacher_constraints:
                            continue

                    for day2 in range(working_days):
                        for period2 in range(daily_limits[day2]):
                            if day1 == day2 and period1 == period2:
                                continue
                            sub2 = timetable[period2][day2]
                            if not sub2:
                                continue
                            if teacher_constraints and subject_teacher_map:
                                tid2 = subject_teacher_map.get(sub2)
                                if tid2 and (tid2, day2, period2) in teacher_constraints:
                                    continue

                            timetable[period1][day1], timetable[period2][day2] = sub2, sub1
                            new_score = self.sanpin.check_timetable(timetable, class_level, self.tayanch_hours)['score']

                            if new_score > best_score:
                                best_score = new_score
                                improved = True
                                break
                            else:
                                timetable[period1][day1], timetable[period2][day2] = sub1, sub2
                        if improved:
                            break
                    if improved:
                        break
                if improved:
                    break
            if not improved:
                break

        res = self.sanpin.check_timetable(timetable, class_level, self.tayanch_hours)
        return timetable, res['score']

    # ================================================================
    # DECODER: Xromosomani jadvalga aylantirish (TEZLASHTIRILGAN)
    # ================================================================

    def _decode(self, chromosome, lessons, slots, daily_limits,
                teacher_constraints, subject_teacher_map, max_daily_occurrences):
        """
        Xromosomani (0-1 raqamlar) jadvalga dekod qilish.
        Optimizatsiyalandi: pre-compute, sets, kamroq obyekt yaratish.
        """
        timetable = [[""] * 6 for _ in range(PERIODS_PER_DAY)]
        num_lessons = len(lessons)
        num_slots = len(slots)

        # 1-QISM: Darslarni tartibga solish — list comprehension + sorted
        lesson_priority = [(lessons[i], chromosome[i]) for i in range(num_lessons)]
        lesson_priority.sort(key=lambda x: x[1])

        ordered_lessons = [sub for sub, _ in lesson_priority]

        # 2-QISM: Slotlarni to'ldirish — remaining ni set sifatida
        remaining = {}
        for sub in lessons:
            remaining[sub] = remaining.get(sub, 0) + 1

        # Teacher constraints ni set ga aylantirish (tezroq lookup)
        tc_set = set()
        if teacher_constraints and subject_teacher_map:
            tc_set = teacher_constraints

        day_subjects = {d: [] for d in range(6)}
        # Kunlik hisob — dict (tezroq count)
        day_counts = {d: {} for d in range(6)}

        for slot_idx in range(num_slots):
            day, period = slots[slot_idx]

            # Gene qiymati
            gene_idx = num_lessons + slot_idx
            gene = chromosome[gene_idx] if gene_idx < len(chromosome) else 0.5

            # Nomzod fanlar — faqat qoldiq > 0
            candidates = []
            dc = day_counts[day]
            for sub in ordered_lessons:
                rem = remaining.get(sub, 0)
                if rem <= 0:
                    continue
                # Kunlik takrorlanish
                sub_count = dc.get(sub, 0)
                max_per_day = max_daily_occurrences.get(sub, 1)
                if sub_count >= max_per_day:
                    continue
                # Teacher bandligi
                if tc_set and subject_teacher_map:
                    tid = subject_teacher_map.get(sub)
                    if tid and (tid, day, period) in tc_set:
                        continue
                candidates.append(sub)

            if not candidates:
                # Faqat teacher ziddiyatisiz + kunlik takrorlanishsiz nomzodlar
                for sub in ordered_lessons:
                    if remaining.get(sub, 0) <= 0:
                        continue
                    if day_subjects[day].count(sub) >= max_daily_occurrences.get(sub, 1):
                        continue
                    if tc_set and subject_teacher_map:
                        tid = subject_teacher_map.get(sub)
                        if tid and (tid, day, period) in tc_set:
                            continue
                    candidates.append(sub)
                if not candidates:
                    continue

            # Gene ga qarab tanlash
            choice_idx = int(gene * len(candidates))
            choice_idx = min(choice_idx, len(candidates) - 1)

            # Heuristic bilan tartiblash
            scored_candidates = self._score_candidates(
                candidates, day, period, timetable, daily_limits
            )
            final_idx = min(choice_idx, len(scored_candidates) - 1)
            chosen = scored_candidates[final_idx]

            timetable[period][day] = chosen
            remaining[chosen] = remaining.get(chosen, 0) - 1
            day_subjects[day].append(chosen)
            dc[chosen] = dc.get(chosen, 0) + 1

        return timetable

    def _score_candidates(self, candidates, day, period, timetable, daily_limits):
        """
        Nomzodlarni SanPIN qoidalari bo'yicha baholash va saralash.
        Past ball = yaxshi (kam xato).
        Penalty qiymatlari SanPIN scoring ga moslashtirildi.
        """
        scored = []
        # Kunlik qiyinliklar — oldindan hisoblash
        day_diff_total = {}
        for d in range(6):
            total = 0
            for p in range(PERIODS_PER_DAY):
                cell = timetable[p][d]
                if cell:
                    total += self.sanpin.get_difficulty(cell)
            day_diff_total[d] = total

        # Kunlik fan sonlari — oldindan hisoblash
        day_sub_counts = {}
        for d in range(6):
            counts = {}
            for p in range(PERIODS_PER_DAY):
                cell = timetable[p][d]
                if cell:
                    counts[cell] = counts.get(cell, 0) + 1
            day_sub_counts[d] = counts

        for sub in candidates:
            diff = self.sanpin.get_difficulty(sub)
            optimal = self.sanpin.get_optimal_period(sub)
            penalty = 0

            # 1. Ketma-ket qiyin fanlar
            if period > 0:
                prev = timetable[period - 1][day]
                if prev:
                    prev_diff = self.sanpin.get_difficulty(prev)
                    if diff >= 11 and prev_diff >= 11:
                        penalty += 5

            # 2. 1-darsda juda qiyin
            if period == 0 and diff >= 9:
                penalty += 3

            # 3. Oxirgi darsda qiyin
            if daily_limits[day] > 0 and period == daily_limits[day] - 1 and diff >= 8:
                penalty += 3

            # 4. Sportdan keyin qiyin
            if period > 0:
                prev = timetable[period - 1][day]
                if prev in ("Sport", "Jismoniy tarbiya") and diff >= 11:
                    penalty += 4

            # 5. Optimal soatda emas
            if (period + 1) not in optimal:
                penalty += 2

            # 6. Bir kunda ko'p marta takrorlangan
            sub_count = day_sub_counts[day].get(sub, 0)
            if sub_count >= 1 and sub not in ("Matematika", "Algebra"):
                penalty += 8

            # 7. Kun qiyinligi balansi
            if day_diff_total[day] + diff > 65:
                penalty += 3

            scored.append((sub, penalty))

        # Past ball → oldinda
        scored.sort(key=lambda x: (x[1], random.random()))
        return [s[0] for s in scored]

    # ================================================================
    # FITNESS: JADVALNI BAHOLASH (TEZLASHTIRILGAN)
    # ================================================================

    def _fitness(self, timetable, class_level):
        """
        Jadval ballini hisoblash — tezroq versiya.
        Faqat asosiy qoidalarni tekshiradi (to'liq SanPIN emas).
        """
        max_daily = self.sanpin.max_daily_lessons.get(class_level, 7)
        max_weekly = self.sanpin.max_weekly_lessons.get(class_level, 34)
        score = 100

        # Kunlik darslar soni
        for day in range(6):
            count = 0
            for period in range(PERIODS_PER_DAY):
                if timetable[period][day]:
                    count += 1
            if count > max_daily:
                score -= 10

        # Haftalik darslar soni (Kelajak soatisiz)
        total = sum(1 for d in range(6) for p in range(PERIODS_PER_DAY)
                    if timetable[p][d] and 'kelajak' not in timetable[p][d].lower())
        if total > max_weekly:
            score -= 15

        # 1-4 sinflarda ketma-ket bir xil fan
        if class_level <= 4:
            for day in range(6):
                for period in range(6):
                    if (timetable[period][day] and timetable[period + 1][day]
                            and timetable[period][day] == timetable[period + 1][day]):
                        score -= 15

        # Ketma-ket qiyin fanlar
        for day in range(6):
            prev_hard = False
            for period in range(PERIODS_PER_DAY):
                cell = timetable[period][day]
                if cell:
                    is_hard = cell in self.sanpin.hard_subjects
                    if is_hard and prev_hard:
                        score -= 5
                    prev_hard = is_hard
                else:
                    prev_hard = False

        # Oyna (gap)
        for day in range(6):
            has_lesson = False
            gap_found = False
            for period in range(PERIODS_PER_DAY):
                cell = timetable[period][day]
                if cell:
                    if gap_found:
                        score -= 10
                        break
                    has_lesson = True
                else:
                    if has_lesson:
                        gap_found = True

        # TEACHER CONSTRAINT VIOLATION — eng og'ir jazo
        if self._teacher_constraints and self._subject_teacher_map:
            for day in range(6):
                for period in range(PERIODS_PER_DAY):
                    cell = timetable[period][day]
                    if cell:
                        tid = self._subject_teacher_map.get(cell)
                        if tid and (tid, day, period) in self._teacher_constraints:
                            score -= 50  # QATTIQ JAZO — teacher ziddiyati

        return max(0, min(100, score))

    # ================================================================
    # INITIAL POPULATION
    # ================================================================

    def _create_random_chromosome(self, num_lessons, num_slots):
        """Tasodifiy xromosoma yaratish: darslar + slotlar uchun genlar"""
        total = num_lessons + num_slots
        return [random.random() for _ in range(total)]

    def _create_greedy_chromosome(self, lessons, slots, daily_limits,
                                  teacher_constraints, subject_teacher_map,
                                  max_daily_occurrences):
        """
        Greedy xromosoma — SanPIN qoidalariga mos boshlang'ich yechim.
        Qiyin fanlarni 2-3 darsga, yengillarni oxirgi darslarga qo'yadi.
        """
        num_lessons = len(lessons)
        num_slots = len(slots)

        # Darslar tartibi: qiyin fanlar avval (2-3 dars uchun)
        lesson_priority = []
        for sub in lessons:
            diff = self.sanpin.get_difficulty(sub)
            # Qiyin fanlar (diff >= 11) → past gene (avval qo'yiladi)
            # Yengil fanlar (diff <= 5) → yuqori gene (keyin qo'yiladi)
            gene_val = max(0.0, min(1.0, 1.0 - (diff / 13.0)))
            lesson_priority.append(gene_val)

        # Slotlar tartibi: 2-3 darslar avval (qiyin fanlar uchun)
        slot_genes = []
        for day, period in slots:
            # 2-3 darslar → past gene (avval to'ldiriladi)
            if period in [1, 2]:
                gene_val = 0.1 + random.uniform(0, 0.2)
            elif period in [0, 3]:
                gene_val = 0.3 + random.uniform(0, 0.2)
            else:
                gene_val = 0.6 + random.uniform(0, 0.3)
            slot_genes.append(gene_val)

        return lesson_priority + slot_genes

    def _init_population(self, num_lessons, num_slots, lessons=None, slots=None,
                         daily_limits=None, teacher_constraints=None,
                         subject_teacher_map=None, max_daily_occurrences=None):
        """Boshlang'ich populyatsiya yaratish — 20% greedy, 80% tasodifiy"""
        population = []

        # 20% greedy chromosomes
        greedy_count = max(2, int(self.population_size * 0.2))
        if lessons and slots:
            for _ in range(greedy_count):
                chrom = self._create_greedy_chromosome(
                    lessons, slots, daily_limits,
                    teacher_constraints, subject_teacher_map,
                    max_daily_occurrences
                )
                population.append(chrom)

        # Qolganini tasodifiy
        remaining = self.population_size - len(population)
        for _ in range(remaining):
            population.append(self._create_random_chromosome(num_lessons, num_slots))

        return population

    # ================================================================
    # CROSSOVER: Ikki ota-onadan yangi avlod
    # ================================================================

    def _crossover(self, parent1, parent2):
        """
        Biased crossover: elite ota-onadan ko'proq gen olinadi.
        Optimizatsiyalandi: list comprehension.
        """
        r = random.random
        return [p1 if r() < 0.7 else p2 for p1, p2 in zip(parent1, parent2)]

    # ================================================================
    # MUTATION: Tasodifiy o'zgarish (TEZLASHTIRILGAN)
    # ================================================================

    def _mutate(self, chromosome, mutation_rate=0.05):
        """Genlarning mutation_rate qismiga mutatsiya"""
        mutated = list(chromosome)
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                mutated[i] = max(0.0, min(1.0, mutated[i] + random.uniform(-0.1, 0.1)))
        return mutated

    # ================================================================
    # ASOSIY ALGORITM
    # ================================================================

    def generate_timetable(self, subjects_hours, class_level,
                           max_daily=None, working_days=6,
                           teacher_constraints=None, subject_teacher_map=None,
                           tayanch_hours=None, verbose=False):
        """
        BRKGA yordamida dars jadvalini generatsiya qilish.

        subjects_hours: {"Matematika": 5, "Fizika": 3, ...}
        class_level: int (1-11)
        max_daily: int (ixtiyoriy)
        working_days: 5 yoki 6
        teacher_constraints: set of (teacher_id, day, period)
        subject_teacher_map: {subject_name: teacher_id}
        tayanch_hours: dict - tayanch rejadagi soatlar (SanPIN ustunligi uchun)

        Qaytaradi: (timetable, score)
        """
        self.tayanch_hours = tayanch_hours
        self._teacher_constraints = teacher_constraints
        self._subject_teacher_map = subject_teacher_map
        if max_daily is None:
            max_daily = self.sanpin.max_daily_lessons.get(class_level, 7)

        # Darslar ro'yxatini tayyorlash
        import math
        lessons = []
        for sub, hours in subjects_hours.items():
            h = math.ceil(hours) if hours != int(hours) else int(hours)
            for _ in range(h):
                lessons.append(sub)

        total = len(lessons)
        if total == 0:
            return [["" for _ in range(6)] for _ in range(PERIODS_PER_DAY)], 0

        # ============================================================
        # 1-QADAM: TEZ GREEDY — avval sinab ko'rish
        # ============================================================
        greedy_timetable, greedy_score = self._fast_greedy(
            subjects_hours, class_level, max_daily,
            working_days, teacher_constraints, subject_teacher_map
        )

        # Agar greedy yaxshi natija bersa — BRKGA kerak emas
        # Greedy + swap yetarli — BRKGA sekinlashtiradi
        return greedy_timetable, greedy_score

        # ============================================================
        # 2-QADAM: BRKGA — greedy dan yomonroq bo'lsa
        # ============================================================
        # Slotlarni hisoblash
        daily_limits = self._compute_daily_limits(total, working_days, max_daily)
        slots = []
        for day in range(6):
            for period in range(daily_limits[day]):
                slots.append((day, period))

        num_slots = len(slots)

        # Fan qiyinlik darajalari
        subjects_counts = {}
        for sub in lessons:
            subjects_counts[sub] = subjects_counts.get(sub, 0) + 1

        max_daily_occurrences = {}
        for sub, count in subjects_counts.items():
            if sub in ["Matematika", "Algebra"] or count > 5:
                max_daily_occurrences[sub] = 2
            else:
                max_daily_occurrences[sub] = 1

        # Boshlang'ich populyatsiya — greedy + tasodifiy
        num_lessons = len(lessons)
        population = self._init_population(
            num_lessons, num_slots, lessons, slots,
            daily_limits, teacher_constraints, subject_teacher_map,
            max_daily_occurrences
        )

        # Baholash — greedy natijasini ham qo'shish
        scored = []

        # Greedy natijasini xromosoma sifatida qo'shish (ixtiyoriy)
        greedy_chrom = [0.5] * (num_lessons + num_slots)
        scored.append((greedy_chrom, greedy_score, greedy_timetable))

        for chrom in population:
            timetable = self._decode(
                chrom, lessons, slots, daily_limits,
                teacher_constraints, subject_teacher_map,
                max_daily_occurrences
            )
            score = self._fitness(timetable, class_level)
            scored.append((chrom, score, timetable))

        # Saralash (eng yuqori ball birinchi)
        scored.sort(key=lambda x: -x[1])
        best_score = scored[0][1]
        best_timetable = [row.copy() for row in scored[0][2]]
        best_chrom = list(scored[0][0])

        patience_counter = 0

        if verbose:
            print(f"BRKGA boshlandi: {self.population_size} yechim, "
                  f"{self.generations} avlod")
            print(f"Slotlar: {num_slots}, Darslar: {total}")
            print(f"Xromosoma uzunligi: {num_lessons + num_slots}")
            print(f"Boshlang'ich eng yaxshi ball: {best_score}")

        # ===== ASOSIY TSIKL =====
        for gen in range(self.generations):
            # To'xtatish tekshiruvi
            if self.cancel_flag:
                if verbose:
                    print(f"  ❌ To'xtatildi! ball: {best_score}")
                break

            # Ota-onalar (eng yaxshilari)
            elites = [s[0] for s in scored[:self.elite_count]]

            # Yangi avlod
            new_population = list(elites)  # Elitlarni saqlash

            # Offspring: crossover — p2 faqat non-elite dan
            non_elite = [s[0] for s in scored[self.elite_count:]]
            for _ in range(self.offspring_count):
                p1 = random.choice(elites)
                p2 = random.choice(non_elite) if non_elite else random.choice(elites)
                child = self._crossover(p1, p2)
                child = self._mutate(child)
                new_population.append(child)

            # Mutantlar: to'liq tasodifiy
            for _ in range(self.mutant_count):
                mutant = self._create_random_chromosome(num_lessons, num_slots)
                new_population.append(mutant)

            # Yangi populyatsiyani baholash — elite cache + decode cache
            scored = []
            for idx, chrom in enumerate(new_population):
                # Jadval hash — decode natijasini cache qilish
                timetable = self._decode(
                    chrom, lessons, slots, daily_limits,
                    teacher_constraints, subject_teacher_map,
                    max_daily_occurrences
                )
                timetable_key = tuple(
                    timetable[p][d] if p < len(timetable) and d < len(timetable[p]) else ""
                    for p in range(PERIODS_PER_DAY) for d in range(6)
                )

                # Jadval allaqachon baholanganmi?
                if timetable_key in self._fitness_cache:
                    score = self._fitness_cache[timetable_key][0]
                else:
                    score = self._fitness(timetable, class_level)
                    if len(self._fitness_cache) < 50000:
                        self._fitness_cache[timetable_key] = (score, timetable)

                scored.append((chrom, score, timetable))

            scored.sort(key=lambda x: -x[1])

            # Eng yaxshisini yangilash
            if scored[0][1] > best_score:
                best_score = scored[0][1]
                best_timetable = [row.copy() for row in scored[0][2]]
                best_chrom = list(scored[0][0])
                patience_counter = 0
            else:
                patience_counter += 1

            if verbose and gen % 50 == 0:
                print(f"  Lod {gen}: eng yaxshi = {scored[0][1]}, "
                      f"ortacha = {sum(s[1] for s in scored) / len(scored):.1f}")

            # Erta to'xtash
            if best_score >= self.early_stop_score:
                if verbose:
                    print(f"  Erta to'xtash: ball {best_score} >= {self.early_stop_score}")
                break
            if patience_counter >= self.early_stop_patience:
                if verbose:
                    print(f"  Sabr tugadi: {patience_counter} avlod yaxshilanmadi")
                break

        # Local search hozircha o'chirildi — BRKGA o'zi yaxshi natija beradi

        if verbose:
            print(f" yakuniy ball: {best_score}")

        # ============================================================
        # TEACHER CONSTRAINT REPAIR — BRKGA dan keyin ziddiyatlarni tuzatish
        # ============================================================
        if teacher_constraints and subject_teacher_map:
            self._repair_teacher_conflicts(
                best_timetable, teacher_constraints, subject_teacher_map,
                lessons, daily_limits, working_days
            )
            # Ballni qayta hisoblash
            res = self.sanpin.check_timetable(best_timetable, class_level, self.tayanch_hours)
            best_score = res['score']

        return best_timetable, best_score

    def _repair_teacher_conflicts(self, timetable, teacher_constraints,
                                   subject_teacher_map, lessons, daily_limits,
                                   working_days):
        """
        BRKGA natijasidagi teacher ziddiyatlarini tuzatish.
        Ziddiyatli darsni boshqa bo'sh slotga ko'chiradi.
        """
        if not teacher_constraints or not subject_teacher_map:
            return

        # Kunlik fan hisoblari
        day_counts = {}
        for sub in lessons:
            day_counts[sub] = day_counts.get(sub, 0) + 1

        max_daily_occurrences = {}
        for sub, count in day_counts.items():
            if sub in ["Matematika", "Algebra"] or count > 5:
                max_daily_occurrences[sub] = 2
            else:
                max_daily_occurrences[sub] = 1

        # Har slot uchun teacher ziddiyatini tekshirish
        for day in range(working_days):
            for period in range(daily_limits[day]):
                sub = timetable[period][day]
                if not sub:
                    continue

                tid = subject_teacher_map.get(sub)
                if not tid:
                    continue

                # Teacher bandmimi?
                if (tid, day, period) in teacher_constraints:
                    # Ziddiyat — darsni boshqa joyga ko'chirish
                    moved = False
                    for new_day in range(working_days):
                        for new_period in range(daily_limits[new_day]):
                            if new_day == day and new_period == period:
                                continue
                            if (tid, new_day, new_period) in teacher_constraints:
                                continue
                            if timetable[new_period][new_day]:
                                continue
                            # Kunlik takrorlanish
                            sub_count = sum(1 for p in range(PERIODS_PER_DAY) if timetable[p][new_day] == sub)
                            if sub_count >= max_daily_occurrences.get(sub, 1):
                                continue

                            timetable[new_period][new_day] = sub
                            timetable[period][day] = ""
                            moved = True
                            break
                        if moved:
                            break

    # ================================================================
    # KUNLIK LIMITLARNI HISOBASH
    # ================================================================

    def _compute_daily_limits(self, total, working_days, max_daily):
        """TENG TAQSIMOT — har bir kun uchun aniq darslar soni"""
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

        return daily_limits

        return daily_limits
