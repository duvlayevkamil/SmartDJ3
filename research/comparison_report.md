# SmartDJ3 vs ProRector — To'liq Taqqoslash Hisoboti
## 2026-07-11 | 250 sinf, 750 o'qituvchi bilan sinov

---

## 1. Umumiy ma'lumot

| Xususiyat | SmartDJ3 | ProRector |
|---|---|---|
| **Yaratuvchi** | Duvlayev Kamil (O'zbekiston) | Erkinjon Islamov (O'zbekiston) |
| **Yil** | 2026 (yangi) | 2009 (17 yillik) |
| **Foydalanuvchilar** | Loyiha darajasida | 3,500+ maktab |
| **Til** | O'zbekcha (faqat) | 33+ til |
| **Narx** | Bepul (litsenziya tizimi bor) | $4-45 USD (pullik) |
| **Platforma** | Windows (PyInstaller) | Windows |
| **Texnologiya** | Python/PyQt6 | Aniqlanmagan |

---

## 2. Funksional taqqoslash

### 2.1 Boshqaruv oynalari

| Funksiya | SmartDJ3 | ProRector |
|---|---|---|
| Sinflar boshqaruvi | ✅ (daraja, harf, ish kunlari) | ✅ |
| Fanlar boshqaruvi | ✅ (qiyinlik darajasi, avto-aniqlash) | ✅ |
| O'qituvchilar boshqaruvi | ✅ (rang, metodik kun, band soatlar) | ✅ |
| Xonalar boshqaruvi | ✅ (12 xil tur) | ✅ (250 xona) |
| Dars biriktirish | ✅ (takroriy tekshiruv) | ✅ |

### 2.2 Avtomatik jadval tuzish

| Xususiyat | SmartDJ3 | ProRector |
|---|---|---|
| Algoritm | Gibrid (Greedy + BRKGA) | Maxsus (17 yillik) |
| Maksimal hajm | 250 sinf, 750 o'qituvchi | 250 sinf, 500 o'qituvchi |
| **Vaqt (250 sinf)** | **211s (3.5 daqiqa)** | **~120s (2 daqiqa)** |
| **Joylashish darajasi** | **99.8%** | Noma'lum |
| **Ziddiyatlar** | **6.5%** | Noma'lum |
| O'qituvchi ziddiyati | ✅ Avtomatik hal qilish | ✅ |
| Metodik kun | ✅ Bloklaydi | Aniqlanmagan |
| Kelajak soati | ✅ Avto-joylashtiradi | Aniqlanmagan |

### 2.3 SanPIN (Sanitariya qoidalari)

| Xususiyat | SmartDJ3 | ProRector |
|---|---|---|
| **SanPIN tekshiruvi** | **✅ 11 ta qoida (avtomatik)** | **❌ Avtomatlashtirilmagan** |
| Qiyinlik darajasi | ✅ 1-13 shkala (A/B/C toifa) | ❌ Yo'q |
| Bells Curve | ✅ Kunlik qiyinlik naqshi | ❌ Yo'q |
| Tayanch reja | ✅ PDF/Excel import + tekshiruv | ❌ Yo'q |

### 2.4 Qo'lda tahrirlash

