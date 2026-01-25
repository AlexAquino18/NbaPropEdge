#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

print('Checking props with DraftKings odds...')
result = supabase.table('props').select('player_name, stat_type, draftkings_line, fanduel_line').not_.is_('draftkings_line', None).limit(10).execute()

print(f'\nFound {len(result.data)} props with DraftKings odds:')
for r in result.data[:10]:
    print(f"  {r['player_name']} - {r['stat_type']}: DK={r['draftkings_line']}, FD={r.get('fanduel_line')}")

print('\nChecking props with FanDuel odds...')
result2 = supabase.table('props').select('player_name, stat_type, draftkings_line, fanduel_line').not_.is_('fanduel_line', None).limit(10).execute()

print(f'\nFound {len(result2.data)} props with FanDuel odds:')
for r in result2.data[:10]:
    print(f"  {r['player_name']} - {r['stat_type']}: DK={r.get('draftkings_line')}, FD={r['fanduel_line']}")

print('\n---')
print('Total props in database:')
total = supabase.table('props').select('id', count='exact').execute()
print(f'  Total: {total.count}')

with_dk = supabase.table('props').select('id', count='exact').not_.is_('draftkings_line', None).execute()
print(f'  With DraftKings odds: {with_dk.count}')

with_fd = supabase.table('props').select('id', count='exact').not_.is_('fanduel_line', None).execute()
print(f'  With FanDuel odds: {with_fd.count}')
