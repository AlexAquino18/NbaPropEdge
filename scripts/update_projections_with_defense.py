import os
import time
from dotenv import load_dotenv
from supabase import create_client
import numpy as np
from scipy import stats as scipy_stats
import subprocess
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# NBA Team Pace and Advanced Stats (2024-25 Season)
NBA_TEAM_STATS = {
    'MIA': {'pace': 104.71, 'off_rtg': 114.9, 'def_rtg': 111.9, 'net_rtg': 3.0, 'efg': 54.3, 'ts': 58.0, 'ast_pct': 65.2, 'tov_pct': 13.4, 'oreb_pct': 28.9, 'dreb_pct': 69.4, 'pie': 52.1, 'poss': 3577},
    'CHI': {'pace': 103.57, 'off_rtg': 113.8, 'def_rtg': 117.3, 'net_rtg': -3.5, 'efg': 55.2, 'ts': 58.7, 'ast_pct': 68.3, 'tov_pct': 14.2, 'oreb_pct': 28.4, 'dreb_pct': 71.5, 'pie': 49.4, 'poss': 3549},
    'ATL': {'pace': 103.11, 'off_rtg': 114.8, 'def_rtg': 115.2, 'net_rtg': -0.4, 'efg': 56.2, 'ts': 59.3, 'ast_pct': 71.4, 'tov_pct': 14.6, 'oreb_pct': 27.5, 'dreb_pct': 67.9, 'pie': 50.1, 'poss': 3732},
    'UTA': {'pace': 102.83, 'off_rtg': 114.7, 'def_rtg': 121.4, 'net_rtg': -6.7, 'efg': 53.7, 'ts': 58.3, 'ast_pct': 72.0, 'tov_pct': 15.2, 'oreb_pct': 31.1, 'dreb_pct': 69.9, 'pie': 46.9, 'poss': 3447},
    'POR': {'pace': 102.43, 'off_rtg': 112.9, 'def_rtg': 116.4, 'net_rtg': -3.4, 'efg': 52.3, 'ts': 56.5, 'ast_pct': 60.9, 'tov_pct': 16.7, 'oreb_pct': 35.7, 'dreb_pct': 67.6, 'pie': 46.7, 'poss': 3606},
    'DAL': {'pace': 102.31, 'off_rtg': 109.5, 'def_rtg': 113.4, 'net_rtg': -3.9, 'efg': 52.8, 'ts': 56.5, 'ast_pct': 60.2, 'tov_pct': 14.8, 'oreb_pct': 27.5, 'dreb_pct': 69.0, 'pie': 48.5, 'poss': 3631},
    'CLE': {'pace': 102.13, 'off_rtg': 116.3, 'def_rtg': 113.7, 'net_rtg': 2.6, 'efg': 54.6, 'ts': 58.0, 'ast_pct': 64.6, 'tov_pct': 13.7, 'oreb_pct': 30.5, 'dreb_pct': 68.6, 'pie': 50.9, 'poss': 3696},
    'WAS': {'pace': 101.93, 'off_rtg': 110.4, 'def_rtg': 120.9, 'net_rtg': -10.5, 'efg': 53.5, 'ts': 56.6, 'ast_pct': 60.9, 'tov_pct': 15.0, 'oreb_pct': 29.0, 'dreb_pct': 66.3, 'pie': 44.4, 'poss': 3389},
    'MEM': {'pace': 101.84, 'off_rtg': 112.9, 'def_rtg': 113.9, 'net_rtg': -0.9, 'efg': 53.0, 'ts': 57.0, 'ast_pct': 69.9, 'tov_pct': 14.9, 'oreb_pct': 31.5, 'dreb_pct': 70.8, 'pie': 50.6, 'poss': 3386},
    'NO': {'pace': 101.63, 'off_rtg': 112.4, 'def_rtg': 119.6, 'net_rtg': -7.3, 'efg': 51.9, 'ts': 56.1, 'ast_pct': 58.3, 'tov_pct': 13.9, 'oreb_pct': 31.7, 'dreb_pct': 67.0, 'pie': 46.2, 'poss': 3698},
    'NOP': {'pace': 101.63, 'off_rtg': 112.4, 'def_rtg': 119.6, 'net_rtg': -7.3, 'efg': 51.9, 'ts': 56.1, 'ast_pct': 58.3, 'tov_pct': 13.9, 'oreb_pct': 31.7, 'dreb_pct': 67.0, 'pie': 46.2, 'poss': 3698},
    'OKC': {'pace': 101.59, 'off_rtg': 118.8, 'def_rtg': 104.5, 'net_rtg': 14.2, 'efg': 57.0, 'ts': 60.9, 'ast_pct': 58.5, 'tov_pct': 12.3, 'oreb_pct': 25.7, 'dreb_pct': 71.2, 'pie': 58.1, 'poss': 3496},
    'IND': {'pace': 101.57, 'off_rtg': 107.8, 'def_rtg': 116.7, 'net_rtg': -8.9, 'efg': 50.5, 'ts': 54.7, 'ast_pct': 60.9, 'tov_pct': 13.8, 'oreb_pct': 27.9, 'dreb_pct': 68.2, 'pie': 45.1, 'poss': 3575},
    'DET': {'pace': 101.28, 'off_rtg': 116.8, 'def_rtg': 110.6, 'net_rtg': 6.2, 'efg': 54.3, 'ts': 58.0, 'ast_pct': 61.5, 'tov_pct': 15.6, 'oreb_pct': 36.5, 'dreb_pct': 68.3, 'pie': 53.9, 'poss': 3461},
    'SAC': {'pace': 101.15, 'off_rtg': 108.5, 'def_rtg': 119.9, 'net_rtg': -11.3, 'efg': 52.0, 'ts': 55.5, 'ast_pct': 61.5, 'tov_pct': 14.2, 'oreb_pct': 27.7, 'dreb_pct': 67.1, 'pie': 44.3, 'poss': 3568},
    'SA': {'pace': 101.09, 'off_rtg': 118.3, 'def_rtg': 112.7, 'net_rtg': 5.6, 'efg': 55.6, 'ts': 59.6, 'ast_pct': 60.5, 'tov_pct': 14.1, 'oreb_pct': 31.7, 'dreb_pct': 72.5, 'pie': 52.8, 'poss': 3450},
    'SAS': {'pace': 101.09, 'off_rtg': 118.3, 'def_rtg': 112.7, 'net_rtg': 5.6, 'efg': 55.6, 'ts': 59.6, 'ast_pct': 60.5, 'tov_pct': 14.1, 'oreb_pct': 31.7, 'dreb_pct': 72.5, 'pie': 52.8, 'poss': 3450},
    'ORL': {'pace': 101.07, 'off_rtg': 114.5, 'def_rtg': 113.3, 'net_rtg': 1.2, 'efg': 52.9, 'ts': 57.4, 'ast_pct': 62.8, 'tov_pct': 13.6, 'oreb_pct': 31.7, 'dreb_pct': 70.8, 'pie': 51.1, 'poss': 3562},
    'MIN': {'pace': 100.93, 'off_rtg': 116.4, 'def_rtg': 112.7, 'net_rtg': 3.7, 'efg': 55.5, 'ts': 59.2, 'ast_pct': 62.9, 'tov_pct': 14.0, 'oreb_pct': 30.3, 'dreb_pct': 69.0, 'pie': 52.3, 'poss': 3469},
    'GS': {'pace': 100.69, 'off_rtg': 114.3, 'def_rtg': 111.8, 'net_rtg': 2.5, 'efg': 54.7, 'ts': 58.7, 'ast_pct': 69.7, 'tov_pct': 16.0, 'oreb_pct': 30.5, 'dreb_pct': 67.8, 'pie': 50.7, 'poss': 3439},
    'GSW': {'pace': 100.69, 'off_rtg': 114.3, 'def_rtg': 111.8, 'net_rtg': 2.5, 'efg': 54.7, 'ts': 58.7, 'ast_pct': 69.7, 'tov_pct': 16.0, 'oreb_pct': 30.5, 'dreb_pct': 67.8, 'pie': 50.7, 'poss': 3439},
    'PHI': {'pace': 100.37, 'off_rtg': 114.4, 'def_rtg': 113.7, 'net_rtg': 0.8, 'efg': 52.3, 'ts': 56.8, 'ast_pct': 60.5, 'tov_pct': 13.9, 'oreb_pct': 32.0, 'dreb_pct': 68.2, 'pie': 49.5, 'poss': 3261},
    'DEN': {'pace': 100.33, 'off_rtg': 123.1, 'def_rtg': 116.4, 'net_rtg': 6.6, 'efg': 58.8, 'ts': 62.7, 'ast_pct': 65.1, 'tov_pct': 13.1, 'oreb_pct': 29.6, 'dreb_pct': 71.0, 'pie': 53.8, 'poss': 3443},
    'PHX': {'pace': 100.06, 'off_rtg': 114.9, 'def_rtg': 113.1, 'net_rtg': 1.8, 'efg': 54.4, 'ts': 57.8, 'ast_pct': 60.2, 'tov_pct': 15.5, 'oreb_pct': 34.1, 'dreb_pct': 68.1, 'pie': 50.4, 'poss': 3417},
    'PHO': {'pace': 100.06, 'off_rtg': 114.9, 'def_rtg': 113.1, 'net_rtg': 1.8, 'efg': 54.4, 'ts': 57.8, 'ast_pct': 60.2, 'tov_pct': 15.5, 'oreb_pct': 34.1, 'dreb_pct': 68.1, 'pie': 50.4, 'poss': 3417},
    'NY': {'pace': 99.68, 'off_rtg': 120.9, 'def_rtg': 114.9, 'net_rtg': 5.9, 'efg': 55.8, 'ts': 59.3, 'ast_pct': 63.0, 'tov_pct': 13.5, 'oreb_pct': 33.1, 'dreb_pct': 70.6, 'pie': 52.6, 'poss': 3390},
    'NYK': {'pace': 99.68, 'off_rtg': 120.9, 'def_rtg': 114.9, 'net_rtg': 5.9, 'efg': 55.8, 'ts': 59.3, 'ast_pct': 63.0, 'tov_pct': 13.5, 'oreb_pct': 33.1, 'dreb_pct': 70.6, 'pie': 52.6, 'poss': 3390},
    'LAL': {'pace': 99.66, 'off_rtg': 117.1, 'def_rtg': 117.8, 'net_rtg': -0.6, 'efg': 56.9, 'ts': 61.0, 'ast_pct': 59.5, 'tov_pct': 15.6, 'oreb_pct': 30.2, 'dreb_pct': 69.3, 'pie': 50.1, 'poss': 3092},
    'CHA': {'pace': 99.63, 'off_rtg': 115.4, 'def_rtg': 118.3, 'net_rtg': -2.9, 'efg': 54.1, 'ts': 58.1, 'ast_pct': 64.9, 'tov_pct': 15.6, 'oreb_pct': 34.0, 'dreb_pct': 71.7, 'pie': 48.3, 'poss': 3416},
    'TOR': {'pace': 99.49, 'off_rtg': 113.7, 'def_rtg': 112.5, 'net_rtg': 1.2, 'efg': 53.8, 'ts': 57.2, 'ast_pct': 69.2, 'tov_pct': 14.3, 'oreb_pct': 31.1, 'dreb_pct': 69.1, 'pie': 50.9, 'poss': 3505},
    'MIL': {'pace': 99.28, 'off_rtg': 113.4, 'def_rtg': 116.2, 'net_rtg': -2.7, 'efg': 57.3, 'ts': 59.8, 'ast_pct': 63.1, 'tov_pct': 14.9, 'oreb_pct': 25.9, 'dreb_pct': 68.4, 'pie': 48.4, 'poss': 3495},
    'BKN': {'pace': 97.80, 'off_rtg': 111.6, 'def_rtg': 116.5, 'net_rtg': -4.9, 'efg': 53.0, 'ts': 57.1, 'ast_pct': 66.9, 'tov_pct': 16.3, 'oreb_pct': 29.8, 'dreb_pct': 68.0, 'pie': 46.0, 'poss': 3122},
    'HOU': {'pace': 96.96, 'off_rtg': 121.8, 'def_rtg': 112.7, 'net_rtg': 9.0, 'efg': 56.1, 'ts': 59.6, 'ast_pct': 57.8, 'tov_pct': 16.4, 'oreb_pct': 41.3, 'dreb_pct': 70.2, 'pie': 55.1, 'poss': 3068},
    'LAC': {'pace': 96.80, 'off_rtg': 115.3, 'def_rtg': 116.6, 'net_rtg': -1.3, 'efg': 55.2, 'ts': 59.8, 'ast_pct': 60.0, 'tov_pct': 15.8, 'oreb_pct': 29.2, 'dreb_pct': 68.6, 'pie': 49.3, 'poss': 3214},
    'BOS': {'pace': 96.65, 'off_rtg': 121.3, 'def_rtg': 114.2, 'net_rtg': 7.0, 'efg': 56.0, 'ts': 58.9, 'ast_pct': 55.7, 'tov_pct': 12.7, 'oreb_pct': 33.1, 'dreb_pct': 67.3, 'pie': 52.6, 'poss': 3184},
}

