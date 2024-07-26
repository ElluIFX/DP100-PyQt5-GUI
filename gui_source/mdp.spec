# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ["mdp_main.py", "mdp_gui.py"],
    pathex=[],
    binaries=[],
    datas=[
        (".\\icon.ico", "."),
        (".\\en_US.qm", "."),
    ],
    hiddenimports=["pyi_splash"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "llvm",
        "matplotlib",
        "wx",
        "scipy",
        "PIL",
        "llvmlite",
        "numba",
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
    name="MDP-P906",
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
