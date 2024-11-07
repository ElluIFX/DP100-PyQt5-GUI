echo "Building MDP-P906"

.venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp.spec

echo "Building MDP-P906-Numba"

.venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp_numba.spec
