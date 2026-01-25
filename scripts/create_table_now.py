#!/usr/bin/env python3
"""
Create odds_history table using Supabase REST API with service role
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import requests

load_dotenv()

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')

print('=' * 60)
print('🔧 CREATING ODDS_HISTORY TABLE')
print('=' * 60)
print()

# SQL to create the table
SQL = """
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
"""

# Save SQL to file
sql_file = 'create_odds_history.sql'
with open(sql_file, 'w') as f:
    f.write(SQL)

print(f'💾 SQL saved to: {sql_file}')
print()
print('📋 COPY THIS SQL AND RUN IT IN SUPABASE:')
print()
print('1. Go to: https://supabase.com/dashboard/project/aimvwybpqhykuwiqddzu/sql/new')
print('2. Paste the SQL below')
print('3. Click RUN')
print()
print('=' * 60)
print(SQL)
print('=' * 60)
print()

# Also copy to clipboard if possible
try:
    import pyperclip
    pyperclip.copy(SQL)
    print('✅ SQL copied to clipboard! Just paste (Ctrl+V) in Supabase.')
except:
    print('💡 Tip: Install pyperclip for auto-copy: pip install pyperclip')

print()
input('Press ENTER after you have run the SQL in Supabase Dashboard...')

# Test if table was created
print()
print('🧪 Testing table...')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    result = supabase.table('odds_history').select('*').limit(1).execute()
    print('✅ Table exists!')
    print()
    print('🚀 Running odds tracker...')
    print()
    
    import subprocess
    subprocess.run(['python', 'scripts/track_odds_history.py'])
    
except Exception as e:
    print(f'❌ Table not found: {e}')
    print('   Please run the SQL in Supabase Dashboard first.')
