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
    const { playerName, opponentTeam, statsType } = await req.json();

    if (!playerName) {
      return new Response(
        JSON.stringify({ error: 'Player name is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log(`Fetching ${statsType || 'recent'} stats for ${playerName}${opponentTeam ? ` vs ${opponentTeam}` : ''}`);

    // Use Google Gemini API - has generous free tier
    const geminiApiKey = Deno.env.get('GEMINI_API_KEY');
    
    if (!geminiApiKey) {
      console.error('GEMINI_API_KEY not found');
      return new Response(
        JSON.stringify({ error: 'AI API key not configured' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const prompt = opponentTeam
      ? `Get the last 5 NBA games for ${playerName} against ${opponentTeam} from the 2025-26 season. Return ONLY a valid JSON array with this exact structure, no markdown, no explanations:
[{"game_date": "2026-01-01", "points": 25, "rebounds": 8, "assists": 6, "three_pointers_made": 3, "minutes": 35, "opponent": "LAL"}]
Use real current 2025-26 NBA season data. Include actual game dates and stats from this season.`
      : `Get the last 10 NBA games for ${playerName} from the 2025-26 season. Return ONLY a valid JSON array with this exact structure, no markdown, no explanations:
[{"game_date": "2026-01-01", "points": 25, "rebounds": 8, "assists": 6, "three_pointers_made": 3, "minutes": 35, "opponent": "LAL"}]
Use real current 2025-26 NBA season data. Include actual game dates and stats from this season.`;

    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${geminiApiKey}`;
    
    const geminiResponse = await fetch(geminiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: prompt
          }]
        }],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 2000,
        }
      }),
    });

    if (!geminiResponse.ok) {
      const error = await geminiResponse.text();
      console.error('Gemini API error:', error);
      throw new Error('Failed to fetch stats from AI');
    }

    const aiData = await geminiResponse.json();
    const content = aiData.candidates?.[0]?.content?.parts?.[0]?.text || '';
    
    if (!content) {
      throw new Error('No content returned from AI');
    }
    
    // Remove markdown code blocks if present
    const jsonContent = content
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .replace(/^[^[{]*/, '') // Remove any text before the JSON array/object
      .replace(/[^}\]]*$/, '') // Remove any text after the JSON array/object
      .trim();
    
    let stats;
    try {
      stats = JSON.parse(jsonContent);
    } catch (parseError) {
      console.error('Failed to parse AI response:', content);
      console.error('Cleaned content:', jsonContent);
      throw new Error('Invalid JSON response from AI');
    }

    // Ensure stats is an array
    if (!Array.isArray(stats)) {
      stats = [stats];
    }

    // Add player_name and player_id to each stat
    const formattedStats = stats.map((stat: any) => ({
      player_name: playerName,
      player_id: `player-${playerName.replace(/\s/g, '-')}`,
      game_date: stat.game_date,
      points: stat.points || 0,
      rebounds: stat.rebounds || 0,
      assists: stat.assists || 0,
      three_pointers_made: stat.three_pointers_made || 0,
      minutes: stat.minutes || 0,
      opponent: stat.opponent || 'UNK',
    }));

    console.log(`Successfully fetched ${formattedStats.length} games for ${playerName}`);

    return new Response(
      JSON.stringify({ stats: formattedStats }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Error in ai-fetch-player-stats:', error);
    return new Response(
      JSON.stringify({ error: error.message || 'Unknown error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});