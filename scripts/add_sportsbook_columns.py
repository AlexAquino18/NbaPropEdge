#!/usr/bin/env python3
"""
Add sportsbook odds columns to props table using Supabase client
This bypasses the need to access the Supabase dashboard
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('🔧 Adding sportsbook odds columns to props table...')
print()

# SQL to add columns
sql = """
ALTER TABLE public.props 
ADD COLUMN IF NOT EXISTS draftkings_line DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS draftkings_over_odds INTEGER,
ADD COLUMN IF NOT EXISTS draftkings_under_odds INTEGER,
ADD COLUMN IF NOT EXISTS fanduel_line DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS fanduel_over_odds INTEGER,
ADD COLUMN IF NOT EXISTS fanduel_under_odds INTEGER;
"""

try:
    # Try to execute using the rpc method
    result = supabase.rpc('exec', {'sql': sql}).execute()
    print('✅ Successfully added sportsbook odds columns!')
except Exception as e:
    error_msg = str(e)
    
    # Check if columns already exist
    if 'already exists' in error_msg.lower():
        print('✅ Sportsbook odds columns already exist!')
    elif 'could not find' in error_msg.lower() and 'exec' in error_msg.lower():
        # RPC function doesn't exist, try alternative method
        print('⚠️  Cannot add columns via API.')
        print()
        print('📋 Please ask the person who created the Supabase project to run this SQL:')
        print('=' * 60)
        print(sql)
        print('=' * 60)
        print()
        print('Or, if you have the DATABASE_URL, add it to your .env file:')
        print('DATABASE_URL=postgresql://...')
    else:
        print(f'❌ Error: {e}')
        print()
        print('📋 Please run this SQL manually in Supabase:')
        print('=' * 60)
        print(sql)
        print('=' * 60)

print()
print('Once columns are added, run: python scripts\\fetch_sportsbook_odds.py')
