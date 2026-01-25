# Quick script to create odds_history table in Supabase
# Load environment variables
$envContent = Get-Content .env
$supabaseUrl = ($envContent | Select-String "VITE_SUPABASE_URL=(.*)").Matches.Groups[1].Value
$supabaseKey = ($envContent | Select-String "VITE_SUPABASE_PUBLISHABLE_KEY=(.*)").Matches.Groups[1].Value

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CREATING ODDS_HISTORY TABLE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$sql = @'
CREATE TABLE IF NOT EXISTS public.odds_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    player_id UUID REFERENCES public.players(id) ON DELETE CASCADE,
    player_name TEXT NOT NULL,
    stat_type TEXT NOT NULL,
    game_id UUID REFERENCES public.games(id) ON DELETE CASCADE,
    sportsbook TEXT NOT NULL,
    line DECIMAL(10,2) NOT NULL,
    over_odds INTEGER NOT NULL,
    under_odds INTEGER NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_odds_history_player_stat ON public.odds_history(player_name, stat_type);
CREATE INDEX IF NOT EXISTS idx_odds_history_game ON public.odds_history(game_id);
CREATE INDEX IF NOT EXISTS idx_odds_history_recorded ON public.odds_history(recorded_at DESC);
ALTER TABLE public.odds_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read access" ON public.odds_history;
CREATE POLICY "Allow public read access" ON public.odds_history FOR SELECT USING (true);
DROP POLICY IF EXISTS "Allow authenticated insert" ON public.odds_history;
CREATE POLICY "Allow authenticated insert" ON public.odds_history FOR INSERT WITH CHECK (true);
'@

# Copy SQL to clipboard
$sql | Set-Clipboard

Write-Host "SQL copied to clipboard!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Opening Supabase Dashboard SQL Editor..." -ForegroundColor White
Write-Host "2. Paste (Ctrl+V) and click RUN" -ForegroundColor White
Write-Host ""

# Open Supabase Dashboard
Start-Process "https://supabase.com/dashboard/project/_/sql/new"

Write-Host "Waiting for you to run the SQL in browser..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press ENTER after you've run the SQL in Supabase Dashboard" -ForegroundColor Cyan
$null = Read-Host

Write-Host ""
Write-Host "Testing if table was created..." -ForegroundColor Cyan

# Test if table exists
python -c "from dotenv import load_dotenv; import os; from supabase import create_client; load_dotenv(); s = create_client(os.getenv('VITE_SUPABASE_URL'), os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')); result = s.table('odds_history').select('*').limit(1).execute(); print('Table exists!')"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Now running odds tracker..." -ForegroundColor Green
    python scripts/track_odds_history.py
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
} else {
    Write-Host "Table was not created. Please try running the SQL again." -ForegroundColor Red
}
