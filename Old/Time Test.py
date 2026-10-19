from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import time

# Define the task
def my_task():
    print(f"Task executed at {datetime.now()}")

scheduler = BackgroundScheduler()

start_time_str = "2024-12-04 11:30:00"
start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")

# Add the job with IntervalTrigger
scheduler.add_job(
    my_task,
    trigger=IntervalTrigger(start_date=start_time, seconds=1),  # Executes every second
)

# Start the scheduler
scheduler.start()

try:
    print("Scheduler is running...")
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler stopped.")