export interface Game {
  id: string;
  external_id: string | null;
  home_team: string;
  away_team: string;
  home_team_abbr: string | null;
  away_team_abbr: string | null;
  game_time: string;
  status: string | null;
  created_at: string;
  updated_at: string;
}

export interface Prop {
  id: string;
  game_id: string | null;
  external_id: string | null;
  player_name: string;
  player_id: string | null;
  team: string | null;
  stat_type: string;
  line: number;
  projection: number | null;
  edge: number | null;
  probability_over: number | null;
  confidence: string | null;
  created_at: string;
  updated_at: string;
  // Sportsbook odds
  prizepicks_odds: number | null;
  draftkings_line: number | null;
  draftkings_over_odds: number | null;
  draftkings_under_odds: number | null;
  fanduel_line: number | null;
  fanduel_over_odds: number | null;
  fanduel_under_odds: number | null;
}

export interface PlayerStat {
  id: string;
  player_name: string;
  player_id: string | null;
  game_date: string;
  opponent: string | null;
  minutes: number | null;
  points: number | null;
  rebounds: number | null;
  assists: number | null;
  steals: number | null;
  blocks: number | null;
  turnovers: number | null;
  three_pointers_made: number | null;
  field_goals_made: number | null;
  field_goals_attempted: number | null;
  free_throws_made: number | null;
  free_throws_attempted: number | null;
  created_at: string;
}

export interface GameWithProps extends Game {
  props: Prop[];
  topProps: Prop[];
}

export type StatType = 
  | 'Points'
  | 'Rebounds'
  | 'Assists'
  | 'Pts+Rebs+Asts'
  | 'Pts+Rebs'
  | 'Pts+Asts'
  | 'Rebs+Asts'
  | '3-Pointers Made'
  | 'Steals'
  | 'Blocks'
  | 'Turnovers'
  | 'Fantasy Score';

export const STAT_TYPES: StatType[] = [
  'Points',
  'Rebounds',
  'Assists',
  'Pts+Rebs+Asts',
  'Pts+Rebs',
  'Pts+Asts',
  'Rebs+Asts',
  '3-Pointers Made',
  'Steals',
  'Blocks',
  'Turnovers',
  'Fantasy Score',
];
