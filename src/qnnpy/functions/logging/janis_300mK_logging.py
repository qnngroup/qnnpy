# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:38:22 2023

@author: omedeiro
"""

import sys
from time import sleep

sys.path.append(r"Q:\qnnpy")
import qnnpy.functions.functions as qf
from qnnpy.instruments.lakeshore336 import Lakeshore336

# https://stackoverflow.com/questions/59125493/how-to-constantly-run-python-script-in-the-background-on-windows


while True:
    try:
        ls1 = Lakeshore336("GPIB0::13::INSTR")
    except Exception:
        print("failed connection to Lakeshore336")

    try:
        stage_3K = ls1.read_temp("D4")
        sleep(2)
        stage_40K = ls1.read_temp("D2")
        sleep(2)
        stage_SORB = ls1.read_temp("D3")
        sleep(2)
        stage_He3Pot = ls1.read_temp("D1")
        sleep(1)
        # print([stage_3K, stage_40K, stage_SORB, stage_He3Pot])
    except Exception:
        print("failed to read temp")
    # ls1.read_temp('D')

    try:
        qf.log_data_to_database(
            table_name="janis_300mK_logging",
            stage_3K=stage_3K,
            stage_40K=stage_40K,
            stage_SORB=stage_SORB,
            stage_He3Pot=stage_He3Pot,
        )
    except Exception:
        print("failed to write to database")

    sleep(1)
