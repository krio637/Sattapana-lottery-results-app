"""
Fetch today's lottery results from sattaking-result.in
Run: python fetch_results.py
"""
import os
import re
import datetime
import django
import requests
from bs4 import BeautifulSoup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sattapana.settings')
django.setup()

from lottery.models import LotteryResult

# State mapping
STATE_MAPPING = {
    'DELHI BAZAR': 'Delhi Bazar',
    'SHRI GANESH': 'Shri Ganesh',
    'DISAWAR': 'Disawar',
    'DISAWER': 'Disawar',
    'FARIDABAD': 'Faridabad',
    'GHAZIABAD': 'Ghaziabad',
    'GAZIYABAD': 'Ghaziabad',
    'GALI': 'Gali'
}

# Manual states (not available on website)
MANUAL_STATES = ['Dwarka City', 'Ujjain King']


def fetch_results():
    """Fetch today's results from sattaking-result.in"""
    url = "https://sattaking-result.in/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    today = datetime.date.today()
    
    print(f"{'='*50}")
    print(f"Fetching results for {today}")
    print(f"{'='*50}\n")
    
    added, updated = 0, 0
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        html_text = soup.get_text()
        
        # Find results in the page
        for key, state_name in STATE_MAPPING.items():
            # Look for pattern: STATE_NAME followed by number
            pattern = rf'{key}\s*[\n\r\s]*(\d{{2}})'
            match = re.search(pattern, html_text, re.IGNORECASE)
            
            if match:
                winning_number = match.group(1)
                
                result, created = LotteryResult.objects.update_or_create(
                    date=today,
                    state=state_name,
                    defaults={'winning_number': winning_number}
                )
                
                if created:
                    added += 1
                    print(f"✓ Added: {state_name} - {winning_number}")
                else:
                    updated += 1
                    print(f"↻ Updated: {state_name} - {winning_number}")
            else:
                # Add with waiting status if not found
                result, created = LotteryResult.objects.update_or_create(
                    date=today,
                    state=state_name,
                    defaults={'winning_number': ''}
                )
                if created:
                    added += 1
                    print(f"✓ Added: {state_name} - WAITING")
        
        # Add manual states with WAITING status
        print("\nAdding manual states...")
        for state_name in MANUAL_STATES:
            result, created = LotteryResult.objects.update_or_create(
                date=today,
                state=state_name,
                defaults={'winning_number': ''}
            )
            if created:
                added += 1
                print(f"✓ Added: {state_name} - WAITING")
            else:
                print(f"↻ Exists: {state_name}")
        
        print(f"\n{'='*50}")
        print(f"✅ Complete! Added: {added}, Updated: {updated}")
        print(f"Total in database: {LotteryResult.objects.count()}")
        print(f"{'='*50}")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    fetch_results()
