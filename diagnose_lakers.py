import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta, timezone

load_dotenv()
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('🔍 DIAGNOSING LAKERS PROPS ISSUE')
print('=' * 60)

# Check Lakers props
print('\n1️⃣ Checking Lakers props in database...')
lakers_props = supabase.table('props').select('*').or_('team.eq.LAL,team.eq.LAK,team.eq.Lakers').limit(10).execute()
print(f'   Found {len(lakers_props.data)} Lakers props')
if lakers_props.data:
    for prop in lakers_props.data[:3]:
        print(f'   - {prop["player_name"]}: {prop["stat_type"]} {prop["line"]} (team={prop.get("team")}, game_id={prop.get("game_id")})')

# Check all teams in props
print('\n2️⃣ Checking all unique team abbreviations in props...')
all_props = supabase.table('props').select('team').limit(1000).execute()
teams = set(p.get('team') for p in all_props.data if p.get('team'))
print(f'   Unique teams: {sorted(teams)}')

# Check games for today
print('\n3️⃣ Checking games scheduled for today...')
now = datetime.now(timezone.utc)
start = now.replace(hour=0, minute=0, second=0, microsecond=0)
end = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)

games = supabase.table('games').select('*').gte('game_time', start.isoformat()).lte('game_time', end.isoformat()).execute()
print(f'   Found {len(games.data)} games today')
for game in games.data:
    print(f'   - {game.get("away_team_abbr")} @ {game.get("home_team_abbr")} ({game.get("game_time")})')

# Check Lakers games specifically
print('\n4️⃣ Checking Lakers games (any time)...')
lakers_games = supabase.table('games').select('*').or_('home_team_abbr.eq.LAL,away_team_abbr.eq.LAL,home_team_abbr.eq.LAK,away_team_abbr.eq.LAK').order('game_time', desc=True).limit(5).execute()
print(f'   Found {len(lakers_games.data)} Lakers games (recent)')
for game in lakers_games.data:
    print(f'   - {game.get("away_team_abbr")} @ {game.get("home_team_abbr")} ({game.get("game_time")})')

# Check props with OPP/UNK
print('\n5️⃣ Checking props with "OPP" opponent...')
all_props_full = supabase.table('props').select('player_name, team, game_id, stat_type, line').limit(500).execute()
opp_count = 0
unk_count = 0
for prop in all_props_full.data:
    team = prop.get('team')
    if team == 'OPP':
        opp_count += 1
        if opp_count <= 3:
            print(f'   - {prop["player_name"]} (team=OPP, game_id={prop.get("game_id")})')
    elif team == 'UNK':
        unk_count += 1

print(f'   Total with OPP: {opp_count}')
print(f'   Total with UNK: {unk_count}')

print('\n' + '=' * 60)
print('✅ DIAGNOSIS COMPLETE')
print('=' * 60)
