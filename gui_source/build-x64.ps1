# echo "> Building DP100"

# .venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp.spec

# echo "> Building DP100-Numba"

# .venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp_numba.spec

echo "> Building DP100 and DP100-Numba in parallel"
# Start both builds in parallel
$job1 = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\.venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp.spec --log-level WARN
}

$job2 = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\.venv\Scripts\pyinstaller.exe --noconfirm --upx-dir C:\Toolchains\upx .\mdp_numba.spec --log-level WARN
}

# Wait for both jobs to complete
Wait-Job $job1, $job2

# Get output from jobs
echo "> DP100 build output:"
Receive-Job $job1
echo "> DP100-Numba build output:"
Receive-Job $job2

# Clean up
Remove-Job $job1, $job2

echo "> Build completed"
