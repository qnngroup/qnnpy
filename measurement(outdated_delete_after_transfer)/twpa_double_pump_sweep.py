'''
TWPA double pump sweep.
6/26/2019

'''
#%%
import serial.tools.list_ports
import sys
sys.path.append('C:\Users\ICE\Desktop\git-repo\qnn-lab-instr-python')
import numpy as np
import matplotlib.pyplot as plt 
import os

from qnnpy.instruments.synthhd import SynthHD
from qnnpy.instruments.keysight_n5224a import KeysightN5224a
from qnnpy.functions.save_data_vs_param import *

from time import sleep, time

#%%
#initiate vna
pna = KeysightN5224a("GPIB0::16::INSTR")
pna.reset(measurement = 'S21', if_bandwidth = 1e3, start_freq=200e6,
              stop_freq = 15e9, power = -40)

#initiate signal generator
# list out the com ports
print([comport.device for comport in serial.tools.list_ports.comports()])

sg = SynthHD('COM17') # Windows, change the COM number
#dev = SynthHD('/dev/ttyACM0') # Linux, change the tty id
print("Initialized? ", sg.initialized()) # check if it is initialized successfully
print('Current Channel: ', sg.get_channel())

#%%

filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\TWPA8_double_pump'
sample_name = 'TWPA_disp_free'
device_name = 'TWPA8'


test_type = '2D_sweep'


pna_power = -40
#pna.set_measurement('S21') #measurement type
pna.set_start(5.5e9) #starting frequency in Hz
pna.set_stop(5.5e9) #stop freq
pna.set_points(1) #number of points
pna.set_if_bw(10) #if bandwidth
pna.set_power(pna_power) #power in dBm



f1 = 3#in GHz

A = 0 #channel number
B = 1


sg.set_channel(1) #1 is B, low freq
sg.set_freq(f1*1e3)


f2 = 8 # in GHz
sg.set_channel(0) #0 is A, high freq
sg.set_freq(f2*1e3)

sg.open_all() # turn on both channels

sg.set_power([-30, -30])
sg.set_channel(0) #we will be tunning this channel
#dev.set_freq([50.00, 100.00]) # in MHz, set frequency on both channels
# dev.open() # turn on current channel

#sg.close(1) # turn off channel 1
# dev.close() # turn off current channel
# dev.close_all() # turn off both channels

#%%some useful commands for signal generator
#dev.set_freq(8000.00) # in MHz, set frequency on current channel
#
#sleep(2)
#
#dev.set_freq([50.00, 100.00]) # in MHz, set frequency on both channels
#
#dev.set_power(-30) # in dBm, set power on current channel
#
#sleep(2)
#
#dev.set_power([2,1]) # in dBm, set power on both channels


#%%

#t1 = time()
#
#
#t2 = time()
#
#print('full time ', tstop-t1)

sg.close_all()



pump_power=  np.linspace(-24,-20, 20)

#pump_freq = np.linspace(5,15,51)
pump_freq = [6]

f1= 5.5

S21 = []
S21_ref = []
S21_norm = [] #gain


for pf in pump_freq:
    #set sg freq
    sg.set_channel(A)
    sg.set_freq(pf*1e3)
    
    # change the second pump power to account for attenuation at higher freq
    pump_power_offset =0 # 1.6 * (pf-5) 
    
    #set VNA freq
    f0 = np.mean([f1, pf]) #in GHz
    pna.set_start(f0*1e9) #starting frequency in Hz
    pna.set_stop(f0*1e9) #stop freq
    pna.set_points(1) #number of points
    #base line
    sg.close_all(); sleep(.2)
    S21_ref_temp = []
    
    for i in range(10):
        f, S = pna.single_sweep()
        sleep(.1)
        S21_ref_temp.append(20*np.log10(abs(S)))
    base_line = np.mean(S21_ref_temp)
    S21_ref.append(base_line)
    
    S21_single_row = []
    S21_norm_single_row = []
    for p in pump_power: #power
        sg.set_channel(A)
        sg.set_power(p + pump_power_offset)
        sg.open_all()
        sleep(.2)
        
        f, S = pna.single_sweep()
        sleep(.1)
        S_mag = 20*np.log10(abs(S))
        S21_single_row.append(S_mag)
        S21_norm_single_row.append(S_mag-base_line)
        print('f  = {}GHz, p = {}dBm, S = {}dB, gain = {}dB'.format(pf, p, S_mag, S_mag-base_line))
    S21.append(S21_single_row)
    S21_norm.append(S21_norm_single_row)
    
