#!/usr/bin/env python3
"""
Directly create odds_history table using PostgreSQL connection
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Build PostgreSQL connection string from Supabase URL
SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
PROJECT_ID = os.getenv('VITE_SUPABASE_PROJECT_ID')

# Supabase PostgreSQL connection string
# Format: postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
conn_string = f"postgresql://postgres.{PROJECT_ID}:@db.{PROJECT_ID}.supabase.co:6543/postgres?sslmode=require"

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

print('=' * 60)
print('🔧 CREATING ODDS_HISTORY TABLE DIRECTLY')
print('=' * 60)
print()

try:
    # Try to connect
    print(f'🔌 Connecting to Supabase PostgreSQL...')
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print('✅ Connected!')
    print()
    print('📝 Executing SQL...')
    
    cursor.execute(SQL)
    
    print('✅ Table created successfully!')
    print()
    
    # Verify table exists
    cursor.execute("SELECT COUNT(*) FROM public.odds_history;")
    count = cursor.fetchone()[0]
    print(f'📊 Table verified! Current records: {count}')
    
    cursor.close()
    conn.close()
    
    print()
    print('=' * 60)
    print('🎉 SUCCESS! NOW RUNNING ODDS TRACKER...')
    print('=' * 60)
    print()
    
    # Now run the tracker
    import subprocess
    subprocess.run(['python', 'scripts/track_odds_history.py'])
    
except psycopg2.OperationalError as e:
    print(f'❌ Connection failed: {e}')
    print()
    print('🔑 Need database password!')
    print()
    print('📋 Go to Supabase Dashboard > Project Settings > Database')
    print('   Copy your database password and run:')
    print()
    print('   Set environment variable:')
    print('   $env:SUPABASE_DB_PASSWORD="your-password"')
    print()
    print('   Or use this connection string:')
    print(f'   {conn_string.replace(":", ":[YOUR-PASSWORD]", 1)}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    print()
    print('📋 Falling back to manual method...')
    print()
    print('Please run this SQL in Supabase Dashboard > SQL Editor:')
    print('=' * 60)
    print(SQL)
    print('=' * 60)
