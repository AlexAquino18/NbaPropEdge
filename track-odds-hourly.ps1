# Hourly Odds Tracking Script
# Run this script with Task Scheduler to automatically track odds history

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   HOURLY ODDS TRACKING" -ForegroundColor Cyan
Write-Host "   $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Run the odds history tracking script
python scripts/track_odds_history.py

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "   Odds tracking complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
