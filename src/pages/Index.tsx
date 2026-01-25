import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Calendar, Zap, Database, Calculator } from 'lucide-react';
import { Navbar } from '@/components/Navbar';
import { supabase } from '@/integrations/supabase/client';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface Game {
  id: string;
  home_team: string;
  away_team: string;
  home_team_abbr: string;
  away_team_abbr: string;
  game_time: string;
}

interface Prop {
  id: string;
  game_id: string;
  player_name: string;
  team: string;
  stat_type: string;
  line: number;
  projection: number;
  edge: number;
  confidence: string;
  probability_over: number;
}

export default function Index() {
  const { data: games, isLoading } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('games')
        .select('*')
        .order('game_time', { ascending: true });
      
      if (error) throw error;
      return data as Game[];
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { data: props } = useQuery({
    queryKey: ['props'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('props')
        .select('*')
        .order('edge', { ascending: false });
      
      if (error) throw error;
      
      // Filter out Free Throws Made props
      const filteredData = (data as Prop[]).filter(
        prop => prop.stat_type !== 'Free Throws Made'
      );
      
      return filteredData;
    },
    refetchInterval: 30000,
    staleTime: 0, // Always fetch fresh data
    cacheTime: 0, // Don't cache
    refetchOnMount: 'always', // Always refetch when component mounts
    refetchOnWindowFocus: true, // Refetch when user returns to tab
  });

  const getPropsForGame = (gameId: string) => {
    if (!props) return [];
    return props.filter(p => p.game_id === gameId).slice(0, 3);
  };

  const formatTime = (isoDate: string) => {
    const date = new Date(isoDate);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const runFetchPlayerStats = () => {
    toast.info('📊 How to Run: Fetch Player Stats', {
      description: 'Open PowerShell in project folder and run: .\\fetch-stats.ps1',
      duration: 20000,
      action: {
        label: 'Copy Command',
        onClick: () => {
          navigator.clipboard.writeText('.\\fetch-stats.ps1');
          toast.success('✅ Copied! Paste in PowerShell and press Enter');
        }
      }
    });
    
    toast.info('💡 The script will show:', {
      description: 'Blue banner → "FETCHING PLAYER STATS" → Progress updates → Green "COMPLETE!"',
      duration: 15000
    });
  };

  const runAdvancedProjections = () => {
    toast.info('🧮 How to Run: Advanced Projections', {
      description: 'Open PowerShell in project folder and run: .\\run-projections.ps1',
      duration: 20000,
      action: {
        label: 'Copy Command',
        onClick: () => {
          navigator.clipboard.writeText('.\\run-projections.ps1');
          toast.success('✅ Copied! Paste in PowerShell and press Enter');
        }
      }
    });
    
    setTimeout(() => {
      toast.info('📈 Advanced Projections Include:', {
        description: '✓ Defensive matchups ✓ Pace adjustments ✓ Team stats ✓ Efficiency ratings',
        duration: 15000
      });
    }, 500);
    
    setTimeout(() => {
      toast.info('💡 The script will show:', {
        description: 'Blue banner → Detailed examples → Progress → Green "COMPLETE!" → Refresh page to see updates',
        duration: 15000
      });
    }, 1000);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <Skeleton className="h-10 w-64 mb-2" />
            <Skeleton className="h-6 w-96" />
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-80 rounded-xl" />
            ))}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Navbar />

      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Calendar className="h-8 w-8 text-emerald-500" />
                <h1 className="text-4xl font-bold text-white">Today's NBA Games</h1>
              </div>
              <p className="text-slate-400 text-lg">
                January 3, 2026 • {games?.length || 0} games with high-edge props
              </p>
            </div>

            {/* Admin Buttons */}
            <div className="flex gap-3">
              <Button
                onClick={runFetchPlayerStats}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Database className="h-4 w-4 mr-2" />
                Fetch Player Stats
              </Button>
              <Button
                onClick={runAdvancedProjections}
                className="bg-emerald-600 hover:bg-emerald-700 text-white"
              >
                <Calculator className="h-4 w-4 mr-2" />
                Run Projections
              </Button>
            </div>
          </div>
        </div>

        {/* Games Not Found */}
        {!games || games.length === 0 ? (
          <Card className="p-12 text-center bg-slate-900/50 border-slate-800">
            <Calendar className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-white mb-2">No Games Found</h3>
            <p className="text-slate-400">
              Loading games for January 3, 2026... Please wait.
            </p>
          </Card>
        ) : (
          <>
            {/* Games Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {games.map((game) => {
                const gameProps = getPropsForGame(game.id);
                
                return (
                  <Card 
                    key={game.id}
                    className="bg-slate-900/50 border-slate-800 hover:border-emerald-500/50 transition-all duration-300 overflow-hidden group"
                  >
                    {/* Game Header */}
                    <div className="bg-gradient-to-r from-emerald-500/10 to-blue-500/10 p-6 border-b border-slate-800">
                      <div className="flex items-center justify-between mb-4">
                        <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
                          {formatTime(game.game_time)}
                        </Badge>
                        <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/30">
                          {gameProps.length} Props
                        </Badge>
                      </div>
                      
                      {/* Teams */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-white font-bold">
                              {game.away_team_abbr}
                            </div>
                            <div>
                              <p className="text-white font-semibold">{game.away_team}</p>
                              <p className="text-xs text-slate-500">Away</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-center">
                          <div className="text-slate-600 font-bold">@</div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-white font-bold">
                              {game.home_team_abbr}
                            </div>
                            <div>
                              <p className="text-white font-semibold">{game.home_team}</p>
                              <p className="text-xs text-slate-500">Home</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Props */}
                    <div className="p-6">
                      <div className="flex items-center gap-2 mb-4">
                        <Zap className="h-4 w-4 text-emerald-500" />
                        <h3 className="text-sm font-semibold text-white">Top Props</h3>
                      </div>
                      
                      {gameProps.length === 0 ? (
                        <p className="text-slate-500 text-sm">No props available</p>
                      ) : (
                        <div className="space-y-3">
                          {gameProps.map((prop) => (
                            <div 
                              key={prop.id}
                              className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50 hover:border-emerald-500/50 transition-all"
                            >
                              <div className="flex items-start justify-between mb-2">
                                <div>
                                  <p className="text-white font-semibold">{prop.player_name}</p>
                                  <p className="text-xs text-slate-400">{prop.team} • {prop.stat_type}</p>
                                </div>
                                <Badge 
                                  className={
                                    prop.edge >= 20 
                                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' 
                                      : 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                                  }
                                >
                                  +{prop.edge}%
                                </Badge>
                              </div>
                              
                              <div className="flex items-center justify-between text-sm">
                                <div>
                                  <p className="text-slate-500">Line</p>
                                  <p className="text-white font-semibold">{prop.line}</p>
                                </div>
                                <div className="text-right">
                                  <p className="text-slate-500">Projection</p>
                                  <p className="text-emerald-400 font-semibold">{prop.projection}</p>
                                </div>
                              </div>
                              
                              {prop.confidence && (
                                <Badge 
                                  variant="outline" 
                                  className="mt-2 text-xs bg-slate-900/50"
                                >
                                  {prop.confidence.toUpperCase()} CONFIDENCE
                                </Badge>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>

            {/* Stats Footer */}
            <div className="mt-12 grid gap-4 md:grid-cols-3">
              <Card className="bg-gradient-to-br from-emerald-500/10 to-emerald-500/5 border-emerald-500/20 p-6">
                <p className="text-slate-400 text-sm mb-1">Total Games</p>
                <p className="text-4xl font-bold text-white">{games.length}</p>
              </Card>
              <Card className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border-blue-500/20 p-6">
                <p className="text-slate-400 text-sm mb-1">Total Props</p>
                <p className="text-4xl font-bold text-white">{props?.length || 0}</p>
              </Card>
              <Card className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border-purple-500/20 p-6">
                <p className="text-slate-400 text-sm mb-1">High Edge Props</p>
                <p className="text-4xl font-bold text-white">
                  {props?.filter(p => p.edge >= 18).length || 0}
                </p>
              </Card>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
