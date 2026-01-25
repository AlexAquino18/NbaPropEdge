import os
import requests
from datetime import date
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict
import numpy as np
from scipy import stats as scipy_stats
import sys
import shutil

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

BALLDONTLIE_API_KEY = 'd096acdb-bd8a-419a-b921-05a24a0f44f9'

TEAM_ABBR_MAP = {
    'ATL': 'ATL', 'BOS': 'BOS', 'BKN': 'BKN', 'CHA': 'CHA', 'CHI': 'CHI',
    'CLE': 'CLE', 'DAL': 'DAL', 'DEN': 'DEN', 'DET': 'DET', 'GSW': 'GSW',
    'HOU': 'HOU', 'IND': 'IND', 'LAC': 'LAC', 'LAL': 'LAL', 'MEM': 'MEM',
    'MIA': 'MIA', 'MIL': 'MIL', 'MIN': 'MIN', 'NOP': 'NOP', 'NYK': 'NYK',
    'OKC': 'OKC', 'ORL': 'ORL', 'PHI': 'PHI', 'PHX': 'PHO', 'POR': 'POR',
    'SAC': 'SAC', 'SAS': 'SAS', 'TOR': 'TOR', 'UTA': 'UTA', 'WAS': 'WAS'
}

TEAM_FULL_NAMES = {
    'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets',
    'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors', 'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers',
    'LAC': 'Los Angeles Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves',
    'NOP': 'New Orleans Pelicans', 'NYK': 'New York Knicks', 'OKC': 'Oklahoma City Thunder',
    'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHO': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers', 'SAC': 'Sacramento Kings', 'SAS': 'San Antonio Spurs',
    'TOR': 'Toronto Raptors', 'UTA': 'Utah Jazz', 'WAS': 'Washington Wizards'
}

def step0_refresh_props():
    """Step 0: Fetch latest player props via Supabase Edge Function"""
    print('=' * 60)
    print('STEP 0: FETCHING PLAYER PROPS')
    print('=' * 60)

    url = os.getenv('VITE_SUPABASE_URL')
    anon = os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
    if not url or not anon:
        print('Missing Supabase env vars, skipping props refresh')
        return False

    def invoke(fn_name: str):
        try:
            fn_url = f"{url}/functions/v1/{fn_name}"
            headers = {
                'Authorization': f'Bearer {anon}',
                'apikey': anon,
                'Content-Type': 'application/json',
            }
            resp = requests.post(fn_url, headers=headers, timeout=60)
            ok = resp.status_code in (200, 202)
            print(f"Invoke {fn_name}: status {resp.status_code}{' (ok)' if ok else ''}")
            if not ok:
                print(resp.text[:200])
            return ok
        except Exception as e:
            print(f"Error invoking {fn_name}: {e}")
            return False

    # First, load/update player stats if needed
    invoke('fetch-player-stats')
    # Then, refresh props from provider/board
    return invoke('refresh-data')

