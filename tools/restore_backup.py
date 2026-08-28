"""Backup bazadan asosiy bazani qayta tiklash"""
import sqlite3

# Backup bazadan o'qish
backup = sqlite3.connect('D:/SmartDJ3/smartdj_backup_real.db')
bc = backup.cursor()

# Asosiy bazaga yozish
main = sqlite3.connect('D:/SmartDJ3/smartdj.db')
mc = main.cursor()

# 1. Sinflarni tiklash
bc.execute('SELECT id, name, level, students_count, working_days FROM classes')
classes = bc.fetchall()
mc.execute('DELETE FROM classes')
for c in classes:
    mc.execute('INSERT INTO classes (id, name, level, students_count, working_days) VALUES (?, ?, ?, ?, ?)', c)
print(f'Sinflar: {len(classes)} ta tiklandi')

# 2. Fanlarni tiklash
bc.execute('SELECT id, name, short_name, difficulty FROM subjects')
subjects = bc.fetchall()
mc.execute('DELETE FROM subjects')
for s in subjects:
    mc.execute('INSERT INTO subjects (id, name, short_name, difficulty) VALUES (?, ?, ?, ?)', s)
print(f'Fanlar: {len(subjects)} ta tiklandi')

# 3. O'qituvchilarni tiklash
bc.execute('SELECT id, full_name, phone, color, class_teacher_of, methodic_day, short_name FROM teachers')
teachers = bc.fetchall()
mc.execute('DELETE FROM teachers')
for t in teachers:
    mc.execute('INSERT INTO teachers (id, full_name, phone, color, class_teacher_of, methodic_day, short_name) VALUES (?, ?, ?, ?, ?, ?, ?)', t)
print(f'Oqituvchilar: {len(teachers)} ta tiklandi')

# 4. Dars biriktirishlarni tiklash
bc.execute('SELECT id, class_id, subject_id, teacher_id, classroom_id, weekly_hours FROM lesson_assignments')
assignments = bc.fetchall()
mc.execute('DELETE FROM lesson_assignments')
for a in assignments:
    mc.execute('INSERT INTO lesson_assignments (id, class_id, subject_id, teacher_id, classroom_id, weekly_hours) VALUES (?, ?, ?, ?, ?, ?)', a)
print(f'Dars biriktirishlar: {len(assignments)} ta tiklandi')

# 5. Band soatlarni tiklash
bc.execute('SELECT id, teacher_id, day, period, availability_type FROM teacher_unavailable')
unavail = bc.fetchall()
mc.execute('DELETE FROM teacher_unavailable')
for u in unavail:
    mc.execute('INSERT INTO teacher_unavailable (id, teacher_id, day, period, availability_type) VALUES (?, ?, ?, ?, ?)', u)
print(f'Band soatlar: {len(unavail)} ta tiklandi')

# 6. Xonalarni tiklash
bc.execute('SELECT id, room_number, capacity, room_type FROM classrooms')
rooms = bc.fetchall()
mc.execute('DELETE FROM classrooms')
for r in rooms:
    mc.execute('INSERT INTO classrooms (id, room_number, capacity, room_type) VALUES (?, ?, ?, ?)', r)
print(f'Xonalar: {len(rooms)} ta tiklandi')

# 7. Tayanch rejani tiklash
bc.execute('SELECT id, subject_name, subject_short, class_level, weekly_hours, pdf_source, order_index FROM tayanch_reja')
tayanch = bc.fetchall()
mc.execute('DELETE FROM tayanch_reja')
for t in tayanch:
    mc.execute('INSERT INTO tayanch_reja (id, subject_name, subject_short, class_level, weekly_hours, pdf_source, order_index) VALUES (?, ?, ?, ?, ?, ?, ?)', t)
print(f'Tayanch reja: {len(tayanch)} ta tiklandi')

main.commit()
backup.close()
main.close()

print()
print('BAZA TO-LIQ TIKLANDI!')
