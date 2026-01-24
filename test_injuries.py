import requests
from bs4 import BeautifulSoup

url = 'https://sportsethos.com/live-injury-report/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print('🏥 Scraping NBA injuries from sportsethos.com...\n')

response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

tables = soup.find_all('table')
print(f'📋 Found {len(tables)} team tables\n')

injuries = []

for table in tables:
    rows = table.find_all('tr')
    
    for row in rows[1:]:  # Skip header
        cells = row.find_all(['td', 'th'])
        
        if len(cells) >= 3:
            player_name = cells[0].get_text(strip=True)
            team = cells[1].get_text(strip=True)
            status = cells[2].get_text(strip=True)
            
            if player_name and team and status:
                injuries.append((player_name, team, status))

print(f'✅ Found {len(injuries)} total injured players\n')
print('=' * 70)
print(f'{"#":<4} {"Player":<30} {"Team":<6} {"Status"}')
print('=' * 70)

for i, (name, team, status) in enumerate(injuries[:20], 1):
    print(f'{i:<4} {name[:29]:<30} {team:<6} {status}')

if len(injuries) > 20:
    print(f'\n... and {len(injuries) - 20} more injured players')

print('\n' + '=' * 70)
print(f'\n📊 Summary by status:')

from collections import Counter
status_counts = Counter([status.lower() for _, _, status in injuries])

for status, count in status_counts.most_common():
    print(f'   {status}: {count} players')
