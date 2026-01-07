import { Navbar } from '@/components/Navbar';
import { Card } from '@/components/ui/card';
import { TrendingUp, BarChart3, Shield, Target } from 'lucide-react';

export default function About() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">About NBA Prop Edge</h1>
        
        <Card className="p-8 mb-8">
          <div className="space-y-6">
            <section>
              <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
              <p className="text-muted-foreground text-lg">
                NBA Prop Edge was created to help sports bettors make more informed decisions 
                when betting on NBA player props. We provide free, data-driven analysis that 
                combines historical player performance, defensive matchups, team pace, and 
                statistical trends to identify value opportunities in the betting market.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">What We Do</h2>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <BarChart3 className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-bold mb-2">Analyze Player Performance</h3>
                    <p className="text-muted-foreground">
                      We track every NBA player's performance over their last 15 games, 
                      analyzing points, rebounds, assists, steals, blocks, and three-pointers. 
                      Our algorithms weight recent games more heavily to reflect current form.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Shield className="h-6 w-6 text-accent flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-bold mb-2">Account for Matchups</h3>
                    <p className="text-muted-foreground">
                      We adjust projections based on opponent defensive strength by position, 
                      team pace, and efficiency ratings to provide context-aware predictions.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Target className="h-6 w-6 text-emerald-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-bold mb-2">Calculate Statistical Edge</h3>
                    <p className="text-muted-foreground">
                      We compare our projections to sportsbook lines to identify props with 
                      positive expected value, helping you find the best betting opportunities.
                    </p>
                  </div>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">Why We're Different</h2>
              <ul className="space-y-3 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span><strong>100% Free:</strong> No subscriptions, no paywalls, no hidden fees</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span><strong>Advanced Analytics:</strong> Defensive matchups, pace adjustments, and efficiency ratings</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span><strong>Daily Updates:</strong> Fresh data and projections for every NBA game</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span><strong>Easy to Use:</strong> Simple interface with powerful filters and search</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span><strong>Transparent:</strong> We show you exactly how we calculate our projections</span>
                </li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">Data Sources</h2>
              <p className="text-muted-foreground">
                Our projections are powered by official NBA statistics, team performance data, 
                and advanced basketball analytics. We update our data daily to ensure accuracy 
                and relevance for each game day.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">Responsible Gaming</h2>
              <p className="text-muted-foreground mb-4">
                NBA Prop Edge is a research and entertainment tool. We believe in responsible 
                gaming and encourage all users to:
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li>• Only bet what you can afford to lose</li>
                <li>• Set limits on time and money spent on betting</li>
                <li>• Never chase losses</li>
                <li>• Seek help if gambling becomes a problem</li>
              </ul>
              <p className="text-muted-foreground mt-4">
                Resources: <a href="https://www.ncpgambling.org" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">National Council on Problem Gambling</a>
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">Disclaimer</h2>
              <p className="text-muted-foreground">
                All projections and analysis are for informational and entertainment purposes only. 
                Past performance does not guarantee future results. Sports betting involves risk, 
                and you should never bet more than you can afford to lose. We are not responsible 
                for any losses incurred from using our projections.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">Affiliate Disclosure</h2>
              <p className="text-muted-foreground">
                NBA Prop Edge participates in affiliate programs with various sportsbooks and 
                fantasy sports platforms. When you sign up through our referral links, we may 
                earn a commission at no additional cost to you. These partnerships help us keep 
                our service free for all users.
              </p>
            </section>
          </div>
        </Card>
      </main>
    </div>
  );
}