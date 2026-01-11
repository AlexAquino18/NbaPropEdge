import { supabase } from "@/integrations/supabase/client";
import type { Game, PlayerStat, GameWithProps, Prop } from "@/types";
import { mergePropsWithProjectionCache, updateProjectionCacheFromProps, setLastPropsCache, getLastPropsCache } from '@/lib/utils';

// Filter out unwanted stat types
const shouldExcludeProp = (statType: string): boolean => {
  const statTypeLower = statType.toLowerCase();
  return (
    statTypeLower.includes('1st 3 minutes') ||
    statTypeLower.includes('first 3 minutes') ||
    statTypeLower.includes('quarters with') ||
    statTypeLower.includes('two pointers made') ||
    statTypeLower.includes('2 pointers made') ||
    statTypeLower.includes('two pointers attempted') ||
    statTypeLower.includes('2 pointers attempted') ||
    statTypeLower.includes('offensive rebounds') ||
    statTypeLower.includes('offensive rebound') ||
    statTypeLower.includes('defensive rebounds') ||
    statTypeLower.includes('defensive rebound') ||
    statTypeLower.includes('fantasy score') ||
    statTypeLower.includes('fantasy points')
  );
};

// Ensure all Prop fields exist (fill missing sportsbook fields with null)
function normalizeProps(rows: any[] | null | undefined): Prop[] {
  const arr = Array.isArray(rows) ? rows : [];
  return arr.map((r: any) => ({
    id: r.id,
    game_id: r.game_id ?? null,
    external_id: r.external_id ?? null,
    player_name: r.player_name,
    player_id: r.player_id ?? null,
    team: r.team ?? null,
    stat_type: r.stat_type,
    line: r.line,
    projection: r.projection ?? null,
    edge: r.edge ?? null,
    probability_over: r.probability_over ?? null,
    confidence: r.confidence ?? null,
    created_at: r.created_at,
    updated_at: r.updated_at,
    prizepicks_odds: r.prizepicks_odds ?? null,
    draftkings_line: r.draftkings_line ?? null,
    draftkings_over_odds: r.draftkings_over_odds ?? null,
    draftkings_under_odds: r.draftkings_under_odds ?? null,
    fanduel_line: r.fanduel_line ?? null,
    fanduel_over_odds: r.fanduel_over_odds ?? null,
    fanduel_under_odds: r.fanduel_under_odds ?? null,
  }));
}

export const fetchGamesWithTopProps = async (): Promise<GameWithProps[]> => {
  try {
    console.log('Fetching games with props from database...');
    
    // Fetch games
    const { data: games, error: gamesError } = await supabase
      .from('games')
      .select('*')
      .order('game_time', { ascending: true });
    
    if (gamesError) {
      console.error('Error fetching games:', gamesError);
      throw gamesError;
    }

    if (!games || games.length === 0) {
      return [];
    }

    // Fetch all props
    const { data: props, error: propsError } = await supabase
      .from('props')
      .select('*')
      .order('edge', { ascending: false, nullsFirst: false });
    
    if (propsError) {
      console.error('Error fetching props:', propsError);
      throw propsError;
    }

    const allProps = normalizeProps(props);

    // Filter out unwanted prop types
    const filteredProps = allProps.filter((prop) => !shouldExcludeProp(prop.stat_type));

    // Merge projections from cache so they persist
    const mergedProps = mergePropsWithProjectionCache(filteredProps);
    // Update cache with any fresh projections
    updateProjectionCacheFromProps(mergedProps);

    // Map games with their props and top props
    const gamesWithProps: GameWithProps[] = games.map((game) => {
      const gameProps = mergedProps.filter((prop) => prop.game_id === game.id);
      const topProps = gameProps.filter((prop) => prop.edge !== null && prop.edge > 0);
      
      return {
        ...game,
        props: gameProps,
        topProps: topProps,
      };
    });

    console.log(`Successfully fetched ${gamesWithProps.length} games with props`);
    return gamesWithProps;
  } catch (error) {
    console.error('Error in fetchGamesWithTopProps:', error);
    throw error;
  }
};

export const fetchPlayerStats = async (
  playerName: string,
  opponentTeam?: string
): Promise<PlayerStat[]> => {
  try {
    console.log(`Fetching stats for ${playerName}${opponentTeam ? ` vs ${opponentTeam}` : ''}`);
    
    // Fetch from database first (we'll populate this with real data)
    const { data: stats, error } = await supabase
      .from('player_stats')
      .select('*')
      .ilike('player_name', playerName)
      .order('game_date', { ascending: false })
      .limit(15);

    if (error) {
      console.error('Error fetching player stats from DB:', error);
    }

    if (stats && stats.length > 0) {
      console.log(`Found ${stats.length} games in database for ${playerName}`);
      
      // Filter by opponent if specified
      if (opponentTeam) {
        return stats.filter(stat => 
          stat.opponent?.toUpperCase().includes(opponentTeam.toUpperCase())
        );
      }
      
      return stats;
    }

    console.log('No stats found in database');
    return [];
  } catch (error) {
    console.error('Error in fetchPlayerStats:', error);
    return [];
  }
};

export const fetchGameById = async (gameId: string): Promise<Game> => {
  try {
    console.log(`Fetching game ${gameId} from database...`);
    const { data: game, error } = await supabase
      .from('games')
      .select('*')
      .eq('id', gameId)
      .single();
    
    if (error) {
      console.error('Error fetching game:', error);
      throw error;
    }

    if (!game) {
      throw new Error('Game not found');
    }

    return game;
  } catch (error) {
    console.error('Error in fetchGameById:', error);
    throw error;
  }
};

