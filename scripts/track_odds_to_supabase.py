#!/usr/bin/env python3
"""
Track sportsbook odds history directly to Supabase
Run this script hourly to capture odds snapshots for line movement analysis
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

# The Odds API configuration
ODDS_API_KEY = os.getenv('ODDS_API_KEY', 'dd30c0f0f1f494e7c0a5cef66366da2b')
BASE_URL = "https://api.the-odds-api.com/v4"

# Stat type mapping from The Odds API to our database
ODDS_API_STAT_MAP = {
    'player_points': 'Points',
    'player_rebounds': 'Rebounds',
    'player_assists': 'Assists',
    'player_threes': '3-PT Made',
    'player_blocks': 'Blocked Shots',
    'player_steals': 'Steals',
    'player_turnovers': 'Turnovers',
    'player_points_rebounds_assists': 'Pts+Rebs+Asts',
    'player_points_rebounds': 'Pts+Rebs',
    'player_points_assists': 'Pts+Asts',
    'player_rebounds_assists': 'Rebs+Asts',
    'player_blocks_steals': 'Blks+Stls'
}

def get_nba_games():
    """Fetch upcoming NBA games from The Odds API"""
    try:
        url = f"{BASE_URL}/sports/basketball_nba/events"
        params = {
            'apiKey': ODDS_API_KEY,
            'dateFormat': 'iso'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        games = response.json()
        return games
        
    except Exception as e:
        print(f"❌ Error fetching games: {e}")
        return []

def get_player_prop_odds(game_id):
    """Fetch player prop odds for a specific game"""
    try:
        bookmakers = 'draftkings,fanduel'
        
        markets = ','.join([
            'player_points',
            'player_rebounds', 
            'player_assists',
            'player_threes',
            'player_blocks',
            'player_steals',
            'player_turnovers',
            'player_points_rebounds_assists',
            'player_points_rebounds',
            'player_points_assists',
            'player_rebounds_assists',
            'player_blocks_steals',
        ])
        
        url = f"{BASE_URL}/sports/basketball_nba/events/{game_id}/odds"
        params = {
            'apiKey': ODDS_API_KEY,
            'regions': 'us',
            'markets': markets,
            'oddsFormat': 'american',
            'bookmakers': bookmakers
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except Exception as e:
        print(f"⚠️  Error fetching odds for game {game_id}: {e}")
        return None

def store_odds_to_supabase(odds_data):
    """Store odds snapshot directly in Supabase odds_history table"""
    if not odds_data or 'bookmakers' not in odds_data:
        return 0
    
    count = 0
    records_to_insert = []
    
    # Organize odds by player and stat
    player_odds = {}
    
    for bookmaker in odds_data.get('bookmakers', []):
        sportsbook_name = bookmaker.get('title', '').lower()
        
        for market in bookmaker.get('markets', []):
            market_key = market.get('key')
            stat_type = ODDS_API_STAT_MAP.get(market_key)
            
            if not stat_type:
                continue
            
            for outcome in market.get('outcomes', []):
                player_name = outcome.get('description')
                line = outcome.get('point')
                
                if outcome.get('name') == 'Over':
                    over_price = outcome.get('price')
                    
                    # Find corresponding under
                    under_price = None
                    for other in market.get('outcomes', []):
                        if (other.get('description') == player_name and 
                            other.get('name') == 'Under' and 
                            other.get('point') == line):
                            under_price = other.get('price')
                            break
                    
                    if over_price and under_price and line:
                        key = (player_name, stat_type)
                        
                        if key not in player_odds:
                            player_odds[key] = {
                                'player_name': player_name,
                                'stat_type': stat_type,
                                'draftkings_line': None,
                                'draftkings_over_odds': None,
                                'draftkings_under_odds': None,
                                'fanduel_line': None,
                                'fanduel_over_odds': None,
                                'fanduel_under_odds': None,
                                'recorded_at': datetime.now(timezone.utc).isoformat()
                            }
                        
                        if 'draftkings' in sportsbook_name:
                            player_odds[key]['draftkings_line'] = float(line)
                            player_odds[key]['draftkings_over_odds'] = int(over_price)
                            player_odds[key]['draftkings_under_odds'] = int(under_price)
                        elif 'fanduel' in sportsbook_name:
                            player_odds[key]['fanduel_line'] = float(line)
                            player_odds[key]['fanduel_over_odds'] = int(over_price)
                            player_odds[key]['fanduel_under_odds'] = int(under_price)
    
    # Prepare records for batch insert
    for odds_record in player_odds.values():
        records_to_insert.append(odds_record)
    
    # Insert records into Supabase in batches
    if records_to_insert:
        try:
            # Supabase can handle large inserts, but we'll batch at 100 for safety
            batch_size = 100
            for i in range(0, len(records_to_insert), batch_size):
                batch = records_to_insert[i:i+batch_size]
                result = supabase.table('odds_history').insert(batch).execute()
                count += len(batch)
        except Exception as e:
            print(f"⚠️  Error inserting to Supabase: {e}")
            # Try individual inserts as fallback
            for record in records_to_insert:
                try:
                    supabase.table('odds_history').insert(record).execute()
                    count += 1
                except Exception as e2:
                    print(f"⚠️  Error storing odds for {record['player_name']}: {e2}")
    
    return count

def main():
    print('=' * 60)
    print('📈 TRACKING ODDS HISTORY TO SUPABASE')
    print(f'⏰ Snapshot time: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}')
    print('=' * 60)
    print()
    
    # Check API key
    if not ODDS_API_KEY or ODDS_API_KEY == 'your_odds_api_key_here':
        print('❌ Error: ODDS_API_KEY not set in environment')
        print('   Set it in your .env file or environment variables')
        return
    
    # Check Supabase connection
    try:
        supabase.table('odds_history').select('id').limit(1).execute()
        print('✅ Connected to Supabase')
    except Exception as e:
        print(f'❌ Error connecting to Supabase: {e}')
        return
    
    print()
    
    # Get upcoming games
    print('📅 Fetching upcoming NBA games...')
    games = get_nba_games()
    
    if not games:
        print('❌ No games found')
        return
    
    print(f'✅ Found {len(games)} upcoming games')
    print()
    
    # Fetch odds for each game
    print('💰 Fetching and storing current odds...')
    
    total_recorded = 0
    
    for i, game in enumerate(games[:10], 1):
        game_id = game.get('id')
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        
        print(f'  [{i}/{min(10, len(games))}] {away_team} @ {home_team}', end=' ')
        
        odds_data = get_player_prop_odds(game_id)
        
        if odds_data:
            count = store_odds_to_supabase(odds_data)
            total_recorded += count
            print(f'✅ {count} odds recorded to Supabase')
        else:
            print('⚠️  No odds')
    
    print()
    print('=' * 60)
    print('✅ ODDS HISTORY SNAPSHOT COMPLETE')
    print('=' * 60)
    print(f'📈 Total odds recorded to Supabase: {total_recorded}')
    print(f'☁️  Data now available on live website!')
    print()
    print('💡 Run this script hourly to build line movement history')
    print('   Use Task Scheduler (Windows) or cron (Linux/Mac) for automation')
    print()
    print('📊 The odds history charts on your website will now show this data!')

if __name__ == '__main__':
    main()
