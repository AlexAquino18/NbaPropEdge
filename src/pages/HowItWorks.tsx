import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card } from '@/components/ui/card';
import { TrendingUp, BarChart3, Target, Shield, Zap, LineChart, Users, Award } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export default function HowItWorks() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 py-12 max-w-5xl">
        <h1 className="text-4xl md:text-5xl font-bold mb-6">How NBA Prop Edge Works</h1>
        <p className="text-xl text-muted-foreground mb-12">
          A complete guide to understanding our NBA player prop analysis system, 
          how we calculate edges, and how to use our tools to find winning bets.
        </p>

        {/* What Are NBA Player Props */}
        <Card className="p-8 mb-8">
          <div className="flex items-start gap-4 mb-6">
            <Award className="h-10 w-10 text-primary flex-shrink-0" />
            <div>
              <h2 className="text-3xl font-bold mb-4">What Are NBA Player Props?</h2>
              <p className="text-muted-foreground text-lg mb-4">
                NBA player props (short for "proposition bets") are wagers on individual player 
                statistics rather than the outcome of the game. Instead of betting on which team 
                wins, you bet on whether a player will go over or under a specific statistical line.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-xl font-bold">Common Player Prop Types:</h3>
            <ul className="space-y-3 text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                <div>
                  <strong>Points:</strong> Will LeBron James score over or under 27.5 points?
                </div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                <div>
                  <strong>Rebounds:</strong> Will Nikola Jokic grab over or under 11.5 rebounds?
                </div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                <div>
                  <strong>Assists:</strong> Will Luka Doncic dish out over or under 8.5 assists?
                </div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                <div>
                  <strong>Three-Pointers Made:</strong> Will Stephen Curry hit over or under 4.5 threes?
                </div>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                <div>
                  <strong>Steals & Blocks:</strong> Will Anthony Davis get over or under 1.5 blocks?
                </div>
              </li>
            </ul>

            <p className="text-muted-foreground mt-6">
              Player props are popular because they allow you to focus on individual performances 
              rather than team outcomes, and you can find value by analyzing matchups, recent form, 
              and opponent weaknesses.
            </p>
          </div>
        </Card>

        {/* How Sportsbooks Set Lines */}
        <Card className="p-8 mb-8">
          <div className="flex items-start gap-4 mb-6">
            <BarChart3 className="h-10 w-10 text-accent flex-shrink-0" />
            <div>
              <h2 className="text-3xl font-bold mb-4">How Sportsbooks Set Player Prop Lines</h2>
              <p className="text-muted-foreground text-lg mb-4">
                Understanding how sportsbooks create lines is key to finding value. Sportsbooks 
                use a combination of algorithms, historical data, and market demand to set their 
                lines, but they're not always perfect.
              </p>
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-3">Factors Sportsbooks Consider:</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-bold mb-2">Season Averages</h4>
                  <p className="text-sm text-muted-foreground">
                    Player's points, rebounds, assists averages over the full season
                  </p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-bold mb-2">Recent Performance</h4>
                  <p className="text-sm text-muted-foreground">
                    Last 5-10 games to identify hot or cold streaks
                  </p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-bold mb-2">Opponent Defense</h4>
                  <p className="text-sm text-muted-foreground">
                    How well the opposing team defends against that position
                  </p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-bold mb-2">Market Sentiment</h4>
                  <p className="text-sm text-muted-foreground">
                    Public betting trends and where money is flowing
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-primary/10 border border-primary/20 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-3">Why Lines Aren't Always Perfect</h3>
              <p className="text-muted-foreground mb-4">
                Sportsbooks can't account for everything in real-time. They often:
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">✓</span>
                  <span>React slowly to recent player form or injury updates</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">✓</span>
                  <span>Oversimplify matchup analysis (miss position-specific trends)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">✓</span>
                  <span>Set lines to balance betting action, not just statistical accuracy</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">✓</span>
                  <span>Miss pace of play and efficiency adjustments</span>
                </li>
              </ul>
              <p className="text-muted-foreground mt-4 font-semibold">
                This is where NBA Prop Edge helps you find value.
              </p>
            </div>
          </div>
        </Card>

        {/* How NBA Prop Edge Works */}
        <Card className="p-8 mb-8">
          <div className="flex items-start gap-4 mb-6">
            <Target className="h-10 w-10 text-emerald-500 flex-shrink-0" />
            <div>
              <h2 className="text-3xl font-bold mb-4">How NBA Prop Edge Calculates Value</h2>
              <p className="text-muted-foreground text-lg mb-4">
                Our system uses advanced statistical analysis to identify props where the sportsbook 
                line doesn't match our data-driven projection, giving you an edge.
              </p>
            </div>
          </div>

          <div className="space-y-8">
            {/* Step 1 */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-primary text-primary-foreground rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  1
                </div>
                <h3 className="text-2xl font-bold">Collect Historical Performance Data</h3>
              </div>
              <p className="text-muted-foreground mb-4">
                We track every NBA player's performance over their last 15 games, analyzing:
              </p>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="font-bold mb-1">Points</div>
                  <div className="text-sm text-muted-foreground">Per-game scoring average</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="font-bold mb-1">Rebounds</div>
                  <div className="text-sm text-muted-foreground">Total rebounds per game</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="font-bold mb-1">Assists</div>
                  <div className="text-sm text-muted-foreground">Assists per game</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="font-bold mb-1">Steals</div>
                  <div className="text-sm text-muted-foreground">Steals per game</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="font-bold mb-1">Blocks</div>
                  <div className="text-sm text-muted-foreground">Blocks per game</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="font-bold mb-1">Three-Pointers</div>
                  <div className="text-sm text-muted-foreground">3PM per game</div>
                </div>
              </div>
              <p className="text-muted-foreground mt-4">
                <strong>Weighted Recent Games:</strong> We weight recent games more heavily than older games. 
                A player's last 3 games count more than games from 2 weeks ago, ensuring our projections 
                reflect current form.
              </p>
            </div>

            {/* Step 2 */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-primary text-primary-foreground rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  2
                </div>
                <h3 className="text-2xl font-bold">Adjust for Defensive Matchups</h3>
              </div>
              <p className="text-muted-foreground mb-4">
                Not all opponents are created equal. We adjust projections based on how well the 
                opposing team defends against specific positions:
              </p>
              <div className="bg-accent/10 border border-accent/20 rounded-lg p-6">
                <h4 className="font-bold mb-3">Position-Specific Defense</h4>
                <p className="text-muted-foreground mb-4">
                  If a point guard averages 24 points per game but is facing the #1 ranked defense 
                  against point guards, we adjust the projection down. If they're facing the #30 
                  ranked defense, we adjust it up.
                </p>
                <div className="grid md:grid-cols-2 gap-4 mt-4">
                  <div className="p-3 bg-background rounded">
                    <div className="text-sm font-bold mb-1">Example: Strong Defense</div>
                    <div className="text-xs text-muted-foreground">
                      Player avg: 25 pts → Opponent elite defense → Adjusted: 22.5 pts
                    </div>
                  </div>
                  <div className="p-3 bg-background rounded">
                    <div className="text-sm font-bold mb-1">Example: Weak Defense</div>
                    <div className="text-xs text-muted-foreground">
                      Player avg: 25 pts → Opponent poor defense → Adjusted: 27.8 pts
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-primary text-primary-foreground rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  3
                </div>
                <h3 className="text-2xl font-bold">Factor in Pace & Efficiency</h3>
              </div>
              <p className="text-muted-foreground mb-4">
                Game pace dramatically affects player stats. Teams that play faster create more 
                possessions, leading to more scoring, rebounds, and assists opportunities.
              </p>
              <div className="space-y-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-bold mb-2">Team Pace Adjustment</h4>
                  <p className="text-sm text-muted-foreground">
                    We analyze both teams' pace (possessions per 48 minutes). Fast-paced games 
                    boost scoring props, while slow-paced games reduce them.
                  </p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-bold mb-2">Offensive & Defensive Efficiency</h4>
                  <p className="text-sm text-muted-foreground">
                    We incorporate offensive rating (points per 100 possessions) and defensive 
                    rating to predict realistic game environments.
                  </p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-bold mb-2">Rebound Rate Adjustments</h4>
                  <p className="text-sm text-muted-foreground">
                    For rebounds, we factor in opponent defensive rebound percentage (DREB%). 
                    Teams that give up more rebounds boost opposing players' rebound props.
                  </p>
                </div>
              </div>
            </div>

            {/* Step 4 */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-primary text-primary-foreground rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  4
                </div>
                <h3 className="text-2xl font-bold">Calculate Statistical Probability</h3>
              </div>
              <p className="text-muted-foreground mb-4">
                Using historical data and variance, we calculate the probability that a player 
                goes over the sportsbook line:
              </p>
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-6">
                <h4 className="font-bold mb-3">Probability Calculation</h4>
                <p className="text-muted-foreground mb-4">
                  We use statistical distributions (normal distribution based on mean and standard 
                  deviation) to estimate the chance a player hits over the line.
                </p>
                <div className="grid md:grid-cols-3 gap-4 mt-4">
                  <div className="p-3 bg-background rounded text-center">
                    <div className="text-2xl font-bold text-emerald-500 mb-1">65%</div>
                    <div className="text-xs text-muted-foreground">High Confidence</div>
                  </div>
                  <div className="p-3 bg-background rounded text-center">
                    <div className="text-2xl font-bold text-primary mb-1">55%</div>
                    <div className="text-xs text-muted-foreground">Moderate Confidence</div>
                  </div>
                  <div className="p-3 bg-background rounded text-center">
                    <div className="text-2xl font-bold text-muted-foreground mb-1">48%</div>
                    <div className="text-xs text-muted-foreground">Low Confidence</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 5 */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-primary text-primary-foreground rounded-full w-10 h-10 flex items-center justify-center font-bold">
                  5
                </div>
                <h3 className="text-2xl font-bold">Compare to Sportsbook Lines & Calculate Edge</h3>
              </div>
              <p className="text-muted-foreground mb-4">
                Finally, we compare our projection to the sportsbook line to calculate your edge:
              </p>
              <div className="p-6 bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 rounded-lg">
                <h4 className="font-bold text-lg mb-3">Edge Formula</h4>
                <div className="bg-background p-4 rounded-lg mb-4">
                  <code className="text-sm">
                    Edge = ((Our Projection - Sportsbook Line) / Sportsbook Line) × 100
                  </code>
                </div>
                <h4 className="font-bold mb-2">Example:</h4>
                <ul className="space-y-2 text-muted-foreground">
                  <li>• Sportsbook Line: LeBron James 27.5 points</li>
                  <li>• Our Projection: 30.2 points</li>
                  <li>• Edge: ((30.2 - 27.5) / 27.5) × 100 = <strong className="text-emerald-500">+9.8%</strong></li>
                </ul>
                <p className="mt-4 text-sm">
                  A <strong>+9.8% edge</strong> means our projection is 9.8% higher than the sportsbook 
                  line, suggesting value in betting the over.
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* How to Use the Tool */}
        <Card className="p-8 mb-8">
          <div className="flex items-start gap-4 mb-6">
            <Users className="h-10 w-10 text-primary flex-shrink-0" />
            <div>
              <h2 className="text-3xl font-bold mb-4">How to Use NBA Prop Edge</h2>
              <p className="text-muted-foreground text-lg">
                Follow these steps to find winning NBA player prop bets using our platform.
              </p>
            </div>
          </div>

          <div className="space-y-6">
            <div className="p-6 bg-muted/50 rounded-lg">
              <h3 className="text-xl font-bold mb-3">Step 1: Browse Today's Props</h3>
              <p className="text-muted-foreground mb-3">
                Visit the <Link to="/props" className="text-primary hover:underline">Best Props</Link> page 
                to see all player props for today's NBA games. Props are automatically sorted by edge 
                percentage, with the highest value opportunities at the top.
              </p>
              <p className="text-sm text-muted-foreground italic">
                Tip: Props with +15% edge or higher are typically strong value plays.
              </p>
            </div>

            <div className="p-6 bg-muted/50 rounded-lg">
              <h3 className="text-xl font-bold mb-3">Step 2: Filter & Search</h3>
              <p className="text-muted-foreground mb-3">
                Use our powerful filters to narrow down props:
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span><strong>Player Search:</strong> Type a player's name to see all their props</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span><strong>Team Filter:</strong> Focus on specific teams</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span><strong>Stat Type:</strong> Filter by points, rebounds, assists, etc.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span><strong>Positive Edge Only:</strong> Show only props with positive expected value</span>
                </li>
              </ul>
            </div>

            <div className="p-6 bg-muted/50 rounded-lg">
              <h3 className="text-xl font-bold mb-3">Step 3: Analyze the Prop</h3>
              <p className="text-muted-foreground mb-3">
                For each prop, review these key metrics:
              </p>
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div className="p-3 bg-background rounded">
                  <div className="font-bold mb-1">Edge %</div>
                  <div className="text-sm text-muted-foreground">
                    How much value exists vs. the sportsbook line
                  </div>
                </div>
                <div className="p-3 bg-background rounded">
                  <div className="font-bold mb-1">Projection</div>
                  <div className="text-sm text-muted-foreground">
                    Our data-driven statistical projection
                  </div>
                </div>
                <div className="p-3 bg-background rounded">
                  <div className="font-bold mb-1">Probability Over</div>
                  <div className="text-sm text-muted-foreground">
                    % chance the player goes over the line
                  </div>
                </div>
                <div className="p-3 bg-background rounded">
                  <div className="font-bold mb-1">Confidence</div>
                  <div className="text-sm text-muted-foreground">
                    High, Medium, or Low based on consistency
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 bg-muted/50 rounded-lg">
              <h3 className="text-xl font-bold mb-3">Step 4: Place Your Bet</h3>
              <p className="text-muted-foreground mb-3">
                Once you've identified value props, sign up with a sportsbook using our referral links 
                to get exclusive bonuses:
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span><strong>PrizePicks:</strong> $25 Bonus Funds</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span><strong>Underdog Fantasy:</strong> 100% Deposit Match</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span><strong>DraftKings Pick6:</strong> 100% Match up to $50</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span><strong>Chalkboard:</strong> Promo Pack + $10 Bonus</span>
                </li>
              </ul>
              <p className="text-sm text-muted-foreground mt-3 italic">
                Click "Free Bonuses" in the navigation bar to access all referral links.
              </p>
            </div>
          </div>
        </Card>

        {/* Best Practices */}
        <Card className="p-8 mb-8">
          <h2 className="text-3xl font-bold mb-6">Best Practices for Using NBA Prop Edge</h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-3">✅ Do's</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  <span>Focus on props with +12% edge or higher for better long-term returns</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  <span>Check injury reports before placing bets (injuries can drastically change projections)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  <span>Combine our analysis with your own research for best results</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  <span>Track your bets to identify which prop types work best for you</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">✓</span>
                  <span>Set a bankroll limit and stick to it</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-bold mb-3">❌ Don'ts</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-destructive">✗</span>
                  <span>Don't bet on every prop with positive edge—be selective</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-destructive">✗</span>
                  <span>Don't ignore confidence ratings—low confidence props are riskier</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-destructive">✗</span>
                  <span>Don't chase losses by increasing bet sizes</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-destructive">✗</span>
                  <span>Don't rely solely on one tool—cross-check with other resources</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-destructive">✗</span>
                  <span>Don't bet more than you can afford to lose</span>
                </li>
              </ul>
            </div>
          </div>
        </Card>

        {/* CTA */}
        <Card className="p-8 text-center bg-gradient-to-r from-primary/10 to-accent/10">
          <h2 className="text-3xl font-bold mb-4">Ready to Find Winning Props?</h2>
          <p className="text-lg text-muted-foreground mb-6">
            Start using NBA Prop Edge today to identify high-value player prop opportunities 
            and make smarter betting decisions.
          </p>
          <Link to="/props">
            <Button size="lg" className="text-lg px-8 py-6">
              View Today's Best Props
              <TrendingUp className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </Card>

        {/* Disclaimer */}
        <Card className="p-6 bg-muted/50 mt-8">
          <p className="text-sm text-muted-foreground text-center">
            <strong>Disclaimer:</strong> NBA Prop Edge is a research and entertainment tool. 
            All projections are for informational purposes only. Past performance does not guarantee 
            future results. Sports betting involves risk. Please bet responsibly and only with money 
            you can afford to lose. If you have a gambling problem, seek help at{' '}
            <a href="https://www.ncpgambling.org" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
              ncpgambling.org
            </a>.
          </p>
        </Card>
      </main>

      <Footer />
    </div>
  );
}