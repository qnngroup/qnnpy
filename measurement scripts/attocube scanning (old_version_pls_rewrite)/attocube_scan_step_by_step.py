# standard testing for SNSPD
import sys
import os

# on my Mac
# snspd_measurement_code_dir = r'/Users/dizhu/Desktop/python code for SNSPD measurement/snspd-measurement-code'
# on the probe station
snspd_measurement_code_dir = r"C:\Users\ProbeStation\Desktop\Di Zhu - Probe Station\snspd_measurement_python_code"
dir1 = os.path.join(snspd_measurement_code_dir, "instruments")
dir2 = os.path.join(snspd_measurement_code_dir, "useful_functions")
dir3 = os.path.join(snspd_measurement_code_dir, "measurement")

if snspd_measurement_code_dir not in sys.path:
    sys.path.append(snspd_measurement_code_dir)
    sys.path.append(dir1)
    sys.path.append(dir2)
    sys.path.append(dir3)

# import library
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
ac = AttocubeANC150("ASRL5::INSTR")

######################################
# set attocube parameters
######################################
# axis 1-x, 2-y , 3-z
scan_voltage = 40
scan_frequency = 1000
ac.reset()
for i in range(1, 4):
    ac.setm(i, "stp")
    ac.setv(i, scan_voltage)
    ac.setf(i, scan_frequency)
#######################################
# set labjack parameters
#######################################
# d.streamConfig(NumChannels = 1, ChannelNumbers = [ 0 ], ChannelOptions = [ 0 ], SettlingFactor = 0, ResolutionIndex = 1, ScanFrequency =1000)
# d.streamStart()
start = datetime.now()
#######################################
# set scan parameters
########################################
x_step_size = 10
x_steps = 50
y_step_size = 10
y_steps = 50
#############################
# start the scanning
###############################

for y_step in range(1, y_steps + 1):
    vol_row = []
    if y_step % 2:
        for x_step in range(1, x_steps + 1):
            vol_row.append(d.getAIN(0))
            ac.stepu(1, x_step_size)
            sleep(0.05 + x_step_size / scan_frequency)
    else:
        for x_step in range(1, x_steps + 1):
            ac.stepd(1, x_step_size)
            sleep(0.05 + x_step_size / scan_frequency)
            vol_row.append(d.getAIN(0))
    if y_step == 1:
        vol = np.array(vol_row)
    else:
        if y_step % 2:
            vol = np.vstack((vol, np.array(vol_row)))
        else:
            vol = np.vstack((vol, np.array(vol_row)[::-1]))

    # sleep(x_steps*x_step_size/scan_frequency)
    ac.stepu(2, y_step_size)
    sleep(0.05 + y_step_size / scan_frequency)

# stop timer
stop = datetime.now()
# stop labjack
# d.streamStop()
d.close()
# attocube travel back to the starting point
ac.stepd(2, y_step_size * y_steps)
sleep(0.05 + y_step_size * y_steps / scan_frequency)
if y_steps % 2:
    ac.stepd(1, x_steps * x_step_size)
    sleep(0.05 + x_step_size / scan_frequency)

plt.imshow(vol, extent=[1, x_steps, 1, y_steps], aspect="auto")
# plt.plot(vol)

data_dict = {
    "x_steps": x_steps,
    "y_steps": y_steps,
    "x_step_size": x_step_size,
    "y_step_size": y_step_size,
    "scan_voltage": scan_voltage,
    "scan_frequency": scan_frequency,
    "photo_diode": vol,
}

file_path, file_name = save_data_dict(
    data_dict,
    test_type="scan_image",
    test_name="",
    filedir=r"C:\Users\ProbeStation\Desktop\Di Zhu - Probe Station\scan_test",
    zip_file=True,
)
plt.savefig(file_path + ".png")
plt.show()


def move_to_index(x, y):
    ac.stepu(1, x * x_step_size)
    ac.stepu(2, y * y_step_size)


# move_to_index(20,20)
