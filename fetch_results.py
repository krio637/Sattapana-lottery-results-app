"""
Fetch today's lottery results from satta-resultss.in
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

# State mapping from website
STATE_MAPPING = {
    'DELHI BAZAR': 'Delhi Bazar',
    'SHRI GANESH': 'Shri Ganesh',
    'DISAWER': 'Disawar',
    'FARIDABAD': 'Faridabad',
    'GHAZIABAD': 'Ghaziabad',
    'GAZIYABAD': 'Ghaziabad',
    'GALI': 'Gali'
}

# Manual states (not available on website)
MANUAL_STATES = ['Dwarka City', 'Ujjain King']


def fetch_results():
    """Fetch today's results from satta-resultss.in"""
    url = "https://www.satta-resultss.in/index.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    today = datetime.date.today()
    
    print(f"{'='*50}")
    print(f"Fetching results for {today}")
    print(f"{'='*50}\n")
    
    added, updated = 0, 0
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse tables for results
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                for cell in row.find_all(['td', 'th']):
                    text = cell.get_text(strip=True).upper()
                    
                    for key, state_name in STATE_MAPPING.items():
                        if key in text:
                            # Extract number from format: "STATE{XX}"
                            match = re.search(r'\{(\d+)\s*\}', text)
                            winning_number = match.group(1) if match else ''
                            
                            result, created = LotteryResult.objects.update_or_create(
                                date=today,
                                state=state_name,
                                defaults={'winning_number': winning_number}
                            )
                            
                            status = winning_number or 'WAITING'
                            if created:
                                added += 1
                                print(f"✓ Added: {state_name} - {status}")
                            else:
                                updated += 1
                                print(f"↻ Updated: {state_name} - {status}")
        
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
                updated += 1
                print(f"↻ Updated: {state_name} - WAITING")
        
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
