import os
import sys
from datetime import date, timedelta
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

BALLDONTLIE_API_KEY = os.getenv('BALLDONTLIE_API_KEY') or 'd096acdb-bd8a-419a-b921-05a24a0f44f9'

TEAM_ABBR_MAP = {
    'ATL': 'ATL', 'BOS': 'BOS', 'BKN': 'BKN', 'CHA': 'CHA', 'CHI': 'CHI',
    'CLE': 'CLE', 'DAL': 'DAL', 'DEN': 'DEN', 'DET': 'DET', 'GSW': 'GSW',
    'HOU': 'HOU', 'IND': 'IND', 'LAC': 'LAC', 'LAL': 'LAL', 'MEM': 'MEM',
    'MIA': 'MIA', 'MIL': 'MIL', 'MIN': 'MIN', 'NOP': 'NOP', 'NYK': 'NYK',
    'OKC': 'OKC', 'ORL': 'ORL', 'PHI': 'PHI', 'PHO': 'PHO', 'PHX': 'PHO', 'POR': 'POR',
    'SAC': 'SAC', 'SAS': 'SAS', 'TOR': 'TOR', 'UTA': 'UTA', 'WAS': 'WAS',
    # Variants sometimes seen
    'HAW': 'ATL', 'TIM': 'MIN', 'PAC': 'IND', 'TRA': 'POR', 'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS'
}


def normalize_abbr(abbr: str) -> str:
    if not abbr:
        return abbr
    return TEAM_ABBR_MAP.get(abbr, abbr)


def fetch_games_for_dates(dates):
    all_games = []
    for d in dates:
        url = f'https://api.balldontlie.io/v1/games?dates[]={d}'
        headers = {'Authorization': BALLDONTLIE_API_KEY}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 401:
            url = f'https://api.balldontlie.io/v1/games?dates[]={d}&api_key={BALLDONTLIE_API_KEY}'
            resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            print(f'⚠️  BallDontLie status {resp.status_code} for {d}')
            continue
        data = resp.json().get('data', [])
        for g in data:
            home_abbr = normalize_abbr(g['home_team']['abbreviation'])
            away_abbr = normalize_abbr(g['visitor_team']['abbreviation'])
            home_full = g['home_team']['full_name']
            away_full = g['visitor_team']['full_name']
            # Use game datetime from API, normalize to ISO UTC
            raw_dt = g.get('date')
            game_dt = raw_dt if raw_dt else f'{d}T19:00:00+00:00'
            all_games.append({
                'date': d,
                'home_team': home_full,
                'home_team_abbr': home_abbr,
                'away_team': away_full,
                'away_team_abbr': away_abbr,
                'game_time': game_dt.replace('Z', '+00:00'),
                'status': 1,
            })
    return all_games


def upsert_games(games):
    if not games:
        print('No games to upsert')
        return False
    inserted = 0
    for game in games:
        try:
            # Build day range for the game date in UTC
            day = game['date']
            start = f"{day}T00:00:00+00:00"
            end = f"{day}T23:59:59+00:00"
            # Look for existing game with same home/away on that day
            existing = supabase.table('games').select('id')\
                .eq('home_team_abbr', game['home_team_abbr'])\
                .eq('away_team_abbr', game['away_team_abbr'])\
                .gte('game_time', start)\
                .lte('game_time', end)\
                .limit(1)\
                .execute().data
            payload = {
                'home_team': game['home_team'],
                'home_team_abbr': game['home_team_abbr'],
                'away_team': game['away_team'],
                'away_team_abbr': game['away_team_abbr'],
                'game_time': game['game_time'],
                'status': 1,
            }
            if existing:
                supabase.table('games').update(payload).eq('id', existing[0]['id']).execute()
            else:
                supabase.table('games').insert(payload).execute()
            inserted += 1
        except Exception as e:
            print(f'⚠️  Upsert error: {e}')
    print(f'✅ Upserted {inserted} games')
    return True


def main():
    print('FETCHING BALL DONT LIE GAMES (Today + Tomorrow)')
    today = date.today()
    dates = [today.strftime('%Y-%m-%d'), (today + timedelta(days=1)).strftime('%Y-%m-%d')]
    games = fetch_games_for_dates(dates)
    print(f'Found {len(games)} games across {len(dates)} dates')
    upsert_games(games)

if __name__ == '__main__':
    main()
