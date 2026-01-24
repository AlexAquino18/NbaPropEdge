import os
import time
from dotenv import load_dotenv
from supabase import create_client
import numpy as np
from scipy import stats as scipy_stats
import subprocess
import sys
import requests
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
        
        # Find all injury tables
        injury_tables = soup.find_all('table')
        
        for table in injury_tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 3:
                    try:
                        # Extract player name - remove status in parentheses
                        player_text = cells[0].get_text(strip=True)
                        player_name = player_text.split('(')[0].strip() if '(' in player_text else player_text
                        
                        # Extract team
                        team_abbr = cells[1].get_text(strip=True)
                        
                        # Skip if no real data
                        if not player_name or len(player_name) < 2:
                            continue
                        
                        # Parse status from player text
                        status = 'questionable'  # Default
                        
                        if 'out indefinitely' in player_text.lower() or 'out for season' in player_text.lower():
                            status = 'out'
                        elif 'out for' in player_text.lower():
                            status = 'out'
                        elif 'day-to-day' in player_text.lower():
                            status = 'day-to-day'
                        elif 'week-to-week' in player_text.lower():
                            status = 'out'
                        elif 'probable' in player_text.lower():
                            status = 'questionable'
                        elif 'doubtful' in player_text.lower():
                            status = 'doubtful'
                        elif 're-evaluat' in player_text.lower() or 'reevaluat' in player_text.lower():
                            status = 'out'
                        
                        position = 'SF'  # Default position
                        team_abbr = normalize_team_abbr(team_abbr)
                        
                        if player_name and team_abbr:
                            INJURY_CACHE[player_name] = status
                            
                            if team_abbr not in TEAM_INJURIES:
                                TEAM_INJURIES[team_abbr] = []
                            
                            TEAM_INJURIES[team_abbr].append({
                                'name': player_name,
                                'status': status,
                                'position': position
                            })
                            
                            injuries_found += 1
                    
                    except Exception as e:
                        continue
        
        print(f'✅ Found {injuries_found} injured players')
        
        if injuries_found > 0:
            status_counts = {}
            for inj_list in TEAM_INJURIES.values():
                for inj in inj_list:
                    status = inj['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f'   Status breakdown:')
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                print(f'      • {status}: {count} players')
            
            print(f'\n   Sample injuries by team:')
            for team, injuries in sorted(TEAM_INJURIES.items())[:5]:
                out_count = sum(1 for i in injuries if i['status'] == 'out')
                if out_count > 0:
                    print(f'   {team}: {out_count} OUT')
                    for inj in injuries[:2]:
                        if inj['status'] == 'out':
                            print(f'      • {inj["name"]}: {inj["status"].upper()}')
            
            if len(TEAM_INJURIES) > 5:
                print(f'   ... and {len(TEAM_INJURIES) - 5} more teams with injuries')
        else:
            print('⚠️  No injuries found. Website structure may have changed.')
        
        return injuries_found > 0
        
    except Exception as e:
        print(f'⚠️  Error: {e}')
        return False

def fetch_current_injuries():
    '''Fetch current NBA injuries from sportsethos.com'''
    return scrape_injuries_from_sportsethos()

def get_usage_boost(player_name, player_team, player_position, stat_type):
    '''Calculate usage boost when key teammates are OUT'''
    if player_team not in TEAM_INJURIES:
        return 1.0
    
    HIGH_USAGE_PLAYERS = {
        'Luka Doncic', 'Trae Young', 'Damian Lillard', 'Stephen Curry', 'Kyrie Irving',
        'Tyrese Haliburton', 'Ja Morant', 'Jalen Brunson', 'Darius Garland', 'LaMelo Ball',
        'De\'Aaron Fox', 'Shai Gilgeous-Alexander', 'Chris Paul', 'Russell Westbrook',
        'Cade Cunningham', 'Dejounte Murray', 'Fred VanVleet', 'Jamal Murray',
        'Donovan Mitchell', 'Devin Booker', 'Anthony Edwards', 'Zach LaVine', 'Bradley Beal',
        'Tyler Herro', 'Desmond Bane', 'Jaylen Brown', 'Paul George',
        'LeBron James', 'Kevin Durant', 'Jayson Tatum', 'Jimmy Butler', 'Kawhi Leonard',
        'Brandon Ingram', 'Giannis Antetokounmpo', 'Zion Williamson', 'Julius Randle',
        'Pascal Siakam', 'DeMar DeRozan',
        'Nikola Jokic', 'Joel Embiid', 'Anthony Davis', 'Karl-Anthony Towns',
        'Domantas Sabonis', 'Bam Adebayo'
    }
    
    out_teammates = [
        inj for inj in TEAM_INJURIES[player_team]
        if (inj['status'] == 'out' or inj['status'] == 'doubtful') and inj['name'] != player_name
    ]
    
    if not out_teammates:
        return 1.0
    
    high_usage_out = [inj for inj in out_teammates if inj['name'] in HIGH_USAGE_PLAYERS]
    
    if not high_usage_out:
        return 1.0
    
    USAGE_BOOST_MAP = {
        'PG': {
            'PG': {'Points': 1.12, 'Assists': 1.18, 'Field Goals Made': 1.10, '3-Pointers Made': 1.10},
            'SG': {'Points': 1.10, 'Assists': 1.15, 'Field Goals Made': 1.08, '3-Pointers Made': 1.08},
            'SF': {'Points': 1.08, 'Assists': 1.12, 'Field Goals Made': 1.06},
            'PF': {'Points': 1.05, 'Assists': 1.06, 'Rebounds': 1.04},
            'C': {'Points': 1.05, 'Rebounds': 1.05}
        },
        'SG': {
            'PG': {'Points': 1.10, 'Field Goals Made': 1.08, '3-Pointers Made': 1.10, 'Assists': 1.05},
            'SG': {'Points': 1.12, 'Field Goals Made': 1.10, '3-Pointers Made': 1.12},
            'SF': {'Points': 1.10, 'Field Goals Made': 1.08, '3-Pointers Made': 1.08},
            'PF': {'Points': 1.06, 'Field Goals Made': 1.05},
            'C': {'Points': 1.06, 'Rebounds': 1.04}
        },
        'SF': {
            'PG': {'Points': 1.06, 'Assists': 1.05},
            'SG': {'Points': 1.08, 'Field Goals Made': 1.06, '3-Pointers Made': 1.06},
            'SF': {'Points': 1.10, 'Rebounds': 1.06, 'Field Goals Made': 1.08},
            'PF': {'Points': 1.08, 'Rebounds': 1.08},
            'C': {'Points': 1.06, 'Rebounds': 1.08}
        },
        'PF': {
            'PG': {'Points': 1.04, 'Assists': 1.04},
            'SG': {'Points': 1.05, 'Field Goals Made': 1.04},
            'SF': {'Points': 1.06, 'Rebounds': 1.06},
            'PF': {'Points': 1.08, 'Rebounds': 1.10},
            'C': {'Points': 1.08, 'Rebounds': 1.12}
        },
        'C': {
            'PG': {'Points': 1.04, 'Assists': 1.05},
            'SG': {'Points': 1.05},
            'SF': {'Points': 1.06, 'Rebounds': 1.08},
            'PF': {'Points': 1.08, 'Rebounds': 1.12},
            'C': {'Points': 1.10, 'Rebounds': 1.15, 'Blocks': 1.12}
        }
    }
    
    total_boost = 1.0
    
    for injured in high_usage_out:
        injured_pos = injured.get('position', 'UNK')
        
        if injured_pos == 'G':
            injured_pos = 'PG'
        elif injured_pos == 'F':
            injured_pos = 'SF'
        
        if injured_pos not in USAGE_BOOST_MAP:
            continue
        
        if player_position in USAGE_BOOST_MAP[injured_pos]:
            boosts = USAGE_BOOST_MAP[injured_pos][player_position]
            
            for stat_pattern, boost_value in boosts.items():
                if stat_pattern in stat_type:
                    total_boost *= boost_value
                    break
    
    return min(total_boost, 1.30)

def get_injury_adjustment(player_name):
    '''Check if player is injured and return adjustment factor'''
    if player_name not in INJURY_CACHE:
        return 1.0
    
    status = INJURY_CACHE[player_name].lower()
    
    if status == 'out':
        return 0.0
    elif status == 'doubtful':
        return 0.70
    elif status == 'questionable':
        return 0.85
    elif 'day-to-day' in status or 'day to day' in status:
        return 0.95
    
    return 1.0

# Complete defensive matchup data with stat-specific rankings
# Format: {team_abbr: {position: {stat_rank}}} where rank 1 = best defense (hardest), 30 = worst defense (easiest)
DEFENSIVE_MATCHUPS = {
    'ATL': {
        'PG': {'pts': 18, 'reb': 15, 'ast': 24, 'stl': 20, 'blk': 10},
        'SG': {'pts': 27, 'reb': 22, 'ast': 24, 'stl': 30, 'blk': 12},
        'SF': {'pts': 29, 'reb': 27, 'ast': 26, 'stl': 30, 'blk': 28},
        'PF': {'pts': 6, 'reb': 5, 'ast': 16, 'stl': 11, 'blk': 16},
        'C': {'pts': 24, 'reb': 5, 'ast': 16, 'stl': 16, 'blk': 15}
    },
    'BOS': {
        'PG': {'pts': 13, 'reb': 8, 'ast': 5, 'stl': 6, 'blk': 1},
        'SG': {'pts': 15, 'reb': 23, 'ast': 20, 'stl': 17, 'blk': 10},
        'SF': {'pts': 10, 'reb': 18, 'ast': 6, 'stl': 2, 'blk': 7},
        'PF': {'pts': 3, 'reb': 16, 'ast': 4, 'stl': 3, 'blk': 2},
        'C': {'pts': 10, 'reb': 6, 'ast': 4, 'stl': 1, 'blk': 1}
    },
    'BKN': {
        'PG': {'pts': 25, 'reb': 22, 'ast': 25, 'stl': 10, 'blk': 17},
        'SG': {'pts': 3, 'reb': 1, 'ast': 6, 'stl': 16, 'blk': 24},
        'SF': {'pts': 22, 'reb': 19, 'ast': 24, 'stl': 15, 'blk': 25},
        'PF': {'pts': 18, 'reb': 22, 'ast': 18, 'stl': 7, 'blk': 26},
        'C': {'pts': 28, 'reb': 25, 'ast': 25, 'stl': 28, 'blk': 29}
    },
    'CHA': {
        'PG': {'pts': 20, 'reb': 24, 'ast': 14, 'stl': 16, 'blk': 21},
        'SG': {'pts': 8, 'reb': 3, 'ast': 14, 'stl': 9, 'blk': 16},
        'SF': {'pts': 21, 'reb': 14, 'ast': 29, 'stl': 21, 'blk': 28},
        'PF': {'pts': 16, 'reb': 11, 'ast': 12, 'stl': 20, 'blk': 17},
        'C': {'pts': 9, 'reb': 15, 'ast': 8, 'stl': 25, 'blk': 5}
    },
    'CHI': {
        'PG': {'pts': 28, 'reb': 29, 'ast': 29, 'stl': 23, 'blk': 25},
        'SG': {'pts': 19, 'reb': 8, 'ast': 13, 'stl': 8, 'blk': 20},
        'SF': {'pts': 18, 'reb': 29, 'ast': 25, 'stl': 16, 'blk': 15},
        'PF': {'pts': 28, 'reb': 25, 'ast': 26, 'stl': 8, 'blk': 11},
        'C': {'pts': 27, 'reb': 17, 'ast': 24, 'stl': 20, 'blk': 19}
    },
    'CLE': {
        'PG': {'pts': 15, 'reb': 13, 'ast': 6, 'stl': 8, 'blk': 5},
        'SG': {'pts': 10, 'reb': 4, 'ast': 11, 'stl': 3, 'blk': 6},
        'SF': {'pts': 30, 'reb': 30, 'ast': 27, 'stl': 19, 'blk': 13},
        'PF': {'pts': 7, 'reb': 6, 'ast': 13, 'stl': 27, 'blk': 9},
        'C': {'pts': 6, 'reb': 11, 'ast': 11, 'stl': 13, 'blk': 16}
    },
    'DAL': {
        'PG': {'pts': 17, 'reb': 6, 'ast': 9, 'stl': 12, 'blk': 18},
        'SG': {'pts': 21, 'reb': 29, 'ast': 26, 'stl': 21, 'blk': 21},
        'SF': {'pts': 9, 'reb': 10, 'ast': 13, 'stl': 6, 'blk': 12},
        'PF': {'pts': 21, 'reb': 20, 'ast': 24, 'stl': 22, 'blk': 5},
        'C': {'pts': 14, 'reb': 8, 'ast': 23, 'stl': 14, 'blk': 6}
    },
    'DEN': {
        'PG': {'pts': 1, 'reb': 1, 'ast': 18, 'stl': 21, 'blk': 9},
        'SG': {'pts': 25, 'reb': 14, 'ast': 29, 'stl': 12, 'blk': 22},
        'SF': {'pts': 16, 'reb': 6, 'ast': 20, 'stl': 20, 'blk': 23},
        'PF': {'pts': 11, 'reb': 8, 'ast': 11, 'stl': 21, 'blk': 21},
        'C': {'pts': 17, 'reb': 22, 'ast': 12, 'stl': 24, 'blk': 18}
    },
    'DET': {
        'PG': {'pts': 29, 'reb': 12, 'ast': 7, 'stl': 29, 'blk': 19},
        'SG': {'pts': 1, 'reb': 5, 'ast': 1, 'stl': 11, 'blk': 7},
        'SF': {'pts': 28, 'reb': 22, 'ast': 21, 'stl': 28, 'blk': 18},
        'PF': {'pts': 14, 'reb': 19, 'ast': 9, 'stl': 19, 'blk': 18},
        'C': {'pts': 20, 'reb': 21, 'ast': 28, 'stl': 21, 'blk': 25}
    },
    'GSW': {
        'PG': {'pts': 7, 'reb': 18, 'ast': 4, 'stl': 9, 'blk': 29},
        'SG': {'pts': 14, 'reb': 21, 'ast': 23, 'stl': 15, 'blk': 30},
        'SF': {'pts': 17, 'reb': 25, 'ast': 17, 'stl': 10, 'blk': 8},
        'PF': {'pts': 15, 'reb': 7, 'ast': 8, 'stl': 2, 'blk': 23},
        'C': {'pts': 5, 'reb': 18, 'ast': 18, 'stl': 19, 'blk': 17}
    },
    'HOU': {
        'PG': {'pts': 21, 'reb': 11, 'ast': 8, 'stl': 25, 'blk': 23},
        'SG': {'pts': 23, 'reb': 25, 'ast': 8, 'stl': 13, 'blk': 18},
        'SF': {'pts': 2, 'reb': 12, 'ast': 1, 'stl': 9, 'blk': 26},
        'PF': {'pts': 24, 'reb': 14, 'ast': 19, 'stl': 12, 'blk': 29},
        'C': {'pts': 3, 'reb': 12, 'ast': 2, 'stl': 12, 'blk': 26}
    },
    'IND': {
        'PG': {'pts': 10, 'reb': 4, 'ast': 16, 'stl': 5, 'blk': 15},
        'SG': {'pts': 22, 'reb': 10, 'ast': 17, 'stl': 5, 'blk': 13},
        'SF': {'pts': 24, 'reb': 28, 'ast': 28, 'stl': 8, 'blk': 22},
        'PF': {'pts': 10, 'reb': 17, 'ast': 3, 'stl': 26, 'blk': 1},
        'C': {'pts': 11, 'reb': 20, 'ast': 6, 'stl': 6, 'blk': 7}
    },
    'LAC': {
        'PG': {'pts': 11, 'reb': 9, 'ast': 12, 'stl': 17, 'blk': 3},
        'SG': {'pts': 6, 'reb': 2, 'ast': 4, 'stl': 24, 'blk': 4},
        'SF': {'pts': 20, 'reb': 16, 'ast': 11, 'stl': 29, 'blk': 16},
        'PF': {'pts': 9, 'reb': 12, 'ast': 15, 'stl': 17, 'blk': 8},
        'C': {'pts': 7, 'reb': 9, 'ast': 29, 'stl': 29, 'blk': 22}
    },
    'LAL': {
        'PG': {'pts': 6, 'reb': 3, 'ast': 22, 'stl': 19, 'blk': 7},
        'SG': {'pts': 18, 'reb': 20, 'ast': 27, 'stl': 13, 'blk': 3},
        'SF': {'pts': 8, 'reb': 4, 'ast': 10, 'stl': 14, 'blk': 6},
        'PF': {'pts': 22, 'reb': 15, 'ast': 7, 'stl': 14, 'blk': 3},
        'C': {'pts': 13, 'reb': 24, 'ast': 21, 'stl': 15, 'blk': 10}
    },
    'MEM': {
        'PG': {'pts': 12, 'reb': 27, 'ast': 20, 'stl': 24, 'blk': 27},
        'SG': {'pts': 28, 'reb': 18, 'ast': 22, 'stl': 23, 'blk': 19},
        'SF': {'pts': 25, 'reb': 20, 'ast': 30, 'stl': 26, 'blk': 27},
        'PF': {'pts': 23, 'reb': 27, 'ast': 22, 'stl': 30, 'blk': 14},
        'C': {'pts': 18, 'reb': 4, 'ast': 3, 'stl': 9, 'blk': 21}
    },
    'MIA': {
        'PG': {'pts': 24, 'reb': 26, 'ast': 26, 'stl': 18, 'blk': 24},
        'SG': {'pts': 4, 'reb': 13, 'ast': 2, 'stl': 4, 'blk': 25},
        'SF': {'pts': 12, 'reb': 11, 'ast': 12, 'stl': 5, 'blk': 19},
        'PF': {'pts': 5, 'reb': 9, 'ast': 17, 'stl': 5, 'blk': 4},
        'C': {'pts': 16, 'reb': 27, 'ast': 10, 'stl': 8, 'blk': 11}
    },
    'MIL': {
        'PG': {'pts': 22, 'reb': 25, 'ast': 19, 'stl': 7, 'blk': 12},
        'SG': {'pts': 16, 'reb': 28, 'ast': 16, 'stl': 1, 'blk': 1},
        'SF': {'pts': 4, 'reb': 8, 'ast': 4, 'stl': 13, 'blk': 2},
        'PF': {'pts': 4, 'reb': 4, 'ast': 6, 'stl': 13, 'blk': 7},
        'C': {'pts': 15, 'reb': 16, 'ast': 13, 'stl': 17, 'blk': 4}
    },
    'MIN': {
        'PG': {'pts': 19, 'reb': 21, 'ast': 11, 'stl': 14, 'blk': 13},
        'SG': {'pts': 2, 'reb': 11, 'ast': 5, 'stl': 10, 'blk': 8},
        'SF': {'pts': 5, 'reb': 3, 'ast': 2, 'stl': 22, 'blk': 4},
        'PF': {'pts': 27, 'reb': 21, 'ast': 23, 'stl': 29, 'blk': 15},
        'C': {'pts': 22, 'reb': 14, 'ast': 27, 'stl': 26, 'blk': 20}
    },
    'NOP': {
        'PG': {'pts': 23, 'reb': 28, 'ast': 27, 'stl': 27, 'blk': 28},
        'SG': {'pts': 26, 'reb': 24, 'ast': 28, 'stl': 26, 'blk': 9},
        'SF': {'pts': 27, 'reb': 9, 'ast': 15, 'stl': 24, 'blk': 20},
        'PF': {'pts': 25, 'reb': 24, 'ast': 27, 'stl': 24, 'blk': 24},
        'C': {'pts': 21, 'reb': 29, 'ast': 19, 'stl': 3, 'blk': 24}
    },
    'NYK': {
        'PG': {'pts': 26, 'reb': 23, 'ast': 21, 'stl': 15, 'blk': 22},
        'SG': {'pts': 9, 'reb': 7, 'ast': 9, 'stl': 2, 'blk': 15},
        'SF': {'pts': 23, 'reb': 13, 'ast': 9, 'stl': 4, 'blk': 21},
        'PF': {'pts': 1, 'reb': 1, 'ast': 2, 'stl': 1, 'blk': 6},
        'C': {'pts': 2, 'reb': 2, 'ast': 7, 'stl': 11, 'blk': 13}
    },
    'OKC': {
        'PG': {'pts': 5, 'reb': 15, 'ast': 2, 'stl': 1, 'blk': 4},
        'SG': {'pts': 11, 'reb': 27, 'ast': 12, 'stl': 18, 'blk': 27},
        'SF': {'pts': 7, 'reb': 23, 'ast': 7, 'stl': 3, 'blk': 10},
        'PF': {'pts': 12, 'reb': 13, 'ast': 5, 'stl': 4, 'blk': 22},
        'C': {'pts': 4, 'reb': 26, 'ast': 20, 'stl': 5, 'blk': 9}
    },
    'ORL': {
        'PG': {'pts': 16, 'reb': 2, 'ast': 1, 'stl': 4, 'blk': 2},
        'SG': {'pts': 5, 'reb': 15, 'ast': 3, 'stl': 6, 'blk': 11},
        'SF': {'pts': 13, 'reb': 21, 'ast': 16, 'stl': 25, 'blk': 11},
        'PF': {'pts': 2, 'reb': 2, 'ast': 1, 'stl': 18, 'blk': 20},
        'C': {'pts': 1, 'reb': 1, 'ast': 1, 'stl': 2, 'blk': 3}
    },
    'PHI': {
        'PG': {'pts': 3, 'reb': 7, 'ast': 17, 'stl': 2, 'blk': 11},
        'SG': {'pts': 7, 'reb': 6, 'ast': 18, 'stl': 7, 'blk': 2},
        'SF': {'pts': 26, 'reb': 15, 'ast': 23, 'stl': 1, 'blk': 9},
        'PF': {'pts': 17, 'reb': 23, 'ast': 21, 'stl': 6, 'blk': 30},
        'C': {'pts': 12, 'reb': 7, 'ast': 17, 'stl': 23, 'blk': 23}
    },
    'PHO': {
        'PG': {'pts': 9, 'reb': 19, 'ast': 13, 'stl': 13, 'blk': 20},
        'SG': {'pts': 17, 'reb': 16, 'ast': 19, 'stl': 20, 'blk': 14},
        'SF': {'pts': 3, 'reb': 1, 'ast': 8, 'stl': 12, 'blk': 1},
        'PF': {'pts': 29, 'reb': 29, 'ast': 30, 'stl': 25, 'blk': 19},
        'C': {'pts': 26, 'reb': 13, 'ast': 14, 'stl': 10, 'blk': 2}
    },
    'POR': {
        'PG': {'pts': 8, 'reb': 20, 'ast': 10, 'stl': 22, 'blk': 8},
        'SG': {'pts': 13, 'reb': 9, 'ast': 10, 'stl': 27, 'blk': 26},
        'SF': {'pts': 11, 'reb': 17, 'ast': 19, 'stl': 17, 'blk': 17},
        'PF': {'pts': 13, 'reb': 3, 'ast': 9, 'stl': 23, 'blk': 25},
        'C': {'pts': 25, 'reb': 28, 'ast': 30, 'stl': 27, 'blk': 28}
    },
    'SAC': {
        'PG': {'pts': 4, 'reb': 10, 'ast': 23, 'stl': 3, 'blk': 14},
        'SG': {'pts': 29, 'reb': 19, 'ast': 21, 'stl': 22, 'blk': 4},
        'SF': {'pts': 6, 'reb': 2, 'ast': 3, 'stl': 7, 'blk': 5},
        'PF': {'pts': 26, 'reb': 18, 'ast': 25, 'stl': 10, 'blk': 13},
        'C': {'pts': 23, 'reb': 19, 'ast': 26, 'stl': 30, 'blk': 12}
    },
    'SAS': {
        'PG': {'pts': 2, 'reb': 13, 'ast': 15, 'stl': 11, 'blk': 6},
        'SG': {'pts': 30, 'reb': 30, 'ast': 30, 'stl': 29, 'blk': 17},
        'SF': {'pts': 1, 'reb': 5, 'ast': 5, 'stl': 11, 'blk': 3},
        'PF': {'pts': 30, 'reb': 30, 'ast': 29, 'stl': 28, 'blk': 27},
        'C': {'pts': 8, 'reb': 3, 'ast': 5, 'stl': 4, 'blk': 8}
    },
    'TOR': {
        'PG': {'pts': 14, 'reb': 5, 'ast': 3, 'stl': 26, 'blk': 15},
        'SG': {'pts': 24, 'reb': 12, 'ast': 7, 'stl': 25, 'blk': 23},
        'SF': {'pts': 15, 'reb': 24, 'ast': 18, 'stl': 23, 'blk': 30},
        'PF': {'pts': 20, 'reb': 28, 'ast': 28, 'stl': 14, 'blk': 10},
        'C': {'pts': 19, 'reb': 23, 'ast': 22, 'stl': 18, 'blk': 30}
    },
    'UTA': {
        'PG': {'pts': 27, 'reb': 15, 'ast': 28, 'stl': 28, 'blk': 30},
        'SG': {'pts': 20, 'reb': 17, 'ast': 25, 'stl': 28, 'blk': 29},
        'SF': {'pts': 19, 'reb': 7, 'ast': 14, 'stl': 18, 'blk': 24},
        'PF': {'pts': 8, 'reb': 10, 'ast': 13, 'stl': 9, 'blk': 28},
        'C': {'pts': 29, 'reb': 10, 'ast': 15, 'stl': 22, 'blk': 27}
    },
    'WAS': {
        'PG': {'pts': 30, 'reb': 30, 'ast': 30, 'stl': 30, 'blk': 26},
        'SG': {'pts': 12, 'reb': 25, 'ast': 15, 'stl': 19, 'blk': 28},
        'SF': {'pts': 14, 'reb': 26, 'ast': 22, 'stl': 27, 'blk': 13},
        'PF': {'pts': 19, 'reb': 26, 'ast': 20, 'stl': 16, 'blk': 12},
        'C': {'pts': 30, 'reb': 30, 'ast': 9, 'stl': 7, 'blk': 14}
    }
}

# Position mapping for players (you can expand this with actual player positions)
PLAYER_POSITIONS = {
    # ===================== GUARDS =====================
    # Point Guards
    'Trae Young':'PG','Luka Doncic':'PG','Damian Lillard':'PG','Stephen Curry':'PG',
    'Kyrie Irving':'PG','Tyrese Haliburton':'PG','Ja Morant':'PG','Jalen Brunson':'PG',
    'Darius Garland':'PG','LaMelo Ball':'PG','De\'Aaron Fox':'PG','Shai Gilgeous-Alexander':'PG',
    'Jrue Holiday':'PG','Jamal Murray':'PG','Fred VanVleet':'PG','Dejounte Murray':'PG',
    'Mike Conley':'PG','Russell Westbrook':'PG','Cade Cunningham':'PG','Scoot Henderson':'PG',
    'Chris Paul':'PG','Immanuel Quickley':'PG','Tyus Jones':'PG','Tre Jones':'PG',
    'Cole Anthony':'PG','T.J. McConnell':'PG','Dennis Schroder':'PG','Malcolm Brogdon':'PG',

    # Shooting Guards
    'Donovan Mitchell':'SG','Devin Booker':'SG','Anthony Edwards':'SG','Zach LaVine':'SG',
    'Tyler Herro':'SG','CJ McCollum':'SG','Jalen Green':'SG','Desmond Bane':'SG',
    'Bradley Beal':'SG','Jaylen Brown':'SG','Paul George':'SG','Klay Thompson':'SG',
    'Jordan Poole':'SG','Anfernee Simons':'SG','Malik Monk':'SG','Austin Reaves':'SG',
    'Josh Giddey':'SG','Alex Caruso':'SG','Norman Powell':'SG','Donte DiVincenzo':'SG',
    'Kevin Huerter':'SG','Gary Trent Jr.':'SG','Jordan Clarkson':'SG','Luke Kennard':'SG',

    # ===================== FORWARDS =====================
    # Small Forwards
    'LeBron James':'SF','Kevin Durant':'SF','Jayson Tatum':'SF','Jimmy Butler':'SF',
    'Brandon Ingram':'SF','Kawhi Leonard':'SF','Mikal Bridges':'SF','Franz Wagner':'SF',
    'OG Anunoby':'SF','Michael Porter Jr.':'SF','RJ Barrett':'SF','Andrew Wiggins':'SF',
    'DeMar DeRozan':'SF','Harrison Barnes':'SF','Cam Johnson':'SF','Josh Hart':'SF',
    'Herbert Jones':'SF','Dillon Brooks':'SF','Kentavious Caldwell-Pope':'SF',

    # Power Forwards
    'Giannis Antetokounmpo':'PF','Zion Williamson':'PF','Julius Randle':'PF','Paolo Banchero':'PF',
    'Evan Mobley':'PF','Jaren Jackson Jr.':'PF','Pascal Siakam':'PF','Jalen Johnson':'PF',
    'Aaron Gordon':'PF','Jerami Grant':'PF','Draymond Green':'PF','Kristaps Porzingis':'PF',
    'John Collins':'PF','Kyle Kuzma':'PF','Naz Reid':'PF','Bobby Portis':'PF',
    'Jabari Smith Jr.':'PF','P.J. Washington':'PF','Tobias Harris':'PF','Kelly Oubre Jr.':'PF',

    # ===================== CENTERS =====================
    'Nikola Jokic':'C','Joel Embiid':'C','Anthony Davis':'C','Bam Adebayo':'C',
    'Rudy Gobert':'C','Jarrett Allen':'C','Domantas Sabonis':'C','Karl-Anthony Towns':'C',
    'Myles Turner':'C','Brook Lopez':'C','Nic Claxton':'C','Ivica Zubac':'C',
    'Clint Capela':'C','Jakob Poeltl':'C','Walker Kessler':'C','Deandre Ayton':'C',
    'Daniel Gafford':'C','Alperen Sengun':'C','Jonas Valanciunas':'C','Mitchell Robinson':'C',
    'Victor Wembanyama':'C','Chet Holmgren':'C','Jusuf Nurkic':'C','Wendell Carter Jr.':'C',
    'Isaiah Hartenstein':'C','Al Horford':'C','Jarrett Vanderbilt':'C'
}


load_dotenv()
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

def get_player_position(player_name):
    '''Get player position, default to SF if unknown'''
    return PLAYER_POSITIONS.get(player_name, 'SF')

def get_defensive_adjustment(opponent_team, player_position, stat_type):
    '''Nonlinear, capped defensive adjustment based on opponent positional matchups'''
    if opponent_team not in DEFENSIVE_MATCHUPS:
        return 1.0

    if player_position not in DEFENSIVE_MATCHUPS[opponent_team]:
        return 1.0

    stat_key_map = {
        'Points': 'pts',
        'Rebounds': 'reb',
        'Assists': 'ast',
        'Steals': 'stl',
        'Blocks': 'blk',
        'Blocked Shots': 'blk',
        '3-Pointers Made': 'pts',
        '3-PT Made': 'pts',
        'Field Goals Made': 'pts',
        'FG Made': 'pts',
        'Free Throws Made': 'pts',
        'Pts+Rebs': 'pts',
        'Pts+Asts': 'pts',
        'Pts+Rebs+Asts': 'pts',
        'Rebs+Asts': 'reb',
        'Blks+Stls': 'blk',
    }

    stat_key = stat_key_map.get(stat_type, 'pts')
    rank = DEFENSIVE_MATCHUPS[opponent_team][player_position].get(stat_key)

    if not rank:
        return 1.0

    # Convert rank ΓåÆ percentile (0 best, 1 worst)
    percentile = (rank - 1) / 29

    # Nonlinear curve (elite defenses matter more)
    adjustment = 0.92 + (percentile ** 1.35) * 0.16

    return max(0.90, min(1.10, adjustment))

def get_pace_adjustment(player_team, opponent_team):
    '''Calculate pace adjustment based on team paces'''
    player_pace = NBA_TEAM_STATS.get(player_team, {}).get('pace', LEAGUE_AVG_PACE)
    opponent_pace = NBA_TEAM_STATS.get(opponent_team, {}).get('pace', LEAGUE_AVG_PACE)
    avg_pace = (player_pace + opponent_pace) / 2
    return avg_pace / LEAGUE_AVG_PACE

def get_rebound_adjustment(player_team, opponent_team, stat_type):
    '''Rebound adj: opponent DREB% and miss proxy via DefRtg'''
    if 'Reb' not in stat_type:
        return 1.0

    opp = NBA_TEAM_STATS.get(opponent_team, {})

    opp_dreb = opp.get('dreb_pct', LEAGUE_AVG_DREB)
    opp_def_rtg = opp.get('def_rtg', LEAGUE_AVG_DEF_RTG)

    # More misses = more rebounds; lower DREB% = more available
    miss_factor = opp_def_rtg / LEAGUE_AVG_DEF_RTG
    dreb_factor = LEAGUE_AVG_DREB / opp_dreb

    adjustment = miss_factor * dreb_factor

    return max(0.92, min(1.08, adjustment))

def get_assist_adjustment(player_team, opponent_team, stat_type):
    '''Assist adj: blend team AST% and opponent pace'''
    if 'Ast' not in stat_type:
        return 1.0

    team_ast_pct = NBA_TEAM_STATS.get(player_team, {}).get('ast_pct', LEAGUE_AVG_AST)
    opp_pace = NBA_TEAM_STATS.get(opponent_team, {}).get('pace', LEAGUE_AVG_PACE)

    adjustment = (team_ast_pct / LEAGUE_AVG_AST) * (opp_pace / LEAGUE_AVG_PACE)

    return max(0.90, min(1.10, adjustment))

def get_efficiency_adjustment(player_team, opponent_team, stat_type):
    '''Efficiency adj for scoring stats using normalized DefRtg'''
    if stat_type not in ['Points', 'Field Goals Made', 'FG Made', '3-Pointers Made', '3-PT Made']:
        return 1.0

    opp_def_rtg = NBA_TEAM_STATS.get(opponent_team, {}).get('def_rtg', LEAGUE_AVG_DEF_RTG)

    adjustment = opp_def_rtg / LEAGUE_AVG_DEF_RTG

    return max(0.93, min(1.07, adjustment))

def calculate_projection(player_stats, line, stat_type, opponent_team, player_position, player_team):
    '''Calculate projection using real stats + blended defense + pace + stat-specific adj'''
    if not player_stats or len(player_stats) == 0:
        return line, 0.5, 'low'

    # Stat mapping
    stat_map = {
        'Points': 'points',
        'Rebounds': 'rebounds',
        'Assists': 'assists',
        'Steals': 'steals',
        'Blocks': 'blocks',
        'Blocked Shots': 'blocks',
        'Turnovers': 'turnovers',
        '3-Pointers Made': 'three_pointers_made',
        '3-PT Made': 'three_pointers_made',
        'Field Goals Made': 'field_goals_made',
        'FG Made': 'field_goals_made',
        'Free Throws Made': 'free_throws_made',
        'Pts+Rebs': lambda s: s.get('points', 0) + s.get('rebounds', 0),
        'Pts+Asts': lambda s: s.get('points', 0) + s.get('assists', 0),
        'Pts+Rebs+Asts': lambda s: s.get('points', 0) + s.get('rebounds', 0) + s.get('assists', 0),
        'Rebs+Asts': lambda s: s.get('rebounds', 0) + s.get('assists', 0),
        'Blks+Stls': lambda s: s.get('blocks', 0) + s.get('steals', 0),
    }

    # Extract values
    if stat_type in stat_map:
        if callable(stat_map[stat_type]):
            values = [stat_map[stat_type](s) for s in player_stats]
        else:
            values = [s.get(stat_map[stat_type], 0) for s in player_stats]
    else:
        return line, 0.5, 'low'

    if len(values) == 0:
        return line, 0.5, 'low'

    # Weighted average (recent games weighted more)
    weights = np.exp(np.linspace(-1, 0, len(values)))
    weights = weights / weights.sum()
    weighted_avg = np.average(values, weights=weights)

    # Blend positional defense and opponent efficiency ONCE
    pos_def_adj = get_defensive_adjustment(opponent_team, player_position, stat_type)
    eff_adj_for_blend = get_efficiency_adjustment(player_team, opponent_team, stat_type)
    def_adj = (pos_def_adj * 0.65) + (eff_adj_for_blend * 0.35)

    adjusted_projection = weighted_avg * def_adj

    # Apply pace adjustment
    pace_adj = get_pace_adjustment(player_team, opponent_team)
    adjusted_projection *= pace_adj

    # Apply stat-specific adjustments
    rebound_adj = get_rebound_adjustment(player_team, opponent_team, stat_type)
    adjusted_projection *= rebound_adj

    assist_adj = get_assist_adjustment(player_team, opponent_team, stat_type)
    adjusted_projection *= assist_adj

    # Calculate standard deviation
    std_dev = np.std(values) if len(values) > 1 else weighted_avg * 0.25

    # Calculate probability
    z_score = (adjusted_projection - line) / (std_dev + 0.01)
    prob_over = scipy_stats.norm.cdf(z_score)

    # Confidence level
    if len(values) >= 10:
        cv = std_dev / (weighted_avg + 0.01)
        confidence = 'high' if cv < 0.3 else 'medium' if cv < 0.5 else 'low'
    else:
        confidence = 'low'

    return round(adjusted_projection, 1), round(prob_over, 4), confidence

def run_script_safely(args: list[str], label: str, timeout: int = 60):
    try:
        print(f"≡ƒöº {label}...")
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout,
        )
        out = (result.stdout or '').strip()
        err = (result.stderr or '').strip()
        if result.returncode == 0:
            if out:
                print(out[:1000])
            print(f"Γ£à {label} complete\n")
            return True
        else:
            if err:
                print(f"ΓÜá∩╕Å  {label} warning:\n{err[:1000]}\n")
            else:
                print(f"ΓÜá∩╕Å  {label} warning: (no error output)\n")
            return False
    except Exception as e:
        print(f"ΓÜá∩╕Å  {label} error: {e}\n")
        return False

