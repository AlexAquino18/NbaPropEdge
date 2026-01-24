import os
import requests
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone

load_dotenv()
supabase = create_client(
    os.getenv('VITE_SUPABASE_URL'),
    os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
)

BALLDONTLIE_API = 'https://api.balldontlie.io/v1'

def fetch_injuries():
    """Fetch current NBA player injuries from Ball Don't Lie API"""
    print('🏥 FETCHING NBA INJURIES')
    print('=' * 60)
    
    try:
        # Ball Don't Lie doesn't have a dedicated injuries endpoint
        # We'll need to track this differently - using a manual injuries table
        # Or scraping from an injuries API like sportsdata.io or ESPN
        
        # For now, let's create a structure to manually track key injuries
        # You can populate this from news sources or other APIs
        
        print('⚠️  Ball Don\'t Lie API does not provide injury data')
        print('📝 To track injuries, you can:')
        print('   1. Use ESPN injury API: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard')
        print('   2. Use sportsdata.io (paid): https://sportsdata.io/')
        print('   3. Manually update injuries table in Supabase')
        print('   4. Web scrape from ESPN injury report')
        
        # Let's try ESPN injury data
        fetch_espn_injuries()
        
    except Exception as e:
        print(f'❌ Error fetching injuries: {e}')
        return False

def fetch_espn_injuries():
    """Fetch injuries from ESPN API"""
    try:
        url = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        injuries = []
        now = datetime.now(timezone.utc).isoformat()
        
        # ESPN includes injuries in game data
        if 'events' in data:
            for event in data['events']:
                for competition in event.get('competitions', []):
                    for competitor in competition.get('competitors', []):
                        team = competitor.get('team', {}).get('abbreviation')
                        
                        # Check for injuries in roster
                        for athlete in competitor.get('athletes', []):
                            injury_status = athlete.get('injuries')
                            if injury_status:
                                for injury in injury_status:
                                    player_name = athlete.get('displayName')
                                    status = injury.get('status', 'unknown')
                                    details = injury.get('details', {})
                                    injury_type = details.get('type', 'unknown')
                                    
                                    injuries.append({
                                        'player_name': player_name,
                                        'team': team,
                                        'status': status,
                                        'injury_type': injury_type,
                                        'updated_at': now
                                    })
        
        if injuries:
            print(f'📋 Found {len(injuries)} injured players')
            
            # Upsert injuries to Supabase
            for injury in injuries:
                try:
                    supabase.table('player_injuries').upsert(injury, on_conflict='player_name').execute()
                except Exception as e:
                    print(f'⚠️  Could not upsert injury for {injury.get("player_name")}: {e}')
            
            print(f'✅ Upserted {len(injuries)} injuries')
            
            # Print summary
            print('\n📊 Injury Summary:')
            for injury in injuries[:10]:  # Show first 10
                print(f'  • {injury["player_name"]} ({injury["team"]}): {injury["status"]} - {injury["injury_type"]}')
            
            if len(injuries) > 10:
                print(f'  ... and {len(injuries) - 10} more')
            
            return True
        else:
            print('ℹ️  No injuries found in ESPN data')
            return False
            
    except Exception as e:
        print(f'❌ Error fetching ESPN injuries: {e}')
        return False

if __name__ == '__main__':
    fetch_injuries()
