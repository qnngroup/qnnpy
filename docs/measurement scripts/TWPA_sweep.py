#%%
import pyvisa
from time import sleep
import numpy as np
from matplotlib import pyplot as plt
import os, sys

sys.path.append('C:\Users\ICE\Desktop\git-repo\qnn-lab-instr-python')


from qnnpy.functions.save_data_vs_param import *
from qnnpy.instruments.keysight_n5224a import KeysightN5224a
from qnnpy.instruments.rs_sgs100a import SGS100A



#%%
#connect PNA
pna = KeysightN5224a("GPIB0::16::INSTR")

pna.reset(measurement = 'S21', if_bandwidth = 1e3, start_freq=200e6,
              stop_freq = 15e9, power = -30)

#connect signal generator
sg = SGS100A('USB0::0x0AAD::0x0088::110963::INSTR')
#%%

filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\GND_TWPA_small'
sample_name = 'GNDTWPA_S'
device_name = ''

sg.basic_setup()
sg.set_output('OFF')


test_type = '2D_sweep'

#
pna_power = -30
#pna.set_measurement('S21') #measurement type
pna.set_start(4e9) #starting frequency in Hz
pna.set_stop(4e9) #stop freq
pna.set_points(1) #number of points
pna.set_if_bw(20) #if bandwidth
pna.set_power(pna_power) #power in dBm

#pna.set_sweep_mode('CONT')
#pna.set_sweep_mode('HOLD')

 

sg.set_frequency(6)
sg.set_power(-10)
sg.set_output('OFF')


S21_ref = []
sg.set_output('OFF')
for i in range(10):
    f, S = pna.single_sweep()
    sleep(.1)
    S21_ref.append(20*np.log10(abs(S)))
    
S21_ref = np.mean(S21_ref)


pump_power=  np.arange(-30, 0, 1)
pump_freq = np.arange(4.5, 5.5, 0.1)
#
#pump_power=  np.arange(-22, -15, 1)
#pump_freq = np.arange(7.2, 7.7, 0.1)

S21 = []

sg.set_output('ON')
for p in pump_power:
    S21_single_row = []
    for pf in pump_freq:
        sg.set_frequency(pf)
        sg.set_power(p)
        sleep(.2)
        f, S = pna.single_sweep()
        sleep(.1)
        S_mag = 20*np.log10(abs(S))
        S21_single_row.append(S_mag)
        print('f  = {}GHz, p = {}dBm, S = {}dB'.format(pf, p, S_mag))
    S21.append(S21_single_row)
        
sg.set_output('OFF')


S21a = np.squeeze(np.array(S21))

S21a_norm = S21a - S21_ref
plt.imshow(S21a_norm, aspect='auto',extent = [pump_freq[0], pump_freq[-1],pump_power[-1], pump_power[0]])

plt.colorbar()
plt.clim(0,30)

        
#S21 = []
#att = []
#for p in range(-50, 10, 3):
#    pna.set_power(p)
#    print('power = {} dBm'.format(pna.get_power()))
#    f, S = pna.single_sweep()
#    att.append(pna.get_source_attenuation())
#    S21.append(S)
#    
data_dict = {'pna_power':pna_power, 'S21_ref':S21_ref, 'S21a_norm':S21a_norm, 'S21':S21, 'pump_power':pump_power, 'pump_freq':pump_freq}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)
plt.savefig(file_path + '.png') 
plt.show()

#for i in range(len(S21)):
#    S = S21[i]
#    a = att[i]
#    plt.plot(f/1e9, 20*np.log10(abs(np.array(S)))+a)
#plt.savefig(file_path + '.png')              
#plt.show()


#%%

test_type = 'gain_curve'


#find the opt operating point
#ind = np.unravel_index(np.argmax(S21a_norm, axis = None), S21a_norm.shape)
#pump_freq_opt = pump_freq[ind[1]]
#pump_power_opt = pump_power[ind[0]]
pump_freq_opt = 7.62
pump_power_opt = -17.8


sg.set_frequency(pump_freq_opt)
sg.set_power(pump_power_opt)
sg.set_output('ON')



pna_power = -70

pna.reset()
#pna.set_measurement('S21') #measurement type
pna.set_start(3e9) #starting frequency in Hz
pna.set_stop(10e9) #stop freq
pna.set_points(1001) #number of points
pna.set_if_bw(1) #if bandwidth
pna.set_power(pna_power) #power in dBm

