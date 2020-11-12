# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 18:45:02 2018

@author: ICE
"""

import sys
import os

snspd_measurement_code_dir = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\snspd-measurement-code'
dir1 = os.path.join(snspd_measurement_code_dir,'instruments')
dir2 = os.path.join(snspd_measurement_code_dir,'useful_functions')
dir3 = os.path.join(snspd_measurement_code_dir,'measurement')

if snspd_measurement_code_dir not in sys.path:
    sys.path.append(snspd_measurement_code_dir)
    sys.path.append(dir1)
    sys.path.append(dir2)
    sys.path.append(dir3)

#import library
from measurement.ic_sweep import *
from useful_functions.save_data_vs_param import *
from agilent_53131a import Agilent53131a
from jds_ha9 import JDSHA9
#from instruments.ThorlabsPM100_meta import *
from cryocon34 import *
from keithley_2700 import *
from fva3100_optical_attenuator import *
import visa
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
import numpy as np
import time

DVM = Keithley2700('GPIB::3')
DVM.reset()


current = 1.0E-6;
#log file
#myfile = r'C:\Users\ICE\Desktop\aedane\r_log.txt'

myfile = open(r'C:\Users\ICE\Desktop\aedane\NbSe2\chip_01\r_NbSe2_01_deviceD.txt','w') 

try:
    while True:
        this_V = DVM.read_voltage()
        myfile.write(str(this_V/current)+', '+str(time.time())+ '\n')
        print(str(this_V/current)+', '+str(time.time()))
        time.sleep(1)
except KeyboardInterrupt:
    myfile.close()