sg.close_all()


    



S21a_norm = np.squeeze(np.array(S21_norm))

plt.imshow(S21a_norm, aspect='auto',extent = [pump_power[0],pump_power[-1],   pump_freq[-1], pump_freq[0]])

plt.colorbar()
#plt.clim(0,30)
#S21 = []
#att = []
#for p in range(-50, 10, 3):
#    pna.set_power(p)
#    print('power = {} dBm'.format(pna.get_power()))
#    f, S = pna.single_sweep()
#    att.append(pna.get_source_attenuation())
#    S21.append(S)
#    
data_dict = {'pna_power':pna_power, 'S21_ref':S21_ref, 'S21_norm':S21a_norm, 'S21':S21, 'pump_power':pump_power,
             'pump_freq':pump_freq}
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)
plt.savefig(file_path + '.png') 
plt.show()


#%% look for critical power

#pump freq
fB = 3
fA = 8


#pump_freq = np.linspace(5,15,51)
pump_freq = [fA, fB] # ,fB]
chns = [A, B]
sg.close_all()

#pump A first
pump_power=  np.linspace(-20, 0, 26)


S21 = [[] for idx in pump_freq]
S21_ref = [[] for idx in pump_freq]
S21_norm = [[] for idx in pump_freq] #gain


#sg.set_channel(B)
#sg.set_power(-13)
#sg.set_freq(fB*1e3)


for idx, pf in enumerate(pump_freq):
    chn = chns[idx]
    sg.set_channel(chn)    
    sg.set_freq(pf* 1e3)
#    print(pf)
#    print(chn)    
#    sg.set_power(-50)

 
    # change the second pump power to account for attenuation at higher freq
    pump_power_offset =0 # 1.6 * (pf-5) 
    
    #set VNA freq
#    f0 = pf-.5 #in GHz
    f0 = 5.5 #in GHz
    pna.set_start(f0*1e9) #starting frequency in Hz
    pna.set_stop(f0*1e9) #stop freq
    pna.set_points(1) #number of points
    #base line
    sg.close_all(); sleep(.2)
    S21_ref_temp = []
    
    for i in range(10):
        f, S = pna.single_sweep()
        sleep(.1)
        S21_ref_temp.append(20*np.log10(abs(S)))
    base_line = np.mean(S21_ref_temp)
    S21_ref[idx].append(base_line)
    
    S21_single_row = []
    S21_norm_single_row = []
    for p in pump_power: #power
        sg.set_channel(chn)
        sg.set_power(p + pump_power_offset)
        sg.open(chn)
#        sg.open_all()
        sleep(.2)
        
        f, S = pna.single_sweep()
        sleep(.1)
        S_mag = 20*np.log10(abs(S))
        S21_single_row.append(S_mag)
        S21_norm_single_row.append(S_mag-base_line)
        print('f  = {}GHz, p = {}dBm, S = {}dB, gain = {}dB'.format(pf, p, S_mag, S_mag-base_line))
    S21[idx].append(S21_single_row)
    S21_norm[idx].append(S21_norm_single_row)
    

sg.close_all()



    
for idx in range(len(pump_freq)):
    print("Frequency: %d GHz" % pump_freq[idx])
    S21a_norm = np.squeeze(np.array(S21_norm[idx]))
    plt.plot(pump_power, S21a_norm, label='%d GHz, VNA: %d dBm' % (pump_freq[idx],pna_power))
    plt.xlabel("Pump Power (dBm)")
    plt.ylabel("Normalized Gain (dB)")
    plt.title("Pump Power Sweep at %d GHz" % pump_freq[idx])
    plt.legend()
    data_dict = {'pna_power':pna_power, 'S21_ref':S21_ref[idx], 'S21_norm':S21a_norm[idx], 'S21':S21[idx], 'pump_power':pump_power,
             'pump_freq':pump_freq[idx]}
    file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                            filedir = filedirectry, zip_file=True)
    plt.savefig(file_path + '.png') 
    plt.show()


#plt.clim(0,30)
#S21 = []
#att = []
#for p in range(-50, 10, 3):
#    pna.set_power(p)
#    print('power = {} dBm'.format(pna.get_power()))
#    f, S = pna.single_sweep()
#    att.append(pna.get_source_attenuation())
#    S21.append(S)
#    

