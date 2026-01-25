#!/usr/bin/env python3
"""
Create the odds_history table in Supabase with the correct schema
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Connect to Supabase
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('=' * 60)
print('🔧 CREATING ODDS_HISTORY TABLE IN SUPABASE')
print('=' * 60)
print()

# SQL to create the table with the correct schema
sql = """
-- Drop the old table if it exists with wrong schema
DROP TABLE IF EXISTS public.odds_history CASCADE;

-- Create odds_history table with correct schema
CREATE TABLE public.odds_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    prop_id UUID,
    player_name TEXT NOT NULL,
    stat_type TEXT NOT NULL,
    draftkings_line DECIMAL(10,2),
    draftkings_over_odds INTEGER,
    draftkings_under_odds INTEGER,
    fanduel_line DECIMAL(10,2),
    fanduel_over_odds INTEGER,
    fanduel_under_odds INTEGER,
    prizepicks_line DECIMAL(10,2),
    recorded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create indexes
CREATE INDEX idx_odds_history_player_stat ON public.odds_history(player_name, stat_type);
CREATE INDEX idx_odds_history_recorded ON public.odds_history(recorded_at DESC);

-- Enable RLS
ALTER TABLE public.odds_history ENABLE ROW LEVEL SECURITY;

-- Allow public read
CREATE POLICY "Allow public read" ON public.odds_history FOR SELECT USING (true);

-- Allow service role to insert
CREATE POLICY "Allow insert" ON public.odds_history FOR INSERT WITH CHECK (true);
"""

print('📋 SQL to execute:')
print(sql)
print()
print('⚠️  You need to run this SQL manually in Supabase Dashboard:')
print()
print('1. Go to https://supabase.com/dashboard')
print('2. Select your project')
print('3. Click "SQL Editor" in the left sidebar')
print('4. Click "New Query"')
print('5. Paste the SQL above')
print('6. Click "Run"')
print()
print('=' * 60)
print('After creating the table, run:')
print('  python scripts/track_odds_to_supabase.py')
print('=' * 60)