def step1_fetch_games():
    """Step 1: Fetch today's NBA games from Ball Don't Lie API"""
    print('=' * 60)
    print('STEP 1: FETCHING TODAY\'S NBA GAMES')
    print('=' * 60)
    
    today = date.today()
    date_str = today.strftime('%Y-%m-%d')
    
    print(f'Fetching games for {date_str}...')
    
    try:
        # Try with Authorization header first
        url = f'https://api.balldontlie.io/v1/games?dates[]={date_str}'
        headers = {
            'Authorization': BALLDONTLIE_API_KEY
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # If 401, try as query parameter
        if response.status_code == 401:
            print('Trying alternative API key format...')
            url = f'https://api.balldontlie.io/v1/games?dates[]={date_str}&api_key={BALLDONTLIE_API_KEY}'
            response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f'API Error: Status {response.status_code}')
            print(f'Response: {response.text[:200]}')
            print('\nFalling back to manually fetched games for today...')
            
            # Hardcoded games for January 6, 2026 (as backup)
            matchups = [
                ('Cleveland Cavaliers', 'CLE', 'Indiana Pacers', 'IND'),
                ('Orlando Magic', 'ORL', 'Washington Wizards', 'WAS'),
                ('San Antonio Spurs', 'SAS', 'Memphis Grizzlies', 'MEM'),
                ('Miami Heat', 'MIA', 'Minnesota Timberwolves', 'MIN'),
                ('Los Angeles Lakers', 'LAL', 'New Orleans Pelicans', 'NOP'),
                ('Dallas Mavericks', 'DAL', 'Sacramento Kings', 'SAC'),
            ]
            
            print(f'Using {len(matchups)} known games for today:\n')
            for i, (away_full, away_abbr, home_full, home_abbr) in enumerate(matchups, 1):
                print(f'{i}. {away_abbr} @ {home_abbr} - {away_full} at {home_full}')
            
            print(f'\nSuccess! Using {len(matchups)} games for today')
            return matchups
        
        data = response.json()
        games_data = data.get('data', [])
        
        print(f'Found {len(games_data)} games\n')
        
        if len(games_data) == 0:
            print('No games found for today')
            # Fallback to hardcoded games
            matchups = [
                ('Cleveland Cavaliers', 'CLE', 'Indiana Pacers', 'IND'),
                ('Orlando Magic', 'ORL', 'Washington Wizards', 'WAS'),
                ('San Antonio Spurs', 'SAS', 'Memphis Grizzlies', 'MEM'),
                ('Miami Heat', 'MIA', 'Minnesota Timberwolves', 'MIN'),
                ('Los Angeles Lakers', 'LAL', 'New Orleans Pelicans', 'NOP'),
                ('Dallas Mavericks', 'DAL', 'Sacramento Kings', 'SAC'),
            ]
            return matchups
        
        matchups = []
        
        for i, game in enumerate(games_data):
            home_team = game['home_team']
            visitor_team = game['visitor_team']
            
            home_abbr = TEAM_ABBR_MAP.get(home_team['abbreviation'], home_team['abbreviation'])
            away_abbr = TEAM_ABBR_MAP.get(visitor_team['abbreviation'], visitor_team['abbreviation'])
            
            home_full = TEAM_FULL_NAMES.get(home_abbr, home_team['full_name'])
            away_full = TEAM_FULL_NAMES.get(away_abbr, visitor_team['full_name'])
            
            matchups.append((away_full, away_abbr, home_full, home_abbr))
            print(f'{i+1}. {away_abbr} @ {home_abbr} - {away_full} at {home_full}')
        
        print(f'\nSuccess! Found {len(matchups)} games for today')
        return matchups
        
    except Exception as e:
        print(f'Error: {e}')
        print('\nFalling back to manually fetched games for today...')
        
        # Hardcoded games for January 6, 2026 (as backup)
        matchups = [
            ('Cleveland Cavaliers', 'CLE', 'Indiana Pacers', 'IND'),
            ('Orlando Magic', 'ORL', 'Washington Wizards', 'WAS'),
            ('San Antonio Spurs', 'SAS', 'Memphis Grizzlies', 'MEM'),
            ('Miami Heat', 'MIA', 'Minnesota Timberwolves', 'MIN'),
            ('Los Angeles Lakers', 'LAL', 'New Orleans Pelicans', 'NOP'),
            ('Dallas Mavericks', 'DAL', 'Sacramento Kings', 'SAC'),
        ]
        
        print(f'Using {len(matchups)} known games for today')
        return matchups

