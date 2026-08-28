"""Fix week loading in manual_schedule_window.py"""
import os

filepath = r'D:\SmartDJ3\ui\manual_schedule_window.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the saved = ... block
old_block = """            # Bazadan saqlangan jadvalni yuklash
            saved = self.db.load_scheduled_lessons()
            if saved:
                self.timetable_data = saved
                # Widgetlarni qayta yaratish
                for (class_id, day, period), info in saved.items():"""

new_block = """            # Bazadan saqlangan jadvalni yuklash — 1-hafta va 2-hafta
            saved_w1 = self.db.load_scheduled_lessons(week_index=0)
            saved_w2 = self.db.load_scheduled_lessons(week_index=1)

            if saved_w1:
                self.timetable_data = saved_w1
                self.timetable_data_week2 = saved_w2 if saved_w2 else {}
                # Widgetlarni qayta yaratish
                for (class_id, day, period), info in saved_w1.items():"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("1. Block replaced")
else:
    print("1. Block NOT found")
    # Try with tabs
    old_block_tabs = old_block.replace("    ", "\t")
    if old_block_tabs in content:
        content = content.replace(old_block_tabs, new_block)
        print("1. Block replaced (tabs)")
    else:
        print("1. Block NOT found (tabs)")

# Replace the status_label text
old_status = '''                self.status_label.setText(
                    f"✅ Yuklandi: {len(self.classes)} sinf | "
                    f"{len(saved)} dars bazadan olindi"
                )'''

new_status = '''                self.status_label.setText(
                    f"✅ Yuklandi: {len(self.classes)} sinf | "
                    f"1-hafta: {len(saved_w1)} dars | "
                    f"2-hafta: {len(saved_w2) if saved_w2 else 0} dars"
                )'''

if old_status in content:
    content = content.replace(old_status, new_status)
    print("2. Status replaced")
else:
    print("2. Status NOT found")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
