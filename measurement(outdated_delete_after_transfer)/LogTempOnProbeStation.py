import sys
from threading import Timer
import time
import datetime
from time import sleep
import numpy as np
from matplotlib import pyplot as plt
#instruments
from cryocon34 import *
from keithley_2700 import *


I = 100e-6;
keithley = Keithley2700("GPIB::16")
keithley.reset()

filedirectry = r'C:\Users\ProbeStation\Desktop\Di Zhu - Probe Station\cooldown'
time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

crapcryocon = Cryocon34('GPIB0::8')
crapcryocon.stop_heater()


to = time.time()
t = []
T = []
V = []
t1 = 0
while(t1<5):
    t1 = time.time()-to
    T1 = crapcryocon.read_temp(channel='A')
    V1 = keithley.read_voltage()
    t.append(t1)
    T.append(T1)
    V.append(V1)

    print  'time: %.2f, temperature: %.2f, voltage: %.2f' %(t1, T1, V1)
    sleep(2)



data_dict = {'t':t, 'V':V, 'T':T, 'I':I}
file_path, file_name  = save_data_dict(data_dict, test_type = 'cool_down', test_name = '',
                        filedir = filedirectry, zip_file=True)

plt.subplot(3, 1, 1)
plt.plot(t, T, 'yo-')
plt.title('Cool down')
plt.ylabel('Temperature (K)')
plt.xlabel('Time (s)')

plt.subplot(3, 1, 2)
plt.plot(t, V, 'r.-')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')

plt.subplot(3, 1, 3)
plt.plot(T, V, 'r.-')
plt.xlabel('Temperature (K)')
plt.ylabel('Voltage (V)')
plt.savefig(file_path + '.png')
plt.show()

