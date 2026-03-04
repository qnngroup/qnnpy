# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:38:22 2023

@author: omedeiro, davide, reedf
"""

import sys
from time import sleep

import logging
import pyvisa

import qnnpy.functions.functions as qf
from qnnpy.instruments.lakeshore336 import Lakeshore336

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

ls1 = Lakeshore336("GPIB0::12::INSTR")
ls2 = Lakeshore336("GPIB0::13::INSTR")

def read_temps(ls1, ls2):
    T_sample_stage = ls1.read_temp("A")
    T_4k_stage = ls1.read_temp("B")
    T_sample_holder = ls1.read_temp("C")
    T_rad_shield = ls2.read_temp("A")
    T_second_shield = ls2.read_temp("B")
    return T_sample_stage, T_4k_stage, T_sample_holder, T_rad_shield, T_second_shield

while True:
    try:
        T_sample_stage, T_4k_stage, T_sample_holder, T_rad_shield, T_second_shield = read_temps(ls1, ls2)
        try:
            qf.log_data_to_database(
                table_name="probe_station_logging",
                sample_stage=T_sample_stage,
                fourK_stage=T_4k_stage,
                sample_holder=T_sample_holder,
                radiation_shield=T_rad_shield,
                second_shield=T_second_shield,
            )
            logging.info(
                f"Logged temperatures successfully: "
                f"sample_stage={T_sample_stage}, "
                f"4K_stage={T_4k_stage}, "
                f"T_rad_shield={T_rad_shield}, "
                f"T_second_shield={T_second_shield}"
            )
        except Exception:
            logging.error("failed to write to database")
    except Exception as e:
        logging.error(f"problem connecting to lakeshore: {str(e)}")
        logging.info(f"attempting to reconnect")
        try:
            ls1.pyvisa.close()
            ls2.pyvisa.close()
            # not sure if these sleeps are necessary (reedf)
            sleep(1)
            rm = pyvisa.ResourceManager()
            sleep(1)
            ls1.pyvisa = rm.open_resource("GPIB0::12::INSTR")
            ls2.pyvisa = rm.open_resource("GPIB0::13::INSTR")
        except Exception as e:
            logging.error(f"problem reconnecting to lakeshore: {str(e)}")

    sleep(10)