import { supabase } from '@/integrations/supabase/client';
import type { PlayerStat } from '@/types';

const API_BASE_URL = 'http://localhost:5000/api';

export interface OddsHistoryPoint {
  player_name: string;
  stat_type: string;
  draftkings_line: number | null;
  draftkings_over_odds: number | null;
  draftkings_under_odds: number | null;
  fanduel_line: number | null;
  fanduel_over_odds: number | null;
  fanduel_under_odds: number | null;
  recorded_at: string;
}

export async function fetchGameById(gameId: string) {
  try {
    const { data, error } = await supabase
      .from('games')
      .select('*')
      .eq('id', gameId)
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error fetching game:', error);
    throw error;
  }
}

export async function fetchPropsForGame(gameId: string) {
  try {
    const { data, error } = await supabase
      .from('props')
      .select('*')
      .eq('game_id', gameId)
      .order('edge', { ascending: false, nullsFirst: false });
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching props:', error);
    return [];
  }
}

export async function fetchRealPlayerStats(playerName: string) {
  try {
    const { data, error } = await supabase
      .from('player_stats')
      .select('*')
      .eq('player_name', playerName)
      .order('game_date', { ascending: false })
      .limit(15);
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching real player stats:', error);
    return [];
  }
}

export async function fetchRealHeadToHeadStats(playerName: string, opponentTeam: string) {
  try {
    const { data, error } = await supabase
      .from('player_stats')
      .select('*')
      .eq('player_name', playerName)
      .ilike('opponent', `%${opponentTeam}%`)
      .order('game_date', { ascending: false })
      .limit(10);
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching head-to-head stats:', error);
    return [];
  }
}

export async function fetchAllProps() {
  try {
    // Add timestamp to prevent caching
    const cacheKey = Date.now();
    
    const { data, error } = await supabase
      .from('props')
      .select(`
        *,
        games (
          id,
          home_team,
          away_team,
          home_team_abbr,
          away_team_abbr,
          game_time
        )
      `)
      .order('edge', { ascending: false, nullsFirst: false });
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching all props:', error);
    return [];
  }
}

export async function fetchPlayerStats(playerName: string): Promise<PlayerStat[]> {
  try {
    const { data, error } = await supabase
      .from('player_stats')
      .select('*')
      .eq('player_name', playerName)
      .order('game_date', { ascending: false })
      .limit(15);
    
    if (error) {
      console.error('Error fetching player stats:', error);
      throw error;
    }
    
    return data || [];
  } catch (error) {
    console.error('Error fetching player stats:', error);
    return [];
  }
}

export async function fetchOddsHistory(
  playerName: string,
  statType: string
): Promise<OddsHistoryPoint[]> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/odds-history?player_name=${encodeURIComponent(playerName)}&stat_type=${encodeURIComponent(statType)}`
    );
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching odds history:', error);
    return [];
  }
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
}
