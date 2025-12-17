"""
Fetch today's lottery results from sattaking-result.in
Run: python fetch_results.py
Optimized for fast and accurate data fetching
"""
import os
import re
import time
from typing import Optional
import datetime
import django
import requests
from bs4 import BeautifulSoup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sattapana.settings')
django.setup()

from lottery.models import LotteryResult

# States to fetch automatically from website
STATES = {
    'DISAWAR': {'name': 'Disawar', 'time': '05:00 AM'},
    'DELHI BAZAR': {'name': 'Delhi Bazar', 'time': '03:00 PM'},
    'SHRI GANESH': {'name': 'Shri Ganesh', 'time': '04:00 PM'},
    'FARIDABAD': {'name': 'Faridabad', 'time': '06:15 PM'},
    'GHAZIABAD': {'name': 'Ghaziabad', 'time': '08:40 PM'},
    'GALI': {'name': 'Gali', 'time': '11:30 PM'},
}

# Manual states - only create WAIT entries (admin will add results manually)
MANUAL_STATES = {
    'Dwarka City': '10:00 AM',
    'Ujjain King': '12:00 PM',
}

def _extract_today_result(lines: list, key: str) -> Optional[str]:
    """
    Extract today's result from the website.
    
    Website format (each on separate line):
    GAME_NAME
    ( TIME )
    { XX }  <-- yesterday's result  
    [ XX ]  <-- today's result (empty [ ] = waiting)
    
    We need the number inside square brackets [ XX ]
    """
    # Find the line with exact game name match (case-insensitive)
    key_upper = key.upper()
    for i, line in enumerate(lines):
        line_upper = line.upper()
        # Match exact or partial (for flexibility)
        if line_upper == key_upper or key_upper in line_upper:
            # Look at next few lines for the [ XX ] pattern (today's result)
            for j in range(i + 1, min(i + 6, len(lines))):
                next_line = lines[j]
                # Match [ XX ] where XX is 1-2 digits (today's result)
                match = re.search(r'\[\s*(\d{1,2})\s*\]', next_line)
                if match:
                    return match.group(1)
                # Check for empty brackets [ ] meaning waiting
                if re.search(r'\[\s*\]', next_line):
                    return None  # Result not yet available
            break
    return None

def fetch_results():
    """Fetch today's results from sattaking-result.in"""
    url = "https://sattaking-result.in/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    today = datetime.date.today()
    
    print(f"Fetching results for {today}")
    print("=" * 50)
    
    added, updated = 0, 0
    found_results = {}
    
    try:
        # Try with retry logic for reliability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                print(f"Status Code: {response.status_code}")
                break
            except requests.Timeout:
                if attempt < max_retries - 1:
                    print(f"⏳ Timeout, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    raise
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get page text and split into lines
        full_text = soup.get_text()
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        # Extract results for each game (with better matching)
        for key, info in STATES.items():
            result = _extract_today_result(lines, key)
            if result:
                # Pad single digit to 2 digits
                found_results[info['name']] = result.zfill(2)
                print(f"✓ Found: {info['name']} = {result.zfill(2)}")
            else:
                print(f"⏳ Waiting: {info['name']} = (no result yet)")
        
        print(f"\nTotal found: {len(found_results)}")
        
        # Save to database
        for key, info in STATES.items():
            state_name = info['name']
            result_time = info['time']
            winning_number = found_results.get(state_name)
            
            result_obj, created = LotteryResult.objects.get_or_create(
                date=today,
                state=state_name,
                defaults={
                    'winning_number': winning_number or '',
                    'result_time': result_time
                }
            )

            if created:
                added += 1

            update_fields = []
            if winning_number and winning_number != result_obj.winning_number:
                result_obj.winning_number = winning_number
                update_fields.append('winning_number')
            if result_obj.result_time != result_time:
                result_obj.result_time = result_time
                update_fields.append('result_time')

            if update_fields:
                result_obj.save(update_fields=update_fields + ['updated_at'])
                if not created:
                    updated += 1
                status = "Added" if created else "Updated"
            else:
                status = "Added" if created else "Unchanged"

            num = winning_number if winning_number else "WAITING"
            print(f"{status}: {state_name} ({result_time}) - {num}")
        
        # Create manual states with WAIT status (admin will update from panel)
        for state, time in MANUAL_STATES.items():
            result, created = LotteryResult.objects.get_or_create(
                date=today,
                state=state,
                defaults={
                    'winning_number': '',
                    'result_time': time
                }
            )
            if created:
                added += 1
                print(f"Added (Manual): {state} ({time}) - WAITING")
        
        print(f"\n{'='*50}")
        print(f"✅ Done! Added: {added}, Updated: {updated}")
        print(f"📝 Manual states (update from admin panel): {', '.join(MANUAL_STATES.keys())}")
        
    except requests.Timeout:
        print("❌ Error: Request timeout - website took too long to respond")
    except requests.ConnectionError:
        print("❌ Error: Connection failed - check internet connection")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    fetch_results()