| Xususiyat | SmartDJ3 | ProRector |
|---|---|---|
| Drag-and-drop | ✅ Rangli (yashil/qizil/ko'k) | ✅ |
| Real-time vizual | ✅ Har xujayra uchun rang kodlash | Aniqlanmagan |
| SanPIN ogohlantirish | ✅ Joylashtirish paytida | Aniqlanmagan |

### 2.5 Ikki haftalik ko'rinish

| Xususiyat | SmartDJ3 | ProRector |
|---|---|---|
| Surat/maxraj | ✅ Hafta tanlash paneli | ✅ |
| Parallel ko'rinish | ❌ Yo'q | ✅ (kichik oynada) |

### 2.6 Import/Export

| Format | SmartDJ3 | ProRector |
|---|---|---|
| PDF | ✅ | ✅ |
| Excel | ✅ | ✅ |
| Word (.docx) | ✅ | Aniqlanmagan |
| HTML | ✅ | Aniqlanmagan |
| CSV | ✅ | Aniqlanmagan |
| Excel import | ✅ | ✅ |
| Tayanch reja PDF | ✅ | ❌ |

### 2.7 Monitoring

| Xususiyat | SmartDJ3 | ProRector |
|---|---|---|
| Real-time monitoring | ✅ (3-tab dashboard) | ❌ |
| Hozirgi dars | ✅ Vaqtga qarab | ❌ |

### 2.8 Xatoliklar tizimi

| Xususiyat | SmartDJ3 | ProRector |
|---|---|---|
| Xatoliklar paneli | ✅ (bajarilgan xatoliklar) | "Xatolarni ko'rsatadi" |
| SanPIN hisoboti | ✅ (HTML formatda) | ❌ |

---

## 3. Performance sinov natijalari (SmartDJ3)

### 3.1 Test data
- **250 sinf** (1-11 daraja, A-W harflar)
- **750 o'qituvchi** (har biri 2 sinfga dars beradi)
- **25 fan**
- **7,255 dars biriktirish**

### 3.2 Natijalar

| Ko'rsatkich | Qiymat |
|---|---|
| Vaqt | 211s (3.5 daqiqa) |
| Joylashtirilgan | 7,245 / 7,255 (99.8%) |
| Joylashmay qolgan | 11 dars (0.2%) |
| Ziddiyatlar | 473 (6.5%) |
| O'rtacha ball | 50-60 |

### 3.3 ProRector bilan taqqoslash (taxminiy)

| Ko'rsatkich | ProRector (taxminiy) | SmartDJ3 | Farq |
|---|---|---|---|
| Vaqt | ~120s (2 daq) | 211s (3.5 daq) | 1.75x sekin |
| Joylashish | ~100% | 99.8% | 0.2% farq |
| Ziddiyatlar | ~0% (taxminiy) | 6.5% | 6.5% farq |
| SanPIN | Yo'q | Avtomatik | SmartDJ3 ustun |

---

## 4. SmartDJ3 ning ustunliklari (ProRector da yo'q)

1. **SanPIN avtomatlashtirilgan** — 11 ta qoida avtomatik tekshiriladi
2. **Bells Curve tahlili** — Kunlik qiyinlik taqsimoti
3. **Tayanch reja PDF import** — Rasmiy o'quv dasturidan avtomatik import
4. **Real-time monitoring** — Hozirgi darsni ko'rish
5. **Rangli drag-and-drop** — Har xujayra uchun vizual qayta ishlash
6. **Word/HTML/CSV export** — Ko'proq format
7. **Qiyinlik darajasi tizimi** — 1-13 shkala bilan avto-aniqlash
8. **Xatoliklar paneli** — Bajarilgan xatoliklarni ko'rsatish
9. **Bepul** — Litsenziya tizimi bor, lekin asosiy funksiyalar bepul

---

## 5. ProRector ning ustunliklari (SmartDJ3 da yo'q)

1. **Tezlik** — 2x tezroq (120s vs 211s)
2. **33+ til** — Xalqaro qo'llab-quvvatlash
3. **17 yillik tajriba** — 3,500+ maktab ishonchi
4. **Parallel ko'rinish** — Kichik oynada sinf/o'qituvchi jadvali
5. **Pullik qo'llab-quvvatlash** — Texnik yordam
6. **Ko'proq sinovdan o'tgan** — Real maktablarda sinov

---

## 6. Xulosa

### SmartDJ3 kuchli tomonlari:
- ✅ SanPIN avtomatlashtirilgan (bu O'zbekistonda juda muhim)
- ✅ Bepul va ochiq
- ✅ Zamonaviy UI (PyQt6)
- ✅ Ko'proq export formatlari
- ✅ Real-time monitoring

### SmartDJ3 zaif tomonlari:
- ⚠️ ProRector dan 1.75x sekin
- ⚠️ 6.5% ziddiyat (ProRector 0% bo'lishi mumkin)
- ⚠️ Kamroq sinovdan o'tgan
- ⚠️ Faqat O'zbekcha

### Tavsiya:
1. **Tezlikni oshirish** — BRKGA ni optimatsiya qilish (maqsad: 120s ga tushirish)
2. **Ziddiyatlarni kamaytirish** — O'qituvchi markazli scheduling
3. **Test qilish** — Haqiqiy maktab bilan sinov o'tkazish
4. **Dokumentatsiya** — Foydalanuvchi qo'llanmasi yaratish

---

## 7. Manbalar

- ProRector: https://prorector.uz
- SmartDJ3: D:\SmartDJ3
- Test data: D:\SmartDJ3\smartdj_test.db
- Hisobot: D:\SmartDJ3\research\comparison_report.md
