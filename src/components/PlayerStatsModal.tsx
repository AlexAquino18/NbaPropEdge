import { useQuery } from '@tanstack/react-query';
import { X, TrendingUp, Activity, Calendar, Target, Zap, Users, BarChart3 } from 'lucide-react';
import { fetchPlayerStats } from '@/lib/api';
import { supabase } from '@/integrations/supabase/client';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { LoadingState } from './LoadingState';
import type { PlayerStat, Prop } from '@/types';

// NBA Team Stats and Defensive Rankings (synced with Python script)
const NBA_TEAM_STATS: Record<string, { pace: number; def_rtg: number; dreb_pct: number; ast_pct: number }> = {
  'MIA': { pace: 104.71, def_rtg: 111.9, dreb_pct: 69.4, ast_pct: 65.2 },
  'NOP': { pace: 101.63, def_rtg: 119.6, dreb_pct: 67.0, ast_pct: 58.3 },
  'OKC': { pace: 101.59, def_rtg: 104.5, dreb_pct: 71.2, ast_pct: 58.5 },
  'CLE': { pace: 102.13, def_rtg: 113.7, dreb_pct: 68.6, ast_pct: 64.6 },
  'DET': { pace: 101.28, def_rtg: 110.6, dreb_pct: 68.3, ast_pct: 61.5 },
  'IND': { pace: 101.57, def_rtg: 116.7, dreb_pct: 68.2, ast_pct: 60.9 },
  'DEN': { pace: 100.33, def_rtg: 116.4, dreb_pct: 71.0, ast_pct: 65.1 },
  'BKN': { pace: 97.80, def_rtg: 116.5, dreb_pct: 68.0, ast_pct: 66.9 },
  'MIN': { pace: 100.93, def_rtg: 112.7, dreb_pct: 69.0, ast_pct: 62.9 },
  'WAS': { pace: 101.93, def_rtg: 120.9, dreb_pct: 66.3, ast_pct: 60.9 },
  'MEM': { pace: 101.84, def_rtg: 113.9, dreb_pct: 70.8, ast_pct: 69.9 },
  'LAL': { pace: 99.66, def_rtg: 117.8, dreb_pct: 69.3, ast_pct: 59.5 },
  'MIL': { pace: 99.28, def_rtg: 116.2, dreb_pct: 68.4, ast_pct: 63.1 },
  'SAC': { pace: 101.15, def_rtg: 119.9, dreb_pct: 67.1, ast_pct: 61.5 },
  'PHO': { pace: 100.06, def_rtg: 113.1, dreb_pct: 68.1, ast_pct: 60.2 },
  'PHX': { pace: 100.06, def_rtg: 113.1, dreb_pct: 68.1, ast_pct: 60.2 },
  'ORL': { pace: 101.07, def_rtg: 113.3, dreb_pct: 70.8, ast_pct: 62.8 },
  'ATL': { pace: 103.11, def_rtg: 115.2, dreb_pct: 67.9, ast_pct: 71.4 },
  'BOS': { pace: 96.65, def_rtg: 114.2, dreb_pct: 67.3, ast_pct: 55.7 },
  'CHI': { pace: 103.57, def_rtg: 117.3, dreb_pct: 71.5, ast_pct: 68.3 },
  'DAL': { pace: 102.31, def_rtg: 113.4, dreb_pct: 69.0, ast_pct: 60.2 },
  'GSW': { pace: 100.69, def_rtg: 111.8, dreb_pct: 67.8, ast_pct: 69.7 },
  'HOU': { pace: 96.96, def_rtg: 112.7, dreb_pct: 70.2, ast_pct: 57.8 },
  'LAC': { pace: 96.80, def_rtg: 116.6, dreb_pct: 68.6, ast_pct: 60.0 },
  'NYK': { pace: 99.68, def_rtg: 114.9, dreb_pct: 70.6, ast_pct: 63.0 },
  'PHI': { pace: 100.37, def_rtg: 113.7, dreb_pct: 68.2, ast_pct: 60.5 },
  'POR': { pace: 102.43, def_rtg: 116.4, dreb_pct: 67.6, ast_pct: 60.9 },
  'SAS': { pace: 101.09, def_rtg: 112.7, dreb_pct: 72.5, ast_pct: 60.5 },
  'TOR': { pace: 99.49, def_rtg: 112.5, dreb_pct: 69.1, ast_pct: 69.2 },
  'UTA': { pace: 102.83, def_rtg: 121.4, dreb_pct: 69.9, ast_pct: 72.0 },
  'CHA': { pace: 99.63, def_rtg: 118.3, dreb_pct: 71.7, ast_pct: 64.9 },
};

