import sys
import os

snspd_measurement_code_dir = r'C:\Users\quu optics\Desktop\python code on the electronics lab computer\snspd-measurement-code'
dir1 = os.path.join(snspd_measurement_code_dir,'instruments')
dir2 = os.path.join(snspd_measurement_code_dir,'useful_functions')
dir3 = os.path.join(snspd_measurement_code_dir,'measurement')

if snspd_measurement_code_dir not in sys.path:
    sys.path.append(snspd_measurement_code_dir)
    sys.path.append(dir1)
    sys.path.append(dir2)
    sys.path.append(dir3)
    
    

from srs_sim928 import SIM928
from keithley_2700 import Keithley2700
from pyvisa import visa
import numpy as np
import time
import datetime
from matplotlib import pyplot as plt
from scipy.optimize import fmin
import scipy.io
import cPickle as pickle
from useful_functions.save_data_vs_param import *
from measurement.goto_temp import *


SRS = SIM928('GPIB0::2', 4)
DVM = Keithley2700('GPIB::16')
tempcon = Cryocon34('GPIB0::5')

SRS.reset()
DVM.reset()

time.sleep(5)

SRS.set_output(False)
SRS.set_voltage(0)
SRS.set_output(True)


#assuming the load is zero ohms, we will trace out a hysteresis loop
#starting at zero current, ramping up to imax, ramping down to -imax
#and then rmaping up to zero
sample_name = 'SPE995_F6'
Rb = 10E3

imax= 25e-6
istep = 0.2e-6
#settings for my 'good' measurment: imax = 100uA, istep = 0.25uA (this is arbitrary)

if imax>20E-3 or (imax*Rb)>20 : print 'current or voltage out of range'

temperatures = np.arange(2.8, 13.2, 0.2)
temp_median_list = []
temp_stdev_list = []




set_vup1 = Rb*np.linspace(0,imax,(imax/(1*istep)))
set_vdown = Rb*np.linspace(imax, -imax, (2*imax/istep))
set_vup2 = Rb*np.linspace(-imax, 0, (imax/(1*istep)))



for t in range(len(temperatures)):

    gototemp (tempcon, 'C', temperatures[t], 300)

    temp_list = []

    for num in range(0,10):
        thistemp = tempcon.read_temp('C')
        temp_list.append(thistemp)
        print 'Temperature measurement %i was %0.4fK' % (num+1,thistemp)
        time.sleep(2)
        
    temp_mean = np.mean(temp_list)
    temp_stdev = np.std(temp_list)
    print 'The measured temperature was %0.4fK +/- %0.5fK' % (temp_mean, temp_stdev)


    V_dut_up1 = []
    V_dut_down = []
    V_dut_up2 = []

    I_dut_up1 = []
    I_dut_down = []
    I_dut_up2 = []

    settling_time = 0.5

    SRS.set_output(True)

    for i in range(len(set_vup1)):
        #set the SRS
        SRS.set_voltage(set_vup1[i])

        #read the voltage across the device
        time.sleep(settling_time)
        voltage = DVM.read_voltage()


        V_dut_up1.append(voltage)
        I_dut_up1.append(1E6*(set_vup1[i]-voltage)/Rb)

        #voltage across Rb = up1[i]*Rb- read voltage
        #current through the device = (up1[i]*Rb- read voltage)/Rb


    for k in range(len(set_vdown)):
        #set the SRS
        SRS.set_voltage(set_vdown[k])

        #read the voltage across the device
        time.sleep(settling_time)
        voltage = DVM.read_voltage()


        V_dut_down.append(voltage)
        I_dut_down.append(1E6*(set_vdown[k]-voltage)/Rb)


    for j in range(len(set_vup2)):
        #set the SRS
        SRS.set_voltage(set_vup2[j])

        #read the voltage across the device
        time.sleep(settling_time)
        voltage = DVM.read_voltage()


        V_dut_up2.append(voltage)
        I_dut_up2.append(1E6*(set_vup2[j]-voltage)/Rb)




    # plt.plot(V_dut_up1, I_dut_up1,'b')
    # plt.plot(V_dut_down, I_dut_down,'r')
    # plt.plot(V_dut_up2, I_dut_up2,'g')

    # plt.title('IV Hysteresis loop')
    # plt.xlabel('Voltage (V)')
    # plt.ylabel('Current (uA)')

    # plt.show()


    ### quick save



    data_dict = {'V_dut_up1':V_dut_up1, 'I_dut_up1':I_dut_up1, 'V_dut_down':V_dut_down, 'I_dut_down':I_dut_down, 'V_dut_up2':V_dut_up2, 'I_dut_up2':I_dut_up2 }
    time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    data_dir = 'C:\\Users\\quu optics\\Desktop\\aedata\\'

    #todo: add real temperature to filename
    filename =  data_dir +'iv_hyst_data %s %s temperature %0.3fK +- %0.4fK' % (time_str, sample_name, temp_mean, temp_stdev)

    scipy.io.savemat(filename + '.mat', mdict=data_dict)



gototemp (tempcon, 'C', 0.0, 1)