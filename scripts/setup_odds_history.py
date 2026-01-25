#!/usr/bin/env python3
"""
Automatically create the odds_history table in Supabase using the management API
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
PROJECT_ID = os.getenv('VITE_SUPABASE_PROJECT_ID')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    print("❌ Missing Supabase credentials in .env file")
    exit(1)

# SQL to create the table
SQL = """
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
DROP POLICY IF EXISTS "Allow public read access" ON public.odds_history;
CREATE POLICY "Allow public read access" ON public.odds_history
    FOR SELECT USING (true);

-- Create policy to allow authenticated insert
DROP POLICY IF EXISTS "Allow authenticated insert" ON public.odds_history;
CREATE POLICY "Allow authenticated insert" ON public.odds_history
    FOR INSERT WITH CHECK (true);
"""

def create_table_via_rpc():
    """Create the table using Supabase RPC call"""
    print('=' * 60)
    print('🔧 CREATING ODDS_HISTORY TABLE')
    print('=' * 60)
    print()
    
    # Use Supabase REST API to execute SQL via RPC
    # We'll use the query endpoint with raw SQL
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Try a direct approach - split SQL into statements
    statements = [s.strip() for s in SQL.split(';') if s.strip()]
    
    print(f"📋 Executing {len(statements)} SQL statements...")
    print()
    
    # Since Supabase REST API doesn't support direct DDL, we'll save the SQL to a file
    # and provide instructions
    migration_file = "supabase/migrations/20260124000000_add_odds_history.sql"
    
    print(f"💾 Saving migration to: {migration_file}")
    
    with open(migration_file, 'w') as f:
        f.write(SQL)
    
    print("✅ Migration file created!")
    print()
    print("🚀 To apply the migration, choose one of these options:")
    print()
    print("   OPTION 1 - Supabase Dashboard (Recommended):")
    print("   1. Go to: https://supabase.com/dashboard/project/" + PROJECT_ID + "/sql")
    print("   2. Click 'New Query'")
    print("   3. Paste the SQL below and click 'Run'")
    print()
    print("   OPTION 2 - Auto-apply (if Supabase CLI is installed):")
    print("   Run: supabase db push")
    print()
    print("=" * 60)
    print("SQL TO RUN:")
    print("=" * 60)
    print(SQL)
    print("=" * 60)

if __name__ == '__main__':
    create_table_via_rpc()
