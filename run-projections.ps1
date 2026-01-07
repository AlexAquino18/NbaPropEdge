Write-Host "================================" -ForegroundColor Cyan
Write-Host "  FULL PROJECTION PIPELINE" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Fetch games from Ball Don't Lie" -ForegroundColor Yellow
Write-Host "  2. Link props to games" -ForegroundColor Yellow
Write-Host "  3. Run advanced projections" -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Run the full projection pipeline
Write-Host "Running full projection pipeline..." -ForegroundColor Yellow
python scripts\run_full_projections.py

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "  COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
