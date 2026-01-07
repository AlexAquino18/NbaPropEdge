-- Create games table for NBA games
CREATE TABLE public.games (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  external_id TEXT UNIQUE,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  home_team_abbr TEXT,
  away_team_abbr TEXT,
  game_time TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT DEFAULT 'scheduled',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create props table for player props
CREATE TABLE public.props (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  game_id UUID REFERENCES public.games(id) ON DELETE CASCADE,
  external_id TEXT UNIQUE,
  player_name TEXT NOT NULL,
  player_id TEXT,
  team TEXT,
  stat_type TEXT NOT NULL,
  line DECIMAL(10, 2) NOT NULL,
  projection DECIMAL(10, 2),
  edge DECIMAL(10, 4),
  probability_over DECIMAL(5, 4),
  confidence TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create player_stats table for historical stats
CREATE TABLE public.player_stats (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  player_name TEXT NOT NULL,
  player_id TEXT,
  game_date DATE NOT NULL,
  opponent TEXT,
  minutes DECIMAL(5, 2),
  points INTEGER,
  rebounds INTEGER,
  assists INTEGER,
  steals INTEGER,
  blocks INTEGER,
  turnovers INTEGER,
  three_pointers_made INTEGER,
  field_goals_made INTEGER,
  field_goals_attempted INTEGER,
  free_throws_made INTEGER,
  free_throws_attempted INTEGER,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(player_name, game_date)
);

-- Create indexes for better query performance
CREATE INDEX idx_props_game_id ON public.props(game_id);
CREATE INDEX idx_props_stat_type ON public.props(stat_type);
CREATE INDEX idx_props_edge ON public.props(edge DESC);
CREATE INDEX idx_player_stats_player ON public.player_stats(player_name);
CREATE INDEX idx_player_stats_date ON public.player_stats(game_date DESC);
CREATE INDEX idx_games_time ON public.games(game_time);

-- Enable RLS but make tables publicly readable (no auth required)
ALTER TABLE public.games ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.props ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.player_stats ENABLE ROW LEVEL SECURITY;

-- Public read access for all tables
CREATE POLICY "Public read access for games" ON public.games FOR SELECT USING (true);
CREATE POLICY "Public read access for props" ON public.props FOR SELECT USING (true);
CREATE POLICY "Public read access for player_stats" ON public.player_stats FOR SELECT USING (true);

-- Service role can insert/update/delete (for edge functions)
CREATE POLICY "Service role full access for games" ON public.games FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access for props" ON public.props FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access for player_stats" ON public.player_stats FOR ALL USING (true) WITH CHECK (true);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_games_updated_at
  BEFORE UPDATE ON public.games
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_props_updated_at
  BEFORE UPDATE ON public.props
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();