# Team abbreviation mapping to handle variations
TEAM_ABBR_MAP = {
    'LAK': 'LAL',  # Fix for Los Angeles Lakers
    'SA': 'SAS',
    'NO': 'NOP',
    'NY': 'NYK',
    'GS': 'GSW',
    'PHX': 'PHO',
    'TRA': 'POR',
}

TEAM_ABBR_MAP.update({
    'HAW': 'ATL',   # Hawks
    'TIM': 'MIN',   # Timberwolves
    'PAC': 'IND',   # Pacers
    'OPP': 'UNK',   # Unknown opponent placeholder
})

def normalize_team_abbr(team_abbr):
    '''Normalize team abbreviations to match our data'''
    if not team_abbr:
        return team_abbr
    return TEAM_ABBR_MAP.get(team_abbr, team_abbr)

# League average stats for normalization
LEAGUE_AVG_PACE = 100.0
LEAGUE_AVG_OREB = 30.0
LEAGUE_AVG_DREB = 69.0
LEAGUE_AVG_AST = 63.0
LEAGUE_AVG_TOV = 14.5
LEAGUE_AVG_DEF_RTG = 113.0

# Global injury cache
INJURY_CACHE = {}
TEAM_INJURIES = {}  # Track injuries by team

def scrape_injuries_from_sportsethos():
    """Scrape NBA injuries from sportsethos.com live injury report"""
    global INJURY_CACHE, TEAM_INJURIES
    
    print('🏥 Scraping NBA injuries from sportsethos.com...')
    
    try:
        url = 'https://sportsethos.com/live-injury-report/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        INJURY_CACHE = {}
        TEAM_INJURIES = {}
        injuries_found = 0
        
        # Find all injury entries (structure may vary, let's try multiple approaches)
        # Look for tables, divs, or lists containing injury data
        
        # Try finding table rows with injury data
        injury_tables = soup.find_all('table')
        
        for table in injury_tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 3:  # Need at least player, team, status
                    try:
                        # Extract player name (usually first column)
                        player_name = cells[0].get_text(strip=True)
                        
                        # Extract team (usually second column)
                        team_abbr = cells[1].get_text(strip=True)
                        
                        # Extract injury status (usually third or fourth column)
                        status = cells[2].get_text(strip=True).lower()
                        
                        # Extract position if available
                        position = cells[3].get_text(strip=True) if len(cells) > 3 else 'UNK'
                        
                        # Clean up status
                        if 'out' in status:
                            status = 'out'
                        elif 'doubtful' in status:
                            status = 'doubtful'
                        elif 'questionable' in status or 'gtd' in status:
                            status = 'questionable'
                        elif 'day-to-day' in status or 'day to day' in status:
                            status = 'day-to-day'
                        else:
                            continue  # Skip if status is unclear
                        
                        # Normalize team abbreviation
                        team_abbr = normalize_team_abbr(team_abbr)
                        
                        if player_name and team_abbr:
                            # Store in cache
                            INJURY_CACHE[player_name] = status
                            
                            # Track by team
                            if team_abbr not in TEAM_INJURIES:
                                TEAM_INJURIES[team_abbr] = []
                            
                            TEAM_INJURIES[team_abbr].append({
                                'name': player_name,
                                'status': status,
                                'position': position[:2] if len(position) >= 2 else 'SF'  # Default to SF
                            })
                            
                            injuries_found += 1
                    
                    except Exception as e:
                        continue  # Skip malformed rows
        
        # If table parsing didn't work, try finding divs or cards
        if injuries_found == 0:
            print('⚠️  No injuries found in tables, trying alternative parsing...')
            
            # Look for injury cards or list items
            injury_items = soup.find_all(['div', 'li'], class_=lambda x: x and ('injury' in x.lower() or 'player' in x.lower()))
            
            for item in injury_items:
                try:
                    # Try to extract player name and status from text content
                    text = item.get_text(strip=True)
                    
                    # Look for patterns like "Player Name - Team - Status"
                    if '-' in text:
                        parts = [p.strip() for p in text.split('-')]
                        if len(parts) >= 3:
                            player_name = parts[0]
                            team_abbr = normalize_team_abbr(parts[1])
                            status = parts[2].lower()
                            
                            if 'out' in status:
                                status = 'out'
                            elif 'doubtful' in status:
                                status = 'doubtful'
                            elif 'questionable' in status:
                                status = 'questionable'
                            else:
                                continue
                            
                            INJURY_CACHE[player_name] = status
                            
                            if team_abbr not in TEAM_INJURIES:
                                TEAM_INJURIES[team_abbr] = []
                            
                            TEAM_INJURIES[team_abbr].append({
                                'name': player_name,
                                'status': status,
                                'position': 'SF'
                            })
                            
                            injuries_found += 1
                
                except Exception:
                    continue
        
        print(f'✅ Found {injuries_found} injured players')
        
        if injuries_found > 0:
            print('   Injured players by team:')
            for team, injuries in sorted(TEAM_INJURIES.items())[:5]:
                print(f'   {team}: {len(injuries)} injured')
                for inj in injuries[:3]:
                    print(f'      • {inj["name"]}: {inj["status"]}')
            
            if len(TEAM_INJURIES) > 5:
                total_teams = len(TEAM_INJURIES)
                print(f'   ... and {total_teams - 5} more teams with injuries')
        else:
            print('⚠️  No injuries found. Website structure may have changed.')
            print('   Continuing without injury data...')
        
        return injuries_found > 0
        
    except requests.RequestException as e:
        print(f'⚠️  Could not fetch injuries from sportsethos.com: {e}')
        print('   Continuing without injury data...')
        return False
    except Exception as e:
        print(f'⚠️  Error parsing injury data: {e}')
        print('   Continuing without injury data...')
        return False

