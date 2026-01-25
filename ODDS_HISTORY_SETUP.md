# Odds History Tracking Setup Guide

This guide explains how to set up automatic hourly tracking of sportsbook odds to visualize line movement over time.

## 📋 Overview

The odds history feature tracks changes in betting lines from DraftKings, FanDuel, and PrizePicks over time, allowing you to:
- View line movement graphs for any player prop
- See percentage changes and trends
- Make better betting decisions based on historical data
- Identify value opportunities when lines move

## 🗄️ Database Setup

### Step 1: Run the Migration

You need to create the `odds_history` table in your Supabase database.

**Option A: Using the Python script (Recommended)**
```bash
python scripts/apply_odds_history_migration.py
```

**Option B: Manual SQL (if script fails)**
1. Go to your Supabase Dashboard → SQL Editor
2. Copy and paste the contents of `supabase/migrations/20260124000000_add_odds_history.sql`
3. Click "Run"

The migration creates:
- `odds_history` table to store historical odds data
- Indexes for efficient querying
- Foreign key relationship to the props table

## 📊 Frontend Components

The following components have been created/updated:

### 1. OddsHistoryChart Component
- **Location**: `src/components/OddsHistoryChart.tsx`
- **Features**:
  - Line chart showing odds movement over time
  - Displays DraftKings, FanDuel, and PrizePicks lines
  - Shows percentage changes and current values
  - Opens in a modal dialog when clicked

### 2. Updated PropTable Component
- **Location**: `src/components/PropTable.tsx`
- **Changes**: Added a clickable graph icon (📈) next to sportsbook odds
- **Usage**: Click the blue trending icon to view line movement history

### 3. Updated TypeScript Types
- **Location**: `src/integrations/supabase/types.ts`
- **Changes**: Added `odds_history` table definition and sportsbook columns to props

## 🤖 Automated Tracking

### Python Tracking Script

**Location**: `scripts/track_odds_history.py`

This script:
1. Fetches all current props from the database
2. Records current odds for each prop into the `odds_history` table
3. Runs hourly to build historical data

**Manual Test Run**:
```bash
python scripts/track_odds_history.py
```

### Windows Task Scheduler Setup

To automatically run the tracking script every hour:

#### Option 1: Using PowerShell Script (Easier)

1. **Open PowerShell as Administrator**

2. **Create the scheduled task**:
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"C:\Users\Alex\Downloads\stat-stack-main\stat-stack-main\track-odds-hourly.ps1`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable
Register-ScheduledTask -TaskName "Track Odds History" -Action $action -Trigger $trigger -Settings $settings -Description "Hourly tracking of sportsbook odds for line movement analysis"
```

3. **Verify the task**:
```powershell
Get-ScheduledTask -TaskName "Track Odds History"
```

#### Option 2: Using Task Scheduler GUI

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name it: "Track Odds History"
4. Trigger: **Daily**, starting today
5. Action: **Start a program**
   - Program: `PowerShell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\Users\Alex\Downloads\stat-stack-main\stat-stack-main\track-odds-hourly.ps1"`
6. After creation, right-click the task → **Properties**
7. Go to **Triggers** tab → Edit trigger
8. Check **Repeat task every: 1 hour**
9. Check **for a duration of: Indefinitely**
10. Click **OK**

#### Option 3: Direct Python Execution

If you prefer to run Python directly:

1. Open Task Scheduler
2. Create Basic Task: "Track Odds History"
3. Trigger: Daily, repeat every 1 hour
4. Action: Start a program
   - Program: `python.exe` (full path, e.g., `C:\Python311\python.exe`)
   - Arguments: `"C:\Users\Alex\Downloads\stat-stack-main\stat-stack-main\scripts\track_odds_history.py"`
   - Start in: `C:\Users\Alex\Downloads\stat-stack-main\stat-stack-main`

## 🎯 Usage

### Viewing Line Movement

1. Navigate to the props table on your website
2. Look for the blue **trending up icon (📈)** next to sportsbook odds
3. Click the icon to open the line movement chart
4. The graph shows:
   - Historical line values over time
   - Color-coded lines for each sportsbook
   - Summary statistics showing current value and change percentage

### Building Historical Data

- The system needs to run for at least a few hours to build meaningful data
- After the first run, you'll see "No historical data available yet"
- Each hour adds a new data point to the graph
- Data accumulates over days/weeks for better trend analysis

## 🔍 Monitoring

### Check if Task is Running

**PowerShell**:
```powershell
Get-ScheduledTask -TaskName "Track Odds History" | Get-ScheduledTaskInfo
```

### View Task History

1. Open Task Scheduler
2. Find "Track Odds History" task
3. Click **History** tab (enable if disabled)
4. Review execution logs

### Manual Test

Run the tracking script manually to verify it works:
```bash
cd "C:\Users\Alex\Downloads\stat-stack-main\stat-stack-main"
python scripts/track_odds_history.py
```

Expected output:
```
🔧 Tracking odds history...
✅ Recorded odds for 15 props
📊 Odds history tracking complete!
```

## 🛠️ Troubleshooting

### "No historical data available yet"
- The tracking script needs to run at least once
- Run `python scripts/track_odds_history.py` manually to populate initial data
- Wait for the next hourly run to see trend data

### Script not running automatically
- Check Task Scheduler for errors
- Verify Python is in your PATH
- Check that `.env` file has correct Supabase credentials
- Review Task Scheduler history for error messages

### Database errors
- Ensure the migration was applied successfully
- Verify Supabase credentials in `.env` file
- Check that the `odds_history` table exists in Supabase

### Graph not appearing
- Ensure you've rebuilt the frontend: `npm run build` or restart dev server
- Clear browser cache
- Check browser console for errors

## 📈 Best Practices

1. **Run during peak hours**: Schedule around game times for most accurate data
2. **Monitor storage**: Historical data grows over time; consider archiving old data
3. **Backup data**: Export odds history periodically
4. **Check logs**: Review Task Scheduler logs weekly to ensure smooth operation

## 🔄 Maintenance

### Disable tracking temporarily
```powershell
Disable-ScheduledTask -TaskName "Track Odds History"
```

### Re-enable tracking
```powershell
Enable-ScheduledTask -TaskName "Track Odds History"
```

### Remove tracking task
```powershell
Unregister-ScheduledTask -TaskName "Track Odds History" -Confirm:$false
```

## 📚 Additional Resources

- **Supabase Dashboard**: Check table data and run queries
- **Task Scheduler**: Monitor execution and view logs
- **Browser DevTools**: Debug frontend issues

## ✅ Quick Start Checklist

- [ ] Run database migration (`python scripts/apply_odds_history_migration.py`)
- [ ] Test tracking script (`python scripts/track_odds_history.py`)
- [ ] Set up Windows Task Scheduler (choose an option above)
- [ ] Verify task runs successfully
- [ ] Wait for hourly data collection
- [ ] View line movement graphs in the UI

---

**Need help?** Check the Supabase logs and Task Scheduler history for detailed error messages.
