import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Trophy, Filter } from 'lucide-react';
import { Navbar } from '@/components/Navbar';
import { PropTable } from '@/components/PropTable';
import { StatFilter } from '@/components/StatFilter';
import { LoadingState } from '@/components/LoadingState';
import { EmptyState } from '@/components/EmptyState';
import { fetchAllProps } from '@/lib/api';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function BestProps() {
  const [selectedStat, setSelectedStat] = useState<string | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [showPositiveOnly, setShowPositiveOnly] = useState(true);

  const { data: props, isLoading, error } = useQuery({
    queryKey: ['all-props'],
    queryFn: fetchAllProps,
    refetchInterval: 60000,
  });

  // Get unique teams from props
  const teams = useMemo(() => {
    if (!props) return [];
    const uniqueTeams = new Set<string>();
    props.forEach((p) => {
      if (p.team) uniqueTeams.add(p.team);
    });
    return Array.from(uniqueTeams).sort();
  }, [props]);

  const filteredProps = useMemo(() => {
    if (!props) return [];
    
    let filtered = [...props];
    
    // Filter by stat type
    if (selectedStat) {
      filtered = filtered.filter((p) => p.stat_type === selectedStat);
    }
    
    // Filter by team
    if (selectedTeam) {
      filtered = filtered.filter((p) => p.team === selectedTeam);
    }
    
    // Filter by positive edge
    if (showPositiveOnly) {
      filtered = filtered.filter((p) => p.edge !== null && p.edge > 0);
    }
    
    // Sort by edge descending
    filtered.sort((a, b) => {
      const edgeA = a.edge ?? -Infinity;
      const edgeB = b.edge ?? -Infinity;
      return edgeB - edgeA;
    });
    
    return filtered;
  }, [props, selectedStat, selectedTeam, showPositiveOnly]);

  const positiveEdgeCount = props?.filter((p) => p.edge !== null && p.edge > 0).length || 0;
  const avgEdge = filteredProps.length > 0
    ? filteredProps.reduce((acc, p) => acc + (p.edge || 0), 0) / filteredProps.length
    : 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="fixed inset-0 bg-hero-glow pointer-events-none" />
      
      <Navbar />

      <main className="container mx-auto px-4 py-8 relative">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Trophy className="h-6 w-6 text-accent" />
            <h1 className="text-2xl md:text-3xl font-bold">Best Props</h1>
          </div>
          <p className="text-muted-foreground">
            Top value plays across all today's games, sorted by edge percentage
          </p>
        </header>

        {/* Stats Summary */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <div className="glass-card rounded-xl p-5">
            <p className="text-sm text-muted-foreground mb-1">Total Analyzed</p>
            <p className="text-3xl font-bold">{props?.length || 0}</p>
          </div>
          <div className="glass-card rounded-xl p-5">
            <p className="text-sm text-muted-foreground mb-1">Positive Edge</p>
            <p className="text-3xl font-bold text-primary">{positiveEdgeCount}</p>
          </div>
          <div className="glass-card rounded-xl p-5">
            <p className="text-sm text-muted-foreground mb-1">Avg Edge (Filtered)</p>
            <p className="text-3xl font-bold text-accent">
              {avgEdge > 0 ? '+' : ''}{(avgEdge * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <Button
            variant={showPositiveOnly ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowPositiveOnly(!showPositiveOnly)}
          >
            {showPositiveOnly ? 'Positive Edge Only' : 'Show All'}
          </Button>

          {/* Team Filter */}
          <Select value={selectedTeam || 'all'} onValueChange={(value) => setSelectedTeam(value === 'all' ? null : value)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All Teams" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Teams</SelectItem>
              {teams.map((team) => (
                <SelectItem key={team} value={team}>
                  {team}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Desktop Filter */}
          <div className="hidden lg:block">
            <StatFilter selectedStat={selectedStat} onSelectStat={setSelectedStat} />
          </div>

          {/* Mobile Filter Sheet */}
          <Sheet>
            <SheetTrigger asChild className="lg:hidden">
              <Button variant="outline" size="sm" className="gap-2">
                <Filter className="h-4 w-4" />
                Filter Stats
              </Button>
            </SheetTrigger>
            <SheetContent side="bottom" className="h-[60vh]">
              <SheetHeader>
                <SheetTitle>Filter by Stat Type</SheetTitle>
                <SheetDescription>
                  Select a stat type to filter the props
                </SheetDescription>
              </SheetHeader>
              <div className="mt-6">
                <StatFilter selectedStat={selectedStat} onSelectStat={setSelectedStat} />
              </div>
            </SheetContent>
          </Sheet>

          {(selectedStat || selectedTeam) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSelectedStat(null);
                setSelectedTeam(null);
              }}
              className="text-muted-foreground"
            >
              Clear Filters
            </Button>
          )}
        </div>

        {/* Props Table */}
        {isLoading && <LoadingState message="Loading best props..." />}

        {error && (
          <div className="text-center py-12">
            <p className="text-destructive">Failed to load props. Please try again.</p>
          </div>
        )}

        {!isLoading && !error && filteredProps.length === 0 && (
          <EmptyState
            title="No Props Found"
            description={
              selectedStat || selectedTeam
                ? `No ${selectedStat || 'props'} ${selectedTeam ? `for ${selectedTeam}` : ''} with ${showPositiveOnly ? 'positive edge' : 'data'} available.`
                : `No props with ${showPositiveOnly ? 'positive edge' : 'data'} available.`
            }
            icon="trending"
          />
        )}

        {!isLoading && !error && filteredProps.length > 0 && (
          <>
            <div className="mb-4 text-sm text-muted-foreground">
              Showing {filteredProps.length} prop{filteredProps.length !== 1 ? 's' : ''}
            </div>
            <PropTable props={filteredProps} />
          </>
        )}
      </main>
    </div>
  );
}
