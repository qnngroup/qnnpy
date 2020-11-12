#%%
import pyvisa
from time import sleep
import numpy as np
from matplotlib import pyplot as plt
import os, sys

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
from keysight_n5224a import KeysightN5224a
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
import scipy
from datetime import datetime
from lecroy_620zi import *
import scipy.io as sio
import os



from keysight_n5224a import KeysightN5224a

#%%
#connect PNA
pna = KeysightN5224a("GPIB0::16::INSTR")

pna.reset(measurement = 'S21', if_bandwidth = 1e3, start_freq=200e6,
              stop_freq = 15e9, power = -30)



#SRS = SIM928('GPIB0::1', 2); 
#k = Keithley2700("GPIB0::3"); k.reset()

#%%
#save a simple S21 spectrum


filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\10G_microstrip_taper'
sample_name = '10G_taper_Ch5Ch6'
device_name = 'T=2p0K'

test_type = 'temperature_sweep'

#
pna_power = -30
#pna.set_measurement('S21') #measurement type
pna.set_start(1e9) #starting frequency in Hz
pna.set_stop(20e9) #stop freq
pna.set_points(1001) #number of points
pna.set_if_bw(10) #if bandwidth
pna.set_power(pna_power) #power in dBm

f, S21 = pna.single_sweep()
pna_att = pna.get_source_attenuation()


data_dict = {'S21':S21, 'pna_power':pna_power, 'f':f, 'pna_att':pna_att}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)

plt.plot(f, 20*np.log10(np.abs(S21)))

plt.savefig(file_path + '.png') 
plt.show()

#%%

filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\keysight network analyzer'
sample_name = 'taper_DC_bias'
device_name = ''

test_type = 'DC_bias'

#
pna_power = -50
#pna.set_measurement('S21') #measurement type
pna.set_start(200e6) #starting frequency in Hz
pna.set_stop(10e9) #stop freq
pna.set_points(1001) #number of points
pna.set_if_bw(20) #if bandwidth
pna.set_power(pna_power) #power in dBm

#pna.set_sweep_mode('CONT')
#pna.set_sweep_mode('HOLD')


bias_voltage = np.arange(0, .20, .02)

SRS.set_output(True)

S21 = []

for v in bias_voltage:
    print('bias voltage  = {} V'.format(v))
    SRS.set_voltage(v)
    sleep(.1)
    f, S = pna.single_sweep()
    S21.append(S)
    
    
for i in range(len(bias_voltage)):
    plt.plot(f, 20*np.log10(np.abs(S21[i])), label = 'DC bias={}V'.format(bias_voltage[i]))
plt.legend()

data_dict = {'bias_voltage':bias_voltage, 'S21':S21, 'pna_power':pna_power, 'f':f}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)
plt.savefig(file_path + '.png') 
plt.show()


#%%
#vary temperature

filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\keysight network analyzer'
sample_name = 'taper_1G_no_bias_T'
device_name = ''

T = 11.00

test_type = 'vary_temsperature_T={}K'.format(T)
test_type = test_type.replace('.', 'p')

#
pna_power = -40
#pna.set_measurement('S21') #measurement type
pna.set_start(200e6) #starting frequency in Hz
pna.set_stop(10e9) #stop freq
pna.set_points(1001) #number of points
pna.set_if_bw(20) #if bandwidth
pna.set_power(pna_power) #power in dBm

   
f, S21 = pna.single_sweep()
    
    
plt.plot(f, 20*np.log10(np.abs(S21)))
plt.title('PNA power = {}, temperature = {}K'.format(pna_power, T))
plt.xlabel('Frequency (GHz)')
plt.ylabel('S21 (dB)')

data_dict = {'bias_voltage':bias_voltage, 'S21':S21, 'pna_power':pna_power, 'f':f, 'T':T}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)
plt.savefig(file_path + '.png') 
plt.show()

#%%
#vary VNA power

filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\keysight network analyzer'
sample_name = 'taper_1G_no_bias_T'
device_name = ''

T = 1.28

test_type = 'vary_VNA_power_T={}K'.format(T)
test_type = test_type.replace('.', 'p')

#
#pna.set_measurement('S21') #measurement type
pna.set_start(200e6) #starting frequency in Hz
pna.set_stop(10e9) #stop freq
pna.set_points(1001) #number of points
pna.set_if_bw(20) #if bandwidth
pna.set_power(-40) #power in dBm

pna_power = np.arange(-50,10, 3) 

S21 = []
VNA_att = []
for p in pna_power:
    print('VNA power = {}dBm'.format(p))
    pna.set_power(p)
    f, S = pna.single_sweep()
    S21.append(S)
    VNA_att.append(float(pna.query('SOUR:POW:ATT?').strip()))

for i in range(len(S21)):
    plt.plot(f, 20*np.log10(np.abs(S21[i])-VNA_att[i]), label = 'P = {}dBm'.format(pna_power[i]))
plt.legend()
plt.title('VNA power sweep, temperature = {}K'.format(T))
plt.xlabel('Frequency (GHz)')
plt.ylabel('S21 (dB)')

data_dict = {'S21':S21, 'pna_power':pna_power, 'f':f, 'T':T, 
             'VNA_att': VNA_att}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)
plt.savefig(file_path + '.png') 
plt.show()

pna.set_sweep_mode('HOLD')

#%%

filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\keysight network analyzer'
sample_name = 'green_pasternack_2cables'
device_name = ''

test_type = ''
pna.reset()
#
pna_power = 0
#pna.set_measurement('S21') #measurement type
pna.set_start(200e6) #starting frequency in Hz
pna.set_stop(30e9) #stop freq
pna.set_points(5000) #number of points
pna.set_if_bw(100) #if bandwidth
pna.set_power(pna_power) #power in dBm

VNA_att = pna.get_source_attenuation()

f, S21 = pna.single_sweep()

pna.set_measurement('S11') #measurement type
f, S11 = pna.single_sweep()



data_dict = {'S11':S11, 'S21':S21, 'pna_power':pna_power, 'f':f, 
             'VNA_att': VNA_att}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)

plt.plot(f/1e9, 20*np.log10(abs(S21)))
plt.title('Room temperature cable loss (2xgreen+2xbrown)')
plt.xlabel('Frequency (GHz)')
plt.ylabel('S21 (dB)')
plt.savefig(file_path + '.png') 
plt.show()

pna.set_sweep_mode('HOLD')

#%%
fname = '2019-01-26 10-56-26 green_pasternack_2cables_loss'
M = sio.loadmat(fname+'.mat', squeeze_me = True)
f = M['f']
S21 = M['S21']

plt.plot(f/1e9, 20*np.log10(abs(S21)))
plt.title('Room temperature cable loss (2xgreen)')
plt.xlabel('Frequency (GHz)')
plt.ylabel('S21 (dB)')
plt.savefig(fname + '.png') 
plt.show()