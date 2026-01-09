import os
import time
from dotenv import load_dotenv
from supabase import create_client
import numpy as np
from scipy import stats as scipy_stats
import subprocess
import sys

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
    
   
}

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
    '''Calculate defensive adjustment based on opponent's stat-specific defensive ranking'''
    if opponent_team not in DEFENSIVE_MATCHUPS:
        return 1.0
    
    if player_position not in DEFENSIVE_MATCHUPS[opponent_team]:
        return 1.0
    
    # Map stat types to defensive ranking keys
    stat_key_map = {
        'Points': 'pts',
        'Rebounds': 'reb',
        'Assists': 'ast',
        'Steals': 'stl',
        'Blocks': 'blk',
        'Blocked Shots': 'blk',
        '3-Pointers Made': 'pts',  # Use points defense for 3PT
        '3-PT Made': 'pts',
        'Field Goals Made': 'pts',
        'FG Made': 'pts',
        'Free Throws Made': 'pts',
        'Pts+Rebs': 'pts',  # Use points for combos (primary stat)
        'Pts+Asts': 'pts',
        'Pts+Rebs+Asts': 'pts',
        'Rebs+Asts': 'reb',
        'Blks+Stls': 'blk',
    }
    
    # Get the appropriate stat key
    stat_key = stat_key_map.get(stat_type, 'pts')
    
    # Get the defensive rank for this specific stat
    def_rankings = DEFENSIVE_MATCHUPS[opponent_team][player_position]
    if stat_key not in def_rankings:
        return 1.0
    
    rank = def_rankings[stat_key]
    
    # Convert rank (1-30) to adjustment factor
    # Rank 1 = elite defense (hardest) = 0.85x (reduce by 15%)
    # Rank 15.5 = average defense = 1.00x (no adjustment)
    # Rank 30 = worst defense (easiest) = 1.15x (boost by 15%)
    
    # Linear scaling across full range
    adjustment = 0.85 + ((rank - 1) / 29) * 0.30
    
    return adjustment

def get_pace_adjustment(player_team, opponent_team):
    '''Calculate pace adjustment based on team paces'''
    player_pace = NBA_TEAM_STATS.get(player_team, {}).get('pace', LEAGUE_AVG_PACE)
    opponent_pace = NBA_TEAM_STATS.get(opponent_team, {}).get('pace', LEAGUE_AVG_PACE)
    avg_pace = (player_pace + opponent_pace) / 2
    return avg_pace / LEAGUE_AVG_PACE

def get_rebound_adjustment(player_team, opponent_team, stat_type):
    '''Calculate rebound adjustment based on opponent's defensive rebounding'''
    if 'Reb' not in stat_type:
        return 1.0
    
    opp_stats = NBA_TEAM_STATS.get(opponent_team, {})
    opp_dreb_pct = opp_stats.get('dreb_pct', LEAGUE_AVG_DREB)
    
    # Lower opponent DREB% = more rebounds available for offensive rebounds
    # Use ratio approach: if opponent grabs fewer DREBs, more available
    # 65% DREB = 1.06x boost, 69% (avg) = 1.0x, 73% DREB = 0.95x penalty
    adjustment = LEAGUE_AVG_DREB / opp_dreb_pct
    return max(0.90, min(1.10, adjustment))  # Cap between 0.90-1.10

def get_assist_adjustment(player_team, opponent_team, stat_type):
    '''Calculate assist adjustment based on team's assist rate and opponent pace'''
    if 'Ast' not in stat_type:
        return 1.0
    
    team_stats = NBA_TEAM_STATS.get(player_team, {})
    team_ast_pct = team_stats.get('ast_pct', LEAGUE_AVG_AST)
    
    # Higher team AST% = more assist opportunities for floor generals
    adjustment = team_ast_pct / LEAGUE_AVG_AST
    return max(0.90, min(1.10, adjustment))  # Cap between 0.90-1.10

def get_efficiency_adjustment(player_team, opponent_team, stat_type):
    '''Calculate efficiency-based adjustments for scoring stats'''
    if stat_type not in ['Points', 'Field Goals Made', 'FG Made', '3-Pointers Made', '3-PT Made']:
        return 1.0
    
    opp_stats = NBA_TEAM_STATS.get(opponent_team, {})
    opp_def_rtg = opp_stats.get('def_rtg', 113.0)
    
    # Lower opponent DefRtg = HARDER to score (elite defense)
    # 105 DefRtg (elite) = 0.93x, 113 DefRtg (avg) = 1.0x, 120 DefRtg (poor) = 1.06x
    adjustment = 1.0 - ((113.0 - opp_def_rtg) / 100)
    return max(0.90, min(1.10, adjustment))

def calculate_projection(player_stats, line, stat_type, opponent_team, player_position, player_team):
    '''Calculate projection using real stats + defensive adjustments + pace adjustments'''
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
    
    # Apply defensive adjustment (position-specific)
    defensive_adj = get_defensive_adjustment(opponent_team, player_position, stat_type)
    adjusted_projection = weighted_avg * defensive_adj
    
    # Apply pace adjustment
    pace_adj = get_pace_adjustment(player_team, opponent_team)
    adjusted_projection *= pace_adj
    
    # Apply stat-specific adjustments
    rebound_adj = get_rebound_adjustment(player_team, opponent_team, stat_type)
    adjusted_projection *= rebound_adj
    
    assist_adj = get_assist_adjustment(player_team, opponent_team, stat_type)
    adjusted_projection *= assist_adj
    
    efficiency_adj = get_efficiency_adjustment(player_team, opponent_team, stat_type)
    adjusted_projection *= efficiency_adj
    
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

