# AtomTech Daily — Instagram Auto-Poster
# Este script lo ejecuta el Task Scheduler de Windows
# despues de que el newsletter diario haya terminado.

$env:OPENAI_API_KEY    = [System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY",    "User")
$env:INSTAGRAM_USERNAME = [System.Environment]::GetEnvironmentVariable("INSTAGRAM_USERNAME", "User")
$env:INSTAGRAM_PASSWORD = [System.Environment]::GetEnvironmentVariable("INSTAGRAM_PASSWORD", "User")

$scriptPath = "C:\techpulse-daily\atomtech_instagram.py"
$logPath    = "C:\techpulse-daily\logs\instagram_$(Get-Date -Format 'yyyy-MM-dd').log"

New-Item -ItemType Directory -Path "C:\techpulse-daily\logs" -Force | Out-Null

Write-Host "Iniciando AtomTech Daily Instagram Poster..."
python $scriptPath 2>&1 | Tee-Object -FilePath $logPath

Write-Host "Log guardado en: $logPath"
