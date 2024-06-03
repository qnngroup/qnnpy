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
import logging

import sys, os
# sys.stdout = open("300mK.log", "w");
# sys.stderr = open("300mK.log", "w");

# https://stackoverflow.com/questions/59125493/how-to-constantly-run-python-script-in-the-background-on-windows
# print('beginning to record 300 mK')

while True:        
    try:    
        ls1 = Lakeshore336('GPIB0::13::INSTR')
    except:
        print('failed connection to Lakeshore336')
        
    try:
        stage_3K = ls1.read_temp('D4')
        sleep(2)
        stage_40K = ls1.read_temp('D2')
        sleep(2)
        stage_SORB = ls1.read_temp('D3')
        sleep(2)
        stage_He3Pot = ls1.read_temp('D1')
        sleep(2)
        print([stage_3K, stage_40K, stage_SORB, stage_He3Pot])
    except:
        print('failed to read temp')
    # ls1.read_temp('D')
    
    try:
        qf.log_data_to_database(table_name='janis_300mK_logging', stage_3K=stage_3K, stage_40K=stage_40K, stage_SORB=stage_SORB, stage_He3Pot=stage_He3Pot)
    except:
        print('failed to write to database')
        
    sleep(60)
    
    