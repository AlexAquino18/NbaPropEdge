#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch NBA player props from PrizePicks directly
Store in Supabase without Edge Functions
"""

import os
import sys
import requests
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Supabase client
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

# Team abbreviations mapping
TEAM_ABBR_MAP = {
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN',
    'Charlotte Hornets': 'CHA', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
    'LA Clippers': 'LAC', 'Los Angeles Clippers': 'LAC', 'Los Angeles Lakers': 'LAL',
    'LA Lakers': 'LAL', 'Memphis Grizzlies': 'MEM', 'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN', 'New Orleans Pelicans': 'NOP',
    'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC', 'Orlando Magic': 'ORL',
    'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHO', 'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC', 'San Antonio Spurs': 'SAS', 'Toronto Raptors': 'TOR',
    'Utah Jazz': 'UTA', 'Washington Wizards': 'WAS'
}

def get_team_abbr(team_name):
    return TEAM_ABBR_MAP.get(team_name, team_name[:3].upper())

def fetch_prizepicks_props():
    """Fetch props from PrizePicks API"""
    print('[*] Fetching props from PrizePicks...')
    
    try:
        url = 'https://api.prizepicks.com/projections?league_id=7&per_page=250&single_stat=true'
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://app.prizepicks.com',
            'Referer': 'https://app.prizepicks.com/',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        projections = data.get('data', [])
        included = data.get('included', [])
        
        print(f'[+] Found {len(projections)} projections')
        
        # Build players and games maps
        players_map = {}
        games_map = {}
        
        for item in included:
            if item.get('type') == 'new_player':
                players_map[item['id']] = item
            elif item.get('type') == 'game':
                games_map[item['id']] = item
        
        return projections, players_map, games_map
        
    except Exception as e:
        print(f'[-] Error fetching from PrizePicks: {e}')
        return [], {}, {}

def store_games_from_projections(projections, players_map):
    """Build and store games from projection data"""
    print('[*] Building games from projections...')
    
    # Build games from projections by grouping players by game_id
    games_by_id = {}
    
    for proj in projections:
        game_id = proj.get('attributes', {}).get('game_id')
        if not game_id:
            continue
        
        player_id = proj.get('relationships', {}).get('new_player', {}).get('data', {}).get('id')
        if not player_id or player_id not in players_map:
            continue
        
        player = players_map[player_id]
        team_name = player.get('attributes', {}).get('team_name') or player.get('attributes', {}).get('team', '')
        
        if game_id not in games_by_id:
            games_by_id[game_id] = {
                'teams': set(),
                'scheduled_at': proj.get('attributes', {}).get('start_time')
            }
        
        if team_name:
            games_by_id[game_id]['teams'].add(team_name)
    
    # Create game inserts
    game_inserts = []
    
    for game_id, game_info in games_by_id.items():
        teams = list(game_info['teams'])
        
        if len(teams) >= 2:
            home_team = teams[0]
            away_team = teams[1]
        elif len(teams) == 1:
            home_team = teams[0]
            away_team = 'Opponent'
        else:
            continue
        
        game_inserts.append({
            'external_id': game_id,
            'home_team': home_team,
            'away_team': away_team,
            'home_team_abbr': get_team_abbr(home_team),
            'away_team_abbr': get_team_abbr(away_team),
            'game_time': game_info['scheduled_at'] or datetime.now(timezone.utc).isoformat(),
            'status': 'scheduled'
        })
    
    print(f'[*] Built {len(game_inserts)} games from projections')
    
    if game_inserts:
        try:
            supabase.table('games').insert(game_inserts).execute()
            print(f'[+] Inserted {len(game_inserts)} games')
        except Exception as e:
            print(f'[!] Error inserting games: {e}')
    
    # Get all games to build ID map
    result = supabase.table('games').select('id, external_id').execute()
    game_id_map = {g['external_id']: g['id'] for g in result.data}
    
    print(f'[*] Game ID map has {len(game_id_map)} entries')
    
    return game_id_map

def store_props(projections, players_map, game_id_map):
    """Store props in Supabase"""
    print('[*] Storing props...')
    
    # Debug: Show what game IDs we have
    print(f'[!] Available game IDs in map: {list(game_id_map.keys())[:5]}...')
    
    # Group by player+stat to get middle line
    grouped = {}
    game_ids_in_projections = set()
    
    for proj in projections:
        attrs = proj.get('attributes', {})
        stat_type = attrs.get('stat_type', '')
        game_id = attrs.get('game_id')
        
        if game_id:
            game_ids_in_projections.add(game_id)
        
        # Skip unwanted stat types
        stat_lower = stat_type.lower()
        if any(skip in stat_lower for skip in [
            '1st 3 minutes', 'first 3 minutes', 'quarters with', 
            'two pointers', '2 pointers', 'fantasy'
        ]):
            continue
        
        player_id = proj.get('relationships', {}).get('new_player', {}).get('data', {}).get('id')
        if not player_id:
            continue
        
        key = f"{player_id}-{stat_type}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(proj)
    
    print(f'[!] Game IDs in projections: {list(game_ids_in_projections)[:5]}...')
    print(f'[!] Matching: {sum(1 for gid in game_ids_in_projections if gid in game_id_map)} / {len(game_ids_in_projections)} game IDs match')
    
    # Select middle line for each group
    base_projections = []
    for group in grouped.values():
        lines = [p['attributes']['line_score'] for p in group]
        lines.sort()
        middle_line = lines[len(lines) // 2]
        
        for proj in group:
            if proj['attributes']['line_score'] == middle_line:
                base_projections.append(proj)
                break
    
    print(f'[+] Filtered to {len(base_projections)} props (middle lines only)')
    
    # Insert props
    prop_inserts = []
    skipped_no_player = 0
    skipped_no_game = 0
    
    for proj in base_projections:
        attrs = proj.get('attributes', {})
        player_id = proj.get('relationships', {}).get('new_player', {}).get('data', {}).get('id')
        
        if not player_id or player_id not in players_map:
            skipped_no_player += 1
            continue
        
        player = players_map[player_id]
        player_attrs = player.get('attributes', {})
        player_name = player_attrs.get('display_name', '')
        team = player_attrs.get('team') or player_attrs.get('team_name', '')
        
        game_id = attrs.get('game_id')
        db_game_id = game_id_map.get(game_id) if game_id else None
        
        if not db_game_id:
            skipped_no_game += 1
            # Debug first few mismatches
            if skipped_no_game <= 3:
                print(f'[!] No game match for {player_name} - game_id: {game_id}')
            continue
        
        line = attrs.get('line_score', 0)
        
        prop_inserts.append({
            'game_id': db_game_id,
            'external_id': proj['id'],
            'player_name': player_name,
            'player_id': player_id,
            'team': team,
            'stat_type': attrs.get('stat_type', ''),
            'line': float(line),
            'prizepicks_odds': float(line),
            'projection': None,
            'edge': None,
            'probability_over': None,
            'confidence': None
        })
    
    print(f'[*] Prepared {len(prop_inserts)} props for insert')
    print(f'    Skipped: {skipped_no_player} (no player), {skipped_no_game} (no game match)')
    
    if prop_inserts:
        try:
            # Insert in batches
            batch_size = 100
            total_inserted = 0
            for i in range(0, len(prop_inserts), batch_size):
                batch = prop_inserts[i:i+batch_size]
                result = supabase.table('props').insert(batch).execute()
                total_inserted += len(batch)
                if i == 0:  # Only print first batch
                    print(f'[+] Batch 1: inserted {len(batch)} props')
            
            if len(prop_inserts) > batch_size:
                print(f'[+] ... inserted {total_inserted} props total')
            
            return total_inserted
        except Exception as e:
            print(f'[-] Error inserting props: {e}')
            if prop_inserts:
                print(f'[!] First prop sample: {prop_inserts[0]}')
            return 0
    
    return 0

def main():
    print('=' * 60)
    print('FETCHING PROPS FROM PRIZEPICKS')
    print('=' * 60)
    print()
    
    # Clear existing data
    print('[*] Clearing old data...')
    try:
        supabase.table('props').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        supabase.table('games').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print('[+] Cleared old data')
    except Exception as e:
        print(f'[!] Could not clear old data: {e}')
    
    print()
    
    # Fetch from PrizePicks
    projections, players_map, games_map = fetch_prizepicks_props()
    
    if not projections:
        print('[-] No props found from PrizePicks')
        return
    
    print()
    
    # Store games (built from projections, not from games_map)
    game_id_map = store_games_from_projections(projections, players_map)
    
    print()
    
    # Store props
    props_count = store_props(projections, players_map, game_id_map)
    
    print()
    print('=' * 60)
    print('PROPS FETCH COMPLETE')
    print('=' * 60)
    print(f'Games: {len(game_id_map)}')
    print(f'Props: {props_count}')
    print()
    
    if props_count > 0:
        print('[+] Success! Props are now in Supabase')
        print('    Next: Run .\\run-projections.ps1 to calculate projections')
    else:
        print('[!] No props were inserted. Check the errors above.')

if __name__ == '__main__':
    main()
