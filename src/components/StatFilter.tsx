import { Button } from '@/components/ui/button';
import { STAT_TYPES } from '@/types';

interface StatFilterProps {
  selectedStat: string | null;
  onSelectStat: (stat: string | null) => void;
}

export function StatFilter({ selectedStat, onSelectStat }: StatFilterProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant={selectedStat === null ? 'secondary' : 'ghost'}
        size="sm"
        onClick={() => onSelectStat(null)}
        className="text-xs"
      >
        All Stats
      </Button>
      {STAT_TYPES.map((stat) => (
        <Button
          key={stat}
          variant={selectedStat === stat ? 'secondary' : 'ghost'}
          size="sm"
          onClick={() => onSelectStat(stat)}
          className="text-xs"
        >
          {stat}
        </Button>
      ))}
    </div>
  );
}
