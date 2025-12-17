#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sattapana.settings')
django.setup()

from lottery.models import LotteryResult

def clear_old_results(days_to_keep=30):
    """Clear results older than specified days"""
    cutoff_date = date.today() - timedelta(days=days_to_keep)
    old_results = LotteryResult.objects.filter(date__lt=cutoff_date)
    count = old_results.count()
    old_results.delete()
    print(f"Deleted {count} results older than {cutoff_date}")

def show_today_status():
    """Show today's results status"""
    today = date.today()
    results = LotteryResult.objects.filter(date=today).order_by('result_time')
    
    print(f"\nToday's Results Status ({today}):")
    print("=" * 50)
    
    for result in results:
        status = result.winning_number if result.winning_number else "WAIT"
        print(f"{result.state:<15} ({result.result_time}) - {status}")
    
    total = results.count()
    with_numbers = results.exclude(winning_number='').count()
    waiting = total - with_numbers
    
    print(f"\nSummary: {total} states, {with_numbers} results, {waiting} waiting")

def reset_today_results():
    """Reset all today's results to WAIT"""
    today = date.today()
    updated = LotteryResult.objects.filter(date=today).update(winning_number='')
    print(f"Reset {updated} results to WAIT for {today}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'status':
            show_today_status()
        elif command == 'reset':
            reset_today_results()
            show_today_status()
        elif command == 'clean':
            clear_old_results()
        else:
            print("Usage: python manage_results.py [status|reset|clean]")
    else:
        show_today_status()