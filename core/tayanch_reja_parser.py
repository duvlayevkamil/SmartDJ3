"""
Tayanch Reja PDF Parser — MTT tayanch o'quv rejasini parse qilish.
19 sahifali PDF: har bir ta'lim turi uchun alohida jadval.
"""

import re
import pdfplumber


class TayanchRejaParser:
    """PDF fayldan tayanch reja jadvalini parse qilish."""

    def __init__(self):
        self.errors = []

    def parse(self, pdf_path):
        """
        PDF fayldan barcha tayanch reja jadvallarini topadi.
        Returns: dict — {
            "subjects": [{"name": str, "short": str, "is_group": bool}],
            "classes": [{"name": str, "level": int}],
            "hours": [[int, ...], ...]
        }
        """
        self.errors = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # 1-ILOVA sahifalarini topish (O'zbek tilida)
                target_pages = self._find_ilova_pages(pdf)

                if not target_pages:
                    self.errors.append("PDF faylda 1-ILOVA (o'zbek tili) jadvali topilmadi!")
                    return None

                # Faqat birinchi 1-ILOVA sahifasidan boshlash
                all_rows = []
                for page_idx in target_pages:
                    page = pdf.pages[page_idx]
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            all_rows.extend(table)

                if not all_rows:
                    self.errors.append("PDF faylda jadval topilmadi!")
                    return None

                return self._parse_rows(all_rows)

        except Exception as e:
            self.errors.append(f"PDF o'qishda xatolik: {str(e)}")
            return None

    def _find_ilova_pages(self, pdf):
        """1-ILOVA sahifalarini topish"""
        import re
        ilova_pages = []

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                # "1- ILOVA", "1-ILOVA", "1 ILOVA" formatlarini qidirish
                if re.search(r'1[\s\-]*ILOVA', text, re.IGNORECASE):
                    ilova_pages.append(i)
                    # Keyingi sahifani ham qo'shish (jadval davom etishi mumkin)
                    if i + 1 < len(pdf.pages):
                        next_text = pdf.pages[i + 1].extract_text() or ''
                        # Agar keyingi sahifada ham jadval bo'lsa
                        if 'Tadbirkorlik' in next_text or 'Musiqa' in next_text or 'Jismoniy' in next_text:
                            ilova_pages.append(i + 1)

        # Agar 1-ILOVA topilmasa — birinchi jadvali bor sahifani olish
        if not ilova_pages:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables and len(tables[0]) > 10:
                    ilova_pages.append(i)
                    break

        return ilova_pages

    def _find_uzbek_page(self, pdf):
        """1-ILOVA — o'zbek tilida olib boriladigan umumiy ta'lim sahifasini topish"""
        import re
        candidate = None
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # "1- ILOVA", "1-ILOVA", "1 ILOVA" hamda "ILOVA 1" formatlarini qidirish
                normalized = re.sub(r'[\s\-—]+', ' ', text.lower())
                if '1 ilova' in normalized or 'ilova 1' in normalized:
                    tables = page.extract_tables()
                    if tables and len(tables[0]) > 10:
                        return page
                    if candidate is None:
                        candidate = page
        if candidate:
            return candidate
        # Agar topilmasa — birinchi jadvali bor sahifani olish
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables and len(tables[0]) > 10:
                return page
        return pdf.pages[0] if pdf.pages else None

    def _parse_rows(self, rows):
        """Barcha qatorlarni parse qilish."""
        subjects = []
        hours = []
        classes = []
        header_found = False

        for row in rows:
            if not row or len(row) < 3:
                continue

            # Sarlavha qatorlarini tashlab o'tish
            if self._is_header_row(row):
                if not header_found:
                    # Birinchi marta header topilganda — sinf ustunlarini aniqlash
                    classes = self._extract_class_columns(row)
                    if classes:
                        header_found = True
                continue

            # Agar header hali topilmasa — sinf raqamlarini qidirish
            if not header_found:
                classes = self._extract_class_columns(row)
                if classes:
                    header_found = True
                continue

            # "Jami soat" qatorini tashlab o'tish
            first_cell = self._clean(str(row[0])) if row[0] else ""
            second_cell = self._clean(str(row[1])) if row[1] else ""
            combined = first_cell + " " + second_cell
            if 'jami' in combined.lower():
                continue

            # Fan nomini topish (2-ustun)
            subject_name = second_cell if second_cell else first_cell
            if not subject_name or len(subject_name) < 2:
                continue
            # Raqam yoki keraksiz qator bo'lmasin
            if re.match(r'^\d+$', subject_name):
                continue
            # Sarlavha qoldiqlarini tashlab o'tish
            skip_words = ['nomlari', 'haftalik', 'umumiy', 'soat', 'sinflar',
                          't/r', 'fan yo', 'va nomlari']
            if any(sw in subject_name.lower() for sw in skip_words):
                continue

            # Guruh sarlavhasimi?
            is_group = self._is_group_header(subject_name)

            # Soatlar — ustun 2-12 (sinf 1-11)
            row_hours = []
            for col_idx in range(2, 13):
                if col_idx < len(row):
                    row_hours.append(self._parse_hours(row[col_idx]))
                else:
                    row_hours.append(0)

            # Agar guruh sarlavhasi bo'lsa ham saqlash
            short = "" if is_group else self._make_short(subject_name)
            subjects.append({"name": subject_name, "short": short, "is_group": is_group})
            hours.append(row_hours)

        if not classes:
            classes = [{"name": f"{i}-sinf", "level": i} for i in range(1, 12)]

        if not subjects:
            self.errors.append("Fanlar topilmadi!")
            return None

        return {
            "subjects": subjects,
            "classes": classes,
            "hours": hours,
        }

    def _is_header_row(self, row):
        """Sarlavha qatormi?"""
        # Header qatorlarida "Fan", "soat", "T/r", "nomlari" so'zlari bor
        text = " ".join(self._clean(str(c)) for c in row if c)
        text_lower = text.lower()
        keywords = ['fan', 'soat', 't/r', 'nomlari', 'sinflar', 'haftalik', 'umumiy']
        # Kamida 2 ta kalit so'z bo'lsa — header
        if sum(1 for kw in keywords if kw in text_lower) >= 2:
            return True
        # "Jami soat" yoki "Jami" bilan tugasa — header emas, lekin "Jami" qatorini tashlab o'tish kerak
        if 'jami' in text_lower:
            return True
        return False

    def _extract_class_columns(self, row):
        """Sarlavha qatoridan sinf ustunlarini aniqlash."""
        classes = []
        for i, cell in enumerate(row):
            text = self._clean(str(cell)) if cell else ""
            # Raqam yoki bo'sh bo'lishi kerak
            m = re.match(r'^(\d{1,2})$', text)
            if m:
                level = int(m.group(1))
                if 1 <= level <= 11:
                    classes.append({"name": f"{level}-sinf", "level": level})
            elif text == '' or text is None:
                # Bo'sh katak ham sinf ustuni bo'lishi mumkin
                pass
        return classes

    def _is_group_header(self, text):
        """Guruh sarlavhasi?"""
        t = text.strip().lower()
        # Rim raqami: I. II. III. IV. V.
        if re.match(r'^[ivx]+\.?\s', t):
            return True
        # "fanlar" bilan tugaydi
        if re.search(r'\bfanlar[si]?$', t):
            return True
        return False

    def _clean(self, text):
        """Matnni tozalash."""
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\n', ' ').replace('\r', '')
        return text.strip()

    def _parse_hours(self, cell):
        """Katakdan soat."""
        if cell is None:
            return 0
        text = self._clean(str(cell))
        if not text or text in ('-', '—'):
            return 0
        text = text.replace(',', '.')
        m = re.search(r'(\d+\.?\d*)', text)
        if m:
            val = float(m.group(1))
            return int(val) if val == int(val) else val
        return 0

    def _make_short(self, name):
        """Qisqartma nom."""
        words = name.split()
        if len(words) == 1:
            return name[:4].title()
        return ''.join(w[0].upper() for w in words[:3])

    def parse_for_display(self, pdf_path):
        """Parse qilib, flat formatga o'tkazish."""
        result = self.parse(pdf_path)
        if not result:
            return None

        flat = []
        for i, subj in enumerate(result['subjects']):
            is_group = subj.get('is_group', False)
            for j, cls in enumerate(result['classes']):
                h = result['hours'][i][j] if i < len(result['hours']) and j < len(result['hours'][i]) else 0
                # Guruh sarlavhalari faqat bir marta qo'shiladi (birinchi sinf darajasida)
                if is_group:
                    if j == 0:  # Faqat birinchi sinf
                        flat.append({
                            'subject_name': subj['name'],
                            'subject_short': subj.get('short', ''),
                            'class_level': cls['level'],
                            'weekly_hours': 0,  # Guruhlar uchun 0
                            'is_group': True,
                        })
                else:
                    flat.append({
                        'subject_name': subj['name'],
                        'subject_short': subj.get('short', ''),
                        'class_level': cls['level'],
                        'weekly_hours': h,
                        'is_group': False,
                    })
        return flat
