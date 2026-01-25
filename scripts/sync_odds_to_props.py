#!/usr/bin/env python3
"""
Update live props with latest sportsbook odds from odds_history
This syncs the odds_history table data to the props table for website display
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone, timedelta

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('=' * 60)
print('SYNCING ODDS TO LIVE PROPS')
print('=' * 60)
print()

# Get the most recent odds from odds_history
print('[*] Fetching latest odds from odds_history...')
try:
    # Get odds from the last 2 hours
    cutoff_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    
    response = supabase.table('odds_history')\
        .select('*')\
        .gte('recorded_at', cutoff_time)\
        .order('recorded_at', desc=True)\
        .execute()
    
    odds_records = response.data
    print(f'[+] Found {len(odds_records)} recent odds records')
except Exception as e:
    print(f'[-] Error fetching odds_history: {e}')
    exit(1)

if not odds_records:
    print('[!] No recent odds found in odds_history table')
    print('    Run: python scripts/track_odds_to_supabase.py')
    exit(0)

print()

# Group by player + stat to get the latest odds for each
print('[*] Grouping odds by player and stat...')
latest_odds = {}

for record in odds_records:
    key = (record['player_name'], record['stat_type'])
    
    if key not in latest_odds:
        latest_odds[key] = record
    else:
        # Keep the most recent
        if record['recorded_at'] > latest_odds[key]['recorded_at']:
            latest_odds[key] = record

print(f'[+] Found {len(latest_odds)} unique player props')
print()

# Get all props from database
print('[*] Fetching props from database...')
try:
    props_response = supabase.table('props').select('id, player_name, stat_type').execute()
    props = props_response.data
    print(f'[+] Found {len(props)} props in database')
except Exception as e:
    print(f'[-] Error fetching props: {e}')
    exit(1)

print()

# Match and update
print('[*] Matching odds to props...')
updated_count = 0
errors = 0

for prop in props:
    player_name = prop['player_name']
    stat_type = prop['stat_type']
    key = (player_name, stat_type)
    
    if key in latest_odds:
        odds = latest_odds[key]
        
        # Prepare update
        update_data = {}
        
        if odds.get('draftkings_line') is not None:
            update_data['draftkings_line'] = odds['draftkings_line']
            update_data['draftkings_over_odds'] = odds['draftkings_over_odds']
            update_data['draftkings_under_odds'] = odds['draftkings_under_odds']
        
        if odds.get('fanduel_line') is not None:
            update_data['fanduel_line'] = odds['fanduel_line']
            update_data['fanduel_over_odds'] = odds['fanduel_over_odds']
            update_data['fanduel_under_odds'] = odds['fanduel_under_odds']
        
        if update_data:
            try:
                supabase.table('props').update(update_data).eq('id', prop['id']).execute()
                updated_count += 1
                
                if updated_count <= 5:
                    print(f'    [+] Updated {player_name} - {stat_type}')
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f'    [!] Error updating {player_name}: {e}')

print()
print('=' * 60)
print('ODDS SYNC COMPLETE')
print('=' * 60)
print(f'Updated: {updated_count} props')
print(f'Errors: {errors}')
print()

if updated_count > 0:
    print('[+] Success! Sportsbook odds are now live on your website')
    print('    Refresh your browser to see DraftKings and FanDuel odds')
else:
    print('[!] No props were updated')
    print('    Make sure:')
    print('    1. Props exist in your database (run: .\\run-projections.ps1)')
    print('    2. Odds were tracked (run: python scripts/track_odds_to_supabase.py)')
    print('    3. Player names match between props and odds_history tables')
