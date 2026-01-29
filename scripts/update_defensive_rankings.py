#!/usr/bin/env python3
"""
Update defensive matchups with latest data from HashtagBasketball
Parses the defense vs position rankings and updates update_projections_with_defense.py
"""

import json
from datetime import datetime

# Raw data from HashtagBasketball (2025-26 season)
# Format: [Position, Team, PTS rank, FG%, FT%, 3PM, REB rank, AST rank, STL rank, BLK rank, TO]
HASHTAG_DATA = """
PF	OKC	1	21.2	26	44.5	38	69.5	8	2.3	50	10.6	110	4.1	36	1.3	20	0.8	77	3.3	10
PG	NY	2	21.0	20	42.9	13	78.9	79	2.9	83	5.4	3	8.7	142	1.6	73	0.5	13	3.5	20
PG	OKC	3	21.5	30	41.4	3	71.3	18	3.4	132	6.5	33	7.4	124	1.6	71	0.5	14	3.9	40
SF	DET	4	21.9	41	43.8	28	78.5	73	2.5	56	7.1	60	3.5	11	1.8	95	1.0	91	3.2	13
PF	PHO	5	20.7	17	45.2	51	77.4	63	1.9	33	10.2	104	4.0	30	1.6	62	1.2	105	3.1	5
PG	DET	6	22.1	45	42.5	9	78.1	67	2.4	52	5.8	9	7.4	123	2.5	148	0.5	11	4.0	11
SG	BOS	7	21.9	42	42.9	12	80.3	93	3.2	126	6.4	30	5.3	106	1.2	12	0.5	17	2.5	61
PF	NO	8	21.7	33	45.0	47	74.4	34	2.5	60	10.4	107	4.3	53	1.3	19	2.0	136	3.0	16
PF	HOU	9	20.6	15	46.3	74	72.4	25	1.9	32	8.4	83	3.4	5	1.5	56	1.2	107	2.0	111
SG	DEN	10	21.6	31	43.1	14	83.5	130	3.0	103	6.5	34	5.0	91	1.3	15	0.5	18	2.4	78
SG	HOU	11	20.9	19	42.0	6	74.1	33	3.0	101	6.3	25	5.1	95	1.9	124	0.6	36	2.6	76
PF	GS	12	21.5	28	46.4	79	76.4	49	2.4	54	10.7	111	4.1	37	1.5	54	1.0	93	3.1	12
SF	MIN	13	20.4	10	43.7	23	81.3	107	2.6	68	7.9	77	3.7	19	1.6	61	0.6	54	2.4	100
SF	BOS	14	22.4	57	43.8	24	79.7	88	3.1	116	8.3	80	3.8	20	1.2	5	0.7	60	2.5	72
C	ORL	15	19.5	6	50.8	120	75.6	41	0.6	1	14.5	140	4.1	40	1.4	32	2.4	146	3.2	2
PF	PHI	16	22.3	50	48.7	109	72.9	27	1.9	31	10.8	112	4.4	56	1.2	10	1.7	128	3.2	9
SF	OKC	17	20.6	12	40.3	1	83.4	126	3.0	92	8.4	82	4.5	68	1.5	50	0.8	80	3.1	24
C	PHO	18	21.1	25	56.1	144	70.2	10	1.2	11	14.7	142	4.1	39	1.4	31	1.9	131	3.1	3
C	ATL	19	21.3	27	54.4	136	75.4	40	0.9	4	15.2	144	4.1	34	1.4	25	1.9	132	3.1	1
C	MEM	20	20.0	8	54.7	140	75.2	38	1.2	13	13.6	126	4.5	65	1.3	17	1.9	133	3.2	6
SF	NY	21	23.7	103	44.8	43	76.7	52	3.2	119	7.7	72	3.9	27	1.3	23	0.6	48	2.7	67
SF	PHO	22	22.3	52	44.7	40	77.3	62	2.9	82	7.4	66	4.5	62	1.8	105	0.4	5	2.9	83
PG	HOU	23	22.8	69	44.7	39	76.0	45	3.0	100	5.6	4	7.9	128	1.8	115	0.6	33	3.7	25
C	OKC	24	18.8	3	46.4	78	71.4	20	1.4	22	14.4	137	3.3	4	1.4	30	1.7	127	2.8	137
C	DET	25	17.9	1	52.5	128	75.9	43	1.3	16	13.0	123	3.5	10	1.7	93	2.1	143	3.1	4
PG	PHI	26	23.5	95	45.6	62	77.2	60	2.8	79	6.2	20	8.1	130	1.7	94	0.3	1	3.4	22
SF	SA	27	21.5	29	45.4	54	76.8	53	2.7	71	7.3	64	4.6	76	1.7	81	0.6	46	2.1	98
C	MIL	28	19.5	7	54.4	137	70.5	12	0.9	3	13.2	124	3.7	18	1.3	21	1.3	110	2.4	144
SG	OKC	29	23.3	87	43.5	16	79.1	83	3.6	143	6.7	43	5.2	100	1.5	46	0.5	15	3.2	45
PF	IND	30	22.1	46	49.1	110	70.9	15	1.4	23	10.3	105	3.8	21	1.2	6	1.4	115	2.6	138
PG	BOS	31	21.1	23	41.6	4	84.4	133	3.2	121	5.8	10	9.2	148	1.5	59	0.6	53	3.2	34
C	BOS	32	20.0	9	49.4	112	72.7	26	1.5	26	13.5	125	3.8	22	1.1	4	1.6	122	2.7	141
PG	BKN	33	21.7	34	43.5	18	81.2	106	2.8	80	5.9	11	8.6	137	1.9	117	0.3	2	2.9	84
SF	DAL	34	20.6	16	43.8	25	79.5	85	2.4	51	8.3	81	4.6	73	1.7	89	0.7	62	2.3	110
SG	ORL	35	22.9	72	44.8	41	81.3	110	2.7	69	6.9	55	5.3	105	1.6	67	0.7	57	3.1	18
PF	SA	36	21.8	38	46.5	80	76.9	56	2.4	55	9.3	93	4.3	52	1.3	18	1.0	95	2.9	108
C	TOR	37	19.3	5	52.4	126	74.1	32	0.9	5	14.4	139	2.9	1	1.2	9	2.0	138	2.6	145
PF	LAC	38	20.6	11	47.3	91	73.8	29	2.0	34	9.4	94	3.9	26	1.8	101	1.2	101	2.4	116
SF	GS	39	22.4	54	46.0	70	87.3	150	2.6	63	7.5	68	4.8	86	1.7	80	0.5	19	3.0	14
C	NY	40	19.0	4	52.8	129	75.1	37	1.4	20	14.4	138	3.0	2	1.1	3	2.0	137	2.5	135
SG	MIN	41	22.7	66	41.3	2	83.0	123	3.0	94	5.9	12	5.4	109	1.7	75	0.6	47	2.9	80
SG	IND	42	23.3	86	45.0	46	80.1	92	3.1	108	7.6	71	4.8	87	1.5	47	0.5	16	2.5	62
SF	ORL	43	21.7	36	46.8	85	81.1	103	2.6	66	7.5	69	3.6	12	1.6	60	0.8	82	2.4	104
PF	TOR	44	21.6	32	48.6	108	76.2	46	2.1	39	11.0	116	3.9	24	1.3	22	1.2	109	3.0	121
SF	TOR	45	21.1	21	46.3	75	78.6	75	2.8	75	7.7	74	4.1	42	1.6	65	1.1	99	2.7	94
C	LAL	46	18.0	2	54.7	139	71.7	22	0.8	2	13.6	127	3.6	14	1.5	58	1.3	114	2.8	143
C	PHI	47	21.1	22	54.4	135	68.2	5	1.4	19	14.2	134	3.1	3	1.4	29	2.1	142	2.6	134
SG	CHI	48	22.6	59	43.6	21	83.4	129	3.5	140	6.2	24	5.1	94	1.7	85	0.5	21	2.2	54
PG	DAL	49	23.2	82	42.4	8	84.6	135	2.6	64	6.5	35	8.6	138	2.0	135	0.5	25	3.3	15
SG	PHO	50	23.6	97	46.1	71	81.2	105	3.1	117	6.4	29	4.9	88	1.5	48	0.6	49	3.4	33
"""

