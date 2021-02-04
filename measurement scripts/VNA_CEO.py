#%%
from time import sleep
import numpy as np
from matplotlib import pyplot as plt
import os, sys

sys.path.append(r'Q:\qnnpy')

from datetime import datetime
import scipy.io as sio

import qnnpy.functions.functions as qf
import qnnypy.functions.resonators as Resonators

#import library
from measurement.ic_sweep import *
from useful_functions.save_data_vs_param import *

start_freq = 1e9
stop_freq = 10e9
num_points = 1001
power = 0
if_bandwidth = 100

#%%
#calibrate bias tee

calibration = Resonators(r'Q:\qnnpy\config\vna_ceo_cal.yml')
calibration.S21_measurement(start_freq, stop_freq, num_points, power, if_bandwidth)

calibration.save()
calibration.plot()

#%%
#save a simple S21 spectrum
resonators = Resonators(r'Q:\qnnpy\config\vna_ceo.yml')
resonators.S21_measurement(start_freq, stop_freq, num_points, power, if_bandwidth)

resonators.save()
resonators.plot()

#%% power characterization
pna_powers = [-50, -45, -40, -35, -30,-25, -20,-15, -10]
resonators.power_characterization(start_freq, stop_freq, num_points, powers, if_bandwidth)

#%%coupling tunability

# TODO uses a "k" which is not defined...would probably not run as is

filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\MC\201907_coupler_3section'
#sample_name = 'Ch7Ch5_coupled_-40dbm_'
sample_name = 'i=ch6'
device_name = 'o=ch8'

test_type = 'S31_tunability_current_ch8'


pna_power =-30
#pna.set_measurement('S21') #measurement type
pna.set_start(9e9) #starting frequency in Hz
pna.set_stop(11e9) #stop freq
pna.set_points(1001) #number of points
pna.set_if_bw(20) #if bandwidth
pna.set_power(pna_power) #power in dBm

R_srs = 100e3

# counter.set_trigger(0.04)

Isource_max =70e-6
Isource_min =0e-6
step = 1e-6
#here we go
Isource = np.arange(Isource_min, Isource_max, step)
#Isource2 = np.arange(Isource_max, -Isource_max, -step)
#Isource3= np.arange(-Isource_max, 0, step)
#Isource = np.concatenate([Isource1, Isource2, Isource3])
V_source = Isource*R_srs

V_device = []
I_device = [] 
S21_all=[]
f_all=[]
SRS.set_voltage(0)
SRS.set_output(True)
# TODO what is k?
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
    f, S21 = pna.single_sweep()
    pna_att = pna.get_source_attenuation()
    S21_all.append(S21)
    f_all.append(f)
    plt.plot(f, 20*np.log10(np.abs(S21)))
    plt.show()
plt.savefig(file_path + '.png') 
plt.show()
SRS.set_output(False)
pna_att = pna.get_source_attenuation()
data_dict = {'V_device':V_device, 'I_device':I_device, 'V_source':V_source, 'R_srs':R_srs, 'step':step, 'S21':S21_all, 'pna_power':pna_power, 'f':f_all, 'pna_att':pna_att}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name+'_sweep_other_current',
                        filedir = filedirectry, zip_file=True)
#    V_device.append(vread)
#    I_device.append(iread)
    

#SRS.set_output(False)
#search the switching current in the ramping up
#Isw = I_device[np.argmax(np.array(V_device)>.005)-1]
    
#data_dict = {'V_device':V_device, 'I_device':I_device, 'V_source':V_source, 'R_srs':R_srs, 'step':step}
#file_path, file_name  = save_data_dict(data_dict, test_type = 'Isw_curve', test_name = test_name,
#                        filedir = filedirectry, zip_file=True)


#f, S21 = pna.single_sweep()
#pna_att = pna.get_source_attenuation()


#data_dict = {'S21':S21, 'pna_power':pna_power, 'f':f, 'pna_att':pna_att}
#file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
#                        filedir = filedirectry, zip_file=True)

#plt.plot(f, 20*np.log10(np.abs(S21)))

plt.savefig(file_path + '.png') 
plt.show()



#%%considtency of the switching current

filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\MC\201907_coupler_3section'
#sample_name = 'Ch7Ch5_coupled_-40dbm_'
sample_name = 'i1=ch5'
device_name = 'i2=ch7'

test_name = 'remaining_single_side'

SRS2 = SIM928('GPIB0::1', 4); SRS2.reset()

R_srs = 100e3

# counter.set_trigger(0.04)

Isource_max =80e-6
Isource_min =0e-6
step = 1e-6
#here we go
Isource = np.arange(Isource_min, Isource_max, step)
#Isource2 = np.arange(Isource_max, -Isource_max, -step)
#Isource3= np.arange(-Isource_max, 0, step)
#Isource = np.concatenate([Isource1, Isource2, Isource3])
V_source = Isource*R_srs
V_test = R_srs*np.arange(Isource_min, Isource_max, 2*step)
V_test = [4.4, 4.6, 5.6]
V_device = []
I_device = []
Isw_full=[]
V_device_full = []
I_device_full = []
SRS.set_voltage(0)
SRS.set_output(True)
SRS2.set_voltage(0)
SRS2.set_output(True)
k.read_voltage()
sleep(1)