def step2_link_props_to_games(matchups):
    """Step 2: Link props to their correct games using the load_jan6 approach"""
    print('\n' + '=' * 60)
    print('STEP 2: LINKING PROPS TO GAMES')
    print('=' * 60)
    
    if not matchups:
        print('No matchups to link!')
        return False
    
    today = date.today()
    date_str = today.strftime('%Y-%m-%d')
    
    # Get all existing props to find games with props
    print('Analyzing existing props...')
    props = supabase.table('props').select('game_id, team').execute().data
    print(f'Found {len(props)} props')
    
    # Group props by game_id and find which teams are in each game
    game_teams = defaultdict(set)
    for prop in props:
        game_id = prop.get('game_id')
        team = prop.get('team')
        if game_id and team:
            game_teams[game_id].add(team)
    
    print(f'Found {len(game_teams)} existing games with props')
    
    # Get existing games
    print('Fetching existing games...')
    games_result = supabase.table('games').select('*').execute()
    existing_games = {g['id']: g for g in games_result.data}
    print(f'Found {len(existing_games)} games in database\n')
    
    # Update existing games that have props
    print('Updating existing games with props...')
    updated_existing = 0
    used_matchups = set()
    
    for game_id, teams in game_teams.items():
        teams_list = list(teams)
        
        if len(teams_list) >= 1:
            team_abbr = teams_list[0]
            
            # Find matching matchup
            for away_name, away_abbr, home_name, home_abbr in matchups:
                if away_abbr == team_abbr or home_abbr == team_abbr:
                    # Update the game
                    supabase.table('games').update({
                        'home_team': home_name,
                        'home_team_abbr': home_abbr,
                        'away_team': away_name,
                        'away_team_abbr': away_abbr,
                        'game_time': f'{date_str}T19:00:00-05:00',
                    }).eq('id', game_id).execute()
                    
                    print(f'  Updated: {away_abbr} @ {home_abbr}')
                    updated_existing += 1
                    used_matchups.add((away_abbr, home_abbr))
                    break
    
    # Create any missing games
    print('\nCreating missing games...')
    created_new = 0
    
    for away_name, away_abbr, home_name, home_abbr in matchups:
        if (away_abbr, home_abbr) not in used_matchups:
            # Create new game
            supabase.table('games').insert({
                'home_team': home_name,
                'home_team_abbr': home_abbr,
                'away_team': away_name,
                'away_team_abbr': away_abbr,
                'game_time': f'{date_str}T19:00:00-05:00',
                'status': 1
            }).execute()
            
            print(f'  Created: {away_abbr} @ {home_abbr}')
            created_new += 1
    
    print(f'\nUpdated {updated_existing} existing games')
    print(f'Created {created_new} new games')
    print(f'Total: {updated_existing + created_new} games linked')
    
    return True

def step3_run_projections():
    """Step 3: Run advanced projections with defensive adjustments"""
    print('\n' + '=' * 60)
    print('STEP 3: RUNNING ADVANCED PROJECTIONS')
    print('=' * 60)
    
    # Import the projection script's main function
    import sys
    sys.path.append('scripts')
    
    try:
        from update_projections_with_defense import main as run_projections
        run_projections()
        return True
    except Exception as e:
        print(f'Error running projections: {e}')
        print('Falling back to manual execution...')
        
        import subprocess
        result = subprocess.run(
            [sys.executable, 'scripts/update_projections_with_defense.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(result.stderr)
            return False

def step4_fetch_sportsbook_odds():
    """Step 4: Fetch sportsbook odds for all players"""
    print('\n' + '=' * 60)
    print('STEP 4: FETCHING SPORTSBOOK ODDS')
    print('=' * 60)
    
    try:
        # Run the fetch_sportsbook_odds.py script
        import subprocess
        result = subprocess.run(
            [sys.executable, 'scripts/fetch_sportsbook_odds.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(result.stdout)
            
            # Copy the odds cache to the public folder so it's accessible
            cache_file = 'sportsbook_odds_cache.json'
            public_file = 'public/sportsbook_odds_cache.json'
            
            if os.path.exists(cache_file):
                shutil.copy(cache_file, public_file)
                print(f'✅ Copied odds cache to {public_file}')
            else:
                print('⚠️  Odds cache file not found')
            
            return True
        else:
            print('⚠️  Error fetching sportsbook odds:')
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f'Error running sportsbook odds fetch: {e}')
        return False

def main():
    print('\n')
    print('*' * 60)
    print('  FULL PROJECTION PIPELINE')
    print('  0. Fetch player props (Edge Function)')
    print('  1. Fetch games from Ball Don\'t Lie')
    print('  2. Link props to games')
    print('  3. Run advanced projections')
    print('  4. Fetch sportsbook odds')
    print('*' * 60)
    print('\n')
    
    # Step 0: Fetch/refresh props so they are available before projections
    step0_refresh_props()

    # Step 1: Fetch games
    matchups = step1_fetch_games()
    
    if not matchups:
        print('\nFailed to fetch games. Exiting.')
        return
    
    # Step 2: Link props to games
    success = step2_link_props_to_games(matchups)
    
    if not success:
        print('\nFailed to link props. Exiting.')
        return
    
    # Step 3: Run projections
    print('\nStarting projection calculations...')
    step3_run_projections()
    
    # Step 4: Fetch sportsbook odds
    print('\nFetching sportsbook odds...')
    step4_fetch_sportsbook_odds()
    
    print('\n' + '*' * 60)
    print('  PIPELINE COMPLETE!')
    print('*' * 60)
    print('\nRefresh your browser to see updated projections with sportsbook odds!')

if __name__ == '__main__':
    main()
