"""
SanPIN QOIDALARI — Yangi talablar asosida (2025-2026)

Asosiy qoidalar:
1. Kuniga maksimal dars soatlari (sinf bo'yicha)
2. Haftaga maksimal dars soatlari
3. Fan qiyinlik ballari (1-13 shkala)
4. 1-4 sinflarda ketma-ket bir xil fan taqiqlanadi
5. Kunlik yuklama parabola (Bells Curve) shaklida bo'lishi kerak
6. Bir kunda bir fan takrorlanish cheklovi
7. Darslar orasida "oyna" bo'lmasligi
"""
import math

PERIODS_PER_DAY = 6  # Kuniga maksimal 6 dars (7-dars yo'q)


class SanPINChecker:
    def __init__(self):
        # Kunlik maksimal dars soatlari (Yangi SanPIN)
        # 1-sinf: 4 soat (bir kun 5 mumkin)
        # 2-4 sinflar: 5 soat
        # 5-9 sinflar: 6 soat
        # 10-11 sinflar: 7 soat
        self.max_daily_lessons = {
            1: 4,   # 1-sinf: kuniga 4 (bir kun 5 mumkin)
            2: 5,   # 2-sinf: kuniga 5
            3: 5,   # 3-sinf: kuniga 5
            4: 5,   # 4-sinf: kuniga 5
            5: 6,   # 5-sinf: kuniga 6
            6: 6,   # 6-sinf: kuniga 6
            7: 6,   # 7-sinf: kuniga 6
            8: 6,   # 8-sinf: kuniga 6
            9: 6,   # 9-sinf: kuniga 6
            10: 7,  # 10-sinf: kuniga 7
            11: 7   # 11-sinf: kuniga 7
        }

        # Haftalik maksimal dars soatlari
        self.max_weekly_lessons = {
            1: 20,
            2: 25,
            3: 25,
            4: 26,
            5: 30,
            6: 30,
            7: 32,
            8: 33,
            9: 33,
            10: 34,
            11: 34
        }

        # Fan qiyinlik darajalari — YANGI SHKALA (1-13)
        # Toifa A (Eng qiyin, 11-13 ball):
        #   Matematika, Algebra, Geometriya, Fizika, Kimyo, Informatika, Chet tili
        # Toifa B (O'rtacha, 8-10 ball):
        #   Ona tili, Adabiyot, Biologiya, Geografiya, Tarix
        # Toifa C (Yengil, 3-5 ball):
        #   Tarbiya, Jismoniy tarbiya, Texnologiya, Tasviriy san'at, Musiqa
        self.difficulty = {
            # Toifa A — Eng qiyin (11-13)
            "Matematika": 12,
            "Algebra": 13,
            "Geometriya": 11,
            "Fizika": 13,
            "Kimyo": 12,
            "Informatika": 11,
            "Chet tili": 11,
            "Ingliz tili": 11,
            "Rus tili": 11,

            # Toifa B — O'rtacha (8-10)
            "Ona tili": 9,
            "Adabiyot": 9,
            "Biologiya": 8,
            "Geografiya": 8,
            "Tarix": 9,
            "Huquq": 8,
            "Iqtisodiyot": 8,

            # Toifa C — Yengil (3-5)
            "Tarbiya": 3,
            "Jismoniy tarbiya": 4,
            "Sport": 4,
            "Texnologiya": 5,
            "Tasviriy san'at": 3,
            "Musiqa": 3,
            "San'at": 3,
            "Mehnat": 5,
            "Chaqiriqqacha harbiy tayyorgarlik": 5,
            "Tarbiyaviy soat": 3,
        }

        # Toifa bo'yicha guruhlash
        self.subject_category = {}
        for fan, ball in self.difficulty.items():
            if ball >= 11:
                self.subject_category[fan] = "A"  # Eng qiyin
            elif ball >= 8:
                self.subject_category[fan] = "B"  # O'rtacha
            else:
                self.subject_category[fan] = "C"  # Yengil

        # Qiyin fanlar (Toifa A — ball >= 11)
        self.hard_subjects = [
            fan for fan, ball in self.difficulty.items() if ball >= 11
        ]

        # Yengil fanlar (Toifa C — ball <= 5)
        self.easy_subjects = [
            fan for fan, ball in self.difficulty.items() if ball <= 5
        ]

        # O'rtacha fanlar (Toifa B — ball 8-10)
        self.medium_subjects = [
            fan for fan, ball in self.difficulty.items() if 8 <= ball <= 10
        ]

        # Fitness cache — katta hajm uchun (250 sinf = 50,000+ tekshiruv)
        self._fitness_cache = {}
        self._cache_max_size = 50000

        # Bells Curve — optimal kunlik qiyinlik naqshi
        # 1-dars: o'rtacha, 2-3: eng qiyin, 4: o'rtacha, 5+: yengil
        self.bells_curve = {
            1: (8, 10),   # 1-dars: o'rtacha-yuqori (moslashish)
            2: (11, 13),  # 2-dars: eng qiyin (aqlli faollik cho'qqisi)
            3: (11, 13),  # 3-dars: eng qiyin
            4: (8, 10),   # 4-dars: o'rtacha
            5: (3, 6),    # 5-dars: yengil
            6: (3, 5),    # 6-dars: eng yengil
            7: (3, 5),    # 7-dars: eng yengil
        }

    def _timetable_hash(self, timetable_data, class_level):
        """Jadval uchun tez hash — cache uchun"""
        parts = [class_level]
        for period in range(PERIODS_PER_DAY):
            row = timetable_data[period] if period < len(timetable_data) else None
            for day in range(6):
                cell = row[day] if row and day < len(row) else ""
                parts.append(cell.strip() if cell else "")
        return tuple(parts)

    def check_timetable(self, timetable_data, class_level, tayanch_hours=None):
        """
        Jadvalni to'liq tekshirish — TAYANCH REJA USTUNLIGI bilan

        timetable_data: [[fan1, fan2, ...], [...], ...]  - 7x6 jadval
        class_level: int - sinf raqami (1-11)
        tayanch_hours: dict - tayanch rejadagi soatlar {fan_nomi: soat_soni}
                         Agar berilmasa, eski qoida bo'yicha ishlaydi

        Qoida: Tayanch reja ustun — agar tayanch reja SanPIN limitidan oshsa,
               xato o'rniga ogohlantirish beriladi.
        """
        # Cache tekshirish — tayanch_hours bilan ham ishlaydi
        cache_key = self._timetable_hash(timetable_data, class_level)
        tayanch_key = hash(tuple(sorted(tayanch_hours.items()))) if tayanch_hours else 0
        combined_key = (cache_key, tayanch_key)
        if combined_key in self._fitness_cache:
            cached = self._fitness_cache[combined_key]
            # Nusxa qaytarish — cache'dagi dict o'zgartirilmasligi uchun
            return {
                'score': cached['score'],
                'errors': list(cached['errors']),
                'warnings': list(cached['warnings']),
                'details': list(cached['details']),
            }

        errors = []
        warnings = []
        details = []
        total_score = 100

        kunlar = ["Dushanba", "Seshanba", "Chorshanba",
                  "Payshanba", "Juma", "Shanba"]

        # Tayanch reja yig'indisi (Kelajak soatisiz)
        tayanch_total = sum(h for k, h in tayanch_hours.items() if 'kelajak' not in k.lower()) if tayanch_hours else 0
        tayanch_overrides = tayanch_total > 0  # Tayanch reja ustun rejimi

        # Haftalik jami darslarni hisoblash (Kelajak soatisiz)
        total_lessons = 0
        for dars_index in range(PERIODS_PER_DAY):
            for kun_index in range(6):
                if dars_index < len(timetable_data) and kun_index < len(timetable_data[dars_index]):
                    fan = timetable_data[dars_index][kun_index]
                    if fan and fan.strip():
                        # Kelajak soatini hisobga olmaslik
                        if 'kelajak' not in fan.lower():
                            total_lessons += 1

        # Kunlik fanlarni yig'ish (Kelajak soatisiz)
        daily_fans = {}
        for kun_index in range(6):
            daily_fans[kun_index] = []
            for dars_index in range(PERIODS_PER_DAY):
                if dars_index < len(timetable_data) and kun_index < len(timetable_data[dars_index]):
                    fan = timetable_data[dars_index][kun_index]
                    if fan and fan.strip():
                        if 'kelajak' not in fan.lower():
                            daily_fans[kun_index].append(fan.strip())

        # ========== TEKSHIRUVLAR ==========

        max_daily = self.max_daily_lessons.get(class_level, 7)
        max_weekly = self.max_weekly_lessons.get(class_level, 34)

        # Ish kunlarini jadvaldan aniqlash
        working_days = 6
        for day in range(6):
            has_lesson = False
            for period in range(PERIODS_PER_DAY):
                if period < len(timetable_data) and day < len(timetable_data[period]):
                    if timetable_data[period][day]:
                        has_lesson = True
                        break
            if not has_lesson:
                working_days = day
                break

        # Tayanch reja bo'lsa — chegaralarni tayanch rejaga moslash
        if tayanch_overrides and tayanch_total > 0:
            effective_max_weekly = max(max_weekly, tayanch_total)
            effective_max_daily = max(max_daily, math.ceil(tayanch_total / max(working_days, 1)))
        else:
            effective_max_weekly = max_weekly
            effective_max_daily = max_daily

        # 1. HAFTALIK DARS SOATLARI TEKSHIRUVI
        if total_lessons > effective_max_weekly:
            errors.append(
                f"❌ Haftalik {total_lessons} ta dars bor, "
                f"max {effective_max_weekly} ta bo'lishi kerak ({class_level}-sinf uchun)"
            )
            total_score -= 15
        else:
            details.append(
                f"✅ Haftalik dars soati: {total_lessons}/{effective_max_weekly}"
            )

        # 2. KUNLIK DARS SOATLARI TEKSHIRUVI
        for kun_index in range(6):
            kun_darslari = daily_fans.get(kun_index, [])
            if len(kun_darslari) > effective_max_daily:
                errors.append(
                    f"❌ {kunlar[kun_index]}: {len(kun_darslari)} ta dars bor, "
                    f"max {effective_max_daily} ta bo'lishi kerak ({class_level}-sinf uchun)"
                )
                total_score -= 10

        # 3. 1-4 SINFLARDA KETMA-KET BIR XIL FAN TAQIQLANADI (Hard Constraint)
        if class_level <= 4:
            for kun_index in range(6):
                kun_darslari = daily_fans.get(kun_index, [])
                for i in range(len(kun_darslari) - 1):
                    if kun_darslari[i] == kun_darslari[i + 1]:
                        errors.append(
                            f"❌ {kunlar[kun_index]}: {i+1} va {i+2}-darslarda "
                            f"ketma-ket '{kun_darslari[i]}' — 1-4 sinflarda taqiqlanadi!"
                        )
                        total_score -= 15

        # 4. KETMA-KET QIYIN FANLAR TEKSHIRUVI
        for kun_index in range(6):
            prev_hard = False
            for dars_index in range(PERIODS_PER_DAY):
                if dars_index < len(timetable_data) and kun_index < len(timetable_data[dars_index]):
                    fan = timetable_data[dars_index][kun_index]
                    if fan and fan.strip():
                        is_hard = fan.strip() in self.hard_subjects
                        if is_hard and prev_hard:
                            warnings.append(
                                f"⚠️ {kunlar[kun_index]}: {dars_index}-dars va "
                                f"{dars_index + 1}-darsda ketma-ket qiyin fan!"
                            )
                            total_score -= 5
                        prev_hard = is_hard
                    else:
                        prev_hard = False

        # 4. BIRINCHI DARSDA QIYIN FAN TEKSHIRUVI
        for kun_index in range(6):
            if 0 < len(timetable_data) and kun_index < len(timetable_data[0]):
                fan = timetable_data[0][kun_index]
                if fan and fan.strip() in self.hard_subjects:
                    difficulty = self.difficulty.get(fan.strip(), 5)
                    if difficulty >= 9:
                        warnings.append(
                            f"⚠️ {kunlar[kun_index]}: 1-darsda juda qiyin fan "
                            f"({fan.strip()}) qo'yilgan"
                        )
                        total_score -= 3

        # 5. OXIRGI DARSDA QIYIN FAN TEKSHIRUVI
        for kun_index in range(6):
            last_lesson = None
            last_index = 0
            for dars_index in range(6, -1, -1):
                if dars_index < len(timetable_data) and kun_index < len(timetable_data[dars_index]):
                    fan = timetable_data[dars_index][kun_index]
                    if fan and fan.strip():
                        last_lesson = fan.strip()
                        last_index = dars_index + 1
                        break

            if last_lesson and last_lesson in self.hard_subjects:
                difficulty = self.difficulty.get(last_lesson, 5)
                if difficulty >= 8:
                    warnings.append(
                        f"⚠️ {kunlar[kun_index]}: Oxirgi ({last_index}-)darsda "
                        f"qiyin fan ({last_lesson}) qo'yilgan"
                    )
                    total_score -= 3

        # 6. BIR KUNDA BIR FAN TAKRORLANISHI TEKSHIRUVI
        # Haftada >5 soat bo'lgan fanlar kuniga 2 marta mumkin (tayanch reja bo'yicha)
        for kun_index in range(6):
            kun_fanlari = daily_fans.get(kun_index, [])
            seen = {}
            for fan in kun_fanlari:
                seen[fan] = seen.get(fan, 0) + 1

            for fan, count in seen.items():
                if fan in ["Matematika", "Algebra"]:
                    continue  # Matematika/Algebra doimo 2 marta mumkin
                max_per_day = 2 if (tayanch_hours and tayanch_hours.get(fan, 0) > 5) else 1
                if count > max_per_day:
                    if tayanch_overrides and tayanch_hours and tayanch_hours.get(fan, 0) > 5:
                        # Tayanch reja talabi — ogohlantirish
                        warnings.append(
                            f"⚠️ {kunlar[kun_index]}: '{fan}' {count} marta takrorlangan "
                            f"(tayanch reja: {tayanch_hours[fan]} soat/hafta)"
                        )
                        total_score -= 2
                    else:
                        errors.append(
                            f"❌ {kunlar[kun_index]}: '{fan}' bir kunda "
                            f"{count} marta takrorlangan!"
                        )
                        total_score -= 8

        # 7. SPORT DARSIDAN KEYIN QIYIN FAN TEKSHIRUVI
        sport_fanlar = ["Sport", "Jismoniy tarbiya"]
        for kun_index in range(6):
            kun_fanlari = daily_fans.get(kun_index, [])
            for dars_index in range(len(kun_fanlari) - 1):
                fan = kun_fanlari[dars_index]
                if fan in sport_fanlar:
                    next_fan = kun_fanlari[dars_index + 1]
                    if next_fan in self.hard_subjects:
                        warnings.append(
                            f"⚠️ {kunlar[kun_index]}: Sport darsidan keyin "
                            f"qiyin fan ({next_fan}) qo'yilgan"
                        )
                        total_score -= 4

        # 8. "OYNA" (BO'SH DARS) TEKSHIRUVI
        for kun_index in range(6):
            darslar_bor = False
            oyna_topildi = False

            for dars_index in range(PERIODS_PER_DAY):
                if dars_index < len(timetable_data) and kun_index < len(timetable_data[dars_index]):
                    fan = timetable_data[dars_index][kun_index]
                    if fan and fan.strip():
                        if oyna_topildi and darslar_bor:
                            errors.append(
                                f"❌ {kunlar[kun_index]}: Darslar orasida "
                                f"'oyna' (bo'sh dars) bor!"
                            )
                            total_score -= 10
                            break
                        darslar_bor = True
                        oyna_topildi = False
                    else:
                        if darslar_bor:
                            oyna_topildi = True

        # 9. QIYINLIK BALANSI TEKSHIRUVI
        kun_qiyinliklari = []
        for kun_index in range(6):
            kun_ball = 0
            dars_soni = 0
            for dars_index in range(PERIODS_PER_DAY):
                if dars_index < len(timetable_data) and kun_index < len(timetable_data[dars_index]):
                    fan = timetable_data[dars_index][kun_index]
                    if fan and fan.strip():
                        kun_ball += self.difficulty.get(fan.strip(), 5)
                        dars_soni += 1

            if dars_soni > 0:
                kun_qiyinliklari.append(kun_ball)

        if kun_qiyinliklari:
            max_qiyinlik = max(kun_qiyinliklari)
            min_qiyinlik = min(kun_qiyinliklari)

            if max_qiyinlik - min_qiyinlik > 20:
                warnings.append(
                    f"⚠️ Hafta davomida kunlar qiyinligi juda farq qiladi "
                    f"(max: {max_qiyinlik}, min: {min_qiyinlik})"
                )
                total_score -= 5

            if len(kun_qiyinliklari) >= 3:
                if kun_qiyinliklari[2] == max(kun_qiyinliklari):
                    details.append(
                        "✅ Chorshanba eng qiyin kun - SanPIN bo'yicha to'g'ri"
                    )
                else:
                    warnings.append(
                        "⚠️ SanPIN bo'yicha Chorshanba eng qiyin kun bo'lishi kerak"
                    )
                    total_score -= 2

        # 10. BELLS CURVE — KUNLIK QIYINLIK NAQSHI
        # Faqat 2+ ketma-ket ogohlantirish beriladi (har kunda 1 marta)
        for kun_index in range(6):
            kun_darslari = daily_fans.get(kun_index, [])
            # Kun ichida ogohlantirishlar sonini hisoblash
            period23_warnings = 0
            period5plus_warnings = 0
            for dars_index, fan in enumerate(kun_darslari):
                period = dars_index + 1  # 1-based
                if period not in self.bells_curve:
                    continue
                fan_diff = self.difficulty.get(fan, 5)

                # 2-3 darslarda juda yengil fan (threshold 6 ga tushirildi)
                if period in [2, 3] and fan_diff < 6:
                    period23_warnings += 1

                # 5+ darslarda juda qiyin fan
                if period >= 5 and fan_diff >= 11:
                    period5plus_warnings += 1

            # Faqat 2+ bo'lsa ogohlantirish
            if period23_warnings >= 2:
                warnings.append(
                    f"⚠️ {kunlar[kun_index]}: 2-3 darslarda bir nechta yengil fan — "
                    f"qiyin fanlar ko'proq bo'lishi kerak"
                )
                total_score -= 2

            if period5plus_warnings >= 2:
                warnings.append(
                    f"⚠️ {kunlar[kun_index]}: 5+ darslarda bir nechta juda qiyin fan — "
                    f"yengil fanlar ko'proq bo'lishi kerak"
                )
                total_score -= 2

        # Ball chegarasi
        total_score = max(0, min(100, total_score))

        result = {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'score': total_score,
            'details': details,
            'total_lessons': total_lessons,
            'max_weekly': max_weekly
        }

        # Cache (barcha holatlar uchun — tayanch_hours bilan ham)
        if len(self._fitness_cache) < self._cache_max_size:
            self._fitness_cache[combined_key] = result

        return result

    def clear_cache(self):
        """Fitness cache ni tozalash"""
        self._fitness_cache.clear()

    def get_difficulty(self, subject_name):
        """Fan qiyinlik darajasini olish"""
        return self.difficulty.get(subject_name, 5)

    def get_optimal_period(self, subject_name):
        """Fan uchun optimal dars tartibini tavsiya qilish (Bells Curve asosida)"""
        diff = self.get_difficulty(subject_name)

        # Toifa A (11-13): 2-3 darslar (eng yuqori aqliy faollik)
        if diff >= 11:
            return [2, 3]
        # Toifa B (8-10): 1, 2, 3, 4 darslar
        elif diff >= 8:
            return [1, 2, 3, 4]
        # Toifa C (3-5): 4, 5, 6, 7 darslar (yengil)
        else:
            return [4, 5, 6, 7]