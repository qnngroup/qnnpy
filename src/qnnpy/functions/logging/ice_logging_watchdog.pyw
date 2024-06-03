import os
import psutil
import time
import logging

# Setup logging
log_file = r'C:\Users\ICE\ice-logging\watchdog_logfile.txt'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

logging.info('Watchdog script started.')

# Define the flag file path using a raw string
flag_file = r'C:\Users\ICE\ice-logging\flagfile.txt'

# Check if the primary script is running
def is_primary_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if "Q:\qnnpy\qnnpy\functions\ice_logging_script.pyw" in proc.info['cmdline']:
            logging.info("Script is running")
            return True
        else:
            logging.info("script is not running")
            return False

# Watchdog loop
while True:
    if os.path.exists(flag_file):
        if not is_primary_running():
            logging.warning('Flag file exists but primary script is not running. Removing stale flag file.')
            os.remove(flag_file)
        else:
            logging.info("Primary script is running")
    time.sleep(10)  # Check every 10 seconds
