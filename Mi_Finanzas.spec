# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Mi_Finanzas.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.ico', '.'), ('database.py', '.'), ('ingresos.py', '.'), ('egresos.py', '.'), ('ahorros.py', '.'), ('deudas.py', '.'), ('grafica.py', '.'), ('grafica_ahorros.py', '.'), ('grafica_egresos.py', '.'), ('grafica_deudas.py', '.'), ('historial.py', '.'), ('historial_ahorros.py', '.'), ('historial_egresos.py', '.'), ('historial_deudas.py', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Mi_Finanzas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
