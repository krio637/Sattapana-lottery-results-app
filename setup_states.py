#!/usr/bin/env python
import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sattapana.settings')
django.setup()

from lottery.models import LotteryResult

# All states with their result times
ALL_STATES = {
    'Disawar': '05:00 AM',
    'Dwarka City': '10:00 AM',
    'Ujjain King': '12:00 PM',
    'Delhi Bazar': '03:00 PM', 
    'Shri Ganesh': '04:00 PM',
    'Faridabad': '06:15 PM',
    'Ghaziabad': '08:40 PM',
    'Gali': '11:30 PM',
}

def setup_states():
    """Ensure all states exist in database for today with proper timing"""
    today = date.today()
    
    print(f"Setting up states for {today}")
    print("=" * 50)
    
    added = 0
    updated = 0
    
    for state_name, result_time in ALL_STATES.items():
        result_obj, created = LotteryResult.objects.get_or_create(
            date=today,
            state=state_name,
            defaults={
                'winning_number': '',  # Empty = WAIT
                'result_time': result_time
            }
        )
        
        if created:
            added += 1
            print(f"Added: {state_name} ({result_time}) - WAIT")
        else:
            # Update time if different
            if result_obj.result_time != result_time:
                result_obj.result_time = result_time
                result_obj.save(update_fields=['result_time', 'updated_at'])
                updated += 1
                print(f"Updated time: {state_name} ({result_time}) - {result_obj.winning_number or 'WAIT'}")
            else:
                print(f"Exists: {state_name} ({result_time}) - {result_obj.winning_number or 'WAIT'}")
    
    print(f"\n{'='*50}")
    print(f"Setup complete! Added: {added}, Updated: {updated}")
    print(f"Total states: {len(ALL_STATES)}")

if __name__ == '__main__':
    setup_states()