import { cn } from '@/lib/utils';

interface StatTypeBadgeProps {
  statType: string;
  className?: string;
}

const statColors: Record<string, string> = {
  'Points': 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  'Rebounds': 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  'Assists': 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  'Pts+Rebs+Asts': 'bg-gradient-to-r from-orange-500/10 via-blue-500/10 to-purple-500/10 text-accent border-accent/30',
  'Pts+Rebs': 'bg-gradient-to-r from-orange-500/10 to-blue-500/10 text-cyan-400 border-cyan-500/30',
  'Pts+Asts': 'bg-gradient-to-r from-orange-500/10 to-purple-500/10 text-pink-400 border-pink-500/30',
  'Rebs+Asts': 'bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-indigo-400 border-indigo-500/30',
  '3-Pointers Made': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  'Steals': 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  'Blocks': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  'Turnovers': 'bg-red-500/10 text-red-400 border-red-500/30',
  'Fantasy Score': 'bg-primary/10 text-primary border-primary/30',
};

export function StatTypeBadge({ statType, className }: StatTypeBadgeProps) {
  const colorClass = statColors[statType] || 'bg-muted text-muted-foreground border-muted';

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border',
        colorClass,
        className
      )}
    >
      {statType}
    </span>
  );
}