def link_props_to_games():
    try:
        print('≡ƒöù Linking props to games (internal, today + tomorrow)...')
        # Load props (id, team, game_id)
        props_resp = supabase.table('props').select('id, team, game_id').limit(5000).execute()
        props = props_resp.data or []
        if not props:
            print('Γä╣∩╕Å  No props to link')
            return True

        # Load games
        games_resp = supabase.table('games').select('id, home_team_abbr, away_team_abbr, game_time').limit(5000).execute()
        games = games_resp.data or []
        if not games:
            print('ΓÜá∩╕Å  No games available to link')
            return False

        # Consider games in the next 48 hours (UTC)
        now = datetime.now(timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)
        def parse_time(s):
            try:
                dt = datetime.fromisoformat((s or '').replace('Z','+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                return None
        window_games = []
        for g in games:
            dt = parse_time(g.get('game_time'))
            if dt and start <= dt <= end:
                window_games.append(g)
        games = window_games
        if not games:
            print('ΓÜá∩╕Å  No games found for today/tomorrow')
            return False

        # Build index by team
        from collections import defaultdict
        by_team = defaultdict(list)
        for g in games:
            home = normalize_team_abbr(g.get('home_team_abbr'))
            away = normalize_team_abbr(g.get('away_team_abbr'))
            if home and home not in ('TBD','UNK'):
                by_team[home].append(g)
            if away and away not in ('TBD','UNK'):
                by_team[away].append(g)

        updated = 0
        skipped = 0
        for p in props:
            team = normalize_team_abbr(p.get('team'))
            if not team or team in ('TBD','UNK'):
                skipped += 1
                continue
            candidates = by_team.get(team, [])
            if not candidates:
                skipped += 1
                continue
            # Choose earliest by time
            def sort_key(g):
                dt = parse_time(g.get('game_time'))
                return dt or end
            chosen = sorted(candidates, key=sort_key)[0]
            if p.get('game_id') != chosen['id']:
                supabase.table('props').update({ 'game_id': chosen['id'] }).eq('id', p['id']).execute()
                updated += 1
        print(f'Γ£à Linked {updated} props, skipped {skipped}')
        return True
    except Exception as e:
        print(f'ΓÜá∩╕Å  Linking error: {e}')
        return False

def step0_refresh_props():
    print('=' * 60)
    print('STEP 0: FETCHING PLAYER PROPS')
    print('=' * 60)
    url = os.getenv('VITE_SUPABASE_URL')
    anon = os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
    if not url or not anon:
        print('Missing Supabase env vars, skipping props refresh')
        return False

    def invoke(fn_name: str):
        try:
            fn_url = f"{url}/functions/v1/{fn_name}"
            headers = {
                'Authorization': f'Bearer {anon}',
                'apikey': anon,
                'Content-Type': 'application/json',
            }
            resp = requests.post(fn_url, headers=headers, timeout=60)
            ok = resp.status_code in (200, 202)
            print(f"Invoke {fn_name}: status {resp.status_code}{' (ok)' if ok else ''}")
            if not ok:
                print(resp.text[:200])
            return ok
        except Exception as e:
            print(f"Error invoking {fn_name}: {e}")
            return False

    # Refresh the current props board
    return invoke('refresh-data')

def clear_props_board():
    """Delete all rows from props to ensure only active board props remain after refresh"""
    try:
        print('≡ƒº╣ Clearing existing props board...')
        ids_resp = supabase.table('props').select('id').limit(100000).execute()
        ids = [row['id'] for row in ids_resp.data or []]
        if not ids:
            print('Γä╣∩╕Å  Props board already empty')
            return True
        # Batch delete to avoid URL size limits
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i+batch_size]
            supabase.table('props').delete().in_('id', batch).execute()
        print(f'Γ£à Deleted {len(ids)} props')
        return True
    except Exception as e:
        print(f'ΓÜá∩╕Å  Could not clear props board: {e}')
        return False

def main():
    print('≡ƒÅÇ ADVANCED PROJECTION MODEL')
    print('=' * 60)

    # Step 0a: Clear props so we only keep active board items
    clear_props_board()

    # Step 0b: Refresh props so projections run on the latest board
    refreshed = step0_refresh_props()
    if refreshed:
        print('Γ£à Props refreshed from board (active only)')
        try:
            print('≡ƒöº Fetching player stats via PowerShell (fetch-stats.ps1)...')
            subprocess.run([
                'powershell',
                '-NoProfile',
                '-ExecutionPolicy', 'Bypass',
                '-File', '.\\fetch-stats.ps1',
                '-NoPause'
            ], check=False)
            print('Γ£à Player stats fetch complete\n')
        except Exception as e:
            print(f'ΓÜá∩╕Å  Could not run fetch-stats.ps1: {e}\n')
    else:
        print('ΓÜá∩╕Å  Could not verify props refresh; continuing with existing props')

    # Fetch today's games from Ball Don't Lie before linking
    ok_games = run_script_safely([sys.executable, 'scripts/fetch_balldontlie_games.py'], "Fetch today's games (Ball Don't Lie)", timeout=40)
    if not ok_games:
        # Secondary: try ESPN games
        run_script_safely([sys.executable, 'scripts/fetch_espn_games.py'], "Fetch today's games (ESPN)", timeout=40)

    # Step 1: Ensure games and teams are linked
    print('≡ƒôè Step 1: Linking Games and Teams')
    print('=' * 60)
    print()

    # Normalize before linking to fix team variants
    run_script_safely([sys.executable, 'scripts/fix_team_abbreviations.py'], 'Normalize team abbreviations', timeout=30)

    # Link props to games (today only)
    link_props_to_games()

    # Re-link once more to catch any late fixes
    link_props_to_games()

    print()
    print('=' * 60)
    print('≡ƒôè Step 2: Calculating Advanced Projections')
    print('=' * 60)
    print()

    # Get all props
    print('≡ƒôÑ Fetching props from database...')
    props_response = supabase.table('props').select('*').execute()
    all_props = props_response.data or []
    print(f'Γ£ô Found {len(all_props)} props')

    # Only process props whose game is scheduled today or tomorrow
    games_window_resp = supabase.table('games').select('id, game_time').execute()
    games_window = games_window_resp.data or []
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)
    def parse_time2(s):
        try:
            dt = datetime.fromisoformat((s or '').replace('Z','+00:00'))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return None
    window_game_ids = set(g['id'] for g in games_window if (parse_time2(g.get('game_time')) and start <= parse_time2(g.get('game_time')) <= end))
    props = [p for p in all_props if p.get('game_id') in window_game_ids]
    print(f'Γ£ô Processing {len(props)} props scheduled for today/tomorrow\n')

    updated = 0
    errors = 0
    skipped = 0
    
    # Show first detailed example
    show_details = 1
    
    for i, prop in enumerate(props, 1):
        try:
            player_name = prop['player_name']
            stat_type = prop['stat_type']
            line = prop['line']
            game_id = prop['game_id']
            
            # Get player stats
            stats_response = supabase.table('player_stats')\
                .select('*')\
                .eq('player_name', player_name)\
                .order('game_date', desc=True)\
                .limit(15)\
                .execute()
            
            player_stats = stats_response.data
            
            # Get game info for opponent
            game_response = supabase.table('games')\
                .select('*')\
                .eq('id', game_id)\
                .single()\
                .execute()
            
            game = game_response.data
            home_team = normalize_team_abbr(game.get('home_team_abbr', 'UNK'))
            away_team = normalize_team_abbr(game.get('away_team_abbr', 'UNK'))
            player_team = normalize_team_abbr(prop.get('team', ''))
            
            # Determine opponent team
            if not player_team:
                skipped += 1
                continue
                
            opponent_team = away_team if player_team == home_team else home_team
            if opponent_team == 'UNK' or not opponent_team:
                skipped += 1
                continue
            
            # Get player position
            player_position = get_player_position(player_name)
            
            # Show detailed info for first prop
            if i <= show_details:
                print(f'\n{"="*60}')
                print(f'DETAILED PROJECTION #{i}')
                print(f'{"="*60}')
                print(f'Player: {player_name} ({player_position})')
                print(f'Stat: {stat_type} | Line: {line}')
                print(f'Team: {player_team} vs {opponent_team}')
                print(f'Games analyzed: {len(player_stats)}')
                print(f'\n≡ƒôè ADJUSTMENTS APPLIED:')
                
                # Show each adjustment
                pos_def = get_defensive_adjustment(opponent_team, player_position, stat_type)
                eff_adj = get_efficiency_adjustment(player_team, opponent_team, stat_type)
                def_adj = (pos_def * 0.65) + (eff_adj * 0.35)
                pace_adj = get_pace_adjustment(player_team, opponent_team)
                reb_adj = get_rebound_adjustment(player_team, opponent_team, stat_type)
                ast_adj = get_assist_adjustment(player_team, opponent_team, stat_type)
                
                print(f'  1. Defense blend: {def_adj:.3f}x (pos: {pos_def:.3f}, eff: {eff_adj:.3f})')
                player_pace = NBA_TEAM_STATS.get(player_team, {}).get('pace', LEAGUE_AVG_PACE)
                opp_pace = NBA_TEAM_STATS.get(opponent_team, {}).get('pace', LEAGUE_AVG_PACE)
                print(f'  2. Pace: {pace_adj:.3f}x ({player_team}: {player_pace:.1f}, {opponent_team}: {opp_pace:.1f})')
                
                if reb_adj != 1.0:
                    opp_dreb = NBA_TEAM_STATS.get(opponent_team, {}).get('dreb_pct', LEAGUE_AVG_DREB)
                    print(f'  3. Rebounds: {reb_adj:.3f}x ({opponent_team} DREB: {opp_dreb:.1f}%)')
                
                if ast_adj != 1.0:
                    team_ast = NBA_TEAM_STATS.get(player_team, {}).get('ast_pct', LEAGUE_AVG_AST)
                    print(f'  4. Assists: {ast_adj:.3f}x ({player_team} AST: {team_ast:.1f}%)')
                
                total_adj = def_adj * pace_adj * reb_adj * ast_adj
                print(f'\n  ≡ƒÄ» TOTAL ADJUSTMENT: {total_adj:.3f}x')
            
            # Calculate projection
            projection, prob_over, confidence = calculate_projection(
                player_stats, line, stat_type, opponent_team, player_position, player_team
            )
            
            # Cap probability between 5% and 95% to avoid extreme edges
            prob_over = max(0.05, min(0.95, prob_over))
            
            # Calculate edge (capped at ┬▒30%)
            edge = (prob_over - 0.5) * 100
            edge = max(-30, min(30, edge))
            
            # Show result for detailed example
            if i <= show_details:
                print(f'\n  ≡ƒôê RESULT:')
                print(f'     Projection: {projection}')
                print(f'     Probability Over: {prob_over:.1%}')
                print(f'     Edge: {edge:+.1f}%')
                print(f'     Confidence: {confidence}')
            
            # Update database
            supabase.table('props').update({
                'projection': projection,
                'probability_over': prob_over,
                'edge': edge,
                'confidence': confidence
            }).eq('id', prop['id']).execute()
            
            updated += 1
            
            if i % 100 == 0:
                print(f'\n[{i}/{len(props)}] Processed {updated} props, {errors} errors, {skipped} skipped')
            
        except Exception as e:
            errors += 1
            if i <= show_details or i % 100 == 0:
                print(f'Γ¥î Error on prop {i}: {str(e)[:80]}')
    
    print()
    print('=' * 60)
    print('Γ£à PROJECTION UPDATE COMPLETE')
    print('=' * 60)
    print(f'Γ£à Successfully updated: {updated}/{len(props)} props')
    print(f'ΓÅ¡∩╕Å  Skipped (no team): {skipped}')
    print(f'Γ¥î Errors: {errors}')
    print()
    print('≡ƒÆí Your projections now include:')
    print('   Γ£ô Real player performance data (last 15 games)')
    print('   Γ£ô Weighted recent games more heavily')
    print('   Γ£ô Blended defense (positional + efficiency) applied once')
    print('   Γ£ô Team pace adjustments (both teams)')
    print('   Γ£ô Rebound adjustments (DREB% + miss proxy)')
    print('   Γ£ô Assist adjustments (team AST% ├ù opp pace)')
    print('   Γ£ô Statistical probability calculations')
    print('   Γ£ô Confidence levels based on consistency')
    print('=' * 60)

if __name__ == '__main__':
    main()
