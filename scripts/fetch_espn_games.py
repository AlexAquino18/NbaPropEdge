import os
import requests
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

def get_todays_real_games():
    """Fetch today's real NBA games from ESPN API"""
    print('🏀 FETCHING TODAY\'S REAL NBA GAMES FROM ESPN')
    print('=' * 60)
    
    # Get today's date dynamically
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    
    # ESPN API for NBA scoreboard - this is public and reliable
    url = f'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}'
    
    try:
        print(f'📡 Fetching games for {date_str} ({today.strftime("%B %d, %Y")})...')
        response = requests.get(url)
        data = response.json()
        
        events = data.get('events', [])
        print(f'✅ Found {len(events)} games\n')
        
        if len(events) == 0:
            print('⚠️  No games found for today, trying tomorrow...')
            tomorrow = today + timedelta(days=1)
            date_str = tomorrow.strftime('%Y%m%d')
            url = f'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}'
            response = requests.get(url)
            data = response.json()
            events = data.get('events', [])
            print(f'✅ Found {len(events)} games for tomorrow ({tomorrow.strftime("%B %d, %Y")})\n')
        
        games_to_insert = []
        
        for i, event in enumerate(events):
            competition = event['competitions'][0]
            home_team = competition['competitors'][0]  # First is home
            away_team = competition['competitors'][1]  # Second is away
            
            # Generate a proper UUID for the game
            game_id = str(uuid.uuid4())
            
            game_data = {
                'id': game_id,
                'home_team': home_team['team']['displayName'],
                'away_team': away_team['team']['displayName'],
                'home_team_abbr': home_team['team']['abbreviation'],
                'away_team_abbr': away_team['team']['abbreviation'],
                'game_time': event['date'],
                'status': 1,
            }
            
            # Update existing game if it exists for this matchup today
            day_start = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            day_end = today.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
            
            existing = supabase.table('games').select('id')\
                .eq('home_team_abbr', game_data['home_team_abbr'])\
                .eq('away_team_abbr', game_data['away_team_abbr'])\
                .gte('game_time', day_start)\
                .lte('game_time', day_end)\
                .limit(1)\
                .execute().data
            
            if existing:
                # Update existing game
                supabase.table('games').update({
                    'home_team': game_data['home_team'],
                    'away_team': game_data['away_team'],
                    'game_time': game_data['game_time'],
                    'status': 1,
                }).eq('id', existing[0]['id']).execute()
                print(f'{i+1}. {away_team["team"]["abbreviation"]} @ {home_team["team"]["abbreviation"]} (updated)')
            else:
                # Insert new game
                games_to_insert.append(game_data)
                print(f'{i+1}. {away_team["team"]["abbreviation"]} @ {home_team["team"]["abbreviation"]} (new)')
        
        # Insert new games
        if games_to_insert:
            print(f'\n✅ Inserting {len(games_to_insert)} new games into database...')
            supabase.table('games').insert(games_to_insert).execute()
        
        print('\n' + '=' * 60)
        print('✅ SUCCESS! NBA GAMES UPDATED FROM ESPN')
        print('=' * 60)
        print(f'📅 Games processed: {len(events)}')
        print('\n📋 GAMES:')
        for event in events:
            competition = event['competitions'][0]
            home = competition['competitors'][0]['team']['abbreviation']
            away = competition['competitors'][1]['team']['abbreviation']
            print(f'  • {away} @ {home}')
        print('=' * 60)
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__': 
    get_todays_real_games()
