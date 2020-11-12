#standard testing for SNSPD
#%%
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


#########################################
### Connect to instruments
#########################################

#lecroy_ip = 'QNN-SCOPE1.MIT.EDU'
#lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
# counter = Agilent53131a('GPIB0::3')
# counter.basic_setup()
#cryocon = Cryocon34('GPIB0::5')
# attenuator = JDSHA9('GPIB0::5')
#attenuator = FVA3100('GPIB0::10'); attenuator.set_beam_block(True)
SRS = SIM928('GPIB0::1', 2); SRS.reset()
#initiate the power meter
# pm = ThorlabsPM100Meta('USB0::0x1313::0x8078::P0001093::INSTR')
k = Keithley2700("GPIB0::3"); k.reset()



def count_rate_curve(currents, counting_time = 0.1):
    count_rate_list = []
    start_time = time.time()
    SRS.set_output(True)
    for n, i in enumerate(currents):
        # print '   ---   Time elapsed for measurement %s of %s: %0.2f min    ---   ' % (n, len(currents), (time.time()-start_time)/60.0)
        SRS.set_voltage(np.sign(i)*1e-3); time.sleep(0.05); SRS.set_voltage(i*R_srs); time.sleep(0.05)

        count_rate = counter.count_rate(counting_time=counting_time)
        count_rate_list.append(count_rate)
        print 'Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)' % (i*1e6, count_rate, n, len(currents), (time.time()-start_time)/60.0)
    SRS.set_output(False)
    return np.array(count_rate_list)

#%%
#########################################
### Sample information
#########################################
sample_name = 'SPF787_wide'
device_name = 'S23_2amp'
comments = 'T=1p31'
test_name = sample_name+'_'+device_name+'_'+comments
filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\Ilya\SPF787_Goltsman&Karl\Test for optics'

R_srs = 100e3

# counter.set_trigger(0.04)

Isource_max =40e-6
step = 2e-6
#here we go
Isource1 = np.arange(0, Isource_max, step)
Isource2 = np.arange(Isource_max, -Isource_max, -step)
Isource3= np.arange(-Isource_max, 0, step)
Isource = np.concatenate([Isource1, Isource2, Isource3])
V_source = Isource*R_srs

V_device = []
I_device = [] 
SRS.set_voltage(0)
SRS.set_output(True)
k.read_voltage()
sleep(1)


for v in V_source:
    SRS.set_voltage(v)
    sleep(0.1)
    vread = k.read_voltage()
    iread = (v-vread)/R_srs
    print('V=%.4f V, I=%.2f uA, R =%.2f' %(vread, iread*1e6, vread/iread))
    V_device.append(vread)
    I_device.append(iread)

SRS.set_output(False)
#search the switching current in the ramping up
Isw = I_device[np.argmax(np.array(V_device)>.005)-1]
    
data_dict = {'V_device':V_device, 'I_device':I_device, 'V_source':V_source, 'R_srs':R_srs, 'step':step}
file_path, file_name  = save_data_dict(data_dict, test_type = 'Isw_curve', test_name = test_name,
                        filedir = filedirectry, zip_file=True)

plt.plot(np.array(V_device), np.array(I_device)*1e6, '-o')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (uA)')
plt.title('I-V '+device_name+', Isw = %.2f uA' %(Isw*1e6))
print('Isw = %.2f uA' %(Isw*1e6))
plt.savefig(file_path + '.png')
plt.show()