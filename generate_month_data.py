#!/usr/bin/env python
import os
import django
from datetime import date, timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sattapana.settings')
django.setup()

from lottery.models import LotteryResult

# All states with their result times
STATES = {
    'Disawar': '05:00 AM',
    'Delhi Bazar': '03:00 PM', 
    'Shri Ganesh': '04:00 PM',
    'Faridabad': '06:15 PM',
    'Ghaziabad': '08:40 PM',
    'Gali': '11:30 PM',
    'Dwarka City': '10:00 AM',
    'Ujjain King': '12:00 PM',
}

def generate_month_data():
    """Generate lottery data for current month"""
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Get first day of current month
    first_day = date(current_year, current_month, 1)
    
    print(f"Generating data for {first_day.strftime('%B %Y')}")
    print("=" * 50)
    
    added = 0
    
    # Generate data from first day of month to today
    current_date = first_day
    while current_date <= today:
        print(f"Processing {current_date}")
        
        for state_name, result_time in STATES.items():
            # Generate random 2-digit number for past dates
            if current_date < today:
                winning_number = f"{random.randint(10, 99):02d}"
            else:
                # For today, some results and some waiting
                if random.choice([True, False, False]):  # 1/3 chance of having result
                    winning_number = f"{random.randint(10, 99):02d}"
                else:
                    winning_number = ""  # WAIT
            
            result_obj, created = LotteryResult.objects.get_or_create(
                date=current_date,
                state=state_name,
                defaults={
                    'winning_number': winning_number,
                    'result_time': result_time
                }
            )
            
            if created:
                added += 1
                status = winning_number if winning_number else "WAIT"
                print(f"  Added: {state_name} - {status}")
        
        current_date += timedelta(days=1)
    
    print(f"\n{'='*50}")
    print(f"Generated {added} new results for {first_day.strftime('%B %Y')}")
    
    # Show summary
    total_results = LotteryResult.objects.filter(
        date__year=current_year,
        date__month=current_month
    ).count()
    
    with_numbers = LotteryResult.objects.filter(
        date__year=current_year,
        date__month=current_month
    ).exclude(winning_number='').count()
    
    waiting = total_results - with_numbers
    
    print(f"Total results: {total_results}")
    print(f"With numbers: {with_numbers}")
    print(f"Waiting: {waiting}")
    print(f"Current date: {today}")

if __name__ == '__main__':
    generate_month_data()