for v_out in V_test:
    SRS2.set_output(False)
    SRS2.set_voltage(v_out)
    sleep(3)
    SRS2.set_output(True)
    V_device = []
    I_device = []
    sleep(3)
    SRS.set_output(True)
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
    Isw_full.append(I_device[np.argmax(np.array(V_device)>.05)-1])
    V_device_full.append(V_device)
    I_device_full.append(I_device)
SRS2.set_output(False)
data_dict = {'V_device':V_device_full, 'I_device':I_device_full, 'V_source':V_source, 'V_test':V_test, 'R_srs':R_srs, 'step':step,'Iswitch':Isw_full}
file_path, file_name  = save_data_dict(data_dict, test_type = 'hTron', test_name = test_name,
                        filedir = filedirectry, zip_file=True)
#
#plt.plot(np.array(V_device), np.array(I_device)*1e6, '-o')
#plt.xlabel('Voltage (V)')
#plt.ylabel('Current (uA)')
#plt.title('I-V '+device_name+', Isw = %.2f uA' %(Isw*1e6))
#print('Isw = %.2f uA' %(Isw*1e6))
#plt.savefig(file_path + '.png')
#plt.show()
#
#
#
#
#
#for v in V_source:
#    SRS.set_voltage(v)
#    sleep(0.1)
#    vread = k.read_voltage()
#    iread = (v-vread)/R_srs
#    print('V=%.4f V, I=%.2f uA, R =%.2f' %(vread, iread*1e6, vread/iread))
#    V_device.append(vread)
#    I_device.append(iread)
#    f, S21 = pna.single_sweep()
#    pna_att = pna.get_source_attenuation()
#    S21_all.append(S21)
#    f_all.append(f)
#    plt.plot(f, 20*np.log10(np.abs(S21)))
#    plt.show()
#plt.savefig(file_path + '.png') 
#plt.show()
#SRS.set_output(False)
#pna_att = pna.get_source_attenuation()
#data_dict = {'V_device':V_device, 'I_device':I_device, 'V_source':V_source, 'R_srs':R_srs, 'step':step, 'S21':S21_all, 'pna_power':pna_power, 'f':f_all, 'pna_att':pna_att}
#file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name+'_sweep_other_current',
#                        filedir = filedirectry, zip_file=True)
##    V_device.append(vread)
##    I_device.append(iread)
#    
#
##SRS.set_output(False)
##search the switching current in the ramping up
##Isw = I_device[np.argmax(np.array(V_device)>.005)-1]
#    
##data_dict = {'V_device':V_device, 'I_device':I_device, 'V_source':V_source, 'R_srs':R_srs, 'step':step}
##file_path, file_name  = save_data_dict(data_dict, test_type = 'Isw_curve', test_name = test_name,
##                        filedir = filedirectry, zip_file=True)
#
#
##f, S21 = pna.single_sweep()
##pna_att = pna.get_source_attenuation()
#
#
##data_dict = {'S21':S21, 'pna_power':pna_power, 'f':f, 'pna_att':pna_att}
##file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
##                        filedir = filedirectry, zip_file=True)
#
##plt.plot(f, 20*np.log10(np.abs(S21)))
#
#plt.savefig(file_path + '.png') 
#plt.show()




#%%phase
resonators = Resonators(r'Q:\qnnpy\config\vna_ceo.yml')

resonators.phase_measurement(start_freq, stop_freq, num_points, power, if_bandwidth)
resonators.save()
resonators.plot()


#%% test of couplingv2
# TODO need to know what "k" is
filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\MC\couplerv3\c_sweep'
#sample_name = 'Ch7Ch5_coupled_-40dbm_'
sample_name = 'Ch7Ch6_through_'
device_name = '1p29K'

test_type = 'S21_'



pna_power =-40
#pna.set_measurement('S21') #measurement type
pna.set_start(9.7e9) #starting frequency in Hz
pna.set_stop(10e9) #stop freq
pna.set_points(501) #number of points
pna.set_if_bw(10) #if bandwidth
pna.set_power(pna_power) #power in dBm


R_srs = 100e3

# counter.set_trigger(0.04)

Isource_max =80e-6
step = 1e-6
#here we go
Isource = np.arange(0, -Isource_max, -step)
#Isource2 = np.arange(Isource_max, -Isource_max, -step)
#Isource3= np.arange(-Isource_max, 0, step)
#Isource = np.concatenate([Isource1, Isource2, Isource3])
V_source = Isource*R_srs

V_device = []
I_device = [] 
S21_all=[]
f_all=[]
SRS.set_voltage(0)
SRS.set_output(True)

