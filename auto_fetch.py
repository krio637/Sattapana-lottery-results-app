"""
Auto-fetch lottery results every 5 minutes
Run: python auto_fetch.py
Press Ctrl+C to stop
"""
import time
import schedule
from fetch_results import fetch_results

def job():
    """Run fetch_results"""
    print("\n" + "="*60)
    print("🔄 Auto-fetching results...")
    print("="*60)
    fetch_results()
    print(f"\n⏰ Next fetch in 5 minutes...")

if __name__ == "__main__":
    print("🚀 Starting auto-fetch service...")
    print("📊 Will fetch results every 5 minutes")
    print("⏹️  Press Ctrl+C to stop\n")
    
    # Run immediately on start
    job()
    
    # Schedule to run every 5 minutes
    schedule.every(5).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