const DEFENSIVE_MATCHUPS: Record<string, Record<string, number>> = {
  'NOP': { 'PF': 22, 'PG': 90, 'SF': 139, 'SG': 104, 'C': 144 },
  'MIA': { 'SG': 61, 'PF': 81, 'SF': 115, 'PG': 134, 'C': 89 },
  'OKC': { 'PF': 1, 'PG': 6, 'SF': 18, 'SG': 45, 'C': 21 },
  'CLE': { 'C': 38, 'PG': 84, 'PF': 50, 'SG': 51, 'SF': 131 },
  'DET': { 'SF': 9, 'PG': 17, 'PF': 80, 'SG': 62, 'C': 107 },
  'IND': { 'PF': 29, 'PG': 64, 'SF': 118, 'SG': 55, 'C': 82 },
  'DEN': { 'SG': 19, 'SF': 103, 'PF': 119, 'C': 63, 'PG': 93 },
  'BKN': { 'PG': 13, 'SF': 113, 'SG': 99, 'PF': 116, 'C': 59 },
  'MIN': { 'SF': 7, 'PG': 79, 'SG': 35, 'PF': 66, 'C': 85 },
  'WAS': { 'PG': 149, 'SF': 111, 'C': 133, 'PF': 146, 'SG': 94 },
  'MEM': { 'C': 25, 'PG': 117, 'PF': 43, 'SF': 135, 'SG': 102 },
  'LAL': { 'C': 44, 'SG': 95, 'SF': 130, 'PG': 121, 'PF': 123 },
  'MIL': { 'C': 34, 'PG': 136, 'PF': 37, 'SF': 77, 'SG': 73 },
  'SAC': { 'SF': 54, 'PF': 106, 'C': 148, 'PG': 101, 'SG': 122 },
  'PHO': { 'SF': 26, 'C': 30, 'PF': 33, 'PG': 92, 'SG': 100 },
  'PHX': { 'SF': 26, 'C': 30, 'PF': 33, 'PG': 92, 'SG': 100 },
  'ORL': { 'SG': 14, 'C': 15, 'SF': 39, 'PG': 71, 'PF': 27 },
  'ATL': { 'C': 31, 'PG': 46, 'PF': 56, 'SF': 140, 'SG': 150 },
  'BOS': { 'C': 3, 'PG': 23, 'SF': 12, 'SG': 10, 'PF': 67 },
  'CHI': { 'SG': 41, 'PG': 108, 'SF': 127, 'C': 129, 'PF': 143 },
  'DAL': { 'SF': 36, 'PG': 83, 'PF': 74, 'SG': 124, 'C': 141 },
  'GSW': { 'PF': 8, 'SF': 60, 'C': 70, 'PG': 65, 'SG': 75 },
  'HOU': { 'PF': 5, 'PG': 11, 'SG': 16, 'C': 68, 'SF': 98 },
  'LAC': { 'PF': 42, 'SF': 48, 'C': 110, 'PG': 91, 'SG': 125 },
  'NYK': { 'PG': 2, 'SF': 4, 'C': 52, 'PF': 105, 'SG': 109 },
  'PHI': { 'PG': 20, 'SF': 32, 'C': 49, 'PF': 69, 'SG': 72 },
  'POR': { 'PG': 137, 'C': 78, 'SF': 114, 'PF': 88, 'SG': 120 },
  'SAS': { 'PG': 138, 'PF': 24, 'SG': 47, 'SF': 58, 'C': 76 },
  'TOR': { 'SF': 28, 'PG': 97, 'PF': 87, 'SG': 57, 'C': 40 },
  'UTA': { 'PG': 145, 'C': 86, 'SF': 112, 'SG': 142, 'PF': 147 },
  'CHA': { 'SG': 53, 'SF': 96, 'C': 126, 'PF': 128, 'PG': 132 },
};