export const fetchPropsForGame = async (gameId: string): Promise<Prop[]> => {
  try {
    console.log(`Fetching props for game ${gameId}...`);
    const { data: props, error } = await supabase
      .from('props')
      .select('*')
      .eq('game_id', gameId)
      .order('edge', { ascending: false, nullsFirst: false });
    
    if (error) {
      console.error('Error fetching props:', error);
      throw error;
    }

    const allProps = normalizeProps(props);

    // Filter out unwanted prop types
    const filteredProps = allProps.filter((prop) => !shouldExcludeProp(prop.stat_type));
    const merged = mergePropsWithProjectionCache(filteredProps);
    updateProjectionCacheFromProps(merged);
    setLastPropsCache(merged);
    return merged.length > 0 ? merged : getLastPropsCache().filter(p => p.game_id === gameId);
  } catch (error) {
    console.error('Error in fetchPropsForGame:', error);
    throw error;
  }
};

export const fetchAllProps = async (): Promise<Prop[]> => {
  try {
    console.log('Fetching all props from database (fresh)...');
    const { data: props, error } = await supabase
      .from('props')
      .select('*')
      .order('edge', { ascending: false, nullsFirst: false });
    if (error) {
      console.error('Error fetching all props:', error);
      return [];
    }
    // Normalize and filter only, do NOT merge with cache
    const allProps = normalizeProps(props);
    const filtered = allProps.filter((p) => !shouldExcludeProp(p.stat_type));
    console.log(`Fetched ${filtered.length} fresh props`);
    return filtered;
  } catch (error) {
    console.error('Error in fetchAllProps:', error);
    return [];
  }
};

export const fetchRealPlayerStats = async (playerName: string): Promise<PlayerStat[]> => {
  try {
    console.log(`Fetching real-time stats for ${playerName}...`);
    
    // Fetch from database (populated with real data)
    const { data: stats, error } = await supabase
      .from('player_stats')
      .select('*')
      .ilike('player_name', playerName)
      .order('game_date', { ascending: false })
      .limit(10);

    if (error) {
      console.error('Error fetching real player stats:', error);
      return [];
    }

    console.log(`Successfully fetched ${stats?.length || 0} games for ${playerName}`);
    return stats || [];
  } catch (error) {
    console.error('Error in fetchRealPlayerStats:', error);
    return [];
  }
};

export const fetchRealHeadToHeadStats = async (
  playerName: string,
  opponentTeam: string
): Promise<PlayerStat[]> => {
  try {
    console.log(`Fetching head-to-head stats for ${playerName} vs ${opponentTeam}...`);
    
    // Fetch all stats for player then filter by opponent
    const { data: stats, error } = await supabase
      .from('player_stats')
      .select('*')
      .ilike('player_name', playerName)
      .order('game_date', { ascending: false });

    if (error) {
      console.error('Error fetching head-to-head stats:', error);
      return [];
    }

    if (!stats) return [];

    // Filter by opponent
    const h2hStats = stats.filter(stat => 
      stat.opponent?.toUpperCase().includes(opponentTeam.toUpperCase()) ||
      opponentTeam.toUpperCase().includes(stat.opponent?.toUpperCase() || '')
    );

    console.log(`Successfully fetched ${h2hStats.length} H2H games for ${playerName} vs ${opponentTeam}`);
    return h2hStats;
  } catch (error) {
    console.error('Error in fetchRealHeadToHeadStats:', error);
    return [];
  }
};

export const refreshData = async (): Promise<{ success: boolean; message: string }> => {
  try {
    console.log('Refreshing data...');
    const { data, error } = await supabase.functions.invoke('refresh-data');

    if (error) {
      console.error('Error refreshing data:', error);
      return {
        success: false,
        message: 'Refresh function unavailable. Data is loaded from database.'
      };
    }

    console.log('Data refreshed successfully:', data);
    return {
      success: true,
      message: data?.message || 'Data refreshed successfully'
    };
  } catch (error) {
    console.error('Error in refreshData:', error);
    return {
      success: false,
      message: 'Using existing database data. Refresh function unavailable.'
    };
  }
};

export const fetchNewPlayerGames = async (): Promise<{ success: boolean; message: string }> => {
  try {
    console.log('Fetching new player games...');
    
    // Call the fetch-player-stats function
    const { data, error } = await supabase.functions.invoke('fetch-player-stats');

    if (error) {
      console.error('Error fetching player games:', error);
      return {
        success: false,
        message: error.message || 'Failed to fetch new games'
      };
    }

    console.log('Player games fetched successfully:', data);
    return {
      success: true,
      message: data?.message || 'New player games fetched successfully'
    };
  } catch (error) {
    console.error('Error in fetchNewPlayerGames:', error);
    return {
      success: false,
      message: 'Failed to fetch new player games'
    };
  }
};

export const runProjections = async (): Promise<{ success: boolean; message: string }> => {
  try {
    console.log('Running projections...');
    
    // We'll need to create a new Supabase function for this
    // For now, return a message that it needs to be set up
    return {
      success: false,
      message: 'Projection function needs to be configured in Supabase'
    };
  } catch (error) {
    console.error('Error in runProjections:', error);
    return {
      success: false,
      message: 'Failed to run projections'
    };
  }
};
