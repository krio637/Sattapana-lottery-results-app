# Satta King Results - Fast Fetch Guide

## ✅ Optimizations Done

### 1. States Configuration

**Auto-Fetch States** (6 states - from website):
- **Disawar** (05:00 AM)
- **Delhi Bazar** (03:00 PM)
- **Shri Ganesh** (04:00 PM)
- **Faridabad** (06:15 PM)
- **Ghaziabad** (08:40 PM)
- **Gali** (11:30 PM)

**Manual States** (2 states - update from admin panel):
- **Dwarka City** (10:00 AM) 📝 Manual
- **Ujjain King** (12:00 PM) 📝 Manual

### 2. Faster Data Fetching
- Timeout reduced: 20s → 10s (faster response)
- Better regex matching for accurate results
- Cache-Control headers added for fresh data
- Improved error handling

### 3. Better Result Detection
- Case-insensitive matching
- Partial name matching for flexibility
- Better bracket pattern detection `[ XX ]`
- Handles both single and double digit numbers

## 🚀 How to Use

### Option 1: Manual Fetch (One Time)
```bash
python fetch_results.py
```

### Option 2: Auto Fetch (Every 5 Minutes)
```bash
# Install schedule library first
pip install schedule

# Run auto-fetch
python auto_fetch.py
```
Press `Ctrl+C` to stop auto-fetch.

### Option 3: Setup States First
```bash
python setup_states.py
```

## 📊 Output Example
```
Fetching results for 2025-12-17
==================================================
Status Code: 200
✓ Found: Disawar = 49
✓ Found: Delhi Bazar = 23
✓ Found: Shri Ganesh = 90
⏳ Waiting: Faridabad = (no result yet)
⏳ Waiting: Ghaziabad = (no result yet)
✓ Found: Gali = 43

Total found: 4
Added (Manual): Dwarka City (10:00 AM) - WAITING
Added (Manual): Ujjain King (12:00 PM) - WAITING
==================================================
✅ Done! Added: 8, Updated: 0
📝 Manual states (update from admin panel): Dwarka City, Ujjain King
```

## 🔧 Troubleshooting

### If results not fetching:
1. Check internet connection
2. Verify website is accessible: https://sattaking-result.in/
3. Run with verbose output to see raw data

### If wrong results:
1. Website format might have changed
2. Check the regex patterns in `_extract_today_result()`
3. Verify state names match website exactly

## 📝 Notes
- Results update automatically when available
- Empty brackets `[ ]` = Result pending
- Numbers are auto-padded to 2 digits (9 → 09)
- Database updates only when result changes
