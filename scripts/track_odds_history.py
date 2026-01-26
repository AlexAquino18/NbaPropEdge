#!/usr/bin/env python3
"""
Track sportsbook odds history for line movement analysis
Run this script hourly to capture odds snapshots
Uses SQLite for local storage
"""

import os
import sys
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import requests

# The Odds API configuration
ODDS_API_KEY = os.getenv('ODDS_API_KEY', 'dd6fe3cb5fd32a3bb870c11d1abb22bd')
BASE_URL = "https://api.the-odds-api.com/v4"

# SQLite database path
DB_PATH = Path(__file__).parent.parent / 'odds_history.db'

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

def init_database():
    """Initialize SQLite database with odds_history table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS odds_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            stat_type TEXT NOT NULL,
            draftkings_line REAL,
            draftkings_over_odds INTEGER,
            draftkings_under_odds INTEGER,
            fanduel_line REAL,
            fanduel_over_odds INTEGER,
            fanduel_under_odds INTEGER,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_name, stat_type, recorded_at)
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_player_stat 
        ON odds_history(player_name, stat_type, recorded_at DESC)
    ''')
    
    conn.commit()
    conn.close()
    print('✅ Database initialized')

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

def get_existing_props():
    """Get current props from SQLite to track"""
    # For SQLite version, we'll track all odds we find
    # No need to link to props table
    return {}

def store_odds_history(odds_data, props_map):
    """Store odds snapshot in SQLite odds_history table"""
    if not odds_data or 'bookmakers' not in odds_data:
        return 0
    
    count = 0
    
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
                                'fanduel_under_odds': None
                            }
                        
                        if 'draftkings' in sportsbook_name:
                            player_odds[key]['draftkings_line'] = float(line)
                            player_odds[key]['draftkings_over_odds'] = int(over_price)
                            player_odds[key]['draftkings_under_odds'] = int(under_price)
                        elif 'fanduel' in sportsbook_name:
                            player_odds[key]['fanduel_line'] = float(line)
                            player_odds[key]['fanduel_over_odds'] = int(over_price)
                            player_odds[key]['fanduel_under_odds'] = int(under_price)
    
    # Insert records into SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for odds_record in player_odds.values():
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO odds_history 
                (player_name, stat_type, draftkings_line, draftkings_over_odds, 
                 draftkings_under_odds, fanduel_line, fanduel_over_odds, fanduel_under_odds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                odds_record['player_name'],
                odds_record['stat_type'],
                odds_record['draftkings_line'],
                odds_record['draftkings_over_odds'],
                odds_record['draftkings_under_odds'],
                odds_record['fanduel_line'],
                odds_record['fanduel_over_odds'],
                odds_record['fanduel_under_odds']
            ))
            count += 1
        except Exception as e:
            print(f"⚠️  Error storing odds for {odds_record['player_name']}: {e}")
    
    conn.commit()
    conn.close()
    
    return count

def main():
    print('=' * 60)
    print('📈 TRACKING ODDS HISTORY (SQLite)')
    print(f'⏰ Snapshot time: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}')
    print(f'💾 Database: {DB_PATH}')
    print('=' * 60)
    print()
    
    # Initialize database
    init_database()
    print()
    
    # Check API key
    if not ODDS_API_KEY or ODDS_API_KEY == 'your_odds_api_key_here':
        print('❌ Error: ODDS_API_KEY not set in environment')
        return
    
    # Get existing props for linking
    print('📊 Preparing to track odds...')
    props_map = get_existing_props()
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
    print('💰 Fetching current odds...')
    
    total_recorded = 0
    
    for i, game in enumerate(games[:10], 1):
        game_id = game.get('id')
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        
        print(f'  [{i}/{min(10, len(games))}] {away_team} @ {home_team}', end=' ')
        
        odds_data = get_player_prop_odds(game_id)
        
        if odds_data:
            count = store_odds_history(odds_data, props_map)
            total_recorded += count
            print(f'✅ {count} odds recorded')
        else:
            print('⚠️  No odds')
    
    print()
    print('=' * 60)
    print('✅ ODDS HISTORY SNAPSHOT COMPLETE')
    print('=' * 60)
    print(f'📈 Total odds recorded: {total_recorded}')
    print(f'💾 Stored in: {DB_PATH}')
    print()
    print('💡 Run this script hourly to build line movement history')
    print('   Use Task Scheduler (Windows) or cron (Linux/Mac) for automation')

if __name__ == '__main__':
    main()
