#!/usr/bin/env python3
"""
Load sportsbook odds from JSON cache and update props in database
This allows viewing odds without needing database schema changes
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('=' * 60)
print('📥 LOADING SPORTSBOOK ODDS FROM CACHE')
print('=' * 60)
print()

# Load the JSON cache
try:
    with open('sportsbook_odds_cache.json', 'r') as f:
        odds_cache = json.load(f)
    print(f'✅ Loaded {len(odds_cache)} player props from cache')
except FileNotFoundError:
    print('❌ sportsbook_odds_cache.json not found!')
    print('   Run: python scripts\\fetch_sportsbook_odds.py')
    exit(1)

print()

# Get all props from database
print('📊 Fetching props from database...')
response = supabase.table('props').select('*').execute()
props = response.data

print(f'✅ Found {len(props)} props in database')
print()

# Try to update props with odds
print('🔄 Matching props with sportsbook odds...')
print()

updated_count = 0
matched_props = []

for prop in props:
    player_name = prop['player_name']
    stat_type = prop['stat_type']
    
    # Create the key to look up in cache
    cache_key = f"{player_name}|{stat_type}"
    
    if cache_key in odds_cache:
        odds = odds_cache[cache_key]
        
        # Prepare update data
        update_data = {'id': prop['id']}
        
        # Add DraftKings odds if available
        if 'DraftKings' in odds:
            dk = odds['DraftKings']
            update_data['draftkings_line'] = dk['line']
            update_data['draftkings_over_odds'] = dk['over']
            update_data['draftkings_under_odds'] = dk['under']
        
        # Add FanDuel odds if available
        if 'FanDuel' in odds:
            fd = odds['FanDuel']
            update_data['fanduel_line'] = fd['line']
            update_data['fanduel_over_odds'] = fd['over']
            update_data['fanduel_under_odds'] = fd['under']
        
        matched_props.append({
            'player': player_name,
            'stat': stat_type,
            'update': update_data
        })

print(f'✅ Matched {len(matched_props)} props with sportsbook odds')
print()

if matched_props:
    print('📝 Sample matches:')
    for match in matched_props[:5]:
        print(f"   • {match['player']} - {match['stat']}")
    print()
    
    # Try to update the database
    print('💾 Attempting to update database...')
    
    try:
        # Try updating one prop first to test if columns exist
        test_update = matched_props[0]['update']
        result = supabase.table('props').update(test_update).eq('id', test_update['id']).execute()
        
        print('✅ Database columns exist! Updating all props...')
        print()
        
        # Update all props
        for i, match in enumerate(matched_props, 1):
            try:
                supabase.table('props').update(match['update']).eq('id', match['update']['id']).execute()
                updated_count += 1
                if i % 50 == 0:
                    print(f'   Updated {i}/{len(matched_props)} props...')
            except Exception as e:
                print(f"   ⚠️  Error updating {match['player']}: {e}")
        
        print()
        print('=' * 60)
        print('✅ SPORTSBOOK ODDS UPDATE COMPLETE')
        print('=' * 60)
        print(f'📊 Successfully updated {updated_count} props with sportsbook odds')
        print()
        print('🎉 Refresh your app to see DraftKings and FanDuel odds!')
        print('=' * 60)
        
    except Exception as e:
        error_msg = str(e)
        
        if 'column' in error_msg.lower() and ('does not exist' in error_msg.lower() or 'not found' in error_msg.lower()):
            print('❌ Database columns do not exist yet.')
            print()
            print('📋 The database owner needs to run this SQL:')
            print('-' * 60)
            print('ALTER TABLE public.props')
            print('ADD COLUMN IF NOT EXISTS draftkings_line DECIMAL(10, 2),')
            print('ADD COLUMN IF NOT EXISTS draftkings_over_odds INTEGER,')
            print('ADD COLUMN IF NOT EXISTS draftkings_under_odds INTEGER,')
            print('ADD COLUMN IF NOT EXISTS fanduel_line DECIMAL(10, 2),')
            print('ADD COLUMN IF NOT EXISTS fanduel_over_odds INTEGER,')
            print('ADD COLUMN IF NOT EXISTS fanduel_under_odds INTEGER;')
            print('-' * 60)
            print()
            print('💡 Alternatively, the sportsbook odds are stored in the JSON file')
            print('   and will be displayed once the columns are added.')
        else:
            print(f'❌ Error: {e}')
else:
    print('⚠️  No matching props found.')
    print('   The player names or stat types in your cache may not match')
    print('   the props in your database.')
