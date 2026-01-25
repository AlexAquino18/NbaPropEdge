#!/usr/bin/env python3
"""
Create the odds_history table directly in Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Supabase setup
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

def create_table():
    """Create the odds_history table using Supabase RPC"""
    
    print('=' * 60)
    print('🔧 CREATING ODDS_HISTORY TABLE')
    print('=' * 60)
    print()
    
    # Create the table using raw SQL via Supabase's postgrest
    # Since we can't execute DDL directly via Python client, we'll use insert to test table existence
    # and provide manual SQL if needed
    
    try:
        # Test if table exists by trying to query it
        result = supabase.table('odds_history').select('*').limit(1).execute()
        print('✅ Table "odds_history" already exists!')
        print(f'   Current records: {len(result.data)}')
        return True
    except Exception as e:
        if 'could not find' in str(e).lower() or 'does not exist' in str(e).lower():
            print('❌ Table "odds_history" does not exist yet.')
            print()
            print('📋 Please run this SQL in your Supabase Dashboard > SQL Editor:')
            print('=' * 60)
            print('''
-- Create odds_history table for tracking line movements
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_odds_history_player_stat 
    ON public.odds_history(player_name, stat_type);
    
CREATE INDEX IF NOT EXISTS idx_odds_history_game 
    ON public.odds_history(game_id);
    
CREATE INDEX IF NOT EXISTS idx_odds_history_recorded 
    ON public.odds_history(recorded_at DESC);

-- Enable Row Level Security
ALTER TABLE public.odds_history ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access
CREATE POLICY "Allow public read access" ON public.odds_history
    FOR SELECT USING (true);

-- Create policy to allow authenticated insert
CREATE POLICY "Allow authenticated insert" ON public.odds_history
    FOR INSERT WITH CHECK (true);

COMMENT ON TABLE public.odds_history IS 
    'Historical tracking of sportsbook odds for line movement analysis';
''')
            print('=' * 60)
            print()
            print('After running the SQL above:')
            print('1. Come back and run: python scripts/track_odds_history.py')
            print('2. Set up hourly tracking with: track-odds-hourly.ps1')
            print()
            return False
        else:
            print(f'❌ Unexpected error: {e}')
            return False

if __name__ == '__main__':
    if create_table():
        print()
        print('✅ Ready to track odds! Run:')
        print('   python scripts/track_odds_history.py')
    else:
        print('⚠️  Please create the table first using the SQL above.')
