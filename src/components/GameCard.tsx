import { Link } from 'react-router-dom';
import { Calendar, ChevronRight } from 'lucide-react';
import { format } from 'date-fns';
import { Card, CardContent } from '@/components/ui/card';
import { EdgeBadge } from './EdgeBadge';
import { StatTypeBadge } from './StatTypeBadge';
import type { GameWithProps } from '@/types';

interface GameCardProps {
  game: GameWithProps;
  index: number;
}

export function GameCard({ game, index }: GameCardProps) {
  const gameTime = new Date(game.game_time);
  const formattedTime = format(gameTime, 'h:mm a');
  const formattedDate = format(gameTime, 'MMM d');

  return (
    <Link to={`/game/${game.id}`}>
      <Card 
        className="group glass-card hover:border-primary/40 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5 cursor-pointer overflow-hidden"
        style={{ animationDelay: `${index * 100}ms` }}
      >
        <CardContent className="p-0">
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-border/50">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Calendar className="h-3.5 w-3.5" />
                <span>{formattedDate}</span>
                <span className="text-primary font-medium">{formattedTime}</span>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
          </div>

          {/* Matchup */}
          <div className="px-5 py-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-lg font-bold">{game.away_team_abbr || game.away_team}</p>
                <p className="text-xs text-muted-foreground">Away</p>
              </div>
              <div className="px-4">
                <span className="text-2xl font-black text-muted-foreground/30">@</span>
              </div>
              <div className="flex-1 text-right">
                <p className="text-lg font-bold">{game.home_team_abbr || game.home_team}</p>
                <p className="text-xs text-muted-foreground">Home</p>
              </div>
            </div>
          </div>

          {/* Top Props */}
          {game.topProps.length > 0 && (
            <div className="px-5 pb-5">
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-3 font-semibold">
                Top Value Props
              </p>
              <div className="space-y-2">
                {game.topProps.map((prop) => (
                  <div
                    key={prop.id}
                    className="flex items-center justify-between bg-secondary/50 rounded-lg px-3 py-2"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="font-medium text-sm truncate">{prop.player_name}</span>
                      <StatTypeBadge statType={prop.stat_type} />
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-xs text-muted-foreground">
                        O {prop.line}
                      </span>
                      <EdgeBadge edge={prop.edge} size="sm" showLabel={false} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {game.topProps.length === 0 && (
            <div className="px-5 pb-5">
              <div className="bg-secondary/30 rounded-lg px-4 py-3 text-center">
                <p className="text-xs text-muted-foreground">
                  No props with positive edge available
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