const PLAYER_POSITIONS: Record<string, string> = {
  'Trae Young': 'PG', 'Luka Doncic': 'PG', 'Damian Lillard': 'PG', 'Stephen Curry': 'PG',
  'Tyrese Haliburton': 'PG', 'Ja Morant': 'PG', 'Jalen Brunson': 'PG', 'Cade Cunningham': 'PG',
  'Shai Gilgeous-Alexander': 'PG', 'LaMelo Ball': 'PG', 'Donovan Mitchell': 'SG', 'Devin Booker': 'SG',
  'Anthony Edwards': 'SG', 'Tyler Herro': 'SG', 'Desmond Bane': 'SG', 'Jaylen Brown': 'SG',
  'LeBron James': 'SF', 'Kevin Durant': 'SF', 'Jayson Tatum': 'SF', 'Jimmy Butler': 'SF',
  'Brandon Ingram': 'SF', 'Kawhi Leonard': 'SF', 'Franz Wagner': 'SF', 'Giannis Antetokounmpo': 'PF',
  'Zion Williamson': 'PF', 'Julius Randle': 'PF', 'Paolo Banchero': 'PF', 'Jaren Jackson Jr.': 'PF',
  'Aaron Gordon': 'PF', 'Bobby Portis': 'PF', 'Nikola Jokic': 'C', 'Joel Embiid': 'C',
  'Anthony Davis': 'C', 'Bam Adebayo': 'C', 'Rudy Gobert': 'C', 'Domantas Sabonis': 'C',
};

const LEAGUE_AVG_PACE = 100.0;

const TEAM_ABBR_NORMALIZE: Record<string, string> = {
  'PHO': 'PHX',
  'TRA': 'POR',
  'GS': 'GSW',
  'NY': 'NYK',
  'SA': 'SAS',
};

function normalizeTeam(abbr: string | null | undefined): string | null {
  if (!abbr) return null;
  return TEAM_ABBR_NORMALIZE[abbr] || abbr;
}

function getDefensiveRank(opponentTeam: string, playerName: string): number | null {
  const position = PLAYER_POSITIONS[playerName] || 'SF';
  return DEFENSIVE_MATCHUPS[opponentTeam]?.[position] || null;
}

function getDefensiveRating(rank: number | null): string {
  if (!rank) return 'Unknown';
  if (rank <= 50) return 'Elite';
  if (rank <= 100) return 'Average';
  return 'Weak';
}

function getDefensiveAdjustment(rank: number | null): number {
  if (!rank) return 0;
  if (rank <= 50) {
    const adj = 0.88 + (rank / 50) * 0.07;
    return ((1 - adj) * -100); // Convert to percentage (negative means harder)
  } else if (rank <= 100) {
    const adj = 0.95 + ((rank - 50) / 50) * 0.10;
    return ((adj - 1) * 100);
  } else {
    const adj = 1.05 + ((rank - 100) / 50) * 0.13;
    return ((adj - 1) * 100);
  }
}

function getPaceTempo(playerTeamPace: number, oppTeamPace: number): string {
  const avgPace = (playerTeamPace + oppTeamPace) / 2;
  if (avgPace > 102) return 'Fast';
  if (avgPace < 98) return 'Slow';
  return 'Average';
}

interface PlayerStatsModalProps {
  isOpen: boolean;
  onClose: () => void;
  playerName: string;
  statType?: string;
  line?: number;
  prop?: Prop | null; // Add prop data to show projection breakdown
}

