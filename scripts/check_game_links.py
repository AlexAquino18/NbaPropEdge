import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('CHECKING DATABASE STATUS')
print('=' * 60)

# Get all games
games_response = supabase.table('games').select('*').execute()
games = games_response.data

print(f'\nGAMES IN DATABASE ({len(games)} total):')
print('-' * 60)
for game in games:
    print(f'{game["away_team_abbr"]} @ {game["home_team_abbr"]} (ID: {game["id"]})')

# Get unique teams in props
props_response = supabase.table('props').select('team, game_id').execute()
props = props_response.data

unique_teams = set(p['team'] for p in props if p.get('team'))
print(f'\n\nUNIQUE TEAMS IN PROPS ({len(unique_teams)} teams):')
print('-' * 60)
print(', '.join(sorted(unique_teams)))

# Count props per team
from collections import Counter
team_counts = Counter(p['team'] for p in props if p.get('team'))
print(f'\n\nPROPS PER TEAM:')
print('-' * 60)
for team, count in sorted(team_counts.items()):
    print(f'{team}: {count} props')

# Check which teams are in games but not in props
game_teams = set()
for game in games:
    if game['home_team_abbr'] != 'TBD':
        game_teams.add(game['home_team_abbr'])
    if game['away_team_abbr'] != 'TBD':
        game_teams.add(game['away_team_abbr'])

teams_with_games = unique_teams & game_teams
teams_without_games = unique_teams - game_teams

print(f'\n\nTEAMS WITH GAMES TODAY: {len(teams_with_games)}')
print('-' * 60)
print(', '.join(sorted(teams_with_games)))

print(f'\n\nTEAMS WITHOUT GAMES TODAY: {len(teams_without_games)}')
print('-' * 60)
print(', '.join(sorted(teams_without_games)))

print('\n' + '=' * 60)
