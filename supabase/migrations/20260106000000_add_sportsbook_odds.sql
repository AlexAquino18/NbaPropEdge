-- Add sportsbook odds columns to props table
ALTER TABLE public.props 
ADD COLUMN prizepicks_odds DECIMAL(10, 2),
ADD COLUMN draftkings_line DECIMAL(10, 2),
ADD COLUMN draftkings_over_odds INTEGER,
ADD COLUMN draftkings_under_odds INTEGER,
ADD COLUMN fanduel_line DECIMAL(10, 2),
ADD COLUMN fanduel_over_odds INTEGER,
ADD COLUMN fanduel_under_odds INTEGER;

-- Add indexes for filtering by sportsbook availability
CREATE INDEX idx_props_prizepicks ON public.props(prizepicks_odds) WHERE prizepicks_odds IS NOT NULL;
CREATE INDEX idx_props_draftkings ON public.props(draftkings_line) WHERE draftkings_line IS NOT NULL;
CREATE INDEX idx_props_fanduel ON public.props(fanduel_line) WHERE fanduel_line IS NOT NULL;

-- Add comment to document the odds format
COMMENT ON COLUMN public.props.prizepicks_odds IS 'PrizePicks line (no odds, just the line)';
COMMENT ON COLUMN public.props.draftkings_over_odds IS 'DraftKings over odds in American format (e.g., -110, +105)';
COMMENT ON COLUMN public.props.draftkings_under_odds IS 'DraftKings under odds in American format (e.g., -110, +105)';
COMMENT ON COLUMN public.props.fanduel_over_odds IS 'FanDuel over odds in American format (e.g., -110, +105)';
COMMENT ON COLUMN public.props.fanduel_under_odds IS 'FanDuel under odds in American format (e.g., -110, +105)';