def fetch_current_injuries():
    '''Fetch current NBA injuries - try sportsethos first, then ESPN as fallback'''
    global INJURY_CACHE, TEAM_INJURIES
    
    # Try scraping from sportsethos
    success = scrape_injuries_from_sportsethos()
    
    if success:
        return True
    
    # Fallback to ESPN API
    print('\n🔄 Trying ESPN API as fallback...')
    
    try:
        url = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        injuries_found = 0
        TEAM_INJURIES = {}  # Reset team injuries
        
        # ESPN includes injuries in game data
        if 'events' in data:
            for event in data['events']:
                for competition in event.get('competitions', []):
                    for competitor in competition.get('competitors', []):
                        team_abbr = competitor.get('team', {}).get('abbreviation')
                        
                        # Initialize team injuries list
                        if team_abbr and team_abbr not in TEAM_INJURIES:
                            TEAM_INJURIES[team_abbr] = []
                        
                        # Check for injuries in roster
                        for athlete in competitor.get('athletes', []):
                            injury_status = athlete.get('injuries')
                            if injury_status:
                                for injury in injury_status:
                                    player_name = athlete.get('displayName')
                                    status = injury.get('status', 'unknown').lower()
                                    position = athlete.get('position', {}).get('abbreviation', 'UNK')
                                    
                                    # Store in cache
                                    INJURY_CACHE[player_name] = status
                                    
                                    # Track by team for usage boost
                                    if team_abbr:
                                        TEAM_INJURIES[team_abbr].append({
                                            'name': player_name,
                                            'status': status,
                                            'position': position
                                        })
                                    
                                    injuries_found += 1
        
        if injuries_found > 0:
            print(f'✅ Found {injuries_found} injured players from ESPN')
            return True
        else:
            print('ℹ️  No injuries found from ESPN (may be no games today)')
            return False
        
    except Exception as e:
        print(f'⚠️  ESPN fallback also failed: {e}')
        print('   Continuing without injury data...')
        return False

