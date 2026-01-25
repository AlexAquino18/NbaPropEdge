#!/usr/bin/env python3
"""
Full refresh: Clear old odds, fetch new ones, and sync to props
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('=' * 60)
print('FULL ODDS REFRESH')
print('=' * 60)
print()

# Step 1: Clear old odds from props table
print('[1/3] Clearing old odds from props table...')
try:
    # Get all props
    response = supabase.table('props').select('id').execute()
    props = response.data
    
    print(f'[*] Clearing odds from {len(props)} props...')
    
    # Clear odds in batches
    batch_size = 100
    cleared = 0
    for i in range(0, len(props), batch_size):
        batch = props[i:i+batch_size]
        for prop in batch:
            supabase.table('props').update({
                'draftkings_line': None,
                'draftkings_over_odds': None,
                'draftkings_under_odds': None,
                'fanduel_line': None,
                'fanduel_over_odds': None,
                'fanduel_under_odds': None
            }).eq('id', prop['id']).execute()
            cleared += 1
        
        if (i + batch_size) % 500 == 0:
            print(f'    Cleared {cleared}/{len(props)} props...')
    
    print(f'[+] Cleared odds from {cleared} props')
except Exception as e:
    print(f'[-] Error clearing odds: {e}')

print()

# Step 2: Clear old odds_history (keep last 24 hours only)
print('[2/3] Clearing old odds_history...')
try:
    # Delete odds older than 24 hours
    cutoff = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    result = supabase.table('odds_history').delete().lt('recorded_at', cutoff).execute()
    print(f'[+] Cleared old odds_history records')
except Exception as e:
    print(f'[!] Error clearing odds_history: {e}')

print()

# Step 3: Fetch fresh odds
print('[3/3] Fetching fresh odds...')
print('    Run: python scripts/track_odds_to_supabase.py')
print('    Then: python scripts/sync_odds_to_props.py')
print()

print('=' * 60)
print('ODDS CLEARED - READY FOR FRESH DATA')
print('=' * 60)
print()
print('Next steps:')
print('1. Run: python scripts/track_odds_to_supabase.py')
print('2. Run: python scripts/sync_odds_to_props.py')
print()
print('Or run the full daily update:')
print('  .\\daily-update.ps1')
