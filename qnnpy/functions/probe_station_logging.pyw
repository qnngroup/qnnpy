# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:38:22 2023

@author: omedeiro
"""

from time import sleep
import pyvisa
import sys
sys.path.append(r'Q:\qnnpy')
import qnnpy
import qnnpy.functions.snspd as snspd
import qnnpy.functions.functions as qf
from qnnpy.instruments.lakeshore336 import Lakeshore336

# https://stackoverflow.com/questions/59125493/how-to-constantly-run-python-script-in-the-background-on-windows


while True:       
    
    try:
        ls1 = Lakeshore336('GPIB0::12::INSTR')
        ls2 = Lakeshore336('GPIB0::13::INSTR')
    except:
        print('failed connection to Lakeshore336')
    try:
        T_sample_stage = ls1.read_temp('A')
        T_4k_stage = ls1.read_temp('B')
        T_sample_holder = ls1.read_temp('C')
        # ls1.read_temp('D')
        
        T_rad_shield = ls2.read_temp('A')
        T_second_shield = ls2.read_temp('B')
    except:
        print('failed to read temp')
    try:
        qf.log_data_to_database(table_name='probe_station_logging', sample_stage=T_sample_stage, fourK_stage=T_4k_stage, sample_holder=T_sample_holder, radiation_shield=T_rad_shield, second_shield=T_second_shield)
    except:
        print('failed to write to database')
        
    sleep(1)
    