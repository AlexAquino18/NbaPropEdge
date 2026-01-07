import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Loading...' }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="relative">
        <div className="h-12 w-12 rounded-full border-2 border-primary/20" />
        <Loader2 className="h-12 w-12 text-primary animate-spin absolute inset-0" />
      </div>
      <p className="text-muted-foreground animate-pulse-soft">{message}</p>
    </div>
  );
}

export function GameCardSkeleton() {
  return (
    <div className="glass-card rounded-xl p-5 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="h-4 w-24 bg-muted rounded shimmer" />
        <div className="h-4 w-4 bg-muted rounded shimmer" />
      </div>
      <div className="flex items-center justify-between mb-6">
        <div className="h-6 w-16 bg-muted rounded shimmer" />
        <div className="h-6 w-8 bg-muted rounded shimmer" />
        <div className="h-6 w-16 bg-muted rounded shimmer" />
      </div>
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-10 bg-muted rounded shimmer" />
        ))}
      </div>
    </div>
  );
}
