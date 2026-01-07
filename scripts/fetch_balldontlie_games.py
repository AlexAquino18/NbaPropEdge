import os
import requests
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client
import sys

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

# Ball Don't Lie API key
BALLDONTLIE_API_KEY = 'd096acdb-bd8a-419a-b921-05a24a0f44f9'

# Team name mapping from Ball Don't Lie to standard abbreviations
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

def fetch_todays_games():
    """Fetch today's NBA games from Ball Don't Lie API"""
    print('FETCHING TODAY\'S NBA GAMES FROM BALL DON\'T LIE')
    print('=' * 60)
    
    # Get today's date
    today = date.today()
    date_str = today.strftime('%Y-%m-%d')
    
    print(f'Fetching games for {date_str}...')
    
    try:
        # Ball Don't Lie API v1 with API key as query parameter
        url = f'https://api.balldontlie.io/v1/games?dates[]={date_str}&api_key={BALLDONTLIE_API_KEY}'
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f'API Error: Status {response.status_code}')
            print(f'Response: {response.text}')
            return False
        
        data = response.json()
        games_data = data.get('data', [])
        
        print(f'Found {len(games_data)} games\n')
        
        if len(games_data) == 0:
            print('No games found for today')
            return False
        
        # Prepare games to insert
        games_to_insert = []
        
        for i, game in enumerate(games_data):
            home_team = game['home_team']
            visitor_team = game['visitor_team']
            
            home_abbr = TEAM_ABBR_MAP.get(home_team['abbreviation'], home_team['abbreviation'])
            away_abbr = TEAM_ABBR_MAP.get(visitor_team['abbreviation'], visitor_team['abbreviation'])
            
            home_full = TEAM_FULL_NAMES.get(home_abbr, home_team['full_name'])
            away_full = TEAM_FULL_NAMES.get(away_abbr, visitor_team['full_name'])
            
            game_id = f'game-{i+1}-{date_str}'
            
            # Handle game_time - use today's date with default time if status is not a timestamp
            game_status = game.get('status', '')
            if isinstance(game_status, str) and ('Qtr' in game_status or 'Final' in game_status or 'Half' in game_status):
                # Game is in progress or finished, use today at 7 PM
                game_time = today.isoformat() + 'T19:00:00Z'
            else:
                # Try to use the provided time, fallback to 7 PM
                game_time = game.get('date', today.isoformat() + 'T19:00:00Z')
            
            games_to_insert.append({
                'id': game_id,
                'home_team': home_full,
                'away_team': away_full,
                'home_team_abbr': home_abbr,
                'away_team_abbr': away_abbr,
                'game_time': game_time,
                'status': 1,
            })
            
            print(f'{i+1}. {away_abbr} @ {home_abbr} - {away_full} at {home_full}')
        
        # Clear existing games with TBD
        print(f'\nClearing old TBD games...')
        supabase.table('games').delete().eq('home_team', 'TBD').execute()
        
        # Insert new games
        print(f'Inserting {len(games_to_insert)} games into database...')
        supabase.table('games').insert(games_to_insert).execute()
        
        print('\n' + '=' * 60)
        print('SUCCESS! REAL NBA GAMES LOADED')
        print('=' * 60)
        print(f'Date: {date_str}')
        print(f'Games: {len(games_to_insert)}')
        print('\nGAMES LOADED:')
        for game in games_to_insert:
            print(f'  {game["away_team_abbr"]} @ {game["home_team_abbr"]}')
        print('=' * 60)
        
        return True
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fetch_todays_games()
    if not success:
        print('\nFailed to fetch games. Make sure you have internet connection.')
        exit(1)
