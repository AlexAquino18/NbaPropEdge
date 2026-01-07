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
    'SUN': 'PHO',  # Suns -> Phoenix
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
    
    # Get all props
    print('📥 Fetching props...')
    props_response = supabase.table('props').select('*').execute()
    props = props_response.data
    print(f'✓ Found {len(props)} props\n')
    
    fixed_count = 0
    unchanged_count = 0
    
    for prop in props:
        prop_id = prop['id']
        current_team = prop.get('team', '')
        
        if not current_team:
            unchanged_count += 1
            continue
        
        # Check if this team needs fixing
        if current_team in TEAM_FIX_MAP:
            correct_team = TEAM_FIX_MAP[current_team]
            
            # Update the database
            supabase.table('props').update({
                'team': correct_team
            }).eq('id', prop_id).execute()
            
            print(f'✅ Fixed: {prop["player_name"]} - {current_team} → {correct_team}')
            fixed_count += 1
        else:
            unchanged_count += 1
    
    print()
    print('=' * 60)
    print('✅ FIX COMPLETE')
    print('=' * 60)
    print(f'✅ Fixed: {fixed_count} props')
    print(f'⏭️  Unchanged: {unchanged_count} props')
    print('=' * 60)
    print()
    print('💡 Now run the projections script to see correct matchups!')

if __name__ == '__main__':
    main()
