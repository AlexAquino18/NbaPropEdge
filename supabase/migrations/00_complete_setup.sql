-- =====================================================
-- COMPLETE DATABASE SETUP
-- Run this script in Supabase SQL Editor to set up everything
-- =====================================================

-- Migration 1: Create tables
-- Create games table for NBA games
CREATE TABLE IF NOT EXISTS public.games (
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
CREATE TABLE IF NOT EXISTS public.props (
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
CREATE TABLE IF NOT EXISTS public.player_stats (
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
CREATE INDEX IF NOT EXISTS idx_props_game_id ON public.props(game_id);
CREATE INDEX IF NOT EXISTS idx_props_stat_type ON public.props(stat_type);
CREATE INDEX IF NOT EXISTS idx_props_edge ON public.props(edge DESC);
CREATE INDEX IF NOT EXISTS idx_player_stats_player ON public.player_stats(player_name);
CREATE INDEX IF NOT EXISTS idx_player_stats_date ON public.player_stats(game_date DESC);
CREATE INDEX IF NOT EXISTS idx_games_time ON public.games(game_time);

-- Enable RLS but make tables publicly readable (no auth required)
ALTER TABLE public.games ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.props ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.player_stats ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Public read access for games" ON public.games;
DROP POLICY IF EXISTS "Public read access for props" ON public.props;
DROP POLICY IF EXISTS "Public read access for player_stats" ON public.player_stats;
DROP POLICY IF EXISTS "Service role full access for games" ON public.games;
DROP POLICY IF EXISTS "Service role full access for props" ON public.props;
DROP POLICY IF EXISTS "Service role full access for player_stats" ON public.player_stats;

-- Public read access for all tables
CREATE POLICY "Public read access for games" ON public.games FOR SELECT USING (true);
CREATE POLICY "Public read access for props" ON public.props FOR SELECT USING (true);
CREATE POLICY "Public read access for player_stats" ON public.player_stats FOR SELECT USING (true);

-- Service role can insert/update/delete (for edge functions)
CREATE POLICY "Service role full access for games" ON public.games FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access for props" ON public.props FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access for player_stats" ON public.player_stats FOR ALL USING (true) WITH CHECK (true);

-- Migration 2: Create function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql
SET search_path = public;

-- Create triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS update_games_updated_at ON public.games;
DROP TRIGGER IF EXISTS update_props_updated_at ON public.props;

CREATE TRIGGER update_games_updated_at
  BEFORE UPDATE ON public.games
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_props_updated_at
  BEFORE UPDATE ON public.props
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Migration 3: Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_net;

-- Migration 4: Add sportsbook odds columns to props table
ALTER TABLE public.props 
ADD COLUMN IF NOT EXISTS prizepicks_odds DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS draftkings_line DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS draftkings_over_odds INTEGER,
ADD COLUMN IF NOT EXISTS draftkings_under_odds INTEGER,
ADD COLUMN IF NOT EXISTS fanduel_line DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS fanduel_over_odds INTEGER,
ADD COLUMN IF NOT EXISTS fanduel_under_odds INTEGER;

-- Add indexes for filtering by sportsbook availability
CREATE INDEX IF NOT EXISTS idx_props_prizepicks ON public.props(prizepicks_odds) WHERE prizepicks_odds IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_props_draftkings ON public.props(draftkings_line) WHERE draftkings_line IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_props_fanduel ON public.props(fanduel_line) WHERE fanduel_line IS NOT NULL;

-- Add comments to document the odds format
COMMENT ON COLUMN public.props.prizepicks_odds IS 'PrizePicks line (no odds, just the line)';
COMMENT ON COLUMN public.props.draftkings_over_odds IS 'DraftKings over odds in American format (e.g., -110, +105)';
COMMENT ON COLUMN public.props.draftkings_under_odds IS 'DraftKings under odds in American format (e.g., -110, +105)';
COMMENT ON COLUMN public.props.fanduel_over_odds IS 'FanDuel over odds in American format (e.g., -110, +105)';
COMMENT ON COLUMN public.props.fanduel_under_odds IS 'FanDuel under odds in American format (e.g., -110, +105)';

-- =====================================================
-- Setup complete!
-- =====================================================
