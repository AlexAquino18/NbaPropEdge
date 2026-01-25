# Daily Update Script - Run this once per day
# Updates props, projections, and sportsbook odds

param(
    [switch]$NoPause
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  DAILY WEBSITE UPDATE" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Updating props and projections..." -ForegroundColor Yellow
& .\run-projections.ps1 -NoPause

Write-Host ""
Write-Host "Step 2: Tracking sportsbook odds..." -ForegroundColor Yellow
python scripts/track_odds_to_supabase.py

Write-Host ""
Write-Host "Step 3: Syncing odds to live website..." -ForegroundColor Yellow
python scripts/sync_odds_to_props.py

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "  DAILY UPDATE COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your website is now up to date with:" -ForegroundColor White
Write-Host "  [OK] Latest props from PrizePicks" -ForegroundColor Green
Write-Host "  [OK] Fresh projections and edges" -ForegroundColor Green
Write-Host "  [OK] DraftKings and FanDuel odds" -ForegroundColor Green
Write-Host "  [OK] Odds history for line movement charts" -ForegroundColor Green
Write-Host ""

if (-not $NoPause) {
    Write-Host "Press any key to close..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
