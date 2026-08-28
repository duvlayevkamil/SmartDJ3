"""
Logotip — SmartOIBDO → SmartDJ (faqat doira ichida)
"""
from PIL import Image, ImageDraw, ImageFont
import os
import math

INPUT = r"D:\LOYIHA ISHIMIZ\DASTURLAR\SmartOIBDO_doira_logotip.png"
OUTPUT = r"D:\SmartDJ3\smartdj_logo.png"

img = Image.open(INPUT).convert("RGBA")
width, height = img.size

# Doira parametrlari
center_x = width // 2
center_y = int(height * 0.47)
radius = int(width * 0.42)
inner_radius = radius - 15  # Tashqi chetdan ichkariga

# Fon rangi
bg_color = (7, 34, 62, 255)

# Matn joyi
text_y = int(height * 0.555)

# Doira ichidagi matn maydonini yashirish — FAQAT doira chegarasida
overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

for y in range(text_y - 55, text_y + 55):
    dy = y - center_y
    if abs(dy) < inner_radius:
        half_w = int((inner_radius**2 - dy**2)**0.5)
        draw.line([(center_x - half_w, y), (center_x + half_w, y)], fill=bg_color)

img = Image.alpha_composite(img, overlay)

# Yangi matn
text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
text_draw = ImageDraw.Draw(text_layer)

font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 90)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

text = "SmartDJ"
bbox = text_draw.textbbox((0, 0), text, font=font)
text_w = bbox[2] - bbox[0]
start_x = (width - text_w) // 2
draw_y = text_y

# Gradient ranglar
smart_colors = [lerp_color((80, 180, 255), (40, 140, 220), i/4) for i in range(5)]
dj_colors = [lerp_color((60, 230, 130), (30, 200, 90), i/1) for i in range(2)]
all_colors = smart_colors + dj_colors

x_offset = start_x
for i, char in enumerate(text):
    color = all_colors[i] if i < len(all_colors) else (80, 180, 255)
    
    # Soya
    for dx in [5, 4, 3]:
        text_draw.text((x_offset + dx, draw_y + dx), char,
                       fill=(0, 0, 0, 50), font=font)
    
    # Asosiy matn
    text_draw.text((x_offset, draw_y), char,
                   fill=color + (255,), font=font)
    
    char_bbox = text_draw.textbbox((0, 0), char, font=font)
    x_offset += char_bbox[2] - char_bbox[0]

img = Image.alpha_composite(img, text_layer)

img = img.convert("RGB")
img.save(OUTPUT, "PNG", quality=95)
print(f"✅ Saqlandi: {OUTPUT}")
