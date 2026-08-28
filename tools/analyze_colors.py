"""O'qituvchi ranglarini tahlil qish"""
import sqlite3
import colorsys

def hex_to_hsv(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return colorsys.rgb_to_hsv(r, g, b)

conn = sqlite3.connect('D:/SmartDJ3/smartdj.db')
cursor = conn.cursor()

cursor.execute('SELECT id, full_name, color, class_teacher_of FROM teachers ORDER BY full_name')
teachers = cursor.fetchall()

print('=' * 70)
print("O'QITUVCHILARGA BIRIKTIRILGAN RANGLAR")
print('=' * 70)
print(f"Jami o'qituvchilar: {len(teachers)}")
print()

for t in teachers:
    tid, name, color, ct = t
    ct_text = ''
    if ct:
        cursor.execute('SELECT name FROM classes WHERE id = ?', (ct,))
        row = cursor.fetchone()
        ct_text = f" (sinf rahbari: {row[0]})" if row else ''
    c = color if color else "yo'q"
    print(f"  {name:<25} | Rang: {c:<10}{ct_text}")

print()
print('=' * 70)
print("RANG TAHLILI")
print('=' * 70)

colors = {}
for t in teachers:
    c = t[2]
    if c:
        colors[c] = colors.get(c, 0) + 1

dup = {c: n for c, n in colors.items() if n > 1}
if dup:
    print(f"Dublikat ranglar ({len(dup)} ta):")
    for c, n in dup.items():
        names = [t[1] for t in teachers if t[2] == c]
        print(f"  {c} — {n} marta: {', '.join(names)}")
else:
    print("Dublikat ranglar yo'q")

print()
print("Ranglar ro'yxati:")
for c, n in sorted(colors.items(), key=lambda x: -x[1]):
    print(f"  {c} — {n} marta")

# Masofa tahlili
print()
print('=' * 70)
print("RANGLAR ORASIDAGI MASOFA (HSV)")
print('=' * 70)

color_list = [(t[1], t[2]) for t in teachers if t[2]]
if len(color_list) >= 2:
    min_dist = float('inf')
    min_pair = None
    for i in range(len(color_list)):
        for j in range(i+1, len(color_list)):
            hsv1 = hex_to_hsv(color_list[i][1])
            hsv2 = hex_to_hsv(color_list[j][1])
            dh = min(abs(hsv1[0] - hsv2[0]), 1 - abs(hsv1[0] - hsv2[0]))
            ds = abs(hsv1[1] - hsv2[1])
            dv = abs(hsv1[2] - hsv2[2])
            dist = dh * 2 + ds + dv
            if dist < min_dist:
                min_dist = dist
                min_pair = (color_list[i][0], color_list[j][0], color_list[i][1], color_list[j][1])
    
    print(f"Eng yaqin ranglar (masofa: {min_dist:.3f}):")
    print(f"  {min_pair[0]} ({min_pair[2]})")
    print(f"  {min_pair[1]} ({min_pair[3]})")
    
    if min_dist < 0.3:
        print("  XAVF: Ranglar juda o'xshash!")
    elif min_dist < 0.5:
        print("  OGOGHLANTIRISH: Ranglar biroz o'xshash")
    else:
        print("  YAXSHI: Ranglar yaxshi ajralgan")

conn.close()
