# Jalankan script ini untuk memulai aplikasi di Windows
# Usage: .\start.ps1
# Hentikan proses Flask lama agar tidak bentrok di port 5000
Get-CimInstance Win32_Process |
	Where-Object Name -eq 'python.exe' |
	Where-Object CommandLine -like '*run.py*' |
	ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

& "C:\Python313\python.exe" run.py
