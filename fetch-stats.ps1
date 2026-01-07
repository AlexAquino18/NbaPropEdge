Write-Host "================================" -ForegroundColor Cyan
Write-Host "  FETCHING PLAYER STATS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Run the fetch script
Write-Host "Running fetch_player_stats_robust.py..." -ForegroundColor Yellow
python scripts\fetch_player_stats_robust.py

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "  COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
