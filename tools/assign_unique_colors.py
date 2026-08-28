"""Ko'z bilan ajraluvchi 30 rang — har biri turli color family"""
import sqlite3

# 30 ta TURLI COLOR FAMILY — ko'z bilan ajraluvchi
VISUALLY_DISTINCT_COLORS = [
    # 1-5: Qizil oilasi (har biri turli ton)
    "#DC143C",  # 1. Crimson — chuqur qizil
    "#FF4500",  # 2. OrangeRed — och qizil-pomidor
    "#FF69B4",  # 3. Hot Pink — gul-rang
    "#FF1493",  # 4. Deep Pink — chuqur gul
    "#C71585",  # 5. Medium Violet Red — binafsha-qizil

    # 6-10: Ko'k oilasi
    "#0000FF",  # 6. Blue — asosiy ko'k
    "#1E90FF",  # 7. Dodger Blue — och ko'k
    "#00008B",  # 8. Dark Blue — chuqur ko'k
    "#4169E1",  # 9. Royal Blue — malohat ko'k
    "#00BFFF",  # 10. Deep Sky Blue — osmon

    # 11-15: Yashil oilasi
    "#006400",  # 11. Dark Green — chuqur yashil
    "#32CD32",  # 12. Lime Green — och yashil
    "#008080",  # 13. Teal — zangori-yashil
    "#2E8B57",  # 14. Sea Green — dengiz yashil
    "#90EE90",  # 15. Light Green — och yashil

    # 16-20: Sariq/Pomidor oilasi
    "#FFD700",  # 16. Gold — oltin
    "#FFA500",  # 17. Orange — pomidor
    "#FF8C00",  # 18. Dark Orange — chuqur pomidor
    "#DAA520",  # 19. Goldenrod — jigarrang-sariq
    "#F0E68C",  # 20. Khaki — xaki

    # 21-25: Binafsha/Purple oilasi
    "#800080",  # 21. Purple — binafsha
    "#9400D3",  # 22. Dark Violet — chuqur binafsha
    "#BA55D3",  # 23. Medium Orchid — o'rta orkide
    "#DDA0DD",  # 24. Plum — olcha
    "#4B0082",  # 25. Indigo — indigo

    # 26-30: Maxsus ranglar
    "#8B4513",  # 26. Saddle Brown — jigarrang
    "#2F4F4F",  # 27. Dark Slate Gray — qorong'i kulrang
    "#FF6347",  # 28. Tomato — pomidor
    "#7B68EE",  # 29. Medium Slate Blue — och indigo
    "#00FA9A",  # 30. Medium Spring Green — bahor yashil
]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    """RGB da rang farqi"""
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2) ** 0.5

conn = sqlite3.connect('D:/SmartDJ3/smartdj.db')
c = conn.cursor()

c.execute('SELECT id, full_name FROM teachers ORDER BY full_name')
teachers = c.fetchall()

print("=" * 60)
print("Ko'z bilan ajraluvchi ranglar biriktirish")
print("=" * 60)
print(f"O'qituvchilar: {len(teachers)}")
print()

# Ranglarni taqsimlash
for i, (tid, name) in enumerate(teachers):
    color = VISUALLY_DISTINCT_COLORS[i % len(VISUALLY_DISTINCT_COLORS)]
    c.execute('UPDATE teachers SET color = ? WHERE id = ?', (color, tid))
    print(f"  {name:<25} | {color}")

conn.commit()
print()
print("Bazaga yozildi!")

# Tekshirish — eng yaqin ranglar
print()
print("ENG YAQIN RANGLAR (ko'z bilan):")
min_dist = 999
min_pair = None
for i in range(len(teachers)):
    for j in range(i+1, len(teachers)):
        c1 = VISUALLY_DISTINCT_COLORS[i % len(VISUALLY_DISTINCT_COLORS)]
        c2 = VISUALLY_DISTINCT_COLORS[j % len(VISUALLY_DISTINCT_COLORS)]
        d = color_distance(c1, c2)
        if d < min_dist:
            min_dist = d
            min_pair = (teachers[i][1], c1, teachers[j][1], c2)

if min_pair:
    print(f"  {min_pair[0]} ({min_pair[1]})")
    print(f"  {min_pair[2]} ({min_pair[3]})")
    print(f"  Masofa: {min_dist:.0f} (100+ bo'lsa YAXSHI)")

conn.close()
