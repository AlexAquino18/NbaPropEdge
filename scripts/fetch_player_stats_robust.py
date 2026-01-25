import os
import time
import requests
from dotenv import load_dotenv
from supabase import create_client
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

load_dotenv()
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('🏀 Fetching NBA Player Stats (Incremental Cache Mode)')
print('=' * 60)

# Get unique players from props
print('\n📊 Fetching players from props...')
props = supabase.table('props').select('player_name').execute()
unique_players = list(set([p['player_name'] for p in props.data]))
print(f'✓ Found {len(unique_players)} unique players\n')

# Create a session with retry logic
session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# NBA Stats API with enhanced headers to mimic real browser
NBA_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
}

# Cache the all players response
ALL_PLAYERS_CACHE = None

def get_all_players():
    global ALL_PLAYERS_CACHE
    if ALL_PLAYERS_CACHE:
        return ALL_PLAYERS_CACHE
    
    url = 'https://stats.nba.com/stats/commonallplayers?LeagueID=00&Season=2025-26&IsOnlyCurrentSeason=1'
    
    print('📥 Fetching player list from NBA API...')
    for attempt in range(5):
        try:
            time.sleep(2 * (attempt + 1))
            response = session.get(url, headers=NBA_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                ALL_PLAYERS_CACHE = data
                print(f'✓ Successfully loaded player database\n')
                return data
            elif response.status_code == 429:
                wait_time = 10 * (attempt + 1)
                print(f'      ⚠️  Rate limited. Waiting {wait_time}s...')
                time.sleep(wait_time)
            else:
                print(f'      ⚠️  API returned status {response.status_code}, retrying in {3 * (attempt + 1)}s...')
                time.sleep(3 * (attempt + 1))
        except requests.exceptions.ConnectionError as e:
            print(f'      ⚠️  Connection error, retrying in {5 * (attempt + 1)}s...')
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f'      ⚠️  Request failed: {str(e)[:50]}, retrying in {5 * (attempt + 1)}s...')
            time.sleep(5 * (attempt + 1))
    
    print('❌ Failed to fetch player list after 5 attempts')
    return None

def find_player(player_name):
    all_players = get_all_players()
    if not all_players:
        return None
    
    try:
        players = all_players['resultSets'][0]['rowSet']
        headers = all_players['resultSets'][0]['headers']
        name_idx = headers.index('DISPLAY_FIRST_LAST')
        id_idx = headers.index('PERSON_ID')
        
        import unicodedata
        def normalize_name(name):
            nfkd = unicodedata.normalize('NFKD', name)
            return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower()
        
        search_name = normalize_name(player_name)
        
        # Try exact match first (normalized)
        for player in players:
            if normalize_name(player[name_idx]) == search_name:
                return {'id': player[id_idx], 'name': player[name_idx]}
        
        # Try partial match (normalized)
        for player in players:
            db_name = normalize_name(player[name_idx])
            if search_name in db_name or db_name in search_name:
                return {'id': player[id_idx], 'name': player[name_idx]}
        
        # Try last name only match
        search_last = search_name.split()[-1] if ' ' in search_name else search_name
        for player in players:
            db_name = normalize_name(player[name_idx])
            db_last = db_name.split()[-1] if ' ' in db_name else db_name
            if search_last == db_last and len(search_last) > 3:
                return {'id': player[id_idx], 'name': player[name_idx]}
        
        return None
    except Exception as e:
        print(f'      ❌ Error parsing player data: {e}')
        return None

def get_latest_cached_game_date(player_name):
    """Get the most recent game date we have cached for a player"""
    try:
        result = supabase.table('player_stats')\
            .select('game_date')\
            .eq('player_name', player_name)\
            .order('game_date', desc=True)\
            .limit(1)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]['game_date']
        return None
    except:
        return None

