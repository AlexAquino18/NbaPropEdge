import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Supabase PostgreSQL connection string
# Format: postgresql://postgres:[YOUR-PASSWORD]@db.aimvwybpqhykuwiqddzu.supabase.co:5432/postgres
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print('ERROR: DATABASE_URL not found in .env file')
    print('Please add this line to your .env file:')
    print('DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.aimvwybpqhykuwiqddzu.supabase.co:5432/postgres')
    exit(1)

print('=' * 60)
print('CREATING ODDS_HISTORY TABLE IN SUPABASE')
print('=' * 60)

sql_statements = [
    """
    CREATE TABLE IF NOT EXISTS public.odds_history (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        player_id UUID,
        player_name TEXT NOT NULL,
        stat_type TEXT NOT NULL,
        game_id UUID,
        sportsbook TEXT NOT NULL,
        line DECIMAL(10,2) NOT NULL,
        over_odds INTEGER NOT NULL,
        under_odds INTEGER NOT NULL,
        recorded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_odds_history_player_stat 
        ON public.odds_history(player_name, stat_type)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_odds_history_game 
        ON public.odds_history(game_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_odds_history_recorded 
        ON public.odds_history(recorded_at DESC)
    """,
    """
    ALTER TABLE public.odds_history ENABLE ROW LEVEL SECURITY
    """,
    """
    DROP POLICY IF EXISTS "Allow public read access" ON public.odds_history
    """,
    """
    CREATE POLICY "Allow public read access" ON public.odds_history
        FOR SELECT USING (true)
    """,
]

try:
    print('\nConnecting to database...')
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    for i, sql in enumerate(sql_statements):
        print(f'[{i+1}/{len(sql_statements)}] Executing statement...')
        try:
            cursor.execute(sql)
            conn.commit()
            print('✅ Success')
        except Exception as e:
            print(f'⚠️ {str(e)}')
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print('\n' + '=' * 60)
    print('✅ TABLE CREATED SUCCESSFULLY!')
    print('=' * 60)
    print('\nNext steps:')
    print('1. Run: python upload_odds_to_supabase.py')
    
except Exception as e:
    print(f'\n❌ Error connecting to database: {e}')
    print('\nMake sure your .env file has:')
    print('DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.aimvwybpqhykuwiqddzu.supabase.co:5432/postgres')
