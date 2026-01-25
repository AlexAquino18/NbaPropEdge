// Load sportsbook odds from the JSON cache file
export interface SportsbookOddsData {
  line: number;
  over: number;
  under: number;
}

export interface SportsbookOdds {
  DraftKings?: SportsbookOddsData;
  FanDuel?: SportsbookOddsData;
}

let oddsCache: Record<string, SportsbookOdds> | null = null;

export async function loadSportsbookOdds(): Promise<Record<string, SportsbookOdds>> {
  if (oddsCache) {
    return oddsCache;
  }

  try {
    const response = await fetch('/sportsbook_odds_cache.json');
    if (!response.ok) {
      console.warn('Sportsbook odds cache not found');
      return {};
    }
    oddsCache = await response.json();
    return oddsCache || {};
  } catch (error) {
    console.warn('Error loading sportsbook odds:', error);
    return {};
  }
}

export function getSportsbookOdds(
  playerName: string,
  statType: string
): SportsbookOdds | null {
  if (!oddsCache) {
    return null;
  }
  
  const key = `${playerName}|${statType}`;
  return oddsCache[key] || null;
}