def parse_hashtag_data():
    """Parse the HashtagBasketball data into defensive rankings"""
    print('📊 Parsing HashtagBasketball defense vs position data...')
    
    defensive_matchups = {}
    
    lines = [l.strip() for l in HASHTAG_DATA.strip().split('\n') if l.strip()]
    
    parsed_count = 0
    for line in lines:
        parts = line.split('\t')
        
        if len(parts) < 10:
            continue
        
        try:
            position = parts[0].strip()
            team = parts[1].strip()
            
            # Overall rank (not used, but shows how good the matchup is)
            # overall_rank = int(parts[2])
            
            # Extract the ranking numbers (every other value after team)
            # Format: PTS_val PTS_rank ... REB_val REB_rank ... AST_val AST_rank ... STL_val STL_rank ... BLK_val BLK_rank
            
            print(f'   Stat columns found: {list(stat_cols.keys())}')
            
            # Parse data rows
            current_position = None
            teams_processed = 0
            
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) <= max(pos_col, team_col):
                    continue
                
                # Get position (may span multiple rows)
                pos_text = cells[pos_col].get_text(strip=True)
                if pos_text and pos_text in positions:
                    current_position = pos_text
                
                if not current_position:
                    continue
                
                # Get team name
                team_cell = cells[team_col].get_text(strip=True)
                
                # Match team abbreviation
                team_abbr = None
                for team_name, abbr in team_name_to_abbr.items():
                    if team_name.lower() in team_cell.lower():
                        team_abbr = abbr
                        break
                
                if not team_abbr:
                    # Try direct match if it's already an abbreviation
                    if len(team_cell) == 3 and team_cell.upper() in defensive_data:
                        team_abbr = team_cell.upper()
                
                if not team_abbr:
                    continue
                
                # Extract rankings for each stat
                for stat_name, col_idx in stat_cols.items():
                    if col_idx < len(cells):
                        try:
                            cell_text = cells[col_idx].get_text(strip=True)
                            # Rankings might be formatted as "5th" or just "5"
                            rank_match = re.search(r'(\d+)', cell_text)
                            if rank_match:
                                rank = int(rank_match.group(1))
                                if 1 <= rank <= 30:  # Valid rank
                                    defensive_data[team_abbr][current_position][stat_name] = rank
                                    teams_processed += 1
                        except (ValueError, IndexError):
                            continue
            
            print(f'   ✅ Processed {teams_processed} data points')
        
        # Count how many teams have data
        teams_with_data = sum(1 for team_data in defensive_data.values() 
                               if any(pos_data for pos_data in team_data.values()))
        
        print(f'✅ Scraped defense data for {teams_with_data} teams')
        
        if teams_with_data > 0:
            # Show sample
            sample_team = next((t for t, d in defensive_data.items() if any(p for p in d.values())), None)
            if sample_team:
                print(f'\nSample data - {sample_team}:')
                for pos, stats in defensive_data[sample_team].items():
                    if stats:
                        print(f'  {pos}: {stats}')
        
        return defensive_data if teams_with_data > 0 else None
        
    except Exception as e:
        print(f'❌ Error scraping HashtagBasketball: {e}')
        import traceback
        traceback.print_exc()
        return None

