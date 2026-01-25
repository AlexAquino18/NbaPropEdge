#!/usr/bin/env python3
"""
Debug player name mismatches between props and odds_history
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
print('DEBUGGING PLAYER NAME MISMATCHES')
print('=' * 60)
print()

# Get player names from props
print('[*] Fetching player names from props table...')
props_response = supabase.table('props').select('player_name, stat_type').limit(1000).execute()
props = props_response.data

# Get unique player names from props
props_players = set()
props_map = {}
for prop in props:
    player = prop['player_name']
    stat = prop['stat_type']
    props_players.add(player)
    key = (player, stat)
    props_map[key] = True

print(f'[+] Found {len(props_players)} unique players in props table')
print()

# Get player names from odds_history
print('[*] Fetching player names from odds_history table...')
odds_response = supabase.table('odds_history').select('player_name, stat_type').order('recorded_at', desc=True).limit(1000).execute()
odds = odds_response.data

# Get unique player names from odds
odds_players = set()
odds_map = {}
for odd in odds:
    player = odd['player_name']
    stat = odd['stat_type']
    odds_players.add(player)
    key = (player, stat)
    odds_map[key] = True

print(f'[+] Found {len(odds_players)} unique players in odds_history table')
print()

# Find players in odds_history but NOT in props
print('=' * 60)
print('PLAYERS IN ODDS_HISTORY BUT NOT IN PROPS')
print('=' * 60)

missing_players = odds_players - props_players
if missing_players:
    print(f'Found {len(missing_players)} players:')
    for player in sorted(list(missing_players)[:20]):
        print(f'  - {player}')
    if len(missing_players) > 20:
        print(f'  ... and {len(missing_players) - 20} more')
else:
    print('None - all players match!')

print()

# Check stat type mismatches
print('=' * 60)
print('STAT TYPE MISMATCHES')
print('=' * 60)

# Sample some props and check if they exist in odds with same stat type
sample_props = props[:10]
print(f'Checking first 10 props:')
print()

for prop in sample_props:
    player = prop['player_name']
    stat = prop['stat_type']
    key = (player, stat)
    
    if key in odds_map:
        print(f'✓ {player} - {stat} (MATCH)')
    else:
        print(f'✗ {player} - {stat} (NO MATCH IN ODDS)')
        # Check if player exists with different stat
        player_stats = [s for (p, s) in odds_map.keys() if p == player]
        if player_stats:
            print(f'    Available stats in odds: {", ".join(player_stats[:5])}')

print()

# Show some successful matches
print('=' * 60)
print('SUCCESSFUL MATCHES (sample)')
print('=' * 60)

matched = 0
for key in list(props_map.keys())[:20]:
    if key in odds_map:
        player, stat = key
        print(f'✓ {player} - {stat}')
        matched += 1

print()
print(f'Total matched: {matched}/20 sampled')
