# -*- mode: python ; coding: utf-8 -*-
# Yagona EXE — baza ichida

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('smartdj.db', '.'),
        ('logo.png', '.'),
        ('logo.ico', '.'),
    ],
    hiddenimports=[
        'core', 'core.scheduler', 'core.sanpin', 'core.brkga',
        'core.exporter', 'core.export_dialog', 'core.export_settings',
        'core.excel_parser', 'core.license', 'core.tayanch_reja_parser',
        'database', 'database.db_manager',
        'ui', 'ui.manual_schedule_window', 'ui.teacher_window',
        'ui.class_window', 'ui.subject_window', 'ui.classroom_window',
        'ui.assignment_window', 'ui.tayanch_reja_window',
        'ui.monitoring_window', 'ui.error_panel', 'ui.license_dialog',
        'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'PyQt6.QtCore',
        'PyQt6.QtPrintSupport',
        'openpyxl', 'docx', 'pdfplumber', 'reportlab',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SmartDJ3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
