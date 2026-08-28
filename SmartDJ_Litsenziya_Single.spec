# -*- mode: python ; coding: utf-8 -*-
# Yagona EXE — litsenziya generator

a = Analysis(
    ['license_tool.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('core', 'core'),
    ],
    hiddenimports=[
        'core', 'core.license',
        'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'PyQt6.QtCore',
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
    name='SmartDJ_Litsenziya',
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
