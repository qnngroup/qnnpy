#standard testing for SNSPD
import sys
import os

#on my Mac
# snspd_measurement_code_dir = r'/Users/dizhu/Desktop/python code for SNSPD measurement/snspd-measurement-code'
#on the probe station
snspd_measurement_code_dir = r'C:\Users\ProbeStation\Desktop\Di Zhu - Probe Station\snspd_measurement_python_code'
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
from instruments.ThorlabsPM100_meta import *
from keithley_2700 import *
import visa
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
import u6
from attocube_anc150 import *
from datetime import datetime

d = u6.U6()
ac = AttocubeANC150(u'ASRL5::INSTR')

######################################
#set attocube parameters
######################################
#axis 1-x, 2-y , 3-z
scan_axis = 1
scan_voltage =30
scan_frequency = 1000
ac.reset()
for i in range(1,4):
    ac.setm(i, 'stp')
    ac.setv(i, scan_voltage)
    ac.setf(i, scan_frequency)
#######################################
#set labjack parameters
#######################################
#d.streamConfig(NumChannels = 1, ChannelNumbers = [ 0 ], ChannelOptions = [ 0 ], SettlingFactor = 0, ResolutionIndex = 1, ScanFrequency =1000)
#d.streamStart()
start = datetime.now()


#######################################
#set scan parameters
########################################
#x_step_size = 20
#x_steps = 40
#y_step_size = 20
#y_steps = 40
z_steps =100
z_step_size = 5
#############################
#start the scanning
###############################
vol = []
vol_back = []
for z_step in range(1, z_steps+1):  
    ac.stepu(scan_axis,z_step_size)
    sleep(0.05+z_step_size/scan_frequency)
    vol.append(d.getAIN(0))
#travel back 

for z_step in range(1, z_steps+1):  
    ac.stepd(scan_axis,z_step_size)
    sleep(0.05+z_step_size/scan_frequency)
    vol_back.append(d.getAIN(0))
    
#stop timer
stop = datetime.now()
#stop labjack
#d.streamStop()
d.close()
#attocube travel back to the starting point
#ac.stepd(3, z_step_size*z_steps)

x = range(1,z_steps+1)
plt.plot(x, vol, 'k--', label='forward')
plt.plot(x, vol_back[::-1], 'ro', label='backward')

legend = plt.legend(loc='upper right', shadow=False)
plt.xlabel('steps')
plt.ylabel('photodiode voltage (V)')

data_dict = {'z_steps':z_steps, 'z_steps':z_steps, 'x': x, 'vol': vol, 'vol_back': vol_back}
file_path, file_name  = save_data_dict(data_dict, test_type = 'z_scan', test_name = '',
                        filedir = r'C:\Users\ProbeStation\Desktop\Di Zhu - Probe Station\scan_test', zip_file=True)
plt.savefig(file_path + '.png')
plt.show()


#ac.stepu(1, 60)
