import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

# Mapping from incorrect team abbreviations to correct ones
TEAM_FIX_MAP = {
    'MAG': 'ORL',  # Magic -> Orlando
    'WIZ': 'WAS',  # Wizards -> Washington
    'CAV': 'CLE',  # Cavaliers -> Cleveland
    'WAR': 'GSW',  # Warriors -> Golden State
    'LAK': 'LAL',  # Lakers -> Los Angeles Lakers
    'CLI': 'LAC',  # Clippers -> Los Angeles Clippers
    'THU': 'OKC',  # Thunder -> Oklahoma City
    'HEA': 'MIA',  # Heat -> Miami
    'BUL': 'CHI',  # Bulls -> Chicago
    'HAW': 'ATL',  # Hawks -> Atlanta
    'CEL': 'BOS',  # Celtics -> Boston
    'NET': 'BKN',  # Nets -> Brooklyn
    'HOR': 'CHA',  # Hornets -> Charlotte
    'NUG': 'DEN',  # Nuggets -> Denver
    'PIS': 'DET',  # Pistons -> Detroit
    'ROC': 'HOU',  # Rockets -> Houston
    'PAC': 'IND',  # Pacers -> Indiana
    'GRI': 'MEM',  # Grizzlies -> Memphis
    'BUC': 'MIL',  # Bucks -> Milwaukee
    'TIM': 'MIN',  # Timberwolves -> Minnesota
    'PEL': 'NOP',  # Pelicans -> New Orleans
    'KNI': 'NYK',  # Knicks -> New York
    'SUN': 'PHX',  # Suns -> Phoenix
    '76E': 'PHI',  # 76ers -> Philadelphia
    'TRA': 'POR',  # Trail Blazers -> Portland
    'KIN': 'SAC',  # Kings -> Sacramento
    'SPU': 'SAS',  # Spurs -> San Antonio
    'RAP': 'TOR',  # Raptors -> Toronto
    'JAZ': 'UTA',  # Jazz -> Utah
}

def main():
    print('🔧 FIXING TEAM ABBREVIATIONS')
    print('=' * 60)
    
    # Fix props table
    print('📥 Fetching props...')
    props_response = supabase.table('props').select('*').execute()
    props = props_response.data
    print(f'✓ Found {len(props)} props\n')
    
    fixed_props = 0
    unchanged_props = 0
    
    for prop in props:
        prop_id = prop['id']
        current_team = prop.get('team', '')
        
        if not current_team:
            unchanged_props += 1
            continue
        
        # Check if this team needs fixing
        if current_team in TEAM_FIX_MAP:
            correct_team = TEAM_FIX_MAP[current_team]
            
            # Update the database
            supabase.table('props').update({
                'team': correct_team
            }).eq('id', prop_id).execute()
            
            print(f'✅ Fixed prop: {prop["player_name"]} - {current_team} → {correct_team}')
            fixed_props += 1
        else:
            unchanged_props += 1
    
    # Fix games table
    print(f'\n📥 Fetching games...')
    games_response = supabase.table('games').select('*').execute()
    games = games_response.data
    print(f'✓ Found {len(games)} games\n')
    
    fixed_games = 0
    unchanged_games = 0
    
    for game in games:
        game_id = game['id']
        home_team = game.get('home_team_abbr', '')
        away_team = game.get('away_team_abbr', '')
        
        needs_update = False
        updates = {}
        
        # Check home team
        if home_team in TEAM_FIX_MAP:
            correct_home = TEAM_FIX_MAP[home_team]
            updates['home_team_abbr'] = correct_home
            needs_update = True
            print(f'✅ Fixed game home: {home_team} → {correct_home}')
        
        # Check away team
        if away_team in TEAM_FIX_MAP:
            correct_away = TEAM_FIX_MAP[away_team]
            updates['away_team_abbr'] = correct_away
            needs_update = True
            print(f'✅ Fixed game away: {away_team} → {correct_away}')
        
        if needs_update:
            supabase.table('games').update(updates).eq('id', game_id).execute()
            fixed_games += 1
        else:
            unchanged_games += 1
    
    print()
    print('=' * 60)
    print('✅ FIX COMPLETE')
    print('=' * 60)
    print(f'✅ Fixed props: {fixed_props}')
    print(f'⏭️  Unchanged props: {unchanged_props}')
    print(f'✅ Fixed games: {fixed_games}')
    print(f'⏭️  Unchanged games: {unchanged_games}')
    print('=' * 60)
    print()
    print('💡 Now run the projections script to see correct matchups!')

if __name__ == '__main__':
    main()
