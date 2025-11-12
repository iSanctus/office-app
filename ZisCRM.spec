# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for ZisCRM

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database.py', '.'),
        ('receipt_generator.py', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'reportlab',
        'reportlab.pdfbase',
        'reportlab.pdfbase.ttfonts',
        'reportlab.pdfgen.canvas',
        'reportlab.lib.pagesizes',
        'reportlab.lib.units',
        'reportlab.lib.utils',
        'openpyxl',
        'openpyxl.utils',
        'sqlite3',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ZisCRM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see debug output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',  # Using logo.ico as the application icon
)
