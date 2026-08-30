"""
SmartDJ3 — Yangi dars jadvali tuzish algoritmi

Asosiy printsip:
- Barcha darslarni GLOBAL jadvalda joylashtirish (har bir sinf alohida emas)
- teacher_grid[teacher_id][day][period] = class_id — o'qituvchi bandligi
- class_grid[class_id][day][period] = lesson_info — sinf jadvali
- 1 haftalik, faqat butun soatlar
- Barcha darslar TO'LIQ joylashtiriladi (backtracking bilan)
"""
import random
from collections import defaultdict
from core.sanpin import SanPINChecker

PERIODS_PER_DAY = 6
WORKING_DAYS = 6  # Dushanba-Shanba


class TimetableScheduler:
    def __init__(self, db_manager=None):
        self.db = db_manager
        self.sanpin = SanPINChecker()
        self.cancel_flag = False

        # Global jadvallar
        self.teacher_grid = {}    # {teacher_id: [[None]*6 for _ in range(6)]}
        self.class_grid = {}      # {class_id: [[None]*6 for _ in range(6)]}
        self.blocked_slots = {}   # {teacher_id: set((day, period))}
        self.methodic_slots = {}  # {teacher_id: set((day, period))}

        # Sinf ma'lumotlari
        self.class_info = {}      # {class_id: {name, level, working_days}}
        self.class_daily_limits = {}  # {class_id: [limit_per_day]}

        # Darslar ro'yxati
        self.lessons_to_place = []  # [{class_id, subject, teacher_id, ...}]

        # O'qituvchi sinflari soni (cheklanganlik uchun)
        self.teacher_class_count = defaultdict(int)

    def cancel(self):
        self.cancel_flag = True

    def reset_cancel(self):
        self.cancel_flag = False

    # ================================================================
    # ASOSIY METOD — Barcha sinflar uchun jadval tuzish
    # ================================================================

    def generate_all_class_timetables(self, classes, db_manager,
                                       cancel_flag=None, progress_callback=None):
        """
        Barcha sinflar uchun avtomatik jadval tuzish.

        Qaytaradi:
            all_data: {(class_id, day, period): lesson_info}
            conflicts: [] — bo'sh ro'yxat (ziddiyatlar oldini olish bilan hal qilinadi)
        """
        self.db = db_manager
        self.cancel_flag = False
        self.sanpin.clear_cache()

        # 1-QADAM: Ma'lumotlarni yuklash
        self._load_data(classes, db_manager)

        # 2-QADAM: Darslarni tartibga solish (eng cheklangan birinchi)
        self._sort_lessons()

        # 3-QADAM: Darslarni joylashtirish
        success = self._place_all_lessons(cancel_flag, progress_callback)

        # 4-QADAM: Natijalarni shakllantirish
        all_data = self._build_all_data()

        # 5-QADAM: SanPIN bo'yicha yakuniy tekshirish va ball
        self._calculate_scores()

        return all_data, []

    # ================================================================
    # 1-QADAM: Ma'lumotlarni yuklash
    # ================================================================

    def _load_data(self, classes, db_manager):
        """Barcha kerakli ma'lumotlarni bazadan yuklash"""

        # O'qituvchilarning band soatlarini yuklash
        all_teachers = db_manager.get_all_teachers()
        for t in all_teachers:
            t_id = t[0]
            methodic_day = t[5]
            if methodic_day is not None and methodic_day != '':
                try:
                    methodic_day = int(methodic_day)
                except (ValueError, TypeError):
                    methodic_day = None
            if methodic_day is not None and 0 <= methodic_day < WORKING_DAYS:
                slots = set()
                for p in range(PERIODS_PER_DAY):
                    slots.add((methodic_day, p))
                self.methodic_slots[t_id] = slots

            # Band soatlar (unavailable)
            unavail = db_manager.get_teacher_unavailable(t_id)
            blocked = set()
            for (day, period, avail_type) in unavail:
                if 0 <= day < WORKING_DAYS and 0 <= period < PERIODS_PER_DAY:
                    if avail_type == 'strict':
                        blocked.add((day, period))
            if blocked:
                self.blocked_slots[t_id] = blocked

        # Sinflar va darslarni yuklash
        for cls in classes:
            class_id = cls[0]
            class_name = cls[1]
            class_level = cls[2] if len(cls) > 2 else 5
            working_days = cls[4] if len(cls) > 4 and cls[4] else WORKING_DAYS

            self.class_info[class_id] = {
                'name': class_name,
                'level': class_level,
                'working_days': working_days,
            }

            # Kunlik dars limitlari
            max_daily = self.sanpin.max_daily_lessons.get(class_level, 7)
            self.class_daily_limits[class_id] = max_daily

            # Jadvalni boshlash
            self.class_grid[class_id] = [
                [None] * WORKING_DAYS for _ in range(PERIODS_PER_DAY)
            ]

            # Darslarni yuklash
            assignments = db_manager.get_class_assignments(class_id)
            for a in assignments:
                lesson_id = a[0]
                subject_name = a[1]
                teacher_name = a[2]
                teacher_color = a[3]
                weekly_hours = a[4]
                subject_id = a[5]
                teacher_id = a[6]
                teacher_short = a[7] if len(a) > 7 else ''

                # Faqat butun soatlar
                hours = int(weekly_hours)
                if hours <= 0:
                    continue

                self.teacher_class_count[teacher_id] += 1

                for i in range(hours):
                    suffix = f"_{i+1}" if i > 0 else ""
                    self.lessons_to_place.append({
                        'class_id': class_id,
                        'class_name': class_name,
                        'class_level': class_level,
                        'working_days': working_days,
                        'subject_name': subject_name,
                        'subject_short': subject_name[:3],
                        'subject_id': subject_id,
                        'teacher_id': teacher_id,
                        'teacher_name': teacher_name,
                        'teacher_short': teacher_short,
                        'teacher_color': teacher_color,
                        'lesson_id': lesson_id,
                        'weekly_hours': weekly_hours,
                        'suffix': suffix,
                    })

        # O'qituvchi jadvalini boshlash
        for t_id in set(l['teacher_id'] for l in self.lessons_to_place):
            self.teacher_grid[t_id] = [
                [None] * WORKING_DAYS for _ in range(PERIODS_PER_DAY)
            ]

    # ================================================================
    # 2-QADAM: Darslarni tartibga solish
    # ================================================================

    def _sort_lessons(self):
        """
        Darslarni cheklanganlik darajasiga qarab tartibga solish.
        Eng cheklangan darslar birinchi joylashtiriladi.
        """
        def lesson_priority(lesson):
            t_id = lesson['teacher_id']
            class_id = lesson['class_id']

            # 1. O'qituvchi nechta sinfga dars beradi (ko'p = birinchi)
            t_classes = self.teacher_class_count.get(t_id, 1)

            # 2. O'qituvchining band soatlari soni (ko'p = birinchi)
            blocked_count = len(self.blocked_slots.get(t_id, set()))
            methodic_count = len(self.methodic_slots.get(t_id, set()))
            unavailable = blocked_count + methodic_count

            # 3. Sinfning ish kunlari soni (kam = birinchi)
            working_days = lesson['working_days']

            # 4. Fan qiyinligi (qiyin = birinchi)
            difficulty = self.sanpin.get_difficulty(lesson['subject_name'])

            return (-t_classes, -unavailable, working_days, -difficulty)

        self.lessons_to_place.sort(key=lesson_priority)

    # ================================================================
    # 3-QADAM: Darslarni joylashtirish
    # ================================================================

    def _place_all_lessons(self, cancel_flag=None, progress_callback=None):
        """
        Barcha darslarni joylashtirish.
        Greedy + Backtracking: har bir dars uchun eng yaxshi slotni tanlash.
        Agar joy topilmasa — oldingi darslarni ko'chirish (backtracking).
        """
        total = len(self.lessons_to_place)
        placed = 0
        failed_lessons = []

        for idx, lesson in enumerate(self.lessons_to_place):
            if cancel_flag and cancel_flag():
                return False

            success = self._place_single_lesson(lesson)
            if success:
                placed += 1
            else:
                # Backtracking — oldingi darslarni ko'chirib qayta urinish
                success = self._backtrack_and_place(lesson, max_depth=5)
                if success:
                    placed += 1
                else:
                    failed_lessons.append(lesson)

            if progress_callback and idx % 10 == 0:
                class_name = lesson['class_name']
                progress_callback(class_name, idx + 1, total, 0)

        # Agar hali ham joylashmagan darslar bo'lsa — majburiy joylashtirish
        if failed_lessons:
            self._force_place_remaining(failed_lessons)

        return True

    def _place_single_lesson(self, lesson):
        """Bitta darsni eng yaxshi slotga joylashtirish"""
        valid_slots = self._find_valid_slots(lesson)

        if not valid_slots:
            return False

        # Eng yaxshi slotni tanlash
        best_slot = self._select_best_slot(lesson, valid_slots)

        # Joylashtirish
        day, period = best_slot
        self._do_place(lesson, day, period)
        return True

    def _find_valid_slots(self, lesson):
        """
        Berilgan dars uchun barcha yaroqli slotlarni topish.
        Qoidalar:
        1. O'qituvchi boshqa sinfga dars o'tmayapti
        2. O'qituvchi band soati emas
        3. Sinfda bu vaqtda boshqa dars yo'q
        4. Kunlik dars limiti oshmagan
        5. Bir kunda bir xil fan takrorlanmagan
        6. SanPIN qoidalariga mos
        """
        t_id = lesson['teacher_id']
        class_id = lesson['class_id']
        subject = lesson['subject_name']
        # FIX: working_days kalit yo'q bo'lsa, WORKING_DAYS doimiyni ishlatish
        working_days = lesson.get('working_days', WORKING_DAYS)
        class_level = lesson['class_level']

        blocked = self.blocked_slots.get(t_id, set())
        methodic = self.methodic_slots.get(t_id, set())
        max_daily = self.class_daily_limits.get(class_id, 7)

        valid = []

        for day in range(working_days):
            for period in range(PERIODS_PER_DAY):
                # 1. O'qituvchi bandligi
                if (day, period) in blocked:
                    continue
                if (day, period) in methodic:
                    continue

                # 2. O'qituvchi boshqa sinfga dars o'tayaptimi?
                if self.teacher_grid.get(t_id, [[None]*WORKING_DAYS]*PERIODS_PER_DAY)[period][day] is not None:
                    continue

                # 3. Sinfda bu vaqtda dars bormi?
                if self.class_grid[class_id][period][day] is not None:
                    continue

                # 4. Kunlik dars limiti
                day_count = sum(
                    1 for p in range(PERIODS_PER_DAY)
                    if self.class_grid[class_id][p][day] is not None
                )
                if day_count >= max_daily:
                    continue

                # 5. Bir kunda bir xil fan takrorlanishi
                day_subjects = [
                    self.class_grid[class_id][p][day]['subject_name']
                    for p in range(PERIODS_PER_DAY)
                    if self.class_grid[class_id][p][day] is not None
                ]
                max_per_day = 2 if subject in ["Matematika", "Algebra"] else 1
                if day_subjects.count(subject) >= max_per_day:
                    continue

                # 6. 1-4 sinflarda ketma-ket bir xil fan
                if class_level <= 4:
                    if period > 0 and self.class_grid[class_id][period-1][day]:
                        if self.class_grid[class_id][period-1][day]['subject_name'] == subject:
                            continue
                    if period < PERIODS_PER_DAY - 1 and self.class_grid[class_id][period+1][day]:
                        if self.class_grid[class_id][period+1][day]['subject_name'] == subject:
                            continue

                valid.append((day, period))

        return valid

    def _select_best_slot(self, lesson, valid_slots):
        """
        Eng yaxshi slotni tanlash — ko'p mezonli baholash.
        Mezonlar:
        1. SanPIN optimal soat (Bells Curve)
        2. O'qituvchi oknosini minimallashtirish
        3. Kunlik teng taqsimot
        4. Qiyin fanlar ketma-ket kelmasligi
        """
        t_id = lesson['teacher_id']
        class_id = lesson['class_id']
        subject = lesson['subject_name']
        class_level = lesson['class_level']
        difficulty = self.sanpin.get_difficulty(subject)

        # FIX: Xavfsizlik tekshiruvi
        if 'working_days' not in lesson:
            lesson['working_days'] = WORKING_DAYS

        scored = []

        for day, period in valid_slots:
            score = 0

            # 1. SanPIN optimal soat (Bells Curve)
            optimal = self.sanpin.get_optimal_period(subject)
            if (period + 1) in optimal:
                score += 20
            elif (period + 1) in [o - 1 for o in optimal] or (period + 1) in [o + 1 for o in optimal]:
                score += 10

            # 2. O'qituvchi oknosini minimallashtirish
            teacher_gap = self._calculate_teacher_gap(t_id, day, period)
            score -= teacher_gap * 15  # Katta jazo

            # 3. Kunlik teng taqsimot — kam darsli kunlarga ustunlik
            day_count = sum(
                1 for p in range(PERIODS_PER_DAY)
                if self.class_grid[class_id][p][day] is not None
            )
            # Kam darsli kun = yuqori ball
            max_daily = self.class_daily_limits.get(class_id, 7)
            score += (max_daily - day_count) * 5

            # 4. Qiyin fanlar ketma-ket kelmasligi
            if period > 0 and self.class_grid[class_id][period-1][day]:
                prev_sub = self.class_grid[class_id][period-1][day]['subject_name']
                prev_diff = self.sanpin.get_difficulty(prev_sub)
                if difficulty >= 11 and prev_diff >= 11:
                    score -= 20  # Ketma-ket qiyin fanlar — katta jazo
                if prev_sub in ["Sport", "Jismoniy tarbiya"] and difficulty >= 11:
                    score -= 15  # Sportdan keyin qiyin fan

            # 5. 1-darsda juda qiyin fan
            if period == 0 and difficulty >= 13:
                score -= 10

            # 6. Oxirgi darsda qiyin fan
            day_lessons_count = sum(
                1 for p in range(PERIODS_PER_DAY)
                if self.class_grid[class_id][p][day] is not None
            )
            if period == day_lessons_count and difficulty >= 11:
                score -= 10

            # 7. Tasodifiy kichik farq (bir xil ball bo'lsa)
            score += random.uniform(0, 2)

            scored.append((score, day, period))

        # Eng yuqori ballli slot
        scored.sort(reverse=True, key=lambda x: x[0])
        return (scored[0][1], scored[0][2])

    def _calculate_teacher_gap(self, teacher_id, day, new_period):
        """
        O'qituvchining shu kundagi okno (bo'sh soat) sonini hisoblash.
        Agar yangi dars qo'yilsa, okno qanchaga oshishini qaytaradi.
        """
        grid = self.teacher_grid.get(teacher_id)
        if not grid:
            return 0

        # Hozirgi kundagi darslar
        current_periods = sorted([
            p for p in range(PERIODS_PER_DAY)
            if grid[p][day] is not None
        ])

        if not current_periods:
            return 0  # Birinchi dars — okno yo'q

        # Yangi darsni qo'shish
        all_periods = sorted(set(current_periods + [new_period]))

        # Okno sonini hisoblash
        gaps = 0
        for i in range(len(all_periods) - 1):
            gap = all_periods[i + 1] - all_periods[i] - 1
            if gap > 0:
                gaps += gap

        return gaps

    def _do_place(self, lesson, day, period):
        """Darsni jadvalga joylashtirish"""
        t_id = lesson['teacher_id']
        class_id = lesson['class_id']

        lesson_info = {
            'lesson_id': lesson['lesson_id'],
            'subject_name': lesson['subject_name'],
            'subject_short': lesson['subject_short'],
            'subject_id': lesson['subject_id'],
            'teacher_name': lesson['teacher_name'],
            'teacher_short': lesson['teacher_short'],
            'teacher_id': t_id,
            'class_id': class_id,
            'class_name': lesson['class_name'],
            'color': lesson['teacher_color'],
            'weekly_hours': lesson['weekly_hours'],
        }

        self.class_grid[class_id][period][day] = lesson_info
        self.teacher_grid[t_id][period][day] = class_id

    def _do_remove(self, class_id, day, period):
        """Darsni jadvaldan o'chirish"""
        lesson = self.class_grid[class_id][period][day]
        if lesson:
            t_id = lesson['teacher_id']
            self.class_grid[class_id][period][day] = None
            if self.teacher_grid.get(t_id):
                self.teacher_grid[t_id][period][day] = None
        return lesson

    # ================================================================
    # BACKTRACKING — Joy topilmaganda oldingi darslarni ko'chirish
    # ================================================================

    def _backtrack_and_place(self, lesson, max_depth=5):
        """
        Agar darsni joylashtirib bo'lmasa, oldingi darslarni ko'chirib
        bo'sh joy yaratish. Cheklangan chuqurlikda backtracking.
        """
        t_id = lesson['teacher_id']
        class_id = lesson['class_id']

        # O'qituvchining boshqa sinflardagi darslarini topish
        teacher_lessons = []
        if self.teacher_grid.get(t_id):
            for p in range(PERIODS_PER_DAY):
                for d in range(WORKING_DAYS):
                    cid = self.teacher_grid[t_id][p][d]
                    if cid is not None and cid != class_id:
                        teacher_lessons.append((cid, d, p))

        # Har bir darsni ko'chirib ko'rish
        for other_class, other_day, other_period in teacher_lessons[:max_depth]:
            # Darsni vaqtincha o'chirish
            removed = self._do_remove(other_class, other_day, other_period)

            # Asosiy darsni joylashtirishga urinish
            valid_slots = self._find_valid_slots(lesson)
            if valid_slots:
                best_slot = self._select_best_slot(lesson, valid_slots)
                self._do_place(lesson, best_slot[0], best_slot[1])

                # O'chirilgan darsni boshqa joyga qo'yish
                other_valid = self._find_valid_slots(removed)
                if other_valid:
                    other_best = self._select_best_slot(removed, other_valid)
                    self._do_place(removed, other_best[0], other_best[1])
                    return True
                else:
                    # O'chirilgan darsni qaytarish
                    self._do_place(removed, other_day, other_period)
                    self._do_remove(class_id, best_slot[0], best_slot[1])

        # Sinf ichidagi darslarni ko'chirib ko'rish
        class_lessons = []
        for p in range(PERIODS_PER_DAY):
            for d in range(WORKING_DAYS):
                if self.class_grid[class_id][p][d] is not None:
                    class_lessons.append((class_id, d, p))

        for _, other_day, other_period in class_lessons[:max_depth]:
            removed = self._do_remove(class_id, other_day, other_period)

            valid_slots = self._find_valid_slots(lesson)
            if valid_slots:
                best_slot = self._select_best_slot(lesson, valid_slots)
                self._do_place(lesson, best_slot[0], best_slot[1])

                other_valid = self._find_valid_slots(removed)
                if other_valid:
                    other_best = self._select_best_slot(removed, other_valid)
                    self._do_place(removed, other_best[0], other_best[1])
                    return True
                else:
                    self._do_place(removed, other_day, other_period)
                    self._do_remove(class_id, best_slot[0], best_slot[1])

        return False

    def _force_place_remaining(self, failed_lessons):
        """
        Joylashmagan darslarni majburiy joylashtirish.
        Cheklovlarni buzib bo'lsa ham, barcha darslar joylashtiriladi.
        """
        for lesson in failed_lessons:
            t_id = lesson['teacher_id']
            class_id = lesson['class_id']
            # FIX: working_days kalit yo'q bo'lsa, WORKING_DAYS doimiyni ishlatish
            working_days = lesson.get('working_days', WORKING_DAYS)

            # 1-urush: Barcha cheklovlarni hisobga olgan holda
            placed = False

            for day in range(working_days):
                if placed:
                    break
                for period in range(PERIODS_PER_DAY):
                    # O'qituvchi bandligi — bu cheklovni saqlash kerak
                    blocked = self.blocked_slots.get(t_id, set())
                    methodic = self.methodic_slots.get(t_id, set())
                    if (day, period) in blocked or (day, period) in methodic:
                        continue

                    # O'qituvchi boshqa sinfga dars o'tayaptimi?
                    if self.teacher_grid.get(t_id) and self.teacher_grid[t_id][period][day] is not None:
                        continue

                    # Sinfda dars bormi?
                    if self.class_grid[class_id][period][day] is not None:
                        continue

                    # Joylashtirish
                    self._do_place(lesson, day, period)
                    placed = True
                    break

            if not placed:
                # 2-urush: O'qituvchi cheklovlarini yumshatib
                for day in range(working_days):
                    if placed:
                        break
                    for period in range(PERIODS_PER_DAY):
                        if self.class_grid[class_id][period][day] is not None:
                            continue

                        # O'qituvchi boshqa sinfga dars o'tayaptimi?
                        if self.teacher_grid.get(t_id) and self.teacher_grid[t_id][period][day] is not None:
                            # Boshqa sinfdagi darsni ko'chirish
                            other_class = self.teacher_grid[t_id][period][day]
                            removed = self._do_remove(other_class, day, period)
                            self._do_place(lesson, day, period)

                            # Ko'chirilgan darsni joylashtirish
                            other_valid = self._find_valid_slots(removed)
                            if other_valid:
                                other_best = self._select_best_slot(removed, other_valid)
                                self._do_place(removed, other_best[0], other_best[1])
                            else:
                                # Joy topilmadi — qaytarish
                                self._do_remove(class_id, day, period)
                                self._do_place(removed, day, period)
                                continue

                        self._do_place(lesson, day, period)
                        placed = True
                        break

            if not placed:
                # 3-urush: Cheklovsiz — birinchi bo'sh joyga
                for day in range(working_days):
                    if placed:
                        break
                    for period in range(PERIODS_PER_DAY):
                        if self.class_grid[class_id][period][day] is None:
                            # O'qituvchini majburiy ko'chirish
                            if self.teacher_grid.get(t_id) and self.teacher_grid[t_id][period][day] is not None:
                                other_class = self.teacher_grid[t_id][period][day]
                                self._do_remove(other_class, day, period)
                            self._do_place(lesson, day, period)
                            placed = True
                            break

    # ================================================================
    # 4-QADAM: Natijalarni shakllantirish
    # ================================================================

    def _build_all_data(self):
        """Jadvaldan all_data formatiga o'tkazish"""
        all_data = {}

        for class_id, grid in self.class_grid.items():
            for period in range(PERIODS_PER_DAY):
                for day in range(WORKING_DAYS):
                    lesson = grid[period][day]
                    if lesson:
                        all_data[(class_id, day, period)] = lesson.copy()

        return all_data

    def _calculate_scores(self):
        """Har bir sinf uchun SanPIN ballini hisoblash"""
        self._scores = {}
        for class_id, grid in self.class_grid.items():
            class_level = self.class_info[class_id]['level']
            # grid formatini SanPIN ga moslash
            timetable = []
            for period in range(PERIODS_PER_DAY):
                row = []
                for day in range(WORKING_DAYS):
                    lesson = grid[period][day]
                    row.append(lesson['subject_name'] if lesson else '')
                timetable.append(row)
            res = self.sanpin.check_timetable(timetable, class_level)
            self._scores[class_id] = res['score']
