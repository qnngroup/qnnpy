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
#d.streamStop()
ac = AttocubeANC150(u'ASRL5::INSTR')

###################################
#function definitioini
###################################
def extract_useful_data(c1,c2, trigger, x_steps, stream_frequency, scan_frequency):
    step = stream_frequency/scan_frequency
    ind1 = 0
    for i in range(0, len(c1)):
        if c2[i] >= trigger:
            ind1 = i
            break
    ind2 = ind1 + x_steps - 1
    return c1[ind1:ind2: step]
####################################
######################################
#set attocube parameters
######################################
#axis 1-x, 2-y , 3-z
scan_axis=1
scan_voltage = 35
scan_frequency = 500
ac.reset()
for i in range(1,4):
    ac.setm(i, 'stp')
    ac.setv(i, scan_voltage)
    ac.setf(i, scan_frequency)
#######################################
#set labjack parameters
#######################################
stream_frequency= 2000#stream frequency must be integer multiples of scan frequency
d.streamConfig(NumChannels = 2, ChannelNumbers = [ 0, 1 ], ChannelOptions = [ 0, 0 ], SettlingFactor = 1, ResolutionIndex = 1, ScanFrequency = stream_frequency )
d.streamStart()
start = datetime.now()
#######################################
#set scan parameters
########################################
scan_steps = 1000
#############################
#start the scanning
###############################


trigger = 0.5
#600 points per request
MAX_REQUESTS = np.ceil(scan_steps*stream_frequency/scan_frequency/600.0)
vol=[]
c1_total=[]
c2_total=[]
ac.stepu(scan_axis,scan_steps)
dataCount = 0
for r in d.streamData():
    if dataCount >= MAX_REQUESTS:
        break
    c1=r['AIN0']
    c2=r['AIN1']
    c1_total.extend(c1)
    c2_total.extend(c2)
    dataCount += 1
    vol.extend(extract_useful_data(c1=c1,c2=c2, trigger=trigger, x_steps=scan_steps, stream_frequency=stream_frequency, scan_frequency=scan_frequency))
    #sleep(0.05+x_steps/scan_frequency)
        
#stop = datetime.now()            
#stop labjack
#d.streamStop()
#d.close()

#attocube travel back to the starting point
ac.stepd(scan_axis, scan_steps)
vol_back=[]
#c1_total=[]
#c2_total=[]
dataCount = 0
for r in d.streamData():
    if dataCount >= MAX_REQUESTS:
        break
    c1=r['AIN0']
    c2=r['AIN1']
    c1_total.extend(c1)
    c2_total.extend(c2)
    dataCount += 1
    v = extract_useful_data(c1=c1,c2=c2, trigger=trigger, x_steps=scan_steps, stream_frequency=stream_frequency, scan_frequency=scan_frequency)
    vol_back.extend(v)
    #sleep(0.05+x_steps/scan_frequency)

#data_dict = {'x_steps':x_steps, 'y_steps':y_steps,'scan_voltage': scan_voltage, 'scan_frequency': scan_frequency, 'photo_diode': vol_2d}
#
#file_path, file_name  = save_data_dict(data_dict, test_type = 'scan_image', test_name = '',
#                        filedir = r'C:\Users\ProbeStation\Desktop\Di Zhu - Probe Station\scan_test', zip_file=True)
#plt.savefig(file_path + '.png')
#plt.show()

d.streamStop()



def move_to_index(x, y):
    ac.stepu(1, x)
    ac.stepu(2, y)

            



plt.figure(1)
plt.subplot(211)
plt.plot(c1_total, 'bo', np.array(c2_total)+2, 'k')

plt.subplot(212)
plt.plot(vol, 'r--', vol_back[::-1],'bo')
plt.show()
#
#ac.stepu(2, scan_steps)
#sleep(scan_steps/scan_frequency+0.5)
#ac.stepd(2, scan_steps)


    