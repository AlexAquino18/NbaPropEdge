import { Badge } from '@/components/ui/badge';

interface SportsbookOddsProps {
  prizePicksLine?: number | null;
  ourProjection?: number | null;
  statType?: string;
}

export function SportsbookOdds({ 
  ourProjection,
  statType = ''
}: SportsbookOddsProps) {
  if (!ourProjection) {
    return (
      <div className="text-sm text-muted-foreground">
        No projection
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-500/10 to-cyan-500/10 rounded-lg border border-blue-500/20">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
          <span className="text-white font-bold text-sm">SS</span>
        </div>
        <div>
          <div className="font-semibold text-sm">StatStack</div>
          <div className="text-xs text-muted-foreground">Projection</div>
        </div>
      </div>
      <div className="text-right">
        <Badge variant="outline" className="bg-background">
          {ourProjection.toFixed(1)} {statType}
        </Badge>
      </div>
    </div>
  );
}
