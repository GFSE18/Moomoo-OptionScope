from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import time


start_time_str = "2024-12-11 00:00:00"
start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
end_time_str = "2024-12-11 01:00:00"
end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

def my_job():
    current_time = datetime.now()
    print(f"Job executed at: {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")

scheduler = BackgroundScheduler()

scheduler.add_job(my_job, IntervalTrigger(seconds=1))

def wait_until_start(start_time):
    while True:
        now = datetime.now()
        if now >= start_time:
            print("Start time reached. Starting the scheduler...")
            break
        remaining = (start_time - now).total_seconds()
        print(f"Waiting for start time. Remaining seconds: {remaining:.1f}")
        time.sleep(min(remaining, 1))  # Sleep for the smaller of remaining time or 1 second

try:
    wait_until_start(start_time)

    scheduler.start()
    print("Scheduler running. Press Ctrl+C to stop.")

    while True:
        now = datetime.now()
        if now >= end_time:
            print("End time reached. Shutting down the scheduler...")
            scheduler.shutdown()
            break
        time.sleep(1)

except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler stopped.")
