"""
Backup fetch method with multiple attempts and better error handling
Run: python fetch_results_backup.py
"""
import os
import re
import time
from typing import Optional, Dict
import datetime
import django
import requests
from bs4 import BeautifulSoup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sattapana.settings')
django.setup()

from lottery.models import LotteryResult

# States configuration
STATES = {
    'DISAWAR': {'name': 'Disawar', 'time': '05:00 AM'},
    'DELHI BAZAR': {'name': 'Delhi Bazar', 'time': '03:00 PM'},
    'SHRI GANESH': {'name': 'Shri Ganesh', 'time': '04:00 PM'},
    'FARIDABAD': {'name': 'Faridabad', 'time': '06:15 PM'},
    'GHAZIABAD': {'name': 'Ghaziabad', 'time': '08:40 PM'},
    'GALI': {'name': 'Gali', 'time': '11:30 PM'},
}

MANUAL_STATES = {
    'Dwarka City': '10:00 AM',
    'Ujjain King': '12:00 PM',
}

def fetch_with_retry(url: str, max_retries: int = 3, timeout: int = 30) -> Optional[requests.Response]:
    """Fetch URL with retry logic"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
    }
    
    for attempt in range(max_retries):
        try:
            print(f"   Attempt {attempt + 1}/{max_retries}...", end=" ")
            response = requests.get(url, headers=headers, timeout=timeout)
            print(f"✓ Success (Status: {response.status_code})")
            return response
        except requests.Timeout:
            print(f"✗ Timeout")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"   Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        except requests.ConnectionError:
            print(f"✗ Connection Error")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"   Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"✗ Error: {type(e).__name__}")
            break
    
    return None

def _extract_today_result(lines: list, key: str) -> Optional[str]:
    """Extract today's result from website text"""
    key_upper = key.upper()
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if line_upper == key_upper or key_upper in line_upper:
            for j in range(i + 1, min(i + 6, len(lines))):
                next_line = lines[j]
                match = re.search(r'\[\s*(\d{1,2})\s*\]', next_line)
                if match:
                    return match.group(1)
                if re.search(r'\[\s*\]', next_line):
                    return None
            break
    return None

def fetch_results():
    """Fetch results with improved error handling"""
    url = "https://sattaking-result.in/"
    today = datetime.date.today()
    
    print(f"\n{'='*60}")
    print(f"  SATTA KING RESULTS FETCH - {today}")
    print(f"{'='*60}\n")
    
    print("🌐 Connecting to website...")
    response = fetch_with_retry(url, max_retries=3, timeout=30)
    
    if not response:
        print("\n❌ Failed to connect after multiple attempts")
        print("\n💡 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Try opening https://sattaking-result.in/ in browser")
        print("   3. Website might be temporarily down")
        print("   4. Try again after a few minutes")
        print("\n📝 Manual states will still be created (WAIT mode)")
        
        # Create manual states even if fetch fails
        added = 0
        for state, time in MANUAL_STATES.items():
            result, created = LotteryResult.objects.get_or_create(
                date=today,
                state=state,
                defaults={'winning_number': '', 'result_time': time}
            )
            if created:
                added += 1
                print(f"   Added: {state} ({time}) - WAITING")
        
        if added > 0:
            print(f"\n✅ Created {added} manual states")
        return
    
    print("\n📊 Parsing results...")
    soup = BeautifulSoup(response.content, 'html.parser')
    full_text = soup.get_text()
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
    
    found_results = {}
    for key, info in STATES.items():
        result = _extract_today_result(lines, key)
        if result:
            found_results[info['name']] = result.zfill(2)
            print(f"   ✓ {info['name']}: {result.zfill(2)}")
        else:
            print(f"   ⏳ {info['name']}: WAITING")
    
    print(f"\n📈 Found {len(found_results)} results")
    
    # Save to database
    print("\n💾 Saving to database...")
    added, updated = 0, 0
    
    for key, info in STATES.items():
        state_name = info['name']
        result_time = info['time']
        winning_number = found_results.get(state_name)
        
        result_obj, created = LotteryResult.objects.get_or_create(
            date=today,
            state=state_name,
            defaults={'winning_number': winning_number or '', 'result_time': result_time}
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
    
    # Manual states
    for state, time in MANUAL_STATES.items():
        result, created = LotteryResult.objects.get_or_create(
            date=today,
            state=state,
            defaults={'winning_number': '', 'result_time': time}
        )
        if created:
            added += 1
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE!")
    print(f"   Added: {added} | Updated: {updated}")
    print(f"   Manual states: {', '.join(MANUAL_STATES.keys())}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    fetch_results()
