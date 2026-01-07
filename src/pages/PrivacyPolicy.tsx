import { Navbar } from '@/components/Navbar';
import { Card } from '@/components/ui/card';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
        
        <Card className="p-8">
          <div className="prose prose-invert max-w-none">
            <p className="text-muted-foreground mb-6">
              <strong>Last Updated:</strong> January 7, 2026
            </p>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">1. Information We Collect</h2>
              <p className="text-muted-foreground mb-4">
                NBA Prop Edge collects minimal information to provide our services. We do not require 
                user accounts or personal information to access our prop analysis tools.
              </p>
              <p className="text-muted-foreground">
                We may collect anonymous usage data such as page views, button clicks, and general 
                browsing behavior to improve our service.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">2. Google AdSense</h2>
              <p className="text-muted-foreground mb-4">
                We use Google AdSense to display advertisements on our website. Google AdSense uses 
                cookies and web beacons to serve ads based on your prior visits to our website or 
                other websites.
              </p>
              <p className="text-muted-foreground mb-4">
                Google's use of advertising cookies enables it and its partners to serve ads to you 
                based on your visit to our site and/or other sites on the Internet.
              </p>
              <p className="text-muted-foreground">
                You may opt out of personalized advertising by visiting{' '}
                <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                  Google Ads Settings
                </a>.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">3. Cookies</h2>
              <p className="text-muted-foreground mb-4">
                Our website uses cookies to enhance user experience and enable certain functionality. 
                Cookies are small text files stored on your device.
              </p>
              <p className="text-muted-foreground">
                Third-party vendors, including Google, use cookies to serve ads based on a user's 
                prior visits to our website or other websites.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">4. Third-Party Links</h2>
              <p className="text-muted-foreground">
                Our website contains affiliate links to sportsbooks and fantasy sports platforms 
                (PrizePicks, Underdog Fantasy, DraftKings, Chalkboard). We may earn a commission 
                when you sign up through these links. These third-party sites have their own privacy 
                policies which we encourage you to review.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">5. Analytics</h2>
              <p className="text-muted-foreground">
                We use Vercel Analytics to track website usage and improve our service. This includes 
                tracking page views, visitor sources, and general usage patterns. No personally 
                identifiable information is collected.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">6. Data Security</h2>
              <p className="text-muted-foreground">
                We implement reasonable security measures to protect any data we collect. However, 
                no internet transmission is completely secure, and we cannot guarantee absolute security.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">7. Children's Privacy</h2>
              <p className="text-muted-foreground">
                Our website is not intended for users under 18 years of age. We do not knowingly 
                collect information from minors. Sports betting and fantasy sports are restricted 
                to users 18+ (or 21+ depending on jurisdiction).
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">8. Changes to Privacy Policy</h2>
              <p className="text-muted-foreground">
                We may update this Privacy Policy from time to time. Changes will be posted on this 
                page with an updated "Last Updated" date.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">9. Contact Us</h2>
              <p className="text-muted-foreground">
                If you have questions about this Privacy Policy, please contact us through our 
                website or social media channels.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">10. Consent</h2>
              <p className="text-muted-foreground">
                By using our website, you consent to our Privacy Policy and agree to its terms.
              </p>
            </section>
          </div>
        </Card>
      </main>
    </div>
  );
}