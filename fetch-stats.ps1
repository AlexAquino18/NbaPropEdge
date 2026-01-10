param(
  [switch]$NoPause
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  FETCHING PLAYER STATS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Activate virtual environment if present
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
  & ".\.venv\Scripts\Activate.ps1"
}

Write-Host ""
Write-Host "Running fetch_player_stats_robust.py..." -ForegroundColor Yellow
python scripts\fetch_player_stats_robust.py

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "  COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

if (-not $NoPause) {
  Write-Host ""
  Write-Host "Press any key to close..."
  $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
