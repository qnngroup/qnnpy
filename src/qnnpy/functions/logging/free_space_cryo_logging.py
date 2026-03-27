# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 16:27:34 2023

@author: emmabat
"""
import re
import sys

import qnnpy.functions.functions as qf
import serial
from qnnpy.instruments.cryocon34 import Cryocon34
from time import sleep
import logging

'''
Python log levels:
    DEBUG
    INFO
    WARNING
    ERROR
    CRITICAL
'''
log_level = sys.argv[1]

try:
    logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
except:
    logging.basicConfig(format='%(asctime)s %(message)s', level='ERROR')

def handler(self, signum, frame):
    '''
    Safer exit handling (e.g. on ctrl+c)
    '''
    conn.close()
    ser.close()    
    exit(1)

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

COM_PORT = 'COM3'

try:
    temp_reader = Cryocon34("GPIB0::5")
except:
    logging.error('Failed to make VISA connection to Cryocon')
    exit()

def read_serial_pressure(ser):
    ser.flushInput()
    sleep(1)
    buffer = str(ser.read(64))
    
    logging.info(buffer)
    message = re.search('n[0-9], (.*)n', buffer)
    logging.info(message)
    
    try:
        pressure = float(message.group(0)[4:14])
        success = True
    except:
        pressure = 'NaN'
        success = False
    return pressure, success

with serial.Serial(COM_PORT, timeout=1) as ser:
    # try connecting to pressure sensor
    pressure, success = read_serial_pressure(ser)
    failure_counter = 0
    while (not success) or failure_counter > 10:
        logging.info('failure counter: ' + str(failure_counter))
        ser.write('COM,1\x0D\x0A'.encode('ascii'))
        logging.debug('attempting to connect to serial')
        sleep(5)
        pressure, success = read_serial_pressure(ser)
        failure_counter += 1
    # main loop
    while True:
        logging.info('reading temperature and pressure')
        try:
            tempA = temp_reader.read_temp('A')
            tempB = temp_reader.read_temp('B')
            pressure, success = read_serial_pressure(ser)
            logging.info(f'read temperature, pressure success: T_A={tempA}, T_B={tempB}, pressure={pressure}')
            try:
                qf.log_data_to_database(table_name='freespace_logging', channelA=tempA, channelB=tempB, pressure=pressure)
                logging.info('write to database success')
            except Exception as e:
                logging.error(f'failed to write to database: {repr(e)}')
        except Exception as e:
            logging.error(f'failed to read temperature or pressure {repr(e)}')
        sleep(30)
