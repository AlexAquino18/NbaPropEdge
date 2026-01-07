import { cn } from '@/lib/utils';

interface EdgeBadgeProps {
  edge: number | null;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function EdgeBadge({ edge, size = 'md', showLabel = true }: EdgeBadgeProps) {
  if (edge === null) {
    return (
      <span className="stat-badge bg-muted text-muted-foreground">
        N/A
      </span>
    );
  }

  const isPositive = edge > 0;
  const isNeutral = edge === 0;
  // Edge is already stored as a percentage in the database, no need to multiply by 100
  const edgePercent = edge.toFixed(1);

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  };

  return (
    <span
      className={cn(
        'stat-badge font-mono font-semibold rounded-md border transition-all',
        sizeClasses[size],
        {
          'bg-primary/10 text-primary border-primary/30': isPositive,
          'bg-destructive/10 text-destructive border-destructive/30': !isPositive && !isNeutral,
          'bg-muted text-muted-foreground border-muted': isNeutral,
        }
      )}
    >
      {isPositive && '+'}
      {edgePercent}%{showLabel && ' Edge'}
    </span>
  );
}
