import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { supabase } from '@/integrations/supabase/client';

interface OddsHistoryChartProps {
  playerName: string;
  statType: string;
}

interface OddsHistoryPoint {
  recorded_at: string;
  draftkings_line?: number | null;
  draftkings_over_odds?: number | null;
  draftkings_under_odds?: number | null;
  fanduel_line?: number | null;
  fanduel_over_odds?: number | null;
  fanduel_under_odds?: number | null;
  prizepicks_line?: number | null;
}

export function OddsHistoryChart({ playerName, statType }: OddsHistoryChartProps) {
  const [open, setOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'over' | 'under'>('over');

  // Fetch odds history from Supabase when dialog opens
  const { data: oddsHistory, isLoading } = useQuery({
    queryKey: ['oddsHistory', playerName, statType],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('odds_history')
        .select('*')
        .eq('player_name', playerName)
        .eq('stat_type', statType)
        .order('recorded_at', { ascending: true });
      
      if (error) {
        console.error('Error fetching odds history:', error);
        throw error;
      }
      
      return data as OddsHistoryPoint[];
    },
    enabled: open, // Only fetch when dialog is open
    refetchInterval: 60 * 60 * 1000, // Refetch every hour
  });

  // Transform data for the chart - show odds instead of lines
  const chartData = oddsHistory?.map((point) => ({
    time: format(new Date(point.recorded_at), 'MMM d, h:mm a'),
    line: point.draftkings_line || point.fanduel_line,
    DraftKings: viewMode === 'over' ? point.draftkings_over_odds : point.draftkings_under_odds,
    FanDuel: viewMode === 'over' ? point.fanduel_over_odds : point.fanduel_under_odds,
  })) || [];

  const hasData = chartData.length > 0;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 hover:bg-blue-500/20"
          title="View line movement history"
        >
          <TrendingUp className="h-4 w-4 text-blue-500" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">
            {playerName} • {statType}
          </DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-muted-foreground">Loading odds history...</div>
          </div>
        ) : !hasData ? (
          <div className="flex flex-col items-center justify-center h-64 space-y-2">
            <TrendingUp className="h-12 w-12 text-muted-foreground/50" />
            <div className="text-muted-foreground">No historical data available yet</div>
            <div className="text-sm text-muted-foreground/70">
              Run the odds tracking script hourly to build history
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header with line info and toggle */}
            <div className="flex items-center justify-between bg-muted/50 p-4 rounded-lg">
              <div className="flex items-center gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Line</div>
                  <div className="text-3xl font-bold">{chartData[0]?.line}</div>
                </div>
                <div className="h-12 w-px bg-border" />
                <div>
                  <div className="text-sm text-muted-foreground">Data Points</div>
                  <div className="text-xl font-semibold">{chartData.length}</div>
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button
                  variant={viewMode === 'over' ? 'default' : 'outline'}
                  size="lg"
                  onClick={() => setViewMode('over')}
                  className="min-w-[120px]"
                >
                  Over Odds
                </Button>
                <Button
                  variant={viewMode === 'under' ? 'default' : 'outline'}
                  size="lg"
                  onClick={() => setViewMode('under')}
                  className="min-w-[120px]"
                >
                  Under Odds
                </Button>
              </div>
            </div>
            
            {/* Chart */}
            <div className="bg-card border rounded-lg p-4">
              <ResponsiveContainer width="100%" height={450}>
                <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 80 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis 
                    dataKey="time" 
                    className="text-xs"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    label={{ 
                      value: 'American Odds', 
                      angle: -90, 
                      position: 'insideLeft',
                      style: { fontSize: 14, fontWeight: 500 }
                    }}
                    domain={['dataMin - 20', 'dataMax + 20']}
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => value > 0 ? `+${value}` : value}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--background))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      padding: '12px'
                    }}
                    formatter={(value: any) => {
                      if (typeof value === 'number') {
                        return value > 0 ? `+${value}` : value;
                      }
                      return value;
                    }}
                    labelStyle={{ fontWeight: 600, marginBottom: '8px' }}
                  />
                  <Legend 
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="line"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="DraftKings" 
                    stroke="#ff6b35" 
                    strokeWidth={3}
                    dot={{ fill: '#ff6b35', r: 5, strokeWidth: 2, stroke: '#fff' }}
                    activeDot={{ r: 7 }}
                    connectNulls
                  />
                  <Line 
                    type="monotone" 
                    dataKey="FanDuel" 
                    stroke="#4169e1" 
                    strokeWidth={3}
                    dot={{ fill: '#4169e1', r: 5, strokeWidth: 2, stroke: '#fff' }}
                    activeDot={{ r: 7 }}
                    connectNulls
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Summary stats */}
            <div className="grid grid-cols-2 gap-6">
              {['DraftKings', 'FanDuel'].map((book) => {
                const dataKey = book as keyof Omit<typeof chartData[0], 'time' | 'line'>;
                const values = chartData
                  .map((d) => d[dataKey])
                  .filter((v): v is number => v !== null && v !== undefined);
                
                if (values.length === 0) return null;

                const current = values[values.length - 1];
                const previous = values[0];
                const change = current - previous;
                
                // For odds, more negative (or less positive) is worse for bettor
                const isBetter = viewMode === 'over' 
                  ? change > 0  // Over odds going up is better
                  : change < 0; // Under odds going down is better

                const bookColor = book === 'DraftKings' ? 'border-l-[#ff6b35]' : 'border-l-[#4169e1]';

                return (
                  <div key={book} className={`bg-card border-l-4 ${bookColor} rounded-lg p-6 shadow-sm`}>
                    <div className="flex items-center justify-between mb-4">
                      <div className="text-lg font-semibold">{book}</div>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                        isBetter 
                          ? 'bg-green-500/10 text-green-500' 
                          : 'bg-red-500/10 text-red-500'
                      }`}>
                        {isBetter ? '↑ Better' : '↓ Worse'}
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <div className="text-sm text-muted-foreground mb-1">Current Odds</div>
                        <div className="text-4xl font-bold">
                          {current > 0 ? '+' : ''}{current}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 pt-3 border-t">
                        <div>
                          <div className="text-xs text-muted-foreground">Change</div>
                          <div className={`text-lg font-semibold ${isBetter ? 'text-green-500' : 'text-red-500'}`}>
                            {change >= 0 ? '+' : ''}{change}
                          </div>
                        </div>
                        <div className="h-10 w-px bg-border" />
                        <div>
                          <div className="text-xs text-muted-foreground">Starting Odds</div>
                          <div className="text-lg font-semibold text-muted-foreground">
                            {previous > 0 ? '+' : ''}{previous}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