def main():
    print('🏀 ADVANCED PROJECTION MODEL')
    print('=' * 60)
    print('📊 Step 1: Fetching Today\'s NBA Games')
    print('=' * 60)
    print()
    
    # Run the Ball Don't Lie games fetcher first
    print('🔄 Running Ball Don\'t Lie API to get today\'s games...\n')
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/fetch_balldontlie_games.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print('✅ Games loaded successfully!\n')
        else:
            print('⚠️  Warning: Could not fetch games automatically')
            print(result.stderr)
            print('\n⚠️  Continuing with existing games in database...\n')
    except Exception as e:
        print(f'⚠️  Warning: {e}')
        print('⚠️  Continuing with existing games in database...\n')
    
    print()
    print('=' * 60)
    print('📊 Step 2: Calculating Advanced Projections')
    print('=' * 60)
    print()
    
    # Get all props
    print('📥 Fetching props from database...')
    props_response = supabase.table('props').select('*').execute()
    props = props_response.data
    print(f'✓ Found {len(props)} props\n')
    
    updated = 0
    errors = 0
    skipped = 0
    
    # Show first 3 detailed examples
    show_details = 3
    
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
            
            # Get player position
            player_position = get_player_position(player_name)
            
            # Show detailed info for first few props
            if i <= show_details:
                print(f'\n{"="*60}')
                print(f'DETAILED PROJECTION #{i}')
                print(f'{"="*60}')
                print(f'Player: {player_name} ({player_position})')
                print(f'Stat: {stat_type} | Line: {line}')
                print(f'Team: {player_team} vs {opponent_team}')
                print(f'Games analyzed: {len(player_stats)}')
                print(f'\n📊 ADJUSTMENTS APPLIED:')
                
                # Show each adjustment
                def_adj = get_defensive_adjustment(opponent_team, player_position, stat_type)
                pace_adj = get_pace_adjustment(player_team, opponent_team)
                reb_adj = get_rebound_adjustment(player_team, opponent_team, stat_type)
                ast_adj = get_assist_adjustment(player_team, opponent_team, stat_type)
                eff_adj = get_efficiency_adjustment(player_team, opponent_team, stat_type)
                
                print(f'  1. Defensive Matchup: {def_adj:.3f}x', end='')
                if opponent_team in DEFENSIVE_MATCHUPS and player_position in DEFENSIVE_MATCHUPS[opponent_team]:
                    rank = DEFENSIVE_MATCHUPS[opponent_team][player_position]
                    print(f' (Rank: {rank}/150 vs {player_position})')
                else:
                    print(f' (No data)')
                
                player_pace = NBA_TEAM_STATS.get(player_team, {}).get('pace', LEAGUE_AVG_PACE)
                opp_pace = NBA_TEAM_STATS.get(opponent_team, {}).get('pace', LEAGUE_AVG_PACE)
                print(f'  2. Pace: {pace_adj:.3f}x ({player_team}: {player_pace:.1f}, {opponent_team}: {opp_pace:.1f})')
                
                if reb_adj != 1.0:
                    opp_dreb = NBA_TEAM_STATS.get(opponent_team, {}).get('dreb_pct', LEAGUE_AVG_DREB)
                    print(f'  3. Rebounds: {reb_adj:.3f}x ({opponent_team} DREB: {opp_dreb:.1f}%)')
                
                if ast_adj != 1.0:
                    team_ast = NBA_TEAM_STATS.get(player_team, {}).get('ast_pct', LEAGUE_AVG_AST)
                    print(f'  4. Assists: {ast_adj:.3f}x ({player_team} AST: {team_ast:.1f}%)')
                
                if eff_adj != 1.0:
                    opp_def = NBA_TEAM_STATS.get(opponent_team, {}).get('def_rtg', 113.0)
                    print(f'  5. Efficiency: {eff_adj:.3f}x ({opponent_team} DefRtg: {opp_def:.1f})')
                
                total_adj = def_adj * pace_adj * reb_adj * ast_adj * eff_adj
                print(f'\n  🎯 TOTAL ADJUSTMENT: {total_adj:.3f}x')
            
            # Calculate projection
            projection, prob_over, confidence = calculate_projection(
                player_stats, line, stat_type, opponent_team, player_position, player_team
            )
            
            # Cap probability between 5% and 95% to avoid extreme edges
            prob_over = max(0.05, min(0.95, prob_over))
            
            # Calculate edge (capped at ±30%)
            edge = (prob_over - 0.5) * 100
            edge = max(-30, min(30, edge))
            
            # Show result for detailed examples
            if i <= show_details:
                print(f'\n  📈 RESULT:')
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
                print(f'❌ Error on prop {i}: {str(e)[:80]}')
    
    print()
    print('=' * 60)
    print('✅ PROJECTION UPDATE COMPLETE')
    print('=' * 60)
    print(f'✅ Successfully updated: {updated}/{len(props)} props')
    print(f'⏭️  Skipped (no team): {skipped}')
    print(f'❌ Errors: {errors}')
    print()
    print('💡 Your projections now include:')
    print('   ✓ Real player performance data (last 15 games)')
    print('   ✓ Weighted recent games more heavily')
    print('   ✓ Defensive matchup adjustments by position')
    print('   ✓ Team pace adjustments (both teams)')
    print('   ✓ Rebound adjustments (opponent DREB%)')
    print('   ✓ Assist adjustments (team AST%)')
    print('   ✓ Scoring efficiency (opponent DefRtg)')
    print('   ✓ Statistical probability calculations')
    print('   ✓ Confidence levels based on consistency')
    print('=' * 60)

if __name__ == '__main__':
    main()
