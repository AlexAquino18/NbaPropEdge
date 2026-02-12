#!/usr/bin/env python3
"""
Fetch NBA player prop odds from The Odds API
Store odds in LOCAL SQLite database - NO SUPABASE NEEDED!
"""

import os
import sys
from datetime import datetime, timezone
import requests
import json
import sqlite3

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# The Odds API configuration
ODDS_API_KEY = os.getenv('ODDS_API_KEY', 'dd30c0f0f1f494e7c0a5cef66366da2b')
BASE_URL = "https://api.the-odds-api.com/v4"

# SQLite database file - stored locally, no cloud needed!
DB_FILE = 'odds_history.db'

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

def setup_database():
    """Create SQLite database and table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create odds_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS odds_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            stat_type TEXT NOT NULL,
            game_id TEXT,
            sportsbook TEXT NOT NULL,
            line REAL NOT NULL,
            over_odds INTEGER NOT NULL,
            under_odds INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_player_stat 
        ON odds_history(player_name, stat_type)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_recorded 
        ON odds_history(recorded_at DESC)
    ''')
    
    conn.commit()
    conn.close()
    print('✅ Local SQLite database ready!')

def save_odds_to_db(player_name, stat_type, sportsbook, line, over_odds, under_odds, game_id=None):
    """Save odds to SQLite database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO odds_history 
            (player_name, stat_type, sportsbook, line, over_odds, under_odds, recorded_at, game_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_name,
            stat_type,
            sportsbook,
            float(line),
            int(over_odds),
            int(under_odds),
            datetime.now(timezone.utc).isoformat(),
            game_id
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f'⚠️  Error saving to DB: {e}')
        return False

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
        print(f"✅ Found {len(games)} upcoming NBA games")
        return games
        
    except Exception as e:
        print(f"❌ Error fetching games: {e}")
        return []

def get_player_prop_odds(game_id):
    """Fetch player prop odds for a specific game"""
    try:
        bookmakers = 'draftkings,fanduel'
        
        # Request ALL available player prop markets including combos
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
            'player_double_double',
            'player_triple_double',
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

sportsbook_odds_cache = {}

def store_odds(odds_data, game_id=None):
    """Parse odds data and store in memory cache AND database"""
    if not odds_data or 'bookmakers' not in odds_data:
        return 0, 0
    
    count = 0
    saved_count = 0
    
    for bookmaker in odds_data.get('bookmakers', []):
        sportsbook_name = bookmaker.get('title', '')
        
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
                        
                        if key not in sportsbook_odds_cache:
                            sportsbook_odds_cache[key] = {}
                        
                        sportsbook_odds_cache[key][sportsbook_name] = {
                            'line': float(line),
                            'over': int(over_price),
                            'under': int(under_price)
                        }
                        count += 1
                        
                        # Save to local SQLite database
                        if save_odds_to_db(player_name, stat_type, sportsbook_name, 
                                          line, over_price, under_price, game_id):
                            saved_count += 1
    
    return count, saved_count

def main():
    print('=' * 60)
    print('🎰 FETCHING SPORTSBOOK ODDS (LOCAL SQLITE)')
    print('=' * 60)
    print()
    
    # Check API key
    if not ODDS_API_KEY or ODDS_API_KEY == 'your_odds_api_key_here':
        print('❌ Error: ODDS_API_KEY not set in .env file')
        print('   Get a free API key at: https://the-odds-api.com/')
        return
    
    print(f'🔑 Using API Key: {ODDS_API_KEY[:8]}...{ODDS_API_KEY[-4:]}')
    print()
    
    # Setup local database
    print('🗄️  Setting up local SQLite database...')
    setup_database()
    print(f'📁 Database file: {DB_FILE}')
    print()
    
    # Step 1: Get upcoming games
    print('📅 Step 1: Fetching upcoming NBA games...')
    games = get_nba_games()
    
    if not games:
        print('❌ No games found')
        return
    
    print()
    
    # Step 2: Fetch odds for each game
    print('💰 Step 2: Fetching DraftKings & FanDuel odds...')
    print('   (Storing in local database for line movement tracking)')
    
    total_odds = 0
    total_saved = 0
    
    for i, game in enumerate(games[:10], 1):
        game_id = game.get('id')
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        
        print(f'\n  [{i}/{min(10, len(games))}] {away_team} @ {home_team}')
        
        odds_data = get_player_prop_odds(game_id)
        
        if odds_data:
            count, saved = store_odds(odds_data, game_id)
            total_odds += count
            total_saved += saved
            if count > 0:
                print(f'      ✅ {count} odds ({saved} saved to local DB)')
            else:
                print(f'      ⚠️  No odds available')
        else:
            print(f'      ⚠️  No odds available')
    
    print()
    print('=' * 60)
    print('✅ SPORTSBOOK ODDS FETCH COMPLETE')
    print('=' * 60)
    print(f'📊 Total odds fetched: {total_odds}')
    print(f'💾 Total odds saved to local database: {total_saved}')
    print()
    
    # Show database stats
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM odds_history')
    total_records = cursor.fetchone()[0]
    conn.close()
    
    print(f'🗄️  Database stats:')
    print(f'   Total historical records: {total_records}')
    print(f'   Database file: {DB_FILE}')
    print()
    
    # Display sample odds
    if sportsbook_odds_cache:
        print('📋 Sample Sportsbook Odds:')
        print('-' * 60)
        for (player, stat), books in list(sportsbook_odds_cache.items())[:10]:
            print(f'\n{player} - {stat}:')
            for book, odds in books.items():
                print(f'  {book}: {odds["line"]} (O: {odds["over"]:+d} / U: {odds["under"]:+d})')
        
        if len(sportsbook_odds_cache) > 10:
            print(f'\n... and {len(sportsbook_odds_cache) - 10} more player props')
        
        print()
        print('=' * 60)
        print('💡 SUCCESS! LINE MOVEMENT TRACKING IS NOW ACTIVE!')
        print('=' * 60)
        print(f'📈 Run this script hourly to track line movements')
        print(f'🗄️  All data stored locally in: {DB_FILE}')
        print(f'📊 No cloud, no Supabase, just pure local tracking!')
        print('=' * 60)
    
    # Save to JSON for compatibility
    output_file = 'sportsbook_odds_cache.json'
    with open(output_file, 'w') as f:
        json_cache = {}
        for (player, stat), books in sportsbook_odds_cache.items():
            key = f"{player}|{stat}"
            json_cache[key] = books
        json.dump(json_cache, f, indent=2)
    
    print()
    print(f'💾 Odds also saved to: {output_file}')

if __name__ == '__main__':
    main()
