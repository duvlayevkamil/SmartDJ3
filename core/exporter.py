"""
Dars jadvalini HTML formatda yaratish
Bitta funksiya: timetable_data → HTML string
"""
from datetime import datetime

KUNLAR = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]
KUN_QISQA = ["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan"]
PERIODS_PER_DAY = 6  # Kuniga maksimal 6 dars (7-dars yo'q)


def build_html(tt, classes, etype='umumiy', eid=None, ename='',
               school='', fs=9):
    """
    timetable_data, classes → HTML string

    etype: umumiy | sinf | ustoz | fan
    eid: item ID (class_id, teacher_id, yoki subject_name)
    ename: item nomi (sarlavha uchun)
    school: maktab nomi
    fs: shrift o'lchami (pt)
    """
    title = "DARS JADVALI"

    if etype == 'sinf' and eid:
        title = f"DARS JADVALI — {ename}"
        rows = _grid_rows(tt, [c for c in classes if c[0] == eid], fs)
        tbl = _grid_table(rows)
    elif etype == 'ustoz' and eid:
        title = f"O'QITUVCHI JADVALI — {ename}"
        tbl = _teacher_table(tt, classes, eid, fs)
    elif etype == 'fan' and eid:
        title = f"FAN JADVALI — {ename}"
        tbl = _subject_table(tt, classes, eid, fs)
    else:
        rows = _grid_rows(tt, classes, fs)
        tbl = _grid_table(rows)

    school_html = f'<div class="school">{school}</div>' if school else ''
    now = datetime.now().strftime('%d.%m.%Y %H:%M')

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ margin:0; padding:15px; font-family:Arial,sans-serif; font-size:{fs}pt; color:#000000; }}
h2 {{ text-align:center; color:#2C3E50; margin:6px 0 3px; font-size:{fs+7}pt; }}
.school {{ text-align:center; color:#555; font-size:{fs+1}pt; margin-bottom:3px; }}
.date {{ text-align:center; color:#999; font-size:{fs-1}pt; margin-bottom:8px; }}
table {{ width:100%; border-collapse:collapse; }}
th {{ background:#2C3E50; color:#fff; padding:3px 2px; font-size:{max(5,fs-1)}pt;
      border:1px solid #1a252f; }}
td {{ border:1px solid #ccc; padding:2px 1px; text-align:center; vertical-align:middle;
      font-size:{fs}pt; color:#000000; }}
.nm {{ background:#34495E; color:#fff; font-weight:bold; white-space:nowrap; }}
.ev {{ background:#f5f5f5; }}
.ds {{ border-left:2px solid #2C3E50 !important; }}
.ft {{ text-align:left; color:#999; font-size:{max(5,fs-2)}pt; margin-top:8px; }}
.sm {{ font-size:{max(5,fs-2)}pt; color:#888; }}
</style></head><body>
{school_html}
<h2>{title}</h2>
<div class="date">Sana: {datetime.now().strftime('%d.%m.%Y')}</div>
{tbl}
<div class="ft">SmartDJ3 | {now}</div>
</body></html>"""


def _grid_rows(tt, classes, fs):
    out = []
    for cls in classes:
        cid = cls[0]
        cells = f'<td class="nm">{cls[1]}</td>'
        for day in range(6):
            for period in range(PERIODS_PER_DAY):
                info = tt.get((cid, day, period), {})
                subj = info.get('subject_short', '') if info else ''
                if not subj:
                    subj = info.get('subject_name', '')[:4] if info else ''
                tch = info.get('teacher_short', '') if info else ''
                if not tch:
                    # Agar qisqa nom bo'lmasa, to'liq nomdan yasash
                    tch_full = info.get('teacher_name', '') if info else ''
                    if tch_full:
                        parts = tch_full.split()
                        tch = f"{parts[0]} {parts[1][0]}." if len(parts) >= 2 else tch_full
                cl = ' class="ds"' if period == 0 else ''
                content = f"{subj}<br><span class='sm'>{tch}</span>" if tch else subj
                cells += f'<td{cl}>{content}</td>'
        out.append(f'<tr>{cells}</tr>')
    return '\n'.join(out)


def _grid_table(rows):
    day_h = ''.join(f'<th colspan="7">{k}</th>' for k in KUN_QISQA)
    per_h = ''.join(f'<th>{p}</th>' for day in range(6) for p in range(1, PERIODS_PER_DAY + 1))
    return f'<table><tr><th rowspan="2">Sinf</th>{day_h}</tr><tr>{per_h}</tr>{rows}</table>'


def _teacher_table(tt, classes, tid, fs):
    rows = []
    for p in range(PERIODS_PER_DAY):
        cells = f'<td class="nm">{p+1}-dars</td>'
        for day in range(6):
            subj = ''
            cn = ''
            for key, info in tt.items():
                if key[1] == day and key[2] == p and info.get('teacher_id') == tid:
                    subj = info.get('subject_short', '') or info.get('subject_name', '')[:4]
                    cn = next((c[1] for c in classes if c[0] == key[0]), '')
                    break
            c = f'{subj}<br><span class="sm">{cn}</span>' if subj else ''
            cells += f'<td>{c}</td>'
        rows.append(f'<tr>{cells}</tr>')
    hdr = ''.join(f'<th>{k}</th>' for k in KUNLAR)
    return f'<table><tr><th>Dars</th>{hdr}</tr>{"".join(rows)}</table>'


def _subject_table(tt, classes, sname, fs):
    entries = {}
    for key, info in tt.items():
        if info.get('subject_name') == sname:
            ek = (key[0], info.get('teacher_id'))
            if ek not in entries:
                cn = next((c[1] for c in classes if c[0] == key[0]), '')
                entries[ek] = {'cn': cn, 'tn': info.get('teacher_name', ''), 'slots': []}
            entries[ek]['slots'].append((key[1], key[2]))

    rows = []
    for e in entries.values():
        kun = ''
        for d in range(6):
            s = [str(p+1) for dd, p in e['slots'] if dd == d]
            kun += f'<td>{",".join(s)}</td>'
        rows.append(f'<tr><td class="nm">{e["cn"]}</td><td>{e["tn"]}</td>'
                     f'<td>{len(e["slots"])}</td>{kun}</tr>')
    kh = ''.join(f'<th>{k[:3]}</th>' for k in KUNLAR)
    return f'<table><tr><th>Sinf</th><th>O\'qituvchi</th><th>Soat</th>{kh}</tr>{"".join(rows)}</table>'
