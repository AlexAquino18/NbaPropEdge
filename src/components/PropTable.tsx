import { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { EdgeBadge } from './EdgeBadge';
import { StatTypeBadge } from './StatTypeBadge';
import { PlayerStatsModal } from './PlayerStatsModal';
import { SportsbookOdds } from './SportsbookOdds';
import type { Prop } from '@/types';

interface PropTableProps {
  props: Prop[];
  onPlayerClick?: (playerName: string, statType: string, line: number) => void;
}

type SortKey = 'player_name' | 'stat_type' | 'line' | 'projection' | 'edge' | 'probability_over' | 'confidence';
type SortDirection = 'asc' | 'desc';

export function PropTable({ props, onPlayerClick }: PropTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>('edge');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [selectedPlayer, setSelectedPlayer] = useState<{
    name: string;
    statType: string;
    line: number;
    prop: Prop; // Add the full prop object
  } | null>(null);

  const sortedProps = useMemo(() => {
    return [...props].sort((a, b) => {
      let aVal = a[sortKey];
      let bVal = b[sortKey];

      // Handle nulls
      if (aVal === null) aVal = sortDirection === 'desc' ? -Infinity : Infinity;
      if (bVal === null) bVal = sortDirection === 'desc' ? -Infinity : Infinity;

      // String comparison
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      // Number comparison
      const numA = Number(aVal);
      const numB = Number(bVal);
      return sortDirection === 'asc' ? numA - numB : numB - numA;
    });
  }, [props, sortKey, sortDirection]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('desc');
    }
  };

  const SortIcon = ({ columnKey }: { columnKey: SortKey }) => {
    if (sortKey !== columnKey) {
      return <ArrowUpDown className="h-3.5 w-3.5 text-muted-foreground/50" />;
    }
    return sortDirection === 'asc' ? (
      <ArrowUp className="h-3.5 w-3.5 text-primary" />
    ) : (
      <ArrowDown className="h-3.5 w-3.5 text-primary" />
    );
  };

  const formatProbability = (prob: number | null) => {
    if (prob === null) return 'N/A';
    return `${(prob * 100).toFixed(1)}%`;
  };

  const ConfidenceBadge = ({ confidence }: { confidence: string | null }) => {
    if (!confidence) return <span className="text-xs text-muted-foreground">N/A</span>;
    
    const variants = {
      high: 'bg-green-500/10 text-green-600 border-green-500/20',
      medium: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
      low: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
    };

    return (
      <Badge variant="outline" className={`${variants[confidence as keyof typeof variants] || ''} text-xs font-medium`}>
        {confidence.toUpperCase()}
      </Badge>
    );
  };

  return (
    <>
      <div className="rounded-xl border border-border/50 overflow-hidden bg-card/50">
        <Table>
          <TableHeader>
            <TableRow className="border-border/50 hover:bg-transparent">
              <TableHead className="w-[180px]">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('player_name')}
                  className="gap-1 -ml-3 font-semibold text-xs uppercase tracking-wider"
                >
                  Player
                  <SortIcon columnKey="player_name" />
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('stat_type')}
                  className="gap-1 -ml-3 font-semibold text-xs uppercase tracking-wider"
                >
                  Stat
                  <SortIcon columnKey="stat_type" />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('line')}
                  className="gap-1 font-semibold text-xs uppercase tracking-wider"
                >
                  Line
                  <SortIcon columnKey="line" />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('projection')}
                  className="gap-1 font-semibold text-xs uppercase tracking-wider"
                >
                  Proj
                  <SortIcon columnKey="projection" />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('probability_over')}
                  className="gap-1 font-semibold text-xs uppercase tracking-wider"
                >
                  P(Over)
                  <SortIcon columnKey="probability_over" />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('edge')}
                  className="gap-1 font-semibold text-xs uppercase tracking-wider"
                >
                  Edge
                  <SortIcon columnKey="edge" />
                </Button>
              </TableHead>
              <TableHead className="text-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSort('confidence')}
                  className="gap-1 font-semibold text-xs uppercase tracking-wider"
                >
                  Confidence
                  <SortIcon columnKey="confidence" />
                </Button>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedProps.map((prop, index) => (
              <TableRow 
                key={prop.id} 
                className="table-row-hover border-border/30"
                style={{ animationDelay: `${index * 30}ms` }}
              >
                <TableCell className="font-medium">
                  <div>
                    <button
                      className="text-blue-500 hover:underline"
                      onClick={() => setSelectedPlayer({
                        name: prop.player_name,
                        statType: prop.stat_type,
                        line: prop.line,
                        prop: prop, // Add the full prop object
                      })}
                    >
                      <p className="font-semibold">{prop.player_name}</p>
                    </button>
                    {prop.team && (
                      <p className="text-xs text-muted-foreground">{prop.team}</p>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <StatTypeBadge statType={prop.stat_type} />
                </TableCell>
                <TableCell className="text-right font-mono font-medium">
                  {Number(prop.line).toFixed(1)}
                </TableCell>
                <TableCell className="text-right font-mono">
                  {prop.projection !== null ? Number(prop.projection).toFixed(1) : 'N/A'}
                </TableCell>
                <TableCell className="text-right font-mono">
                  {formatProbability(prop.probability_over)}
                </TableCell>
                <TableCell className="text-right">
                  <EdgeBadge edge={prop.edge} size="sm" showLabel={false} />
                </TableCell>
                <TableCell className="text-center">
                  <ConfidenceBadge confidence={prop.confidence} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {sortedProps.length === 0 && (
          <div className="py-12 text-center text-muted-foreground">
            <p>No props available</p>
          </div>
        )}
      </div>

      <PlayerStatsModal
        isOpen={!!selectedPlayer}
        onClose={() => setSelectedPlayer(null)}
        playerName={selectedPlayer?.name || ''}
        statType={selectedPlayer?.statType}
        line={selectedPlayer?.line}
        prop={selectedPlayer?.prop || null}
      />
    </>
  );
}
