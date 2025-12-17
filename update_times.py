#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sattapana.settings')
django.setup()

from lottery.models import LotteryResult

# State timing mapping (from fetch_results.py)
STATE_TIMES = {
    'Disawar': '05:00 AM',
    'Delhi Bazar': '03:00 PM',
    'Shri Ganesh': '04:00 PM',
    'Faridabad': '06:15 PM',
    'Ghaziabad': '08:40 PM',
    'Gali': '11:30 PM',
    'Dwarka City': '10:00 AM',
    'Ujjain King': '12:00 PM',
    'Taj': '01:00 PM',
    'Time Bazaar': '02:30 PM'
}

def update_result_times():
    print("Updating result times for existing data...")
    
    updated_count = 0
    
    for result in LotteryResult.objects.all():
        if result.state in STATE_TIMES and not result.result_time:
            result.result_time = STATE_TIMES[result.state]
            result.save(update_fields=['result_time'])
            updated_count += 1
            print(f"Updated: {result.state} -> {result.result_time}")
    
    print(f"\nTotal updated: {updated_count}")

if __name__ == '__main__':
    update_result_times()