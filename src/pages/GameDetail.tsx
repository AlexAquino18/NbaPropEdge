import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Calendar, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Navbar } from '@/components/Navbar';
import { PropTable } from '@/components/PropTable';
import { LoadingState } from '@/components/LoadingState';
import { EmptyState } from '@/components/EmptyState';
import { Modal } from '@/components/ui/modal';
import { fetchGameById, fetchPropsForGame, fetchRealPlayerStats, fetchRealHeadToHeadStats } from '@/lib/api';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

export default function GameDetail() {
  const { gameId } = useParams<{ gameId: string }>();

  const { data: game, isLoading: gameLoading } = useQuery({
    queryKey: ['game', gameId],
    queryFn: () => fetchGameById(gameId!),
    enabled: !!gameId,
  });

  const { data: props, isLoading: propsLoading } = useQuery({
    queryKey: ['props', gameId],
    queryFn: () => fetchPropsForGame(gameId!),
    enabled: !!gameId,
    refetchInterval: 60000,
  });

  const isLoading = gameLoading || propsLoading;

  const [selectedPlayer, setSelectedPlayer] = useState<string | null>(null);
  const [selectedProp, setSelectedProp] = useState<any>(null);
  const [playerStats, setPlayerStats] = useState(null);
  const [headToHeadStats, setHeadToHeadStats] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);

  const handlePlayerClick = async (playerName: string, statType: string, line: number) => {
    setSelectedPlayer(playerName);
    setSelectedProp({ statType, line });
    setIsModalOpen(true);
    setIsLoadingStats(true);
    setPlayerStats([]); // Clear previous stats
    setHeadToHeadStats([]); // Clear previous stats

    try {
      // Find the player's prop to get their team
      const playerProp = props?.find(p => p.player_name === playerName && p.stat_type === statType);
      const playerTeam = playerProp?.team?.toUpperCase().trim() || '';
      
      // Determine which team the player will face (opponent)
      // If player is on away team, opponent is home team, and vice versa
      let opponentTeam = '';
      
      const awayTeam = (game?.away_team_abbr || game?.away_team || '').toUpperCase().trim();
      const homeTeam = (game?.home_team_abbr || game?.home_team || '').toUpperCase().trim();
      const awayTeamFull = (game?.away_team || '').toUpperCase().trim();
      const homeTeamFull = (game?.home_team || '').toUpperCase().trim();
      
      // Check if player is on away team (compare with both abbreviation and full name)
      if (playerTeam === awayTeam || playerTeam === awayTeamFull) {
        opponentTeam = game?.home_team_abbr || game?.home_team || '';
      } 
      // Check if player is on home team
      else if (playerTeam === homeTeam || playerTeam === homeTeamFull) {
        opponentTeam = game?.away_team_abbr || game?.away_team || '';
      }
      // Fallback: if we still can't determine, try to infer from partial matches
      else if (awayTeamFull.includes(playerTeam) || playerTeam.includes(awayTeam.slice(0, 3))) {
        opponentTeam = game?.home_team_abbr || game?.home_team || '';
      } else {
        opponentTeam = game?.away_team_abbr || game?.away_team || '';
      }
      
      // Use AI to fetch real-time stats
      const stats = await fetchRealPlayerStats(playerName);
      const headToHead = await fetchRealHeadToHeadStats(playerName, opponentTeam);

      console.log('Player Stats:', stats);
      console.log('Player team:', playerTeam);
      console.log('H2H opponent:', opponentTeam);
      console.log('Selected stat type:', statType);
      
      setPlayerStats(stats);
      setHeadToHeadStats(headToHead);
    } catch (error) {
      console.error(`Error fetching stats for player: ${playerName}`, error);
      setPlayerStats([]);
      setHeadToHeadStats([]);
    } finally {
      setIsLoadingStats(false);
    }
  };

  // Helper function to get the stat value based on stat type
  const getStatValue = (stat: any, statType: string): number => {
    const lowerStatType = statType.toLowerCase();
    if (lowerStatType.includes('point')) return stat.points;
    if (lowerStatType.includes('rebound')) return stat.rebounds;
    if (lowerStatType.includes('assist')) return stat.assists;
    if (lowerStatType.includes('3-pt') || lowerStatType.includes('three')) return stat.three_pointers_made;
    if (lowerStatType.includes('pts+reb+ast') || lowerStatType.includes('fantasy')) {
      return stat.points + stat.rebounds + stat.assists;
    }
    if (lowerStatType.includes('pts+reb')) return stat.points + stat.rebounds;
    if (lowerStatType.includes('pts+ast')) return stat.points + stat.assists;
    if (lowerStatType.includes('reb+ast')) return stat.rebounds + stat.assists;
    return 0;
  };

  // Helper function to get stat label
  const getStatLabel = (statType: string): string => {
    const lowerStatType = statType.toLowerCase();
    if (lowerStatType.includes('point')) return 'PTS';
    if (lowerStatType.includes('rebound')) return 'REB';
    if (lowerStatType.includes('assist')) return 'AST';
    if (lowerStatType.includes('3-pt') || lowerStatType.includes('three')) return '3PM';
    if (lowerStatType.includes('pts+reb+ast')) return 'PTS+REB+AST';
    if (lowerStatType.includes('pts+reb')) return 'PTS+REB';
    if (lowerStatType.includes('pts+ast')) return 'PTS+AST';
    if (lowerStatType.includes('reb+ast')) return 'REB+AST';
    return statType;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <LoadingState message="Loading game details..." />
        </main>
      </div>
    );
  }

  if (!game) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <EmptyState
            title="Game Not Found"
            description="The game you're looking for doesn't exist or has been removed."
            icon="calendar"
          />
        </main>
      </div>
    );
  }

  const gameTime = new Date(game.game_time);
  const positiveEdgeCount = props?.filter((p) => p.edge !== null && p.edge > 0).length || 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="fixed inset-0 bg-hero-glow pointer-events-none" />
      
      <Navbar />

      <main className="container mx-auto px-4 py-8 relative">
        {/* Back Button */}
        <Link to="/">
          <Button variant="ghost" size="sm" className="gap-2 mb-6 -ml-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Games
          </Button>
        </Link>

        {/* Game Header */}
        <header className="glass-card rounded-xl p-6 mb-8">
          <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span>{format(gameTime, 'EEEE, MMMM d, yyyy')}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span className="text-primary font-medium">{format(gameTime, 'h:mm a')}</span>
            </div>
          </div>

          <div className="flex items-center justify-between py-4">
            <div className="text-center">
              <p className="text-3xl md:text-4xl font-black text-primary">{game.away_team_abbr || game.away_team}</p>
              <p className="text-sm text-muted-foreground mt-1">Away</p>
            </div>
            <div className="text-4xl font-black text-muted-foreground/30">VS</div>
            <div className="text-center">
              <p className="text-3xl md:text-4xl font-black text-secondary">{game.home_team_abbr || game.home_team}</p>
              <p className="text-sm text-muted-foreground mt-1">Home</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mt-4 pt-4 border-t border-border/50">
            <div className="text-center">
              <p className="text-2xl font-bold text-accent">{props?.length || 0}</p>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Total Props</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary">{positiveEdgeCount}</p>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">+Edge Props</p>
            </div>
          </div>
        </header>

        {/* Props Table */}
        <section>
          <h2 className="text-xl font-bold mb-4">All Player Props</h2>
          {props && props.length > 0 ? (
            <PropTable
              props={props}
              onPlayerClick={(playerName, statType, line) => handlePlayerClick(playerName, statType, line)}
            />
          ) : (
            <EmptyState
              title="No Props Available"
              description="Props for this game haven't been loaded yet. Try refreshing the data."
              icon="trending"
            />
          )}
        </section>
      </main>

      {isModalOpen && selectedProp && (
        <Modal onClose={() => setIsModalOpen(false)}>
          <div className="space-y-4">
            {/* Header */}
            <div className="border-b border-border pb-4">
              <h2 className="text-2xl font-bold">{selectedPlayer}</h2>
              <p className="text-sm text-muted-foreground mt-1">
                {getStatLabel(selectedProp.statType)} • Line: {selectedProp.line}
              </p>
            </div>

            {isLoadingStats ? (
              <div className="py-12 text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
                <p className="mt-4 text-sm text-muted-foreground">Fetching real-time stats...</p>
              </div>
            ) : (
              <Tabs defaultValue="recent" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="recent">Last 5 Games</TabsTrigger>
                  <TabsTrigger value="vs">vs {game?.home_team_abbr || game?.home_team}</TabsTrigger>
                </TabsList>

                <TabsContent value="recent" className="space-y-3 mt-4">
                  {playerStats && playerStats.length > 0 ? (
                    <>
                      {playerStats.slice(0, 5).map((stat: any, index: number) => {
                        const statValue = getStatValue(stat, selectedProp.statType);
                        const isOver = statValue > selectedProp.line;
                        const percentage = Math.min((statValue / (selectedProp.line * 1.5)) * 100, 100);
                        
                        return (
                          <div key={index} className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <div className="flex items-center gap-2">
                                <span className="text-foreground/70 font-medium">vs {stat.opponent}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-foreground/90">{new Date(stat.game_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                              </div>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className={`text-2xl font-bold ${isOver ? 'text-green-500' : 'text-red-500'}`}>
                                {statValue}
                              </span>
                              <span className={`text-xs px-2 py-1 rounded font-semibold ${isOver ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                                {isOver ? 'OVER' : 'UNDER'}
                              </span>
                            </div>
                            {/* Visual Bar */}
                            <div className="relative h-3 bg-muted rounded-full overflow-hidden">
                              <div
                                className={`h-full transition-all ${isOver ? 'bg-green-500' : 'bg-red-500'}`}
                                style={{ width: `${percentage}%` }}
                              />
                              {/* Line marker */}
                              <div
                                className="absolute top-0 h-full w-0.5 bg-white"
                                style={{ left: `${Math.min((selectedProp.line / (selectedProp.line * 1.5)) * 100, 100)}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                      
                      {/* Average */}
                      <div className="mt-6 pt-4 border-t border-border">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-muted-foreground">Last 5 Games Avg</span>
                          <span className="text-xl font-bold">
                            {(playerStats.slice(0, 5).reduce((sum: number, stat: any) => sum + getStatValue(stat, selectedProp.statType), 0) / Math.min(5, playerStats.length)).toFixed(1)} {getStatLabel(selectedProp.statType)}
                          </span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="py-8 text-center text-muted-foreground">
                      <p>No recent stats available</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="vs" className="space-y-3 mt-4">
                  {headToHeadStats && headToHeadStats.length > 0 ? (
                    <>
                      {headToHeadStats.map((stat: any, index: number) => {
                        const statValue = getStatValue(stat, selectedProp.statType);
                        const isOver = statValue > selectedProp.line;
                        const percentage = Math.min((statValue / (selectedProp.line * 1.5)) * 100, 100);
                        
                        return (
                          <div key={index} className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <div className="flex items-center gap-2">
                                <span className="text-foreground/70 font-medium">vs {stat.opponent}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-foreground/90">{new Date(stat.game_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                              </div>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className={`text-2xl font-bold ${isOver ? 'text-green-500' : 'text-red-500'}`}>
                                {statValue}
                              </span>
                              <span className={`text-xs px-2 py-1 rounded font-semibold ${isOver ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                                {isOver ? 'OVER' : 'UNDER'}
                              </span>
                            </div>
                            {/* Visual Bar */}
                            <div className="relative h-3 bg-muted rounded-full overflow-hidden">
                              <div
                                className={`h-full transition-all ${isOver ? 'bg-green-500' : 'bg-red-500'}`}
                                style={{ width: `${percentage}%` }}
                              />
                              {/* Line marker */}
                              <div
                                className="absolute top-0 h-full w-0.5 bg-white"
                                style={{ left: `${Math.min((selectedProp.line / (selectedProp.line * 1.5)) * 100, 100)}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                      
                      {/* Average */}
                      <div className="mt-6 pt-4 border-t border-border">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-muted-foreground">H2H Average</span>
                          <span className="text-xl font-bold">
                            {(headToHeadStats.reduce((sum: number, stat: any) => sum + getStatValue(stat, selectedProp.statType), 0) / headToHeadStats.length).toFixed(1)} {getStatLabel(selectedProp.statType)}
                          </span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="py-8 text-center text-muted-foreground">
                      <p>No head-to-head stats available</p>
                      <p className="text-xs mt-2">vs {game?.home_team}</p>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
