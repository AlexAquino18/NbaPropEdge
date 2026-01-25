
-- Create odds_history table for tracking line movements
CREATE TABLE IF NOT EXISTS public.odds_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    player_id UUID REFERENCES public.players(id) ON DELETE CASCADE,
    player_name TEXT NOT NULL,
    stat_type TEXT NOT NULL,
    game_id UUID REFERENCES public.games(id) ON DELETE CASCADE,
    sportsbook TEXT NOT NULL,
    line DECIMAL(10,2) NOT NULL,
    over_odds INTEGER NOT NULL,
    under_odds INTEGER NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_odds_history_player_stat 
    ON public.odds_history(player_name, stat_type);
    
CREATE INDEX IF NOT EXISTS idx_odds_history_game 
    ON public.odds_history(game_id);
    
CREATE INDEX IF NOT EXISTS idx_odds_history_recorded 
    ON public.odds_history(recorded_at DESC);

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
