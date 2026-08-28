# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database', 'database'),
        ('ui', 'ui'),
        ('core', 'core'),
        ('smartdj.db', '.'),
        ('logo.png', '.'),
        ('logo.ico', '.'),
    ],
    hiddenimports=[
        # Core modullar
        'core', 'core.scheduler', 'core.sanpin', 'core.brkga',
        'core.exporter', 'core.export_dialog', 'core.export_settings',
        'core.excel_parser', 'core.license', 'core.tayanch_reja_parser',
        # Database
        'database', 'database.db_manager',
        # UI oynalar
        'ui', 'ui.manual_schedule_window', 'ui.teacher_window',
        'ui.class_window', 'ui.subject_window', 'ui.classroom_window',
        'ui.assignment_window', 'ui.tayanch_reja_window',
        'ui.monitoring_window', 'ui.error_panel', 'ui.license_dialog',
        # PyQt6
        'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'PyQt6.QtCore',
        'PyQt6.QtPrintSupport',
        # Kutubxonalar
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
    [],
    exclude_binaries=True,
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SmartDJ3',
)