def fetch_player_stats(player_id, player_name, latest_cached_date=None):
    url = f'https://stats.nba.com/stats/playergamelog?PlayerID={player_id}&Season=2025-26&SeasonType=Regular+Season'
    
    for attempt in range(5):
        try:
            time.sleep(3 + attempt)
            response = session.get(url, headers=NBA_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                games = data['resultSets'][0]['rowSet']
                headers = data['resultSets'][0]['headers']
                
                idx_map = {h: headers.index(h) for h in ['GAME_DATE', 'MATCHUP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG3M', 'FGM', 'FGA', 'FTM', 'FTA']}
                
                stats = []
                for game in games[:15]:  # Last 15 games
                    game_date = game[idx_map['GAME_DATE']]
                    
                    # Skip games we already have cached
                    if latest_cached_date and game_date <= latest_cached_date:
                        continue
                    
                    minutes = game[idx_map['MIN']]
                    if not minutes or minutes == 0:
                        continue
                    
                    matchup = game[idx_map['MATCHUP']] or ''
                    opponent = matchup.split('vs.')[-1].split('@')[-1].strip() if ('vs.' in matchup or '@' in matchup) else 'UNK'
                    
                    stats.append({
                        'player_name': player_name,
                        'player_id': f'nba-{player_id}',
                        'game_date': game_date,
                        'points': game[idx_map['PTS']] or 0,
                        'rebounds': game[idx_map['REB']] or 0,
                        'assists': game[idx_map['AST']] or 0,
                        'steals': game[idx_map['STL']] or 0,
                        'blocks': game[idx_map['BLK']] or 0,
                        'turnovers': game[idx_map['TOV']] or 0,
                        'three_pointers_made': game[idx_map['FG3M']] or 0,
                        'field_goals_made': game[idx_map['FGM']] or 0,
                        'field_goals_attempted': game[idx_map['FGA']] or 0,
                        'free_throws_made': game[idx_map['FTM']] or 0,
                        'free_throws_attempted': game[idx_map['FTA']] or 0,
                        'minutes': minutes,
                        'opponent': opponent,
                    })
                
                return stats
            elif response.status_code == 429:
                wait_time = 15 * (attempt + 1)
                print(f'      ⚠️  Rate limited. Waiting {wait_time}s...')
                time.sleep(wait_time)
            else:
                print(f'      ⚠️  Stats API returned {response.status_code}, retrying in {5 * (attempt + 1)}s...')
                time.sleep(5 * (attempt + 1))
        except requests.exceptions.ConnectionError:
            print(f'      ⚠️  Connection error, retrying in {7 * (attempt + 1)}s...')
            time.sleep(7 * (attempt + 1))
        except Exception as e:
            print(f'      ⚠️  Request failed: {str(e)[:50]}, retrying in {7 * (attempt + 1)}s...')
            time.sleep(7 * (attempt + 1))
    
    return []

# Process players
success = 0
errors = 0
skipped_cached = 0
rate_limited = False

for i, player_name in enumerate(unique_players, 1):
    print(f'[{i}/{len(unique_players)}] 🔍 {player_name}...')
    
    if rate_limited and i % 10 == 0:
        print('   ⏸️  Taking a 30s break to avoid rate limiting...')
        time.sleep(30)
        rate_limited = False
    
    try:
        # Check what we already have cached
        latest_cached = get_latest_cached_game_date(player_name)
        
        if latest_cached:
            # Check how recent the cache is
            try:
                cached_dt = datetime.strptime(latest_cached, '%Y-%m-%d')
                now = datetime.now()
                days_old = (now - cached_dt).days
                
                # If cache is less than 2 days old, skip this player
                if days_old < 2:
                    print(f'  ✓ Cache up-to-date (latest: {latest_cached}), skipping...\n')
                    skipped_cached += 1
                    continue
                else:
                    print(f'  📦 Cache found (latest: {latest_cached}), fetching new games only...')
            except:
                pass
        
        # Find player
        player = find_player(player_name)
        if not player:
            print(f'  ⚠️  Not found\n')
            errors += 1
            time.sleep(2)
            continue
        
        # Fetch only new stats
        stats = fetch_player_stats(player['id'], player['name'], latest_cached)
        
        if not stats or len(stats) == 0:
            if latest_cached:
                print(f'  ✓ No new games since {latest_cached}\n')
                skipped_cached += 1
            else:
                print(f'  ⚠️  No stats found\n')
                errors += 1
            time.sleep(2)
            continue
        
        # Save new games to database
        for stat in stats:
            # Double-check to avoid duplicates
            existing = supabase.table('player_stats')\
                .select('id')\
                .eq('player_name', stat['player_name'])\
                .eq('game_date', stat['game_date'])\
                .execute()
            
            if not existing.data:
                supabase.table('player_stats').insert(stat).execute()
        
        print(f'  ✅ Saved {len(stats)} NEW games')
        print(f'     Latest: {stats[0]["game_date"]} - {stats[0]["points"]} PTS, {stats[0]["rebounds"]} REB, {stats[0]["assists"]} AST vs {stats[0]["opponent"]}\n')
        success += 1
        
        time.sleep(4)
        
    except Exception as e:
        print(f'  ❌ Error: {str(e)[:80]}\n')
        errors += 1
        time.sleep(5)

print('\n' + '=' * 60)
print('📈 SUMMARY')
print('=' * 60)
print(f'✅ Updated: {success} players (new games added)')
print(f'📦 Cached: {skipped_cached} players (already up-to-date)')
print(f'❌ Errors: {errors} players')
print(f'📊 Total: {len(unique_players)} players')
print('=' * 60)
print('\n💡 Incremental caching is active!')
print('   Only new games are fetched, making runs much faster.')
print('=' * 60)