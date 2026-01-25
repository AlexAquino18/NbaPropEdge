#!/usr/bin/env python3
"""
Quick setup - opens Supabase SQL editor and copies SQL to clipboard
"""
import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

SQL = """CREATE TABLE IF NOT EXISTS public.odds_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    player_id UUID,
    player_name TEXT NOT NULL,
    stat_type TEXT NOT NULL,
    game_id UUID,
    sportsbook TEXT NOT NULL,
    line DECIMAL(10,2) NOT NULL,
    over_odds INTEGER NOT NULL,
    under_odds INTEGER NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_odds_history_player_stat ON public.odds_history(player_name, stat_type);
CREATE INDEX IF NOT EXISTS idx_odds_history_recorded ON public.odds_history(recorded_at DESC);
ALTER TABLE public.odds_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read" ON public.odds_history FOR SELECT USING (true);
CREATE POLICY "Allow insert" ON public.odds_history FOR INSERT WITH CHECK (true);"""

print('=' * 60)
print('🚀 QUICK TABLE SETUP')
print('=' * 60)
print()

# Copy to clipboard
try:
    import pyperclip
    pyperclip.copy(SQL)
    print('✅ SQL copied to clipboard!')
except ImportError:
    print('📋 Installing pyperclip...')
    os.system('pip install pyperclip')
    import pyperclip
    pyperclip.copy(SQL)
    print('✅ SQL copied to clipboard!')

print()
print('🌐 Opening Supabase SQL Editor in your browser...')
print()

# Get project ID
project_id = os.getenv('VITE_SUPABASE_PROJECT_ID', 'aimvwybpqhykuwiqddzu')
url = f'https://supabase.com/dashboard/project/{project_id}/sql/new'

# Open browser
webbrowser.open(url)

print(f'📍 Opening: {url}')
print()
print('=' * 60)
print('NEXT STEPS:')
print('=' * 60)
print('1. ✅ SQL is copied to your clipboard')
print('2. 🌐 Browser is opening Supabase SQL Editor')
print('3. 📝 Press Ctrl+V to paste the SQL')
print('4. ▶️  Click the RUN button')
print('5. ✅ Come back here and press ENTER')
print('=' * 60)
print()

input('Press ENTER after you run the SQL in Supabase...')

print()
print('🧪 Testing if table was created...')

from supabase import create_client

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

try:
    result = supabase.table('odds_history').select('id').limit(1).execute()
    print('✅ SUCCESS! Table exists!')
    print()
    print('🎯 Now running the odds tracker with database storage...')
    print()
    os.system('python scripts/fetch_sportsbook_odds.py')
except Exception as e:
    print(f'❌ Table not found: {e}')
    print()
    print('Please make sure you ran the SQL in Supabase Dashboard.')
    print('Then run this script again.')