# TODO what is k? there is no assignment so this will not run
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
    f, S21 = pna.single_sweep()
    pna_att = pna.get_source_attenuation()
    S21_all.append(S21)
    f_all.append(f)
    plt.plot(f, 20*np.log10(np.abs(S21)))
plt.savefig(file_path + '.png') 
plt.show()
SRS.set_output(False)
pna_att = pna.get_source_attenuation()
data_dict = {'V_device':V_device, 'I_device':I_device, 'V_source':V_source, 'R_srs':R_srs, 'step':step, 'S21':S21_all, 'pna_power':pna_power, 'f':f_all, 'pna_att':pna_att}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name+'_sweep_other_current',
                        filedir = filedirectry, zip_file=True)
#    V_device.append(vread)
#    I_device.append(iread)
    

#SRS.set_output(False)
#search the switching current in the ramping up
#Isw = I_device[np.argmax(np.array(V_device)>.005)-1]
    
#data_dict = {'V_device':V_device, 'I_device':I_device, 'V_source':V_source, 'R_srs':R_srs, 'step':step}
#file_path, file_name  = save_data_dict(data_dict, test_type = 'Isw_curve', test_name = test_name,
#                        filedir = filedirectry, zip_file=True)


#f, S21 = pna.single_sweep()
#pna_att = pna.get_source_attenuation()


#data_dict = {'S21':S21, 'pna_power':pna_power, 'f':f, 'pna_att':pna_att}
#file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
#                        filedir = filedirectry, zip_file=True)

#plt.plot(f, 20*np.log10(np.abs(S21)))




#%% test of coupling 
filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\MC\couplerv3\c_sweep'
#sample_name = 'Ch7Ch5_coupled_-40dbm_'
sample_name = 'Ch7Ch6_through_'
device_name = '1p29K'

test_type = 'S21_'



pna_power =-40
#pna.set_measurement('S21') #measurement type
pna.set_start(9.5e9) #starting frequency in Hz
pna.set_stop(10.5e9) #stop freq
pna.set_points(1001) #number of points
pna.set_if_bw(50) #if bandwidth
pna.set_power(pna_power) #power in dBm


R_srs = 100e3

# counter.set_trigger(0.04)

Isource_max =10e-6
step = 1e-6
#here we go
Isource = np.arange(0, Isource_max, step)
#Isource2 = np.arange(Isource_max, -Isource_max, -step)
#Isource3= np.arange(-Isource_max, 0, step)
#Isource = np.concatenate([Isource1, Isource2, Isource3])
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
    f, S21 = pna.single_sweep()
    pna_att = pna.get_source_attenuation()
    data_dict = {'S21':S21, 'pna_power':pna_power, 'f':f, 'pna_att':pna_att, 'I_other_source':V_source/R_srs, 'I_other_device':iread, 'V_other_device':vread}
    file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name+'_'+str(1e6*v/R_srs)+'uA',
                        filedir = filedirectry, zip_file=True)
    plt.plot(f, 20*np.log10(np.abs(S21)))
plt.savefig(file_path + '.png') 
plt.show()
SRS.set_output(False)
#    V_device.append(vread)
#    I_device.append(iread)
    

#SRS.set_output(False)
#search the switching current in the ramping up
#Isw = I_device[np.argmax(np.array(V_device)>.005)-1]
    
#data_dict = {'V_device':V_device, 'I_device':I_device, 'V_source':V_source, 'R_srs':R_srs, 'step':step}
#file_path, file_name  = save_data_dict(data_dict, test_type = 'Isw_curve', test_name = test_name,
#                        filedir = filedirectry, zip_file=True)


#f, S21 = pna.single_sweep()
#pna_att = pna.get_source_attenuation()


#data_dict = {'S21':S21, 'pna_power':pna_power, 'f':f, 'pna_att':pna_att}
#file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
#                        filedir = filedirectry, zip_file=True)

#plt.plot(f, 20*np.log10(np.abs(S21)))

plt.savefig(file_path + '.png') 
plt.show()




#%%
#power sweep


filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\MC\coupler'
sample_name = 'Ch5Ch7_thru_'
device_name = '1p3K'
test_type = 'S21_'

pna_powers = [-50, -40, -30, -20, -10, 0, 10]
#pna.set_measurement('S21') #measurement type
pna.set_start(1e9) #starting frequency in Hz
pna.set_stop(20e9) #stop freq
pna.set_points(1001) #number of points
pna.set_if_bw(100) #if bandwidth


for pna_power in pna_powers: 
    pna.set_power(pna_power) #power in dBm
    f, S21 = pna.single_sweep()
    pna_att = pna.get_source_attenuation()
    data_dict = {'S21':S21, 'pna_power':pna_power, 'f':f, 'pna_att':pna_att}
    file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name+'_'+str(pna_power)+'dBm',
                        filedir = filedirectry, zip_file=True)

#plt.plot(f, 20*np.log10(np.abs(S21)))
#
#plt.savefig(file_path + '.png') 
#plt.show()

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