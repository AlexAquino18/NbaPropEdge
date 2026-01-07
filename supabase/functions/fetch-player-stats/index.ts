import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.49.1';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const url = new URL(req.url);
    const playerName = url.searchParams.get('player');
    const opponent = url.searchParams.get('opponent');

    if (!playerName) {
      return new Response(
        JSON.stringify({ error: 'Player name is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Use balldontlie API v1
    const BALLDONTLIE_BASE_URL = 'https://api.balldontlie.io/v1';
    
    // Search for player
    const searchResponse = await fetch(
      `${BALLDONTLIE_BASE_URL}/players?search=${encodeURIComponent(playerName)}`,
      {
        headers: {
          'Authorization': 'f6c012a1-22d9-4e5a-9f0d-9ff3a4e2a6c7', // Free API key
        },
      }
    );

    if (!searchResponse.ok) {
      throw new Error(`Failed to search player: ${searchResponse.status}`);
    }

    const searchData = await searchResponse.json();

    if (!searchData.data || searchData.data.length === 0) {
      return new Response(
        JSON.stringify({ data: [] }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const playerId = searchData.data[0].id;

    // Fetch player stats
    const perPage = opponent ? 50 : 10;
    const statsResponse = await fetch(
      `${BALLDONTLIE_BASE_URL}/stats?player_ids[]=${playerId}&per_page=${perPage}`,
      {
        headers: {
          'Authorization': 'f6c012a1-22d9-4e5a-9f0d-9ff3a4e2a6c7',
        },
      }
    );

    if (!statsResponse.ok) {
      throw new Error(`Failed to fetch stats: ${statsResponse.status}`);
    }

    const statsData = await statsResponse.json();

    let filteredStats = statsData.data;

    // Filter by opponent if specified
    if (opponent) {
      filteredStats = statsData.data.filter((stat: any) => {
        const gameOpponent = stat.game.home_team_id === stat.team.id
          ? stat.game.visitor_team.abbreviation
          : stat.game.home_team.abbreviation;
        return gameOpponent.toLowerCase().includes(opponent.toLowerCase());
      }).slice(0, 5);
    }

    // Transform the data
    const transformedStats = filteredStats.map((stat: any) => ({
      game_date: stat.game.date,
      points: stat.pts,
      rebounds: stat.reb,
      assists: stat.ast,
      three_pointers_made: stat.fg3m,
      minutes: stat.min?.split(':')[0] || '0',
      opponent: stat.game.home_team_id === stat.team.id
        ? stat.game.visitor_team.abbreviation
        : stat.game.home_team.abbreviation,
    }));

    return new Response(
      JSON.stringify({ data: transformedStats }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Error in fetch-player-stats:', error);
    return new Response(
      JSON.stringify({ error: error.message || 'Unknown error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});