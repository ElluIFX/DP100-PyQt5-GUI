# echo "> Building MDP-P906"

# .venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp.spec

# echo "> Building MDP-P906-Numba"

# .venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp_numba.spec

echo "> Building MDP-P906 and MDP-P906-Numba in parallel"
# Start both builds in parallel
$job1 = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\.venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp.spec
}

$job2 = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\.venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp_numba.spec
}

# Wait for both jobs to complete
Wait-Job $job1, $job2

# Get output from jobs
Receive-Job $job1
Receive-Job $job2

# Clean up
Remove-Job $job1, $job2

echo "> Build completed"
