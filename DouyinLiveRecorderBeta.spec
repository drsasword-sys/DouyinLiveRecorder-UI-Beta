# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ["ui.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("config/config.example.ini", "config"),
        ("config/URL_config.example.ini", "config"),
        ("src/javascript", "src/javascript"),
        ("i18n", "i18n"),
    ],
    hiddenimports=["main"],
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
    [],
    exclude_binaries=True,
    name="DouyinLiveRecorderBeta",
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DouyinLiveRecorderBeta",
)