def save_defensive_data(data):
    """Save defensive data to JSON file"""
    if not data:
        return False
    
    output_file = 'scripts/defensive_matchups_live.json'
    
    with open(output_file, 'w') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'data': data
        }, f, indent=2)
    
    print(f'💾 Saved defensive data to {output_file}')
    return True

def main():
    print('=' * 60)
    print('UPDATING DEFENSIVE MATCHUP DATA')
    print('=' * 60)
    print()
    
    data = scrape_hashtag_basketball_defense()
    
    if data:
        save_defensive_data(data)
        print()
        print('=' * 60)
        print('✅ DEFENSIVE DATA UPDATE COMPLETE')
        print('=' * 60)
        teams_count = sum(1 for t in data.values() if any(p for p in t.values()))
        print(f'Updated {teams_count} teams')
        print('Next: Projections will use this live data')
    else:
        print()
        print('=' * 60)
        print('⚠️  COULD NOT UPDATE DEFENSIVE DATA')
        print('=' * 60)
        print('Using existing static defensive rankings')
        print('\n💡 Your current defensive rankings are already comprehensive!')
        print('   They cover all 30 teams with position-specific rankings for:')
        print('   • Points, Rebounds, Assists, Steals, Blocks')
        print('   • All positions (PG, SG, SF, PF, C)')

if __name__ == '__main__':
    main()
