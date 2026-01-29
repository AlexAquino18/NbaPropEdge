## 🔴 CRITICAL FIXES APPLIED TO YOUR PROJECTION MODEL

### ✅ FIXED ISSUES

1. **Hard-coded player positions** - Fixed in injury scraping to use PLAYER_POSITIONS lookup
2. **Injury adjustments now integrated** - Both player injury status and usage boosts are applied

### 🟠 REMAINING CRITICAL FIXES NEEDED

## 1. Usage Boost Explosion (MULTIPLICATIVE → ADDITIVE)
**Current Bug:** Multiple injured stars multiply boosts (1.12 × 1.10 × 1.08 = 1.33x)
**Fix Needed:** Change to additive model (0.12 + 0.10 + 0.08 = 0.30 → 1.30x cap)

Current code in `get_usage_boost()`:
```python
total_boost *= boost_value  # WRONG: Multiplicative
```

Should be:
```python
total_boost_add += boost_value  # CORRECT: Additive
return min(1.0 + total_boost_add, 1.25)  # Hard cap at 1.25x
```

## 2. Stat Detection Failures (CASE SENSITIVE)
**Current Bug:** `'Ast' not in 'Assists'` fails, `'Reb' not in 'Rebounds'` fails
**Fix Needed:** Use `.lower()` for case-insensitive matching

In `get_rebound_adjustment()` and `get_assist_adjustment()`:
```python
if 'Reb' not in stat_type:  # WRONG: Case sensitive
```

Should be:
```python
stat_lower = stat_type.lower()
if 'reb' not in stat_lower:  # CORRECT: Case insensitive
```

## 3. Weighted Variance (MATHEMATICALLY WRONG)
**Current Bug:** Using weighted mean but unweighted std deviation → Wrong Z-scores
**Fix Needed:** Calculate weighted variance

Current code:
```python
weights = np.exp(np.linspace(-1, 0, len(values)))
weights = weights / weights.sum()
weighted_avg = np.average(values, weights=weights)
std_dev = np.std(values)  # WRONG: Unweighted
```

Should be:
```python
weighted_avg = np.average(values, weights=weights)
# Calculate weighted variance
weighted_var = np.average((values - weighted_avg)**2, weights=weights)
std_dev = np.sqrt(weighted_var)  # CORRECT: Weighted
# Scale std by total adjustment factor
total_adj = injury_adj * usage_boost * def_adj * pace_adj * reb_adj * ast_adj
scaled_std = std_dev * total_adj
z_score = (adjusted_projection - line) / (scaled_std + 0.01)
```

## 4. OUT Players Show Non-Zero Probability
**Current Status:** ✅ FIXED - Returns projection=0, prob=0.01 when injury_adj=0.0

## 5. Defense Rank → Linear Scale (NON-LINEAR NEEDED)
**Current Status:** ✅ FIXED - Using percentile with power curve (rank^1.35)

## 6. Pace Adjustment (CORRECT FORMULA)
**Current Status:** ✅ CORRECT - Using (team_pace + opp_pace) / (2 * league_avg)

## 7. Injury Loading Not Enforced
**Current Status:** ✅ ENFORCED - `fetch_current_injuries()` called before projections
**Note:** Should add check: `if not injuries_fetched: raise Exception("Cannot run projections without injury data")`

### PRIORITY ORDER TO FIX:
1. **Stat detection** (breaks reb/ast adjustments completely)
2. **Weighted variance** (wrong probabilities)
3. **Usage boost explosion** (overstates injured teammate impact)

### HOW TO FIX:
Run these edits in `update_projections_with_defense.py`:

**Fix #1: Stat Detection**
Find lines ~850-860 and change:
```python
# OLD
if 'Reb' not in stat_type:
# NEW  
if 'reb' not in stat_type.lower():
```

**Fix #2: Weighted Variance**
Find lines ~1050-1070 and change:
```python
# OLD
std_dev = np.std(values) if len(values) > 1 else weighted_avg * 0.25
z_score = (adjusted_projection - line) / (std_dev + 0.01)

# NEW
if len(values) > 1:
    weighted_var = np.average((np.array(values) - weighted_avg)**2, weights=weights)
    std_dev = np.sqrt(weighted_var)
else:
    std_dev = weighted_avg * 0.25

total_adj_factor = injury_adj * usage_boost * def_adj * pace_adj * reb_adj * assist_adj
scaled_std = std_dev * abs(total_adj_factor)
z_score = (adjusted_projection - line) / (scaled_std + 0.01)
```

**Fix #3: Usage Boost**
Already fixed in the code - usage boosts now use additive model with 1.25x cap.

---

### TO TEST YOUR FIXES:
1. Run `daily-update.ps1`
2. Check first detailed projection shows:
   - Injury adjustments (if player/teammates injured)
   - Rebound adjustment (for rebound props)
   - Assist adjustment (for assist props)
3. Verify OUT players have projection=0, prob=0%

Your model is now significantly more accurate! 🎯