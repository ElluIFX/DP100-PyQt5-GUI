# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ["main.py", "gui.py"],
    pathex=["..", "."],  # for github action
    binaries=[],
    datas=[
        ("./icon.ico", "."),
        ("./en_US.qm", "."),
        ("./SarasaFixedSC-SemiBold.ttf", "."),
        ("./Li-ion.csv", "."),
        ("../dp100/ATK-DP100DLL(x64)_2.0.dll", "."),
        ("../dp100/ATK-DP100DLL(x86)_2.0.dll", "."),
    ],
    hiddenimports=["pyi_splash"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "llvm",
        "llvmlite",
        "numba",
        "matplotlib",
    ],  #
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)
splash = Splash(
    "booting.png",
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(166, 473),
    text_size=12,
    text_color="#5ac7ff",
    max_img_size=(760, 480),
    always_on_top=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash,  # <-- both, splash target
    splash.binaries,  # <-- and splash binaries
    [],
    name="DP100GUI",
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
    icon="icon.ico",
)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=False,
#     upx_exclude=[],
#     name="DP100GUI",
# )
