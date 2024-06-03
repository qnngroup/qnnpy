import csv
import sys
import os
import atexit 
import logging
import signal
import time
from ice_logging import read_ice_log
sys.path.append(r'Q:\qnnpy')
import qnnpy.functions.functions as qf


PATH = "S:/SC/InstrumentLogging/Cryogenics/Ice/ice-log/Results/"

# Setup logging
log_file = r'C:\Users\ICE\ice-logging\logfile.txt'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

logging.info('Script started.')


# Define the flag file path
flag_file = r'C:\Users\ICE\ice-logging\flagfile.txt'

# Create the flag file
try:
    with open(flag_file, 'w') as f:
        f.write('Running')
        logging.info('Flag file created.')
except Exception as e:
    logging.error(f'Error creating flag file: {e}')

    
# Register the flag file for removal on exit
def remove_flag_file():
    if os.path.exists(flag_file):
        os.remove(flag_file)

atexit.register(remove_flag_file)

def signal_handler(sig, frame):
    logging.info('Signal received: %s. Cleaning up and exiting.', sig)
    remove_flag_file()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)




try:
    while True:
        read_ice_log(PATH)
        time.sleep(120)
        pass
except KeyboardInterrupt:
    logging.info('KeyboardInterrupt received. Exiting.')
finally:
    logging.info('Script ended.')