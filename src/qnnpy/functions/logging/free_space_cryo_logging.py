# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 16:27:34 2023
@author: emmabat, davide, reedf
"""
import re
import sys
import logging
from time import sleep
import serial

import qnnpy.functions.functions as qf
from qnnpy.instruments.cryocon34 import Cryocon34

"""
Python log levels:
    DEBUG
    INFO
    WARNING
    ERROR
    CRITICAL
"""
log_level = sys.argv[1]

try:
    logging.basicConfig(format="%(asctime)s %(message)s", level=log_level)
except Exception:
    logging.basicConfig(format="%(asctime)s %(message)s", level="ERROR")


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback

    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)


def read_serial_pressure(ser):
    buffer = str(ser.read(64))

    logging.info(buffer)
    message = re.search("n[0-9], (.*)n", buffer)
    logging.info(message)

    try:
        pressure = float(message.group(0)[4:14])
        success = True
    except Exception:
        pressure = "NaN"
        success = False
    return pressure, success


sys.excepthook = show_exception_and_exit

COM_PORT = "COM3"

try:
    temp_reader = Cryocon34("GPIB0::5")
except Exception:
    logging.error("Failed to make VISA connection to Cryocon")
    exit
start_temp = 293

# Get Cursor

with serial.Serial(COM_PORT, timeout=1) as ser:
    pressure, success = read_serial_pressure(ser)
    failure_counter = 0
    while (not success) or failure_counter > 10:
        logging.info("failure counter: " + str(failure_counter))
        ser.write("COM,1\x0d\x0a".encode("ascii"))
        logging.debug("attempting to connect to serial")
        sleep(5)
        pressure, success = read_serial_pressure(ser)
        failure_counter += 1
    while True:
        sleep(30)
        logging.info("reading and writing")
        try:
            tempA = temp_reader.read_temp("A")
            tempB = temp_reader.read_temp("B")
            logging.info(f"tempA = {tempA}, tempB = {tempB}")
            logging.info("read temperature success")
        except Exception:
            logging.error("failed to read temperature")
            tempA = 0
            tempB = 0
        try:
            pressure, success = read_serial_pressure(ser)
            if success:
                logging.info(f"pressure = {pressure}")
                logging.info("read pressure success")
            else:
                pressure = 0
        except Exception:
            logging.error("failed to read pressure")
            pressure = 0

        try:
            qf.log_data_to_database(
                table_name="freespace_logging",
                channelA=tempA,
                channelB=tempB,
                pressure=pressure,
            )
            logging.info("write to database success")
        except Exception:
            logging.error("failed to write to database")
conn.close()