export function PlayerStatsModal({
  isOpen,
  onClose,
  playerName,
  statType,
  line,
  prop, // Add prop parameter
}: PlayerStatsModalProps) {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['player-stats', playerName],
    queryFn: () => fetchPlayerStats(playerName),
    enabled: isOpen && !!playerName,
  });

  // Fetch game and opponent info if we have a prop
  const { data: gameInfo } = useQuery({
    queryKey: ['game-info', prop?.game_id],
    queryFn: async () => {
      if (!prop?.game_id) return null;
      const { data, error } = await supabase
        .from('games')
        .select('*')
        .eq('id', prop.game_id)
        .single();
      if (error) throw error;
      return data;
    },
    enabled: !!prop?.game_id,
  });

  // Calculate opponent team
  const opponentTeamRaw = gameInfo && prop?.team
    ? (prop.team === gameInfo.home_team_abbr ? gameInfo.away_team_abbr : gameInfo.home_team_abbr)
    : null;
  const opponentTeam = normalizeTeam(opponentTeamRaw);

  const getStatValue = (stat: PlayerStat, type: string): number | null => {
    const normalizedType = type.toLowerCase();
    console.log('getStatValue called with type:', type, 'normalized:', normalizedType);
    switch (normalizedType) {
      case 'points':
        return stat.points;
      case 'rebounds':
        return stat.rebounds;
      case 'assists':
        return stat.assists;
      case 'pts+rebs+asts':
        return (stat.points || 0) + (stat.rebounds || 0) + (stat.assists || 0);
      case 'pts+rebs':
        return (stat.points || 0) + (stat.rebounds || 0);
      case 'pts+asts':
        return (stat.points || 0) + (stat.assists || 0);
      case 'rebs+asts':
        return (stat.rebounds || 0) + (stat.assists || 0);
      case 'blks+stls':
        return (stat.blocks || 0) + (stat.steals || 0);
      case '3-pointers made':
      case 'threes':
        return stat.three_pointers_made;
      case 'steals':
        return stat.steals;
      case 'blocks':
        return stat.blocks;
      case 'turnovers':
        return stat.turnovers;
      default:
        console.log('No match found for normalized type:', normalizedType);
        return null;
    }
  };

  const calculateAverage = (stats: PlayerStat[], statType: string): number => {
    if (!stats || stats.length === 0) return 0;
    const values = stats
      .map(s => getStatValue(s, statType))
      .filter((v): v is number => v !== null);
    if (values.length === 0) return 0;
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const hitRate = stats && statType && line
    ? stats.filter(s => {
        const value = getStatValue(s, statType);
        return value !== null && value > line;
      }).length
    : null;

  const hitPercentage = hitRate !== null && stats
    ? (hitRate / stats.length) * 100
    : null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <Activity className="h-6 w-6 text-primary" />
            {playerName}
          </DialogTitle>
          <DialogDescription>
            Recent performance and statistics
          </DialogDescription>
        </DialogHeader>

        {isLoading && (
          <div className="py-8">
            <LoadingState />
          </div>
        )}

        {!isLoading && stats && stats.length > 0 && (
          <div className="space-y-6">
            {/* Summary Stats */}
            {statType && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-primary" />
                    <span className="text-xs font-semibold text-muted-foreground uppercase">
                      {statType} Average
                    </span>
                  </div>
                  <p className="text-2xl font-bold">
                    {calculateAverage(stats, statType).toFixed(1)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Last {stats.length} games
                  </p>
                </div>

                {line !== undefined && (
                  <>
                    <div className="p-4 rounded-lg bg-green-500/5 border border-green-500/10">
                      <div className="flex items-center gap-2 mb-2">
                        <Calendar className="h-4 w-4 text-green-600" />
                        <span className="text-xs font-semibold text-muted-foreground uppercase">
                          Hit Rate
                        </span>
                      </div>
                      <p className="text-2xl font-bold">
                        {hitRate} / {stats.length}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Games over {line}
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/10">
                      <div className="flex items-center gap-2 mb-2">
                        <Activity className="h-4 w-4 text-blue-600" />
                        <span className="text-xs font-semibold text-muted-foreground uppercase">
                          Success Rate
                        </span>
                      </div>
                      <p className="text-2xl font-bold">
                        {hitPercentage?.toFixed(0)}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Over the line
                      </p>
                    </div>
                  </>
                )}
              </div>
            )}

            <Separator />

            {/* Recent Games Table */}
            <div>
              <h3 className="font-semibold mb-3">Recent Games</h3>
              <div className="rounded-lg border border-border/50 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50 border-b border-border/50">
                      <tr>
                        <th className="text-left p-3 font-semibold">Date</th>
                        <th className="text-left p-3 font-semibold">Opp</th>
                        <th className="text-right p-3 font-semibold">MIN</th>
                        <th className="text-right p-3 font-semibold">PTS</th>
                        <th className="text-right p-3 font-semibold">REB</th>
                        <th className="text-right p-3 font-semibold">AST</th>
                        <th className="text-right p-3 font-semibold">STL</th>
                        <th className="text-right p-3 font-semibold">BLK</th>
                        <th className="text-right p-3 font-semibold">3PM</th>
                        {statType && line !== undefined && (
                          <th className="text-right p-3 font-semibold">{statType}</th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {stats.map((stat, idx) => {
                        const statValue = statType ? getStatValue(stat, statType) : null;
                        const hitLine = statValue !== null && line !== undefined && statValue > line;
                        
                        return (
                          <tr
                            key={stat.id}
                            className={`border-b border-border/30 hover:bg-muted/30 ${
                              hitLine ? 'bg-green-500/5' : ''
                            }`}
                          >
                            <td className="p-3 text-muted-foreground">
                              {formatDate(stat.game_date)}
                            </td>
                            <td className="p-3">
                              <Badge variant="outline" className="text-xs">
                                {stat.opponent || 'N/A'}
                              </Badge>
                            </td>
                            <td className="p-3 text-right font-mono">
                              {stat.minutes !== null && stat.minutes !== undefined ? stat.minutes.toFixed(0) : '-'}
                            </td>
                            <td className="p-3 text-right font-mono font-semibold">
                              {stat.points !== null && stat.points !== undefined ? stat.points : '-'}
                            </td>
                            <td className="p-3 text-right font-mono">
                              {stat.rebounds !== null && stat.rebounds !== undefined ? stat.rebounds : '-'}
                            </td>
                            <td className="p-3 text-right font-mono">
                              {stat.assists !== null && stat.assists !== undefined ? stat.assists : '-'}
                            </td>
                            <td className="p-3 text-right font-mono">
                              {stat.steals !== null && stat.steals !== undefined ? stat.steals : '-'}
                            </td>
                            <td className="p-3 text-right font-mono">
                              {stat.blocks !== null && stat.blocks !== undefined ? stat.blocks : '-'}
                            </td>
                            <td className="p-3 text-right font-mono">
                              {stat.three_pointers_made !== null && stat.three_pointers_made !== undefined ? stat.three_pointers_made : '-'}
                            </td>
                            {statType && line !== undefined && (
                              <td className="p-3 text-right font-mono font-bold">
                                <span className={hitLine ? 'text-green-600' : ''}>
                                  {statValue !== null ? statValue.toFixed(1) : '-'}
                                </span>
                              </td>
                            )}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {!isLoading && (!stats || stats.length === 0) && (
          <div className="py-12 text-center text-muted-foreground">
            <Activity className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p className="text-lg font-medium">No stats available</p>
            <p className="text-sm mt-1">
              We don't have recent game data for {playerName} yet.
            </p>
          </div>
        )}

        {/* Projection Breakdown - Only show if we have prop data */}
        {prop && prop.projection && (
          <>
            <Separator />
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                <h3 className="font-semibold text-lg">Projection Breakdown</h3>
              </div>

              {/* Main Projection Info */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="h-4 w-4 text-blue-600" />
                    <span className="text-xs font-semibold text-muted-foreground uppercase">
                      Projection
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-blue-600">
                    {prop.projection.toFixed(1)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    vs Line: {line}
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="h-4 w-4 text-purple-600" />
                    <span className="text-xs font-semibold text-muted-foreground uppercase">
                      Probability Over
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-purple-600">
                    {prop.probability_over ? (prop.probability_over * 100).toFixed(0) : '50'}%
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Statistical likelihood
                  </p>
                </div>

                <div className={`p-4 rounded-lg border ${
                  (prop.edge || 0) > 0 
                    ? 'bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-500/20' 
                    : 'bg-gradient-to-br from-red-500/10 to-red-600/5 border-red-500/20'
                }`}>
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className={`h-4 w-4 ${(prop.edge || 0) > 0 ? 'text-green-600' : 'text-red-600'}`} />
                    <span className="text-xs font-semibold text-muted-foreground uppercase">
                      Edge
                    </span>
                  </div>
                  {(() => {
                    const edgeRaw = prop.edge ?? 0;
                    const edgePct = edgeRaw >= 1 ? edgeRaw : edgeRaw * 100;
                    return (
                      <p className={`text-2xl font-bold ${edgePct > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {edgePct > 0 ? '+' : ''}{edgePct.toFixed(1)}%
                      </p>
                    );
                  })()}
                  <p className="text-xs text-muted-foreground mt-1">
                    {(prop.edge || 0) > 0 ? 'Favorable' : 'Unfavorable'}
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="h-4 w-4 text-orange-600" />
                    <span className="text-xs font-semibold text-muted-foreground uppercase">
                      Confidence
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-orange-600 capitalize">
                    {prop.confidence || 'Medium'}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Data reliability
                  </p>
                </div>
              </div>

              {/* Matchup Info */}
              {gameInfo && opponentTeam && (
                <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
                  <div className="flex items-center gap-2 mb-3">
                    <Users className="h-4 w-4 text-primary" />
                    <span className="text-sm font-semibold">Today's Matchup</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground mb-1">Player Team</p>
                      <Badge variant="outline" className="font-semibold">
                        {prop.team}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-muted-foreground mb-1">Opponent</p>
                      <Badge variant="outline" className="font-semibold text-red-600">
                        {opponentTeam}
                      </Badge>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-border/30">
                    <p className="text-xs text-muted-foreground">
                      {gameInfo.away_team} @ {gameInfo.home_team}
                    </p>
                  </div>
                </div>
              )}

              {/* Advanced Matchup Analytics */}
              {opponentTeam && prop.team && (() => {
                // Calculate real stats for display
                const defRank = getDefensiveRank(opponentTeam, playerName);
                const defRating = getDefensiveRating(defRank);
                const defAdjustment = getDefensiveAdjustment(defRank);
                
                const playerTeamStats = NBA_TEAM_STATS[prop.team];
                const oppTeamStats = NBA_TEAM_STATS[opponentTeam];
                const playerPace = playerTeamStats?.pace || 100.0;
                const oppPace = oppTeamStats?.pace || 100.0;
                const paceTempo = getPaceTempo(playerPace, oppPace);
                
                const oppDreb = oppTeamStats?.dreb_pct || 69.0;
                const teamAst = playerTeamStats?.ast_pct || 63.0;
                const oppDefRtg = oppTeamStats?.def_rtg || 113.0;
                
                return (
                <div className="space-y-3">
                  <h4 className="text-sm font-semibold flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Key Factors Influencing This Bet
                  </h4>

                  {/* Defensive Ranking Card */}
                  <div className="p-4 rounded-lg bg-gradient-to-br from-red-500/5 to-red-600/5 border border-red-500/10">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-full bg-red-500/10 flex items-center justify-center">
                          <Users className="h-4 w-4 text-red-600" />
                        </div>
                        <span className="text-sm font-semibold">Opponent Defense vs Position</span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {opponentTeam}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground mb-2">
                      How well {opponentTeam} defends against {PLAYER_POSITIONS[playerName] || 'this position'}
                    </div>
                    <div className="grid grid-cols-3 gap-3 text-center">
                      <div className="p-2 rounded bg-background/50">
                        <p className="text-xs text-muted-foreground mb-1">Rank</p>
                        <p className={`text-lg font-bold ${defRank && defRank <= 50 ? 'text-red-600' : defRank && defRank > 100 ? 'text-green-600' : 'text-yellow-600'}`}>
                          {defRank || '?'}/150
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Position defense</p>
                      </div>
                      <div className="p-2 rounded bg-background/50">
                        <p className="text-xs text-muted-foreground mb-1">Rating</p>
                        <p className={`text-lg font-bold ${defRating === 'Elite' ? 'text-red-600' : defRating === 'Weak' ? 'text-green-600' : 'text-yellow-600'}`}>
                          {defRating}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Defense quality</p>
                      </div>
                      <div className="p-2 rounded bg-background/50">
                        <p className="text-xs text-muted-foreground mb-1">Impact</p>
                        <p className={`text-lg font-bold ${defAdjustment > 0 ? 'text-green-600' : defAdjustment < 0 ? 'text-red-600' : ''}`}>
                          {defAdjustment > 0 ? '+' : ''}{defAdjustment.toFixed(1)}%
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Proj adjustment</p>
                      </div>
                    </div>
                  </div>

                  {/* Pace Analysis Card */}
                  <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/5 to-blue-600/5 border border-blue-500/10">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="h-8 w-8 rounded-full bg-blue-500/10 flex items-center justify-center">
                        <Zap className="h-4 w-4 text-blue-600" />
                      </div>
                      <span className="text-sm font-semibold">Game Pace Forecast</span>
                    </div>
                    <div className="text-xs text-muted-foreground mb-2">
                      Combined pace affects total possessions and scoring opportunities
                    </div>
                    <div className="grid grid-cols-3 gap-3 text-center">
                      <div className="p-2 rounded bg-background/50">
                        <p className="text-xs text-muted-foreground mb-1">{prop.team} Pace</p>
                        <p className="text-lg font-bold">{playerPace.toFixed(1)}</p>
                        <p className="text-xs text-muted-foreground mt-1">Poss/48 min</p>
                      </div>
                      <div className="p-2 rounded bg-background/50">
                        <p className="text-xs text-muted-foreground mb-1">{opponentTeam} Pace</p>
                        <p className="text-lg font-bold">{oppPace.toFixed(1)}</p>
                        <p className="text-xs text-muted-foreground mt-1">Poss/48 min</p>
                      </div>
                      <div className="p-2 rounded bg-background/50">
                        <p className="text-xs text-muted-foreground mb-1">Expected</p>
                        <p className={`text-lg font-bold ${paceTempo === 'Fast' ? 'text-green-600' : paceTempo === 'Slow' ? 'text-red-600' : 'text-blue-600'}`}>
                          {paceTempo}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Game tempo</p>
                      </div>
                    </div>
                  </div>

                  {/* Stat-Specific Factors */}
                  {statType && (
                    <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/5 to-purple-600/5 border border-purple-500/10">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="h-8 w-8 rounded-full bg-purple-500/10 flex items-center justify-center">
                          <Target className="h-4 w-4 text-purple-600" />
                        </div>
                        <span className="text-sm font-semibold">{statType} Specific Factors</span>
                      </div>
                      <div className="space-y-2 text-xs">
                        {(statType.toLowerCase().includes('reb') || statType.toLowerCase().includes('rebounds')) && (
                          <div className="flex items-center justify-between p-2 rounded bg-background/50">
                            <span className="text-muted-foreground">Opponent DREB%:</span>
                            <span className="font-semibold">{oppDreb.toFixed(1)}%</span>
                            <Badge variant="outline" className="text-xs ml-2">
                              {oppDreb > 70 ? 'Harder' : oppDreb < 68 ? 'Easier' : 'Average'}
                            </Badge>
                          </div>
                        )}
                        {(statType.toLowerCase().includes('ast') || statType.toLowerCase().includes('assists')) && (
                          <div className="flex items-center justify-between p-2 rounded bg-background/50">
                            <span className="text-muted-foreground">Team AST%:</span>
                            <span className="font-semibold">{teamAst.toFixed(1)}%</span>
                            <Badge variant="outline" className="text-xs ml-2">
                              {teamAst > 65 ? 'High' : teamAst < 60 ? 'Low' : 'Average'}
                            </Badge>
                          </div>
                        )}
                        {(statType.toLowerCase().includes('pts') || statType.toLowerCase().includes('points')) && (
                          <div className="flex items-center justify-between p-2 rounded bg-background/50">
                            <span className="text-muted-foreground">Opponent DefRtg:</span>
                            <span className="font-semibold">{oppDefRtg.toFixed(1)}</span>
                            <Badge variant="outline" className="text-xs ml-2">
                              {oppDefRtg < 110 ? 'Elite' : oppDefRtg < 115 ? 'Good' : 'Weak'}
                            </Badge>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Quick Summary */}
                  <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
                    <div className="flex items-start gap-2 text-xs">
                      <TrendingUp className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="font-semibold mb-1">Betting Insight:</p>
                        <p className="text-muted-foreground">
                          {(prop.edge || 0) > 15 && '🔥 Strong edge detected! '}
                          {(prop.edge || 0) > 5 && (prop.edge || 0) <= 15 && '✅ Favorable matchup. '}
                          {(prop.edge || 0) >= -5 && (prop.edge || 0) <= 5 && '⚖️ Neutral matchup. '}
                          {(prop.edge || 0) < -5 && '⚠️ Difficult matchup. '}
                          The model analyzed {stats?.length || 0} recent games, defensive rankings, pace factors, and stat-specific adjustments to calculate this projection.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                );
              })()}

              {/* How It's Calculated */}
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  How This Projection Was Calculated
                </h4>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <span className="font-mono text-primary">1.</span>
                    <p><strong>Recent Performance:</strong> Analyzed last 15 games with recent games weighted more heavily</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="font-mono text-primary">2.</span>
                    <p><strong>Defensive Matchup:</strong> Adjusted for opponent's positional defense ranking (1-150 scale)</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="font-mono text-primary">3.</span>
                    <p><strong>Team Pace:</strong> Factored in combined pace of both teams playing</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="font-mono text-primary">4.</span>
                    <p><strong>Advanced Stats:</strong> Applied adjustments for rebounds (opponent DREB%), assists (team AST%), and scoring efficiency (opponent DefRtg)</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="font-mono text-primary">5.</span>
                    <p><strong>Statistical Model:</strong> Used normal distribution to calculate probability based on performance variance</p>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        <Separator />

        {/* Recent Games Table */}
      </DialogContent>
    </Dialog>
  );
}