sg.set_output('OFF')
sleep(.5)
f, S21_off = pna.single_sweep()

pna.set_if_bw(5) #if bandwidth

sg.set_output('ON')
sleep(.5)
f, S21_on = pna.single_sweep()

plt.subplot(211)
plt.plot(f/1e9, 20*np.log10(abs(S21_off)), label = 'pump off')
plt.plot(f/1e9, 20*np.log10(abs(S21_on)), label = 'pump on')
plt.legend()
plt.title('pump power = {}dBm, pump freq = {}GHz, VNA power = {}dBm'
          .format(pump_power_opt,pump_freq_opt, pna_power))
plt.xlabel('Frequency (GHz)')
plt.ylabel('S21 (dB)')

plt.subplot(212)
plt.plot(f/1e9, 20*np.log10(abs(S21_on))-20*np.log10(abs(S21_off)))
#plt.title('pump power = {}dBm, pump freq = {}GHz, VNA power = {}dBm'
#          .format(pump_power_opt,pump_freq_opt, pna_power))
plt.xlabel('Frequency (GHz)')
plt.ylabel('On-off gain (dB)')


data_dict = {'S21_off':S21_off, 'S21_on':S21_on, 'f':f, 'pump_freq_opt':pump_freq_opt,
            'pump_power_opt':pump_power_opt,  'pna_power':pna_power}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)

plt.savefig(file_path + '.png') 

plt.show()

#%%

test_type = 'compression_point'


#find the opt operating point
#ind = np.unravel_index(np.argmax(S21a_norm, axis = None), S21a_norm.shape)
#pump_freq_opt = pump_freq[ind[1]]
#pump_power_opt = pump_power[ind[0]]
#pump_freq_opt = 6.64
#pump_power_opt = -17.32


sg.set_frequency(pump_freq_opt)
sg.set_power(pump_power_opt)
sg.set_output('ON')



pna_power_pump_off = -70


pna_freq = 5e9
pna.reset()
#pna.set_measurement('S21') #measurement type
pna.set_start(pna_freq) #starting frequency in Hz
pna.set_stop(pna_freq) #stop freq
pna.set_points(1) #number of points
pna.set_if_bw(20) #if bandwidth
pna.set_power(pna_power_pump_off) #power in dBm

avg_points = 20

##pump off
#sg.set_output('OFF')
#sleep(.5)
#f, S21_off = pna.single_sweep()

#pump on 
pna_power = np.arange(-70, -30, 1)
S21_on = []
sg.set_output('ON')
sleep(.5)
for p in pna_power:
    pna.set_power(p)
    sleep(.5)
    S_avg_dB = []
    for i in range(avg_points):
        f, S = pna.single_sweep()
        S_avg_dB.append(20*np.log10(np.abs(S)))
    S_avg_dB = np.mean(S_avg_dB)
    print('VNA power = {}dBm, S21={}dB'.format(p, S_avg_dB))
    S21_on.append(S_avg_dB)
    
S21_off = []
sg.set_output('OFF')
sleep(.5)
for p in pna_power:
    pna.set_power(p)
    sleep(.5)
    S_avg_dB = []
    for i in range(avg_points):
        f, S = pna.single_sweep()
        S_avg_dB.append(20*np.log10(np.abs(S)))
    S_avg_dB = np.mean(S_avg_dB)
    print('VNA power = {}dBm, S21={}dB'.format(p, S_avg_dB))
    S21_off.append(S_avg_dB)

    
plt.subplot(211)
plt.plot(pna_power, S21_off, label = 'pump off')
plt.plot(pna_power, S21_on, label = 'pump on')
plt.legend()
plt.title('pump power = {}dBm, pump freq = {}GHz, VNA freq = {}GHz'
          .format(pump_freq_opt, pump_power_opt, pna_freq/1e9))
plt.ylabel('S21 (dB)')

plt.subplot(212)
plt.plot(pna_power, np.array(S21_on)-np.array(S21_off))
plt.ylabel('Gain (dB)')
plt.xlabel('VNA power (dBm)')


data_dict = {'S21_off':S21_off, 'S21_on':S21_on, 'pna_freq':pna_freq, 'pump_freq_opt':pump_freq_opt,
            'pump_power_opt':pump_power_opt,  'pna_power':pna_power}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)

plt.savefig(file_path + '.png') 

plt.show()


sg.set_output('OFF')
pna.set_sweep_mode('HOLD')
