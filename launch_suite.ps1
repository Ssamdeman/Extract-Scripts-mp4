$PROJECT_DIR = "C:\Users\Samue\Documents\projects\github\Extract-Scripts-mp4"

Set-Location $PROJECT_DIR
Clear-Host

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    Speech & Articulation Analysis Suite" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$activate_script = Join-Path $PROJECT_DIR "mp4-script\Scripts\Activate.ps1"

if (Test-Path $activate_script) {
    . $activate_script
    Write-Host "[OK] Virtual Environment Activated." -ForegroundColor Green
} else {
    Write-Host "[WARNING] Virtual environment 'mp4-script' not found in $PROJECT_DIR!" -ForegroundColor Red
}

Write-Host ""
Write-Host "---------------------------------------------------"
Write-Host "Available Commands:"
Write-Host "---------------------------------------------------"
Write-Host "1. Speech Analysis (Filler words, Transcript, Readability)"
Write-Host "   Type: " -NoNewline; Write-Host "python speech_analysis.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Articulation Tracker (Jaw/Tongue mobility, Clarity)"
Write-Host "   Type: " -NoNewline; Write-Host "python articulation.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: Both tools will auto-scan their respective " -ForegroundColor DarkGray
Write-Host "'resources' folders if no specific file is provided." -ForegroundColor DarkGray
Write-Host "---------------------------------------------------"
Write-Host ""