#%%
# fix pump freq, sweep pump powers, dual pump
sg.close_all()

pump_power_A=  np.arange(-23,-3.1, 1)
pump_power_B=  np.arange(-41,-6.1, 1)


#pump_freq = np.linspace(5,15,51)
fB = 3
fA = 8

f_probe = (fA + fB) / 2.0

S21 = []
S21_ref = []
S21_norm = [] #gain

average_number = 5

#        # measure ref level
#        sg.close_all()


#set VNA freq
pna.set_start(f_probe*1e9) #starting frequency in Hz
pna.set_stop(f_probe*1e9) #stop freq
pna.set_points(1) #number of points

#base line
sleep(0.2)
S21_ref_temp = []
for i in range(10):
    f, S = pna.single_sweep()
    sleep(.1)
    S21_ref_temp.append(20*np.log10(abs(S)))
S21_ref = np.mean(S21_ref_temp)

sg.set_freq([fA * 1e3, fB * 1e3])


sg.open_all()

print('power sweeping at %d GHz and %d GHz' % (fA,fB))


t1 = time()
#
for pa in pump_power_A:
    S21_single_row = []
    S21_norm_single_row = []
    for pb in pump_power_B:
        sg.set_power([pa, pb])
        sleep(.2)
        S1_temp = []
        for i in range(average_number):
            f, S = pna.single_sweep()
            S_mag = 20*np.log10(abs(S))
            S1_temp.append(S_mag)
        S_mag = sum(S1_temp)/len(S1_temp)
        
            
        sleep(.1)
        S_mag = 20*np.log10(abs(S))
        S21_single_row.append(S_mag)
        S21_norm_single_row.append(S_mag-S21_ref)
        print('pa = {}dBm,pb = {}dBm, S = {}dB, gain = {}dB'.format(pa, pb, S_mag, S_mag-S21_ref))
        S21.append(S21_single_row)
        S21_norm.append(S21_norm_single_row)
        

t2 = time()

print('full time ', t2-t1)
print('average per point', (t2-t1)/(len(pump_power_A) * len(pump_power_B)))
     
        
        


gain = np.squeeze(np.array(S21_norm))
plt.imshow(gain, aspect='auto',extent = [pump_power_B[0],pump_power_B[-1], pump_power_A[0], pump_power_A[-1]],origin='lower')
plt.colorbar()
plt.xlabel('Pump B Power (dBm)')
plt.ylabel('Pump A Power (dBm)')
plt.title('power sweeping at %d GHz and %d GHz' % (fA,fB))
#plt.imshow(S21a_norm, aspect='auto',extent = [pump_power[0],pump_power[-1],   pump_freq[-1], pump_freq[0]])

#plt.clim(0,30)
#S21 = []
#att = []
#for p in range(-50, 10, 3):
#    pna.set_power(p)
#    print('power = {} dBm'.format(pna.get_power()))
#    f, S = pna.single_sweep()
#    att.append(pna.get_source_attenuation())
#    S21.append(S)
#    
data_dict = {'pna_power':pna_power, 'S21_ref':S21_ref, 'gain':gain, 'S21':S21, 'pump_power_a':pump_power_A,'pump_power_b':pump_power_B,
             'fA':fA, 'fB':fB, 'average_number':average_number }
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)
plt.savefig(file_path + '.png') 
plt.show()

#%%
pna_power = -65
#pna.set_measurement('S21') #measurement type
pna.set_start(f_probe * 1e9) #starting frequency in Hz
pna.set_stop(f_probe * 1e9) #stop freq
pna.set_points(1) #number of points
pna.set_if_bw(5) #if bandwidth
pna.set_power(pna_power) #power in dBm
#%%
# fix pump freq, sweep pump powers, dual pump, 3-point measurements
sg.close_all()

pump_power_A=  np.arange(-15,-1, .5)
pump_power_B=  np.arange(-20,-5, .5)

#pump_power_A=  np.linspace(-23,-3.1, 2)
#pump_power_B=  np.linspace(-41,-15.1, 3)


pconfigs = [[1,1],[0,1],[1,0]] # on (1)/ off(0) configs for the pumps

#pump_freq = np.linspace(5,15,51)
fB = 3
fA = 8

