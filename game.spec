# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['srcs/game.py'],
    pathex=[],
    binaries=[],
    datas=[('pacmen_and_gums', 'pacmen_and_gums'), ('ghosts', 'ghosts'), ('HS.json', '.'), ('config.json', '.'), ('mazegenerator', 'mazegenerator')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources'],
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
    name='game',
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
)
app = BUNDLE(
    exe,
    name='game.app',
    icon=None,
    bundle_identifier=None,
)
