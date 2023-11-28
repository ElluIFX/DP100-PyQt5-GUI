# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ["DP100_main.py", "DP100_gui.py", "DP100API.py"],
    pathex=[],
    binaries=[],
    datas=[
        (".\\ATK-DP100DLL(x64)_2.0.dll", "."),
        (".\\ATK-DP100DLL(x86)_2.0.dll", "."),
        (".\\icon.ico", "."),
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
        "PySide6",
        "cryptography",
        "jedi",
        "gevent",
        "IPython",
        "pygments",
        "h5py",
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
    text_pos=(110, 468),
    text_size=12,
    text_color="#daff6e",
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
    upx=False,
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
