import os
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict

load_dotenv()
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

# January 6th, 2026 NBA Games (Away @ Home)
# List of matchups as (away_name, away_abbr, home_name, home_abbr)
MATCHUPS_JAN_6 = [
    ('Cleveland Cavaliers', 'CLE', 'Indiana Pacers', 'IND'),
    ('Orlando Magic', 'ORL', 'Washington Wizards', 'WAS'),
    ('San Antonio Spurs', 'SAS', 'Memphis Grizzlies', 'MEM'),
    ('Miami Heat', 'MIA', 'Minnesota Timberwolves', 'MIN'),
    ('Los Angeles Lakers', 'LAL', 'New Orleans Pelicans', 'NOP'),
    ('Dallas Mavericks', 'DAL', 'Sacramento Kings', 'SAC'),
]

print('🏀 Updating to January 6th, 2026 NBA Games')
print('=' * 60)

# Get all existing props to find games with props
print('\n📊 Analyzing existing props...')
props = supabase.table('props').select('game_id, team').execute().data
print(f'✓ Found {len(props)} props')

# Group props by game_id and find which teams are in each game
game_teams = defaultdict(set)
for prop in props:
    game_id = prop.get('game_id')
    team = prop.get('team')
    if game_id and team:
        game_teams[game_id].add(team)

print(f'\n🎮 Found {len(game_teams)} existing games with props')

# Get existing games
print('\n📥 Fetching existing games...')
games_result = supabase.table('games').select('*').execute()
existing_games = {g['id']: g for g in games_result.data}
print(f'✓ Found {len(existing_games)} games in database')

# Update existing games that have props
print('\n🔄 Updating existing games with props...')
updated_existing = 0
used_matchups = set()

for game_id, teams in game_teams.items():
    teams_list = list(teams)
    
    if len(teams_list) >= 1:
        team_abbr = teams_list[0]
        
        # Find matching matchup
        for away_name, away_abbr, home_name, home_abbr in MATCHUPS_JAN_6:
            if away_abbr == team_abbr or home_abbr == team_abbr:
                # Update the game
                supabase.table('games').update({
                    'home_team': home_name,
                    'home_team_abbr': home_abbr,
                    'away_team': away_name,
                    'away_team_abbr': away_abbr,
                    'game_time': '2026-01-06T19:00:00-05:00',
                }).eq('id', game_id).execute()
                
                print(f'  ✓ Updated: {away_abbr} @ {home_abbr} - {away_name} at {home_name}')
                updated_existing += 1
                used_matchups.add((away_abbr, home_abbr))
                break

# Create any missing games
print('\n➕ Creating missing games...')
created_new = 0

for away_name, away_abbr, home_name, home_abbr in MATCHUPS_JAN_6:
    if (away_abbr, home_abbr) not in used_matchups:
        # Create new game
        result = supabase.table('games').insert({
            'home_team': home_name,
            'home_team_abbr': home_abbr,
            'away_team': away_name,
            'away_team_abbr': away_abbr,
            'game_time': '2026-01-06T19:00:00-05:00',
            'status': 1
        }).execute()
        
        print(f'  ✓ Created: {away_abbr} @ {home_abbr} - {away_name} at {home_name}')
        created_new += 1

print(f'\n✅ Updated {updated_existing} existing games')
print(f'✅ Created {created_new} new games')
print(f'✅ Total: {updated_existing + created_new} games for January 6th')

# Verify
print('\n🔍 Verification:')
games_check = supabase.table('games').select('*').execute()
print(f'Total games in database: {len(games_check.data)}')
print('\nAll January 6th games:')
for g in games_check.data:
    if '2026-01-06' in g.get('game_time', ''):
        away = g.get('away_team_abbr', '???')
        home = g.get('home_team_abbr', '???')
        print(f"  {away} @ {home} - {g.get('away_team', 'N/A')} at {g.get('home_team', 'N/A')}")

# Check props are still there
props_check = supabase.table('props').select('id').execute()
print(f'\n✅ Props still in database: {len(props_check.data)}')
print('=' * 60)
print('\n💡 Now run the projections script to see correct matchups!')
print('   python scripts\\update_projections_with_defense.py')
