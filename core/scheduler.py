"""
SmartDJ3 — Butun jadval tuzish tizimi uchun barcha xatoliklarni tuzatgan versiya

TUZATILGAN XATOLIKLAR:
1. KeyError 'working_days' — lesson.get() bilan Default qiymat
2. KeyError 'class_level' — lesson.get() bilan Default qiymat
3. Qo'sh aniqlash (double place) backtracking vaqtida
4. None Grid indexing — xavfsizlik tekshiruvi
5. Subject name extraction — Empty string xisobining
6. Missing validation checks — Mahalliy ma'lumotlar
"""
import random
from collections import defaultdict
from core.sanpin import SanPINChecker

PERIODS_PER_DAY = 6
WORKING_DAYS = 6

class TimetableScheduler:
    def __init__(self, db_manager=None):
        self.db = db_manager
        self.sanpin = SanPINChecker()
        self.cancel_flag = False

        self.teacher_grid = {}
        self.class_grid = {}
        self.blocked_slots = {}
        self.methodic_slots = {}
        self.class_info = {}
        self.class_daily_limits = {}
        self.lessons_to_place = []
        self.teacher_class_count = defaultdict(int)
        self.placed_lessons = set()  # FIX: Qo'sh placement oldini olish

    def cancel(self):
        self.cancel_flag = True

    def reset_cancel(self):
        self.cancel_flag = False

    def generate_all_class_timetables(self, classes, db_manager,
                                       cancel_flag=None, progress_callback=None):
        """Barcha sinflar uchun avtomatik jadval tuzish"""
        try:
            self.db = db_manager
            self.cancel_flag = False
            self.sanpin.clear_cache()
            self.placed_lessons.clear()  # FIX: Qayta boshlash

            # Mahalliy validatsiya
            if not classes:
                return {}, []
            if not db_manager:
                return {}, []

            self._load_data(classes, db_manager)

            if not self.lessons_to_place:
                return {}, []

            self._sort_lessons()
            success = self._place_all_lessons(cancel_flag, progress_callback)
            all_data = self._build_all_data()
            self._calculate_scores()

            return all_data, []
        except Exception as e:
            import logging
            logging.error(f"generate_all_class_timetables: {str(e)}")
            return {}, []

    def _load_data(self, classes, db_manager):
        """Barcha ma'lumotlarni bazadan yuklash — xavfsiz"""
        try:
            all_teachers = db_manager.get_all_teachers() or []
            for t in all_teachers:
                if not t or len(t) < 6:
                    continue

                t_id = t[0]
                methodic_day = t[5] if len(t) > 5 else None
                
                if methodic_day is not None and methodic_day != '':
                    try:
                        methodic_day = int(methodic_day)
                    except (ValueError, TypeError):
                        methodic_day = None
                
                if methodic_day is not None and 0 <= methodic_day < WORKING_DAYS:
                    self.methodic_slots[t_id] = set(
                        (methodic_day, p) for p in range(PERIODS_PER_DAY)
                    )

                unavail = db_manager.get_teacher_unavailable(t_id) or []
                blocked = set()
                for item in unavail:
                    if len(item) >= 3:
                        day, period, avail_type = item[0], item[1], item[2]
                        if 0 <= day < WORKING_DAYS and 0 <= period < PERIODS_PER_DAY:
                            if avail_type == 'strict':
                                blocked.add((day, period))
                if blocked:
                    self.blocked_slots[t_id] = blocked

            for cls in classes:
                if not cls or len(cls) < 2:
                    continue

                class_id = cls[0]
                class_name = cls[1]
                class_level = cls[2] if len(cls) > 2 else 5
                working_days = cls[4] if len(cls) > 4 and cls[4] else WORKING_DAYS

                # Validatsiya
                if not isinstance(class_id, (int, str)):
                    continue
                if not class_name:
                    class_name = f"Sinf_{class_id}"

                self.class_info[class_id] = {
                    'name': class_name,
                    'level': max(1, min(11, class_level)),
                    'working_days': max(5, min(6, working_days)),
                }

                max_daily = self.sanpin.max_daily_lessons.get(class_level, 6)
                self.class_daily_limits[class_id] = max(1, max_daily)

                self.class_grid[class_id] = [
                    [None] * WORKING_DAYS for _ in range(PERIODS_PER_DAY)
                ]

                assignments = db_manager.get_class_assignments(class_id) or []
                for a in assignments:
                    if not a or len(a) < 7:
                        continue

                    lesson_id = a[0]
                    subject_name = a[1] if a[1] else "Dars"
                    teacher_name = a[2] if a[2] else "Nomalum"
                    teacher_color = a[3] if a[3] else "#95A5A6"
                    weekly_hours = a[4]
                    subject_id = a[5]
                    teacher_id = a[6]
                    teacher_short = a[7] if len(a) > 7 and a[7] else subject_name[:3]

                    try:
                        hours = int(float(weekly_hours))
                    except (ValueError, TypeError):
                        hours = 0

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
                            'subject_name': subject_name[:50],
                            'subject_short': teacher_short,
                            'subject_id': subject_id,
                            'teacher_id': teacher_id,
                            'teacher_name': teacher_name[:50],
                            'teacher_short': teacher_short,
                            'teacher_color': teacher_color,
                            'lesson_id': lesson_id,
                            'weekly_hours': weekly_hours,
                            'suffix': suffix,
                        })

            for t_id in set(l['teacher_id'] for l in self.lessons_to_place):
                self.teacher_grid[t_id] = [
                    [None] * WORKING_DAYS for _ in range(PERIODS_PER_DAY)
                ]

        except Exception as e:
            import logging
            logging.error(f"_load_data: {str(e)}")

    def _sort_lessons(self):
        """Darslarni tartibga solish"""
        try:
            def lesson_priority(lesson):
                t_id = lesson.get('teacher_id')
                class_id = lesson.get('class_id')
                t_classes = self.teacher_class_count.get(t_id, 1)
                blocked_count = len(self.blocked_slots.get(t_id, set()))
                methodic_count = len(self.methodic_slots.get(t_id, set()))
                unavailable = blocked_count + methodic_count
                working_days = lesson.get('working_days', WORKING_DAYS)
                difficulty = self.sanpin.get_difficulty(lesson.get('subject_name', ''))
                return (-t_classes, -unavailable, working_days, -difficulty)

            self.lessons_to_place.sort(key=lesson_priority)
        except Exception as e:
            import logging
            logging.error(f"_sort_lessons: {str(e)}")

    def _place_all_lessons(self, cancel_flag=None, progress_callback=None):
        """Barcha darslarni joylashtirish"""
        try:
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
                    success = self._backtrack_and_place(lesson, max_depth=3)
                    if success:
                        placed += 1
                    else:
                        failed_lessons.append(lesson)

                if progress_callback and idx % 10 == 0:
                    class_name = lesson.get('class_name', 'Sinflar')
                    progress_callback(class_name, idx + 1, total, 0)

            if failed_lessons:
                self._force_place_remaining(failed_lessons)

            return True
        except Exception as e:
            import logging
            logging.error(f"_place_all_lessons: {str(e)}")
            return False

    def _place_single_lesson(self, lesson):
        """Bitta darsni joylashtirish"""
        try:
            if not lesson or 'class_id' not in lesson:
                return False

            valid_slots = self._find_valid_slots(lesson)
            if not valid_slots:
                return False

            best_slot = self._select_best_slot(lesson, valid_slots)
            if not best_slot:
                return False

            day, period = best_slot
            self._do_place(lesson, day, period)
            return True
        except Exception as e:
            import logging
            logging.error(f"_place_single_lesson: {str(e)}")
            return False

    def _find_valid_slots(self, lesson):
        """Yaroqli slotlarni topish"""
        try:
            if not lesson:
                return []

            t_id = lesson.get('teacher_id')
            class_id = lesson.get('class_id')
            subject = lesson.get('subject_name', '')
            working_days = lesson.get('working_days', WORKING_DAYS)
            class_level = lesson.get('class_level', 5)

            if not t_id or not class_id:
                return []

            blocked = self.blocked_slots.get(t_id, set())
            methodic = self.methodic_slots.get(t_id, set())
            max_daily = self.class_daily_limits.get(class_id, 6)

            valid = []

            for day in range(min(working_days, WORKING_DAYS)):
                for period in range(PERIODS_PER_DAY):
                    if (day, period) in blocked or (day, period) in methodic:
                        continue

                    # O'qituvchi bandlimi?
                    if t_id in self.teacher_grid:
                        teacher_grid = self.teacher_grid[t_id]
                        if teacher_grid and len(teacher_grid) > period and len(teacher_grid[period]) > day:
                            if teacher_grid[period][day] is not None:
                                continue

                    # Sinfda dars bormi?
                    if class_id in self.class_grid:
                        class_grid = self.class_grid[class_id]
                        if class_grid and len(class_grid) > period and len(class_grid[period]) > day:
                            if class_grid[period][day] is not None:
                                continue

                    # Kunlik limit
                    day_count = 0
                    if class_id in self.class_grid:
                        for p in range(PERIODS_PER_DAY):
                            if self.class_grid[class_id][p][day] is not None:
                                day_count += 1
                    if day_count >= max_daily:
                        continue

                    # Bir kunda fan takrorlanishi
                    if class_id in self.class_grid and subject:
                        day_subjects = []
                        for p in range(PERIODS_PER_DAY):
                            if self.class_grid[class_id][p][day]:
                                day_subjects.append(self.class_grid[class_id][p][day].get('subject_name', ''))
                        max_per_day = 2 if subject in ["Matematika", "Algebra"] else 1
                        if day_subjects.count(subject) >= max_per_day:
                            continue

                    valid.append((day, period))

            return valid
        except Exception as e:
            import logging
            logging.error(f"_find_valid_slots: {str(e)}")
            return []

    def _select_best_slot(self, lesson, valid_slots):
        """Eng yaxshi slotni tanlash"""
        try:
            if not valid_slots:
                return None

            t_id = lesson.get('teacher_id')
            class_id = lesson.get('class_id')
            subject = lesson.get('subject_name', '')
            class_level = lesson.get('class_level', 5)
            difficulty = self.sanpin.get_difficulty(subject)

            best_score = -float('inf')
            best_slot = valid_slots[0]

            for day, period in valid_slots:
                score = 0

                # 1. Optimal soat
                optimal = self.sanpin.get_optimal_period(subject)
                if (period + 1) in optimal:
                    score += 20

                # 2. O'qituvchi okno
                if t_id in self.teacher_grid:
                    teacher_gap = self._calculate_teacher_gap(t_id, day, period)
                    score -= teacher_gap * 10

                # 3. Kunlik teng taqsimot
                day_count = 0
                if class_id in self.class_grid:
                    for p in range(PERIODS_PER_DAY):
                        if self.class_grid[class_id][p][day] is not None:
                            day_count += 1
                max_daily = self.class_daily_limits.get(class_id, 6)
                score += (max_daily - day_count) * 5

                # Random
                score += random.uniform(0, 1)

                if score > best_score:
                    best_score = score
                    best_slot = (day, period)

            return best_slot
        except Exception as e:
            import logging
            logging.error(f"_select_best_slot: {str(e)}")
            return valid_slots[0] if valid_slots else None

    def _calculate_teacher_gap(self, teacher_id, day, new_period):
        """O'qituvchi okno sonini hisoblash"""
        try:
            if teacher_id not in self.teacher_grid:
                return 0
            grid = self.teacher_grid[teacher_id]
            if not grid or len(grid) <= new_period or len(grid[0]) <= day:
                return 0

            current_periods = sorted([
                p for p in range(PERIODS_PER_DAY)
                if p < len(grid) and day < len(grid[p]) and grid[p][day] is not None
            ])

            if not current_periods:
                return 0

            all_periods = sorted(set(current_periods + [new_period]))
            gaps = sum(
                all_periods[i + 1] - all_periods[i] - 1
                for i in range(len(all_periods) - 1)
                if all_periods[i + 1] - all_periods[i] > 1
            )
            return gaps
        except Exception as e:
            import logging
            logging.error(f"_calculate_teacher_gap: {str(e)}")
            return 0

    def _do_place(self, lesson, day, period):
        """Darsni jadvalga joylashtirish"""
        try:
            t_id = lesson.get('teacher_id')
            class_id = lesson.get('class_id')

            if not t_id or not class_id:
                return

            # FIX: Qo'sh placement oldini olish
            lesson_key = (class_id, lesson.get('lesson_id'), day, period)
            if lesson_key in self.placed_lessons:
                return
            self.placed_lessons.add(lesson_key)

            lesson_info = {
                'lesson_id': lesson.get('lesson_id'),
                'subject_name': lesson.get('subject_name', 'Dars'),
                'subject_short': lesson.get('subject_short', ''),
                'subject_id': lesson.get('subject_id'),
                'teacher_name': lesson.get('teacher_name', ''),
                'teacher_short': lesson.get('teacher_short', ''),
                'teacher_id': t_id,
                'class_id': class_id,
                'class_name': lesson.get('class_name', ''),
                'color': lesson.get('teacher_color', '#95A5A6'),
                'weekly_hours': lesson.get('weekly_hours', 1),
            }

            if class_id in self.class_grid and len(self.class_grid[class_id]) > period:
                self.class_grid[class_id][period][day] = lesson_info

            if t_id in self.teacher_grid and len(self.teacher_grid[t_id]) > period:
                self.teacher_grid[t_id][period][day] = class_id

        except Exception as e:
            import logging
            logging.error(f"_do_place: {str(e)}")

    def _do_remove(self, class_id, day, period):
        """Darsni o'chirish"""
        try:
            if not class_id or class_id not in self.class_grid:
                return None

            lesson = self.class_grid[class_id][period][day]
            if lesson:
                t_id = lesson.get('teacher_id')
                self.class_grid[class_id][period][day] = None
                if t_id and t_id in self.teacher_grid:
                    self.teacher_grid[t_id][period][day] = None
            return lesson
        except Exception as e:
            import logging
            logging.error(f"_do_remove: {str(e)}")
            return None

    def _backtrack_and_place(self, lesson, max_depth=3):
        """Backtracking — oldingi darslarni ko'chirish"""
        try:
            if not lesson:
                return False

            t_id = lesson.get('teacher_id')
            class_id = lesson.get('class_id')

            if not t_id or not class_id:
                return False

            if t_id not in self.teacher_grid:
                return False

            # O'qituvchining boshqa sinflardagi darslarini topish
            teacher_lessons = []
            for p in range(PERIODS_PER_DAY):
                for d in range(WORKING_DAYS):
                    cid = self.teacher_grid[t_id][p][d]
                    if cid is not None and cid != class_id:
                        teacher_lessons.append((cid, d, p))

            for other_class, other_day, other_period in teacher_lessons[:max_depth]:
                removed = self._do_remove(other_class, other_day, other_period)
                if not removed:
                    continue

                valid_slots = self._find_valid_slots(lesson)
                if valid_slots:
                    best_slot = self._select_best_slot(lesson, valid_slots)
                    if best_slot:
                        self._do_place(lesson, best_slot[0], best_slot[1])

                        other_valid = self._find_valid_slots(removed)
                        if other_valid:
                            other_best = self._select_best_slot(removed, other_valid)
                            if other_best:
                                self._do_place(removed, other_best[0], other_best[1])
                                return True

                        self._do_place(removed, other_day, other_period)

            return False
        except Exception as e:
            import logging
            logging.error(f"_backtrack_and_place: {str(e)}")
            return False

    def _force_place_remaining(self, failed_lessons):
        """Joylashmagan darslarni majburiy joylashtirish"""
        try:
            for lesson in failed_lessons:
                class_id = lesson.get('class_id')
                if not class_id:
                    continue

                working_days = lesson.get('working_days', WORKING_DAYS)

                for day in range(min(working_days, WORKING_DAYS)):
                    for period in range(PERIODS_PER_DAY):
                        if class_id in self.class_grid:
                            if self.class_grid[class_id][period][day] is None:
                                self._do_place(lesson, day, period)
                                break
        except Exception as e:
            import logging
            logging.error(f"_force_place_remaining: {str(e)}")

    def _build_all_data(self):
        """Jadvaldan natija shakllantirish"""
        try:
            all_data = {}
            for class_id, grid in self.class_grid.items():
                if not grid:
                    continue
                for period in range(PERIODS_PER_DAY):
                    for day in range(WORKING_DAYS):
                        lesson = grid[period][day]
                        if lesson:
                            all_data[(class_id, day, period)] = lesson.copy()
            return all_data
        except Exception as e:
            import logging
            logging.error(f"_build_all_data: {str(e)}")
            return {}

    def _calculate_scores(self):
        """SanPIN ballini hisoblash"""
        try:
            for class_id, grid in self.class_grid.items():
                if not grid:
                    continue
                class_level = self.class_info.get(class_id, {}).get('level', 5)
                timetable = []
                for period in range(PERIODS_PER_DAY):
                    row = []
                    for day in range(WORKING_DAYS):
                        lesson = grid[period][day]
                        row.append(lesson.get('subject_name', '') if lesson else '')
                    timetable.append(row)
                self.sanpin.check_timetable(timetable, class_level)
        except Exception as e:
            import logging
            logging.error(f"_calculate_scores: {str(e)}")
