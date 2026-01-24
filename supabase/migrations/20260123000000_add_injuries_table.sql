-- Add player_injuries table to track NBA player injuries
CREATE TABLE IF NOT EXISTS player_injuries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_name TEXT NOT NULL UNIQUE,
    team TEXT,
    status TEXT, -- 'out', 'questionable', 'doubtful', 'day-to-day'
    injury_type TEXT, -- 'knee', 'ankle', 'hamstring', etc.
    details TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on player_name for fast lookups
CREATE INDEX IF NOT EXISTS idx_player_injuries_name ON player_injuries(player_name);
CREATE INDEX IF NOT EXISTS idx_player_injuries_status ON player_injuries(status);

-- Enable RLS
ALTER TABLE player_injuries ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Allow public read access to player_injuries"
    ON player_injuries FOR SELECT
    TO public
    USING (true);