f_probe = (fA + fB) / 2.0

S21 = [[] for idx in pconfigs]
S21_ref = [[] for idx in pconfigs]
S21_norm = [[] for idx in pconfigs] #gain


average_number = 5

#        # measure ref level
#        sg.close_all()


#set VNA freq
pna.set_start(f_probe*1e9) #starting frequency in Hz
pna.set_stop(f_probe*1e9) #stop freq
pna.set_points(1) #number of points

#base line
sleep(0.2)
S21_ref_temp = []
for i in range(30):
    f, S = pna.single_sweep()
    sleep(.1)
    S21_ref_temp.append(20*np.log10(abs(S)))
S21_ref = np.mean(S21_ref_temp)

sg.set_freq([fA * 1e3, fB * 1e3])


sg.close_all()

print('power sweeping at %d GHz and %d GHz' % (fA,fB))


t1 = time()
#



for pa in pump_power_A:
    S21_single_row =  [[] for idx in pconfigs]
    S21_norm_single_row =  [[] for idx in pconfigs]
    S1_temp =  [[] for idx in pconfigs]
    for pb in pump_power_B:
        sg.set_power([pa, pb])
        sleep(.1)
        
        for idx, pconfig in enumerate(pconfigs):

            # open/close the two channels accordingly
            for chn in range(len(pconfig)):
                if pconfig[chn] == 1:
                    sg.open(chn)
            sleep(.1)
        
            for _ in range(average_number):
                f, S = pna.single_sweep()
#                S_mag = 20*np.log10(abs(S))
                S1_temp[idx].append(S)
            S_avg = sum(S1_temp[idx])/len(S1_temp[idx])
            S_mag = 20*np.log10(abs(S_avg))
            
            S21_single_row[idx].append(S_mag)
            S21_norm_single_row[idx].append(S_mag-S21_ref)
            print('config:{}, pa = {:.2f}dBm,pb = {:.2f}dBm, S = {:.2f}dB, gain = {:.2f}dB'.format(pconfig,pa, pb, S_mag[0], S_mag[0]-S21_ref))
            
            sg.close_all() # reset all pumps 
        
    for idx, pconfig in enumerate(pconfigs):
        S21[idx].append(S21_single_row[idx])
        S21_norm[idx].append(S21_norm_single_row[idx])
            
            
            
t2 = time()

print('full time ', t2-t1)
print('average per point', (t2-t1)/(len(pump_power_A) * len(pump_power_B)))
     
gains = [[] for idx in range(len(pconfigs))]       
fig, axes = plt.subplots(1,3,figsize=(20, 10))
plt.suptitle('power sweeping at %d GHz and %d GHz' % (fA,fB))  

clim = []      
for idx, pconfig in enumerate(pconfigs):
    gains[idx] = np.squeeze(np.array(S21_norm[idx]))
    axes[idx].imshow(gains[idx], aspect='auto',extent = [pump_power_B[0],pump_power_B[-1], pump_power_A[0], pump_power_A[-1]],origin='lower')
    if idx == 0:
        im = axes[idx].imshow(gains[idx], aspect='auto',extent = [pump_power_B[0],pump_power_B[-1], pump_power_A[0], pump_power_A[-1]],origin='lower')
        clim = im.properties()['clim']
    else:
        axes[idx].imshow(gains[idx], aspect='auto',extent = [pump_power_B[0],pump_power_B[-1], pump_power_A[0], pump_power_A[-1]],origin='lower',clim=clim)
#    plt.subplot(1,x3,idx + 1)
    
fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.5)
plt.xlabel('Pump B Power (dBm)')
plt.ylabel('Pump A Power (dBm)')
    

plt.show()
#plt.imshow(S21a_norm, aspect='auto',extent = [pump_power[0],pump_power[-1],   pump_freq[-1], pump_freq[0]])

#plt.clim(0,30)
#S21 = []
#att = []
#for p in range(-50, 10, 3):
#    pna.set_power(p)
#    print('power = {} dBm'.format(pna.get_power()))
#    f, S = pna.single_sweep()
#    att.append(pna.get_source_attenuation())
#    S21.append(S)
#    
data_dict = {'pna_power':pna_power, 'S21_ref':S21_ref, 'gains':gains, 'S21':S21, 'pump_power_a':pump_power_A,'pump_power_b':pump_power_B,
             'fA':fA, 'fB':fB, 'average_number':average_number }
