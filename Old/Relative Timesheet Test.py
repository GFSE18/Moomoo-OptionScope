import time
import csv
import random
n = 0  # Counter for how many entries to write
file_name = 'timesheet.csv'

# Open the CSV file once, append data instead of overwriting
with open(file_name, 'a', newline='') as csvfile:
    spamwriter = csv.writer(csvfile)

    while n < 12:
        # Get the current local time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        code=random.randint(1,100)
        # Write the time to the file
        spamwriter.writerow([current_time,code])
        print(f"Written to CSV: {current_time}")

        n += 1  # Increment the counter
        time.sleep(1) 