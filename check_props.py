#!/usr/bin/env python3
"""Check props in database and diagnose matching issues"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('🔍 Checking props in database...\n')

# Get total count
result = supabase.table('props').select('player_name,stat_type', count='exact').limit(10).execute()
total = result.count if hasattr(result, 'count') else len(result.data)

print(f'📊 Total props in database: {total}\n')

if result.data:
    print('Sample props (first 10):')
    for i, prop in enumerate(result.data[:10], 1):
        print(f'  {i}. {prop["player_name"]}: {prop["stat_type"]}')
    
    print('\n' + '=' * 60)
    print('🎯 Testing match with sportsbook players...')
    print('=' * 60)
    
    # Test some common players from today's games
    test_players = [
        'LaMelo Ball',
        'Joel Embiid', 
        'Stephen Curry',
        'Anthony Edwards',
        'Jaylen Brown',
        'Nikola Vucevic'
    ]
    
    for player in test_players:
        result = supabase.table('props').select('player_name,stat_type').eq('player_name', player).execute()
        if result.data:
            print(f'✅ {player}: Found {len(result.data)} props')
        else:
            print(f'❌ {player}: Not found in database')
else:
    print('❌ No props found in database!')
    print('   Run your data refresh script first to fetch props.')