def get_usage_boost(player_name, player_team, player_position, stat_type):
    '''Calculate usage boost when key teammates are OUT - only for high-usage players'''
    if player_team not in TEAM_INJURIES:
        return 1.0
    
    # Define high-usage/starter players who impact teammates when out
    # These are the players whose absence significantly affects team dynamics
    HIGH_USAGE_PLAYERS = {
        # Point Guards (primary ball handlers)
        'Luka Doncic', 'Trae Young', 'Damian Lillard', 'Stephen Curry', 'Kyrie Irving',
        'Tyrese Haliburton', 'Ja Morant', 'Jalen Brunson', 'Darius Garland', 'LaMelo Ball',
        'De\'Aaron Fox', 'Shai Gilgeous-Alexander', 'Chris Paul', 'Russell Westbrook',
        'Cade Cunningham', 'Dejounte Murray', 'Fred VanVleet', 'Jamal Murray',
        
        # Star Shooting Guards (primary scorers)
        'Donovan Mitchell', 'Devin Booker', 'Anthony Edwards', 'Zach LaVine', 'Bradley Beal',
        'Tyler Herro', 'Desmond Bane', 'Jaylen Brown', 'Paul George',
        
        # Star Forwards (high usage scorers/playmakers)
        'LeBron James', 'Kevin Durant', 'Jayson Tatum', 'Jimmy Butler', 'Kawhi Leonard',
        'Brandon Ingram', 'Giannis Antetokounmpo', 'Zion Williamson', 'Julius Randle',
        'Pascal Siakam', 'DeMar DeRozan',
        
        # Star Centers/Bigs (high usage)
        'Nikola Jokic', 'Joel Embiid', 'Anthony Davis', 'Karl-Anthony Towns',
        'Domantas Sabonis', 'Bam Adebayo'
    }
    
    # Get all OUT or DOUBTFUL players on the same team (these have similar impact)
    out_teammates = [
        inj for inj in TEAM_INJURIES[player_team]
        if (inj['status'] == 'out' or inj['status'] == 'doubtful') and inj['name'] != player_name
    ]
    
    if not out_teammates:
        return 1.0
    
    # Filter to only HIGH USAGE players - bench players don't affect projections much
    high_usage_out = [
        inj for inj in out_teammates 
        if inj['name'] in HIGH_USAGE_PLAYERS
    ]
    
    if not high_usage_out:
        # No high-usage players out, minimal boost
        return 1.0
    
    # Define key positions and their impact on other positions
    # Format: {injured_pos: {beneficiary_pos: {stat: boost}}}
    USAGE_BOOST_MAP = {
        # Point Guard out → other guards/forwards get more assists, points
        'PG': {
            'PG': {'Points': 1.12, 'Assists': 1.18, 'Field Goals Made': 1.10, '3-Pointers Made': 1.10},
            'SG': {'Points': 1.10, 'Assists': 1.15, 'Field Goals Made': 1.08, '3-Pointers Made': 1.08},
            'SF': {'Points': 1.08, 'Assists': 1.12, 'Field Goals Made': 1.06},
            'PF': {'Points': 1.05, 'Assists': 1.06, 'Rebounds': 1.04},
            'C': {'Points': 1.05, 'Rebounds': 1.05}
        },
        # Shooting Guard out → other scorers benefit
        'SG': {
            'PG': {'Points': 1.10, 'Field Goals Made': 1.08, '3-Pointers Made': 1.10, 'Assists': 1.05},
            'SG': {'Points': 1.12, 'Field Goals Made': 1.10, '3-Pointers Made': 1.12},
            'SF': {'Points': 1.10, 'Field Goals Made': 1.08, '3-Pointers Made': 1.08},
            'PF': {'Points': 1.06, 'Field Goals Made': 1.05},
            'C': {'Points': 1.06, 'Rebounds': 1.04}
        },
        # Small Forward out → wings and bigs get more opportunities
        'SF': {
            'PG': {'Points': 1.06, 'Assists': 1.05},
            'SG': {'Points': 1.08, 'Field Goals Made': 1.06, '3-Pointers Made': 1.06},
            'SF': {'Points': 1.10, 'Rebounds': 1.06, 'Field Goals Made': 1.08},
            'PF': {'Points': 1.08, 'Rebounds': 1.08},
            'C': {'Points': 1.06, 'Rebounds': 1.08}
        },
        # Power Forward out → bigs get more boards, points
        'PF': {
            'PG': {'Points': 1.04, 'Assists': 1.04},
            'SG': {'Points': 1.05, 'Field Goals Made': 1.04},
            'SF': {'Points': 1.06, 'Rebounds': 1.06},
            'PF': {'Points': 1.08, 'Rebounds': 1.10},
            'C': {'Points': 1.08, 'Rebounds': 1.12}
        },
        # Center out → other bigs dominate the paint
        'C': {
            'PG': {'Points': 1.04, 'Assists': 1.05},
            'SG': {'Points': 1.05},
            'SF': {'Points': 1.06, 'Rebounds': 1.08},
            'PF': {'Points': 1.08, 'Rebounds': 1.12},
            'C': {'Points': 1.10, 'Rebounds': 1.15, 'Blocks': 1.12}
        }
    }
    
    total_boost = 1.0
    boosts_applied = 0
    
    for injured in high_usage_out:
        injured_pos = injured.get('position', 'UNK')
        
        # Normalize position (G → PG/SG, F → SF/PF)
        if injured_pos == 'G':
            injured_pos = 'PG'
        elif injured_pos == 'F':
            injured_pos = 'SF'
        
        if injured_pos not in USAGE_BOOST_MAP:
            continue
        
        # Check if this player's position benefits from the injury
        if player_position in USAGE_BOOST_MAP[injured_pos]:
            boosts = USAGE_BOOST_MAP[injured_pos][player_position]
            
            # Check if the stat type gets a boost
            for stat_pattern, boost_value in boosts.items():
                if stat_pattern in stat_type:
                    # Stack boosts multiplicatively, but cap at reasonable levels
                    total_boost *= boost_value
                    boosts_applied += 1
                    break
    
    # Cap total boost at 1.30x (30% increase max) for multiple star injuries
    total_boost = min(total_boost, 1.30)
    
    return total_boost

def get_injury_adjustment(player_name):
    '''Check if player is injured and return adjustment factor'''
    if player_name not in INJURY_CACHE:
        return 1.0  # No injury data, no adjustment
    
    status = INJURY_CACHE[player_name].lower()
    
    # Injury status multipliers
    if status == 'out':
        return 0.0  # Player won't play
    elif status == 'doubtful':
        return 0.70  # 30% reduction (likely won't play or very limited)
    elif status == 'questionable':
        return 0.85  # 15% reduction
    elif 'day-to-day' in status or 'day to day' in status:
        return 0.95  # 5% reduction
    
    return 1.0  # Unknown status, no adjustment

# The rest of the code remains unchanged
# ...
