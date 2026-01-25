#!/usr/bin/env python3
"""Apply the sportsbook odds migration"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('🔧 Applying sportsbook odds migration...')

# Check if columns already exist
try:
    result = supabase.table('props').select('draftkings_line').limit(1).execute()
    print('✅ Sportsbook odds columns already exist!')
except Exception as e:
    if 'column' in str(e).lower() and 'does not exist' in str(e).lower():
        print('❌ Columns do not exist. You need to run the migration manually.')
        print('\nPlease run this SQL in your Supabase SQL Editor:')
        print('-' * 60)
        with open('supabase/migrations/20260106000000_add_sportsbook_odds.sql', 'r') as f:
            print(f.read())
        print('-' * 60)
    else:
        print(f'Error: {e}')
