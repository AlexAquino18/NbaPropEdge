# Setup Hourly Odds Tracker - Windows Scheduled Task
# This script creates a Windows Task Scheduler job that runs every hour

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SETTING UP HOURLY ODDS TRACKER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get the current directory
$scriptPath = $PSScriptRoot
if (-not $scriptPath) {
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
}
if (-not $scriptPath) {
    $scriptPath = Get-Location
}

Write-Host "Working directory: $scriptPath" -ForegroundColor Yellow
Write-Host ""

# Find Python executable
$pythonCmd = $null
$pythonPaths = @("python", "python3", "py")

foreach ($cmd in $pythonPaths) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "Found Python: $version" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

# Get full path to Python
$pythonPath = (Get-Command $pythonCmd).Source
Write-Host "Python path: $pythonPath" -ForegroundColor Yellow
Write-Host ""

# Path to the odds fetching script
$oddsScript = Join-Path $scriptPath "scripts\fetch_sportsbook_odds.py"

if (-not (Test-Path $oddsScript)) {
    Write-Host "Script not found: $oddsScript" -ForegroundColor Red
    exit 1
}

Write-Host "Odds script: $oddsScript" -ForegroundColor Yellow
Write-Host ""

# Create the task
$taskName = "NBA-Odds-Tracker-Hourly"
$taskDescription = "Fetches NBA sportsbook odds every hour and stores them in local SQLite database for line movement tracking"

Write-Host "Creating scheduled task: $taskName" -ForegroundColor Cyan
Write-Host ""

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action - run Python script
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument "`"$oddsScript`"" `
    -WorkingDirectory $scriptPath

# Create trigger - every hour
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Description $taskDescription `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -User $env:USERNAME `
        -RunLevel Limited `
        -Force | Out-Null
    
    Write-Host "Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "TASK DETAILS" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Task Name:    $taskName" -ForegroundColor White
    Write-Host "Schedule:     Every 1 hour" -ForegroundColor White
    Write-Host "Next Run:     $(Get-Date)" -ForegroundColor White
    Write-Host "Script:       $oddsScript" -ForegroundColor White
    Write-Host "Database:     $scriptPath\odds_history.db" -ForegroundColor White
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "WHAT HAPPENS NOW?" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "- Task runs automatically every hour" -ForegroundColor Green
    Write-Host "- Fetches latest odds from DraftKings and FanDuel" -ForegroundColor Green
    Write-Host "- Stores odds in local database for line tracking" -ForegroundColor Green
    Write-Host "- Runs in background (no window pops up)" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "USEFUL COMMANDS" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "View task in Task Scheduler:" -ForegroundColor Yellow
    Write-Host "  taskschd.msc" -ForegroundColor White
    Write-Host ""
    Write-Host "Run task manually right now:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "Check task status:" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo" -ForegroundColor White
    Write-Host ""
    Write-Host "Disable task:" -ForegroundColor Yellow
    Write-Host "  Disable-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "Enable task:" -ForegroundColor Yellow
    Write-Host "  Enable-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "Delete task:" -ForegroundColor Yellow
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:$false" -ForegroundColor White
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "TIP: Run it now to test!" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Ask if user wants to run now
    $response = Read-Host "Run the task now to test it? (Y/n)"
    if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
        Write-Host ""
        Write-Host "Running task now..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $taskName
        Write-Host "Task started! Check the output above." -ForegroundColor Green
        Write-Host ""
        Write-Host "Database location: $scriptPath\odds_history.db" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "Failed to create scheduled task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Setup complete! Odds will be tracked automatically every hour." -ForegroundColor Green
Write-Host ""
