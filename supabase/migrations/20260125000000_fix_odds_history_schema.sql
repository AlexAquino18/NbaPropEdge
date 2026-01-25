-- Create odds_history table with correct schema for tracking DraftKings and FanDuel odds
CREATE TABLE IF NOT EXISTS public.odds_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    prop_id UUID REFERENCES public.props(id) ON DELETE SET NULL,
    player_name TEXT NOT NULL,
    stat_type TEXT NOT NULL,
    draftkings_line DECIMAL(10,2),
    draftkings_over_odds INTEGER,
    draftkings_under_odds INTEGER,
    fanduel_line DECIMAL(10,2),
    fanduel_over_odds INTEGER,
    fanduel_under_odds INTEGER,
    prizepicks_line DECIMAL(10,2),
    recorded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_odds_history_player_stat 
    ON public.odds_history(player_name, stat_type);
    
CREATE INDEX IF NOT EXISTS idx_odds_history_recorded 
    ON public.odds_history(recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_odds_history_prop
    ON public.odds_history(prop_id);

-- Enable Row Level Security
ALTER TABLE public.odds_history ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access
DROP POLICY IF EXISTS "Allow public read access" ON public.odds_history;
CREATE POLICY "Allow public read access" ON public.odds_history
    FOR SELECT USING (true);

-- Create policy to allow authenticated insert
DROP POLICY IF EXISTS "Allow authenticated insert" ON public.odds_history;
CREATE POLICY "Allow authenticated insert" ON public.odds_history
    FOR INSERT WITH CHECK (true);

-- Grant permissions
GRANT SELECT ON public.odds_history TO anon, authenticated;
GRANT INSERT ON public.odds_history TO authenticated;
