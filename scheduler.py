import schedule
import time
import json
from datetime import datetime
import os

def job():
    # Get the current date and format it as YYYY-MM-DD
    current_date = datetime.now().strftime("%Y-%m-%d")
    os.system(f"/home/ubuntu/miniconda3/bin/conda run -n ip python ip.py --output_file ../ip_results/{current_date}.json")


# Schedule the job to run every day at 10:30 AM
schedule.every().day.at("23:59").do(job)

# Keep the script running to allow the scheduler to execute the tasks
while True:
    schedule.run_pending()
    time.sleep(1)
