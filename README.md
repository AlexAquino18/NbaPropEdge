# 🏀 NBA PropEdge

Advanced NBA player prop betting analytics platform with real-time projections and defensive matchup analysis.

## 🎯 Features

- **Real-time NBA game tracking** - Fetches today's games from Ball Don't Lie API
- **Advanced projections** - Statistical models with defensive matchups, pace adjustments, and team efficiency
- **Player statistics** - Historical performance data for accurate predictions
- **Edge calculation** - Identifies value betting opportunities
- **Responsive design** - Beautiful UI built with React + Tailwind CSS

## 🚀 Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **Backend**: Supabase (Database + Authentication)
- **Analytics**: Python (NumPy, SciPy)
- **Deployment**: Ready for Vercel/Netlify

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/nba-propedge.git
cd nba-propedge
```

2. **Install dependencies**
```bash
npm install
pip install python-dotenv supabase requests numpy scipy
```

3. **Set up environment variables**

Create a `.env` file in the root directory:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_PUBLISHABLE_KEY=your_supabase_key
```

4. **Run the development server**
```bash
npm run dev
```

## 🔄 Updating Projections

To fetch today's games and update projections:

### Windows (PowerShell)
```powershell
.\run-projections.ps1
```

### Manual (Python)
```bash
python scripts/run_full_projections.py
```

This will:
1. Fetch today's NBA games from Ball Don't Lie API
2. Link props to games
3. Calculate advanced projections with defensive adjustments
4. Update Supabase database

## 📊 Projection Features

- **Defensive Matchup Analysis** - Position-specific defensive rankings
- **Pace Adjustments** - Team tempo and possessions per game
- **Efficiency Ratings** - Offensive/defensive ratings impact
- **Statistical Confidence** - Probability calculations using historical data
- **Recent Form Weighting** - Recent games weighted more heavily

## 🛠️ Scripts

- `run_full_projections.py` - Main pipeline (fetch games → link props → run projections)
- `fetch_player_stats_robust.py` - Fetch player statistics from NBA API
- `update_projections_with_defense.py` - Advanced projection calculations
- `load_jan6.py` - Manual game linking for specific dates

## 📁 Project Structure

```
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── lib/            # Utilities and API
│   └── types/          # TypeScript types
├── scripts/            # Python analytics scripts
├── supabase/           # Database migrations
└── public/             # Static assets
```

## 🚢 Deployment

### Deploy to Vercel

1. Push to GitHub
2. Import repository in Vercel
3. Add environment variables (VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY)
4. Deploy!

### Update Projections (Production)

Set up GitHub Actions for automated daily updates at 5 PM EST.

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.
