import { Calendar, TrendingUp } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: 'calendar' | 'trending';
}

export function EmptyState({ title, description, icon = 'calendar' }: EmptyStateProps) {
  const Icon = icon === 'calendar' ? Calendar : TrendingUp;

  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
      <div className="h-16 w-16 rounded-2xl bg-secondary flex items-center justify-center">
        <Icon className="h-8 w-8 text-muted-foreground" />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-1">{title}</h3>
        <p className="text-muted-foreground text-sm max-w-sm">{description}</p>
      </div>
    </div>
  );
}
