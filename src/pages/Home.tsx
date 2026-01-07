import { Link } from 'react-router-dom';
import { TrendingUp, BarChart3, Zap, Shield, Target, LineChart } from 'lucide-react';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <div className="fixed inset-0 bg-hero-glow pointer-events-none" />
      <Navbar />

      <main className="container mx-auto px-4 py-12 relative">
        {/* Hero Section */}
        <section className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            NBA Prop Edge – Smarter NBA Player Prop Research
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            NBA Prop Edge is a free NBA player prop research tool that helps bettors 
            analyze player performance, line movement, and statistical trends to make 
            more informed betting decisions.
          </p>
          <Link to="/props">
            <Button size="lg" className="text-lg px-8 py-6">
              View Today's Props
              <TrendingUp className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </section>

        {/* How It Works */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-6">
              <BarChart3 className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-xl font-bold mb-3">Compare Lines to Performance</h3>
              <p className="text-muted-foreground">
                We analyze sportsbook lines against players' historical performance data 
                from their last 15 games, weighted toward recent performances for accuracy.
              </p>
            </Card>
            
            <Card className="p-6">
              <Target className="h-12 w-12 text-accent mb-4" />
              <h3 className="text-xl font-bold mb-3">Statistical Edge Calculation</h3>
              <p className="text-muted-foreground">
                Our algorithm identifies props with the largest statistical edge by 
                comparing projected performance to betting lines across multiple sportsbooks.
              </p>
            </Card>
            
            <Card className="p-6">
              <Zap className="h-12 w-12 text-emerald-500 mb-4" />
              <h3 className="text-xl font-bold mb-3">Daily Updates</h3>
              <p className="text-muted-foreground">
                Data updates daily for all NBA games, including defensive matchups, 
                pace adjustments, and team efficiency ratings for comprehensive analysis.
              </p>
            </Card>
          </div>
        </section>

        {/* What We Analyze */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">What We Analyze</h2>
          <div className="max-w-4xl mx-auto">
            <Card className="p-8">
              <div className="space-y-6">
                <div className="flex gap-4">
                  <LineChart className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-bold mb-2">Player Performance Trends</h3>
                    <p className="text-muted-foreground">
                      We track each player's last 15 games, analyzing points, rebounds, assists, 
                      steals, blocks, and three-pointers made. Recent games are weighted more 
                      heavily to reflect current form.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Shield className="h-6 w-6 text-accent flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-bold mb-2">Defensive Matchups</h3>
                    <p className="text-muted-foreground">
                      Our system accounts for opponent defensive strength by position, 
                      adjusting projections based on how well the opposing team defends 
                      against specific player positions (PG, SG, SF, PF, C).
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <BarChart3 className="h-6 w-6 text-emerald-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-bold mb-2">Team Pace & Efficiency</h3>
                    <p className="text-muted-foreground">
                      We factor in both teams' pace of play (possessions per game) and 
                      offensive/defensive efficiency ratings to project realistic stat lines 
                      based on game environment.
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </section>

        {/* Who It's For */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">Who It's For</h2>
          <div className="max-w-3xl mx-auto">
            <Card className="p-8">
              <p className="text-lg text-muted-foreground mb-4">
                NBA Prop Edge is designed for sports bettors who want to make more informed 
                decisions when betting on NBA player props. Whether you're betting on PrizePicks, 
                Underdog Fantasy, DraftKings, or traditional sportsbooks, our tool helps you:
              </p>
              <ul className="space-y-3 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Identify value opportunities where lines don't match player performance</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Understand how matchups and pace affect player stat projections</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Save time by filtering props by player, team, or stat type</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Make data-driven decisions with confidence ratings and probability calculations</span>
                </li>
              </ul>
            </Card>
          </div>
        </section>

        {/* How to Use */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">How to Use NBA Prop Edge</h2>
          <div className="max-w-3xl mx-auto">
            <div className="space-y-6">
              <Card className="p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-primary text-primary-foreground rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                    1
                  </div>
                  <div>
                    <h3 className="text-lg font-bold mb-2">Browse Today's Props</h3>
                    <p className="text-muted-foreground">
                      View all player props for today's NBA games, sorted by statistical edge. 
                      Props with the highest edge appear at the top.
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-primary text-primary-foreground rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                    2
                  </div>
                  <div>
                    <h3 className="text-lg font-bold mb-2">Filter & Search</h3>
                    <p className="text-muted-foreground">
                      Use our search bar to find specific players, or filter by team, 
                      stat type (points, rebounds, assists, etc.), or minimum edge percentage.
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-primary text-primary-foreground rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                    3
                  </div>
                  <div>
                    <h3 className="text-lg font-bold mb-2">Review Projections</h3>
                    <p className="text-muted-foreground">
                      Check our projection vs. the sportsbook line, along with probability 
                      over, confidence level, and edge percentage to inform your decision.
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-primary text-primary-foreground rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                    4
                  </div>
                  <div>
                    <h3 className="text-lg font-bold mb-2">Place Your Bets</h3>
                    <p className="text-muted-foreground">
                      Use our referral links to sign up with sportsbooks and get exclusive 
                      bonuses. Then place your informed bets on the props you've researched.
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center mb-16">
          <Card className="p-12 bg-gradient-to-r from-primary/10 to-accent/10">
            <h2 className="text-3xl font-bold mb-4">
              Start Making Smarter NBA Prop Bets Today
            </h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Use the table below to explore today's best NBA player prop opportunities 
              with our advanced analytics and statistical edge calculations.
            </p>
            <Link to="/props">
              <Button size="lg" className="text-lg px-8 py-6">
                View All Props
                <TrendingUp className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </Card>
        </section>

        {/* Disclaimer */}
        <section className="max-w-3xl mx-auto">
          <Card className="p-6 bg-muted/50">
            <p className="text-sm text-muted-foreground text-center">
              <strong>Responsible Gaming:</strong> NBA Prop Edge is a research tool for entertainment 
              purposes. Always bet responsibly and within your means. Past performance does not 
              guarantee future results. Please gamble responsibly and seek help if needed.
            </p>
          </Card>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}