file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
                        filedir = filedirectry, zip_file=True)
plt.savefig(file_path + '.png') 
plt.show()

#%%
#for i in range(len(S21)):
#    S = S21[i]
#    a = att[i]
#    plt.plot(f/1e9, 20*np.log10(abs(np.array(S)))+a)
#plt.savefig(file_path + '.png')              
#plt.show()

#
##%%
#
#test_type = 'gain_curve'
#
#
##find the opt operating point
##ind = np.unravel_index(np.argmax(S21a_norm, axis = None), S21a_norm.shape)
##pump_freq_opt = pump_freq[ind[1]]
##pump_power_opt = pump_power[ind[0]]
#pump_freq_opt = 7.62
#pump_power_opt = -17.8
#
#
#sg.set_frequency(pump_freq_opt)
#sg.set_power(pump_power_opt)
#sg.set_output('ON')
#
#
#
#pna_power = -70
#
#pna.reset()
##pna.set_measurement('S21') #measurement type
#pna.set_start(3e9) #starting frequency in Hz
#pna.set_stop(10e9) #stop freq
#pna.set_points(1001) #number of points
#pna.set_if_bw(1) #if bandwidth
#pna.set_power(pna_power) #power in dBm
#
#sg.set_output('OFF')
#sleep(.5)
#f, S21_off = pna.single_sweep()
#
#pna.set_if_bw(5) #if bandwidth
#
#sg.set_output('ON')
#sleep(.5)
#f, S21_on = pna.single_sweep()
#
#plt.subplot(211)
#plt.plot(f/1e9, 20*np.log10(abs(S21_off)), label = 'pump off')
#plt.plot(f/1e9, 20*np.log10(abs(S21_on)), label = 'pump on')
#plt.legend()
#plt.title('pump power = {}dBm, pump freq = {}GHz, VNA power = {}dBm'
#          .format(pump_power_opt,pump_freq_opt, pna_power))
#plt.xlabel('Frequency (GHz)')
#plt.ylabel('S21 (dB)')
#
#plt.subplot(212)
#plt.plot(f/1e9, 20*np.log10(abs(S21_on))-20*np.log10(abs(S21_off)))
##plt.title('pump power = {}dBm, pump freq = {}GHz, VNA power = {}dBm'
##          .format(pump_power_opt,pump_freq_opt, pna_power))
#plt.xlabel('Frequency (GHz)')
#plt.ylabel('On-off gain (dB)')
#
#
#data_dict = {'S21_off':S21_off, 'S21_on':S21_on, 'f':f, 'pump_freq_opt':pump_freq_opt,
#            'pump_power_opt':pump_power_opt,  'pna_power':pna_power}
#file_path, file_name  = save_data_dict(data_dict, test_type = test_type, test_name = sample_name+'_'+device_name,
#                        filedir = filedirectry, zip_file=True)
#
#plt.savefig(file_path + '.png') 
#
#plt.show()
#
#%%

test_type = 'compression_point'


#find the opt operating point
#ind = np.unravel_index(np.argmax(S21a_norm, axis = None), S21a_norm.shape)
#pump_freq_opt = pump_freq[ind[1]]
#pump_power_opt = pump_power[ind[0]]
#pump_freq_opt = 6.64
#pump_power_opt = -17.32


pump_freq_opt = 6
pump_power_opt = -22


sg.set_channel(A)
sg.set_freq(pump_freq_opt*1e3)
sg.set_power(pump_power_opt)
sg.open()



pna_power_pump_off = -80


pna_freq = 5.5
pna.reset()
#pna.set_measurement('S21') #measurement type
pna.set_start(pna_freq*1e9) #starting frequency in Hz
pna.set_stop(pna_freq*1e9) #stop freq
pna.set_points(1) #number of points
pna.set_if_bw(20) #if bandwidth
pna.set_power(pna_power_pump_off) #power in dBm

avg_points = 20

##pump off
#sg.set_output('OFF')
#sleep(.5)
#f, S21_off = pna.single_sweep()

#pump on 
pna_power = np.concatenate((np.arange(-85, -60, 1), np.arange(-60, -30, 10)))
S21_on = []
sg.open(A)
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
sg.close(A)
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


#sg.set_output('OFF')
pna.set_sweep_mode('HOLD')

