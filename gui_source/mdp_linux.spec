# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ["mdp_gui.py"],
    pathex=["..", "."],  # for github action
    binaries=[],
    datas=[
        ("./en_US.qm", "."),
        ("./SarasaFixedSC-SemiBold.ttf", "."),
        ("./Li-ion.csv", "."),
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
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MDP-P906",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
