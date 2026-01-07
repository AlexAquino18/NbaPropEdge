import { Link } from 'react-router-dom';

export function Footer() {
  return (
    <footer className="border-t border-border/50 bg-background/80 backdrop-blur-xl mt-16">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-muted-foreground">
            © 2026 NBA Prop Edge. All rights reserved.
          </div>
          
          <div className="flex gap-6 text-sm">
            <Link to="/about" className="text-muted-foreground hover:text-foreground transition-colors">
              About
            </Link>
            <Link to="/how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">
              How It Works
            </Link>
            <Link to="/privacy-policy" className="text-muted-foreground hover:text-foreground transition-colors">
              Privacy Policy
            </Link>
            <a 
              href="https://www.ncpgambling.org" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Responsible Gaming
            </a>
          </div>
        </div>
        
        <div className="mt-4 text-center text-xs text-muted-foreground">
          Please gamble responsibly. You must be 21+ to participate in sports betting and fantasy sports.
        </div>
      </div>
    </footer>
  );
}