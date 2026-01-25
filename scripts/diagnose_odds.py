#!/usr/bin/env python3
"""
Diagnose sportsbook odds in Supabase
Check if odds are actually in the props table
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('=' * 60)
print('DIAGNOSING SPORTSBOOK ODDS')
print('=' * 60)
print()

# Check props table
print('[*] Checking props table for sportsbook odds...')
try:
    response = supabase.table('props').select('id, player_name, stat_type, draftkings_line, fanduel_line').limit(10).execute()
    props = response.data
    
    print(f'[+] Found {len(props)} props (showing first 10)')
    print()
    
    has_dk = 0
    has_fd = 0
    has_none = 0
    
    for prop in props:
        dk = prop.get('draftkings_line')
        fd = prop.get('fanduel_line')
        
        if dk is not None:
            has_dk += 1
        if fd is not None:
            has_fd += 1
        if dk is None and fd is None:
            has_none += 1
        
        print(f"  {prop['player_name']} - {prop['stat_type']}")
        print(f"    DraftKings: {dk if dk else 'MISSING'}")
        print(f"    FanDuel: {fd if fd else 'MISSING'}")
        print()
    
    print('=' * 60)
    print('SUMMARY')
    print('=' * 60)
    print(f'Props with DraftKings odds: {has_dk}/10')
    print(f'Props with FanDuel odds: {has_fd}/10')
    print(f'Props with NO odds: {has_none}/10')
    print()
    
    if has_none == 10:
        print('[!] NO SPORTSBOOK ODDS FOUND IN PROPS TABLE')
        print('    The odds are NOT in your props table yet!')
        print()
        print('    Solution: Run this command:')
        print('    python scripts/sync_odds_to_props.py')
    elif has_dk > 0 or has_fd > 0:
        print('[+] Sportsbook odds ARE in your props table!')
        print('    If not showing on website, it may be a frontend issue.')
        print()
        print('    Check your browser console for errors.')
    
except Exception as e:
    print(f'[-] Error: {e}')
    print()

print()
print('[*] Checking odds_history table...')
try:
    response = supabase.table('odds_history').select('player_name, stat_type, draftkings_line, fanduel_line').order('recorded_at', desc=True).limit(5).execute()
    odds = response.data
    
    print(f'[+] Found {len(odds)} recent odds records')
    print()
    
    for odd in odds[:5]:
        print(f"  {odd['player_name']} - {odd['stat_type']}")
        print(f"    DraftKings: {odd.get('draftkings_line')}")
        print(f"    FanDuel: {odd.get('fanduel_line')}")
        print()
    
    if len(odds) > 0:
        print('[+] Odds_history has data!')
        print('    These odds need to be synced to the props table.')
    
except Exception as e:
    print(f'[-] Error: {e}')
