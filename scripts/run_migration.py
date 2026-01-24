import os

# Create SQL for the injuries table
SQL = """
-- Add player_injuries table to track NBA player injuries
CREATE TABLE IF NOT EXISTS player_injuries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_name TEXT NOT NULL UNIQUE,
    team TEXT,
    status TEXT,
    injury_type TEXT,
    details TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
    details TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_player_injuries_name ON player_injuries(player_name);
CREATE INDEX IF NOT EXISTS idx_player_injuries_status ON player_injuries(status);

ALTER TABLE player_injuries ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read access to player_injuries" ON player_injuries;
CREATE POLICY "Allow public read access to player_injuries"
    ON player_injuries FOR SELECT
    TO public
    USING (true);
"""

def run_migration():
    print('🔧 Running Injuries Table Migration')
    print('=' * 60)
    
    try:
        supabase = create_client(
            os.getenv('VITE_SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY')
        )
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'query': SQL}).execute()
        
        print('✅ Migration complete! player_injuries table created.')
        return True
        
    except Exception as e:
        print(f'⚠️  Could not run migration via RPC: {e}')
        print('\n📋 Please run this SQL manually in Supabase Dashboard:')
        print('   https://app.supabase.com → SQL Editor\n')
        print(SQL)
        return False

if __name__ == '__main__':
    run_migration()
