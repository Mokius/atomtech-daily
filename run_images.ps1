$env:PYTHONUTF8         = "1"
$env:OPENAI_API_KEY     = [System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
$env:INSTAGRAM_USERNAME = [System.Environment]::GetEnvironmentVariable("INSTAGRAM_USERNAME", "User")
$env:INSTAGRAM_PASSWORD = [System.Environment]::GetEnvironmentVariable("INSTAGRAM_PASSWORD", "User")
Set-Location "C:\techpulse-daily"
python atomtech_instagram.py --images-only 2>&1 | Tee-Object "C:\techpulse-daily\logs\gen_out.txt"
