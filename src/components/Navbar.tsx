import { Link, useLocation } from 'react-router-dom';
import { TrendingUp, Trophy, RefreshCw, Gift } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { refreshData } from '@/lib/api';
import { toast } from 'sonner';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function Navbar() {
  const location = useLocation();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    toast.info('Refreshing prop data...');
    
    const result = await refreshData();
    
    if (result.success) {
      toast.success('Data refreshed successfully!');
      window.location.reload();
    } else {
      toast.error(result.message || 'Failed to refresh data');
    }
    
    setIsRefreshing(false);
  };

  const referralLinks = [
    {
      name: 'PrizePicks',
      url: 'https://app.prizepicks.com/sign-up?invite_code=PR-YA0U8GS&source=prizepicks&medium=user_referral&campaign=7fe0c867-d058-4651-97a8-3aa738a1b5bc&content=copy_link',
      bonus: '$25 Bonus Funds'
    },
    {
      name: 'Underdog Fantasy',
      url: 'https://play.underdogfantasy.com/alexaquino-bbbdfc02f9d75f4b',
      bonus: '100% Deposit Match + Bonus Funds'
    },
    {
      name: 'DraftKings Pick6',
      url: 'https://pick6.draftkings.com/r/psx/Ace18367/US-PSX/US-TX',
      bonus: '100% Deposit Match up to $50'
    },
    {
      name: 'Chalkboard',
      url: 'https://links.chalkboard.io/refer/cb-alexa',
      bonus: 'Promo Pack + $10 Bonus Funds'
    }
  ];

  const navItems = [
    { path: '/', label: 'Home', icon: TrendingUp },
    { path: '/props', label: 'Best Props', icon: Trophy },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 group-hover:bg-primary/20 transition-colors">
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold tracking-tight">PropEdge</span>
            <span className="text-[10px] uppercase tracking-widest text-muted-foreground">NBA Analytics</span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path;
            return (
              <Link key={path} to={path}>
                <Button
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={`gap-2 ${isActive ? 'bg-secondary text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </Button>
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          {/* Referral Links Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="default"
                size="sm"
                className="gap-2 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-semibold"
              >
                <Gift className="h-4 w-4" />
                <span className="hidden lg:inline">Free Bonuses</span>
                <span className="lg:hidden">Bonuses</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64">
              <DropdownMenuLabel>🎁 Exclusive Sign-Up Bonuses</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {referralLinks.map((link) => (
                <DropdownMenuItem key={link.name} asChild>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex flex-col gap-1 cursor-pointer"
                  >
                    <div className="font-semibold">{link.name}</div>
                    <div className="text-xs text-muted-foreground">{link.bonus}</div>
                  </a>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Refresh Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="gap-2"
            title="Refresh player props"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="hidden lg:inline">Refresh</span>
          </Button>
        </div>
      </div>

      {/* Mobile Navigation */}
      <nav className="md:hidden flex flex-col gap-2 pb-3 px-4">
        <div className="flex items-center justify-center gap-2">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path;
            return (
              <Link key={path} to={path} className="flex-1">
                <Button
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={`w-full gap-2 ${isActive ? 'bg-secondary text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                  size="sm"
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </Button>
              </Link>
            );
          })}
        </div>
        <div className="flex items-center gap-2">
          {/* Mobile Referral Button */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="default"
                size="sm"
                className="gap-2 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-semibold flex-1"
              >
                <Gift className="h-4 w-4" />
                <span className="text-xs">Free Bonuses</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64">
              <DropdownMenuLabel>🎁 Exclusive Sign-Up Bonuses</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {referralLinks.map((link) => (
                <DropdownMenuItem key={link.name} asChild>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex flex-col gap-1 cursor-pointer"
                  >
                    <div className="font-semibold">{link.name}</div>
                    <div className="text-xs text-muted-foreground">{link.bonus}</div>
                  </a>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Mobile Refresh Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="gap-2 flex-1"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="text-xs">Refresh</span>
          </Button>
        </div>
      </nav>
    </header>
  );
}
