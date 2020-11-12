# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 16:35:22 2019

@author: ICE
"""

import sys
import os
import visa
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
import numpy as np
import scipy
from datetime import datetime

sys.path.append('C:\Users\ICE\Desktop\git-repo\qnn-lab-instr-python')


from qnnpy.instruments.keithley_2700 import Keithley2700
from qnnpy.instruments.srs_sim928 import SIM928
from qnnpy.functions.save_data_vs_param import *
from qnnpy.instruments.lecroy_620zi import LeCroy620Zi
from qnnpy.instruments.jds_ha9 import JDSHA9
from qnnpy.instruments.agilent_53131a import Agilent53131a
#%%
#########################################
### Connect to instruments
#########################################
SRS = SIM928('GPIB0::1', 2); SRS.reset()
k = Keithley2700("GPIB0::3"); k.reset()
lecroy_ip = 'QNN-SCOPE1.MIT.EDU'
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
attenuator = JDSHA9('GPIB0::7')
counter = Agilent53131a('GPIB0::30')
counter.basic_setup()
#%%
from datetime import datetime

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

def save_traces(lecroy = lecroy, channels = ['C1', 'C2', 'F1', 'F2'], fname = 'file.mat', fpath = ''):
    """save all traces indicated"""
    lecroy.set_trigger_mode('Stop')
    sleep(0.1)
    data_dict = {}

    for c in channels:
        x,y = lecroy.get_wf_data(c)
        xkey = c+'x'
        ykey = c+'y'
        data_dict[xkey] = x
        data_dict[ykey] = y
    if '.' in fname:
        if fname.split('.')[1] != 'mat':
            print('file extension error') 
    else:
        fname = fname+'.mat'
    #add time to the file name
    t = datetime.now()
    tstr = t.strftime('%Y%m%d')+'_%02d%02d%02d_'% (t.hour, t.minute, t.second)
    #save matlab file
    ffull = os.path.join(fpath, tstr+fname)
    scipy.io.savemat(ffull, mdict=data_dict)
    #save screen shot
    scname = os.path.join(fpath, tstr+fname.split('.')[0]+'.png')
    lecroy.save_screenshot(scname)

def my_get_single_trace(channel = 'C1'):
    """ Sets scope to "single" trigger mode to acquire one trace, then waits until the trigger has happened
    (indicated by the trigger mode changing to "Stopped").  """
    lecroy.set_trigger_mode(trigger_mode = 'Single')
    if lecroy.get_trigger_mode() == 'Single\n':
        while lecroy.get_trigger_mode() == 'Single\n':
            #SRS.set_output(False)
            sleep(1e-4)
            #SRS.set_output(True)
    x,y = lecroy.get_wf_data(channel=channel)
    return x,y
    
def save_traces_multiple(channels = ['C1', 'C2'], num_traces = 20, threshold = [0,0], fpath='', fname='myfile', optout1 = False):
    """save multiple traces multiple times, threshold is set for each channel to eliminate false counts (set to )
    0 if unused"""
    num_ch = len(channels)
    x1list = []; y1list = [];
    x2list = []; y2list = [];
    x3list = []; y3list = [];
    x4list = []; y4list = [];
    q = 0 #number of not useless points
    for i in range(num_traces):
        try:
            if num_ch>0:
                x,y = my_get_single_trace(channels[0])
                if max(abs(y))>threshold[0]:
                    x1list.append(x)
                    y1list.append(y)
                else:
                    q = q+1
                    print('Not useful'),
                    continue
            if num_ch>1:
                x,y = lecroy.get_wf_data(channels[1])
                if max(abs(y))>threshold[1]:
                    x2list.append(x)
                    y2list.append(y)
                else:
                    q = q+1
                    print('Not useful'),
                    x1list.pop();y1list.pop()
                    continue
            if num_ch>2:
                x,y = lecroy.get_wf_data(channels[2])
                if max(abs(y))>threshold[2]:
                    x3list.append(x)
                    y3list.append(y)
                else:
                    q = q+1
                    print('Not useful'),
                    x1list.pop();y1list.pop(); x2list.pop(); y2list.pop()
                    continue
            if num_ch>3:
                x,y = lecroy.get_wf_data(channels[3])
                if max(abs(y))>threshold[3]:
                    x4list.append(x)
                    y4list.append(y)
                else:
                    q = q+1
                    print('Not useful'),
                    x1list.pop();y1list.pop(); x2list.pop(); y2list.pop()
                    x3list.pop(); y3list.pop();
                    continue
            if i%100 == 0:
                print(i),
        except:
            print('error')
            return 0
    
    data_dict = {}
    if optout1==False:
        if num_ch>0:
            data_dict[channels[0]+'x']=x1list
            data_dict[channels[0]+'y']=y1list
    if num_ch>1:
        data_dict[channels[1]+'x']=x2list
        data_dict[channels[1]+'y']=y2list
    if num_ch>2:
        data_dict[channels[2]+'x']=x3list
        data_dict[channels[2]+'y']=y3list
    if num_ch>3:
        data_dict[channels[3]+'x']=x4list
        data_dict[channels[3]+'y']=y4list
    
    if '.' in fname:
        if fname.split('.')[1] != 'mat':
            print('file extension error') 
    else:
        fname = fname+'.mat'
    #add time to the file name
    t = datetime.now()
    tstr = t.strftime('%Y%m%d')+'_%02d%02d%02d_'% (t.hour, t.minute, t.second)
    #save matlab file
    ffull = os.path.join(fpath, tstr+fname)
    scipy.io.savemat(ffull, mdict=data_dict)
    #save screen shot
    scname = os.path.join(fpath, tstr+fname.split('.')[0]+'.png')
    lecroy.save_screenshot(scname)
            

#%%
sample_name = 'SPF920A'
device_name = 'B2'
comments = 'T=1p51'
test_name = sample_name+'_'+device_name+'_'+comments
filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\SPF920A_QW'

#%%


lecroy.clear_sweeps()

#%%
num_of_sampels = 200000
number_of_sweeps = 1

start_number = 0

#voltage = [1.3, 1.4, 1.5, 1.6, 1.65, 1.70];
Ibs = [16.8e-6, 16.9e-6]
R_srs = 100e3
attenuation = 50


#traching number of latching events per sample period. When this is too high, the EOM could have been drifted.
latch_counter = 0
for Ib in Ibs: 
    print('Ib={:.2f}uA'.format(Ib*1e6))
    fname = 'SPF920A_B2_1550nm_{:d}dB_Ib={:.1f}uA'.format(attenuation, Ib*1e6)
    fname = fname.replace('.', 'p')

    for i in range(number_of_sweeps):
        #awg.set_output(True)
        attenuator.set_attenuation_db(attenuation)
        attenuator.set_beam_block(False)
        SRS.set_voltage(Ib*R_srs)
        SRS.set_output(False); sleep(0.5)
        SRS.set_output(True)
        sleep(3)
        lecroy.clear_sweeps()
        lecroy.set_trigger_mode('Normal')
        print '\n starting with i = ' + str(i) +'\n'
        while lecroy.get_num_data_points('P3') < num_of_sampels:
            print lecroy.get_num_data_points('P3'), 
            sleep(5)
            if k.read_voltage()>0.1:
                print 'latched',
                latch_counter = latch_counter+1
                SRS.set_output(False); sleep(0.1); SRS.set_output(True)
                
                #let the EOM to take a rest
            #if latch_counter>20:
            #    print 'latching too often'
            #    awg.set_output(False)
            #    attenuator.set_beam_block(True)
            #    SRS.set_output(False)
            #    lecroy.set_trigger_mode('Stop')
            #    sleep(600)
            #    awg.set_output(True)
            #    attenuator.set_beam_block(False)
            #    SRS.set_output(True)
            #    lecroy.set_trigger_mode('Normal')
            #    latch_counter = 0
            #    sleep(3)
                
                
                
        #fname= fname+'_'+str(i+start_number)
        save_traces(channels = ['C1','C2', 'C3', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10'], fname = fname, fpath = filedirectry)
        sleep(1)
        #reset latch counter
        latch_counter = 0  

lecroy.set_trigger_mode('Stop')
SRS.set_voltage(0); SRS.set_output(False)
attenuator.set_beam_block(True)


#%%


fname = 'SPF920A_B2_1064nm_65dB_Ib=16p6uA'


save_traces(channels = ['C1','C2', 'C3', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10'], fname = fname, fpath = filedirectry)
lecroy.set_trigger_mode('Normal')


#%%
#save some traces
Ibs = [15e-6, 15.5e-6, 16.5e-6, 16.5e-6, 17e-6]
R_srs = 100e3
att = 50
for Ib in Ibs:
    lecroy.clear_sweeps()
    SRS.set_voltage(Ib*R_srs)    
    fname = 'SPF920A_B2_1550nm_{}dB_Ib={:.1f}uA_trigger_traces'.format(att, Ib*1e6)
    fname = fname.replace('.','p')    
    SRS.set_output(False); SRS.set_output(True)
    save_traces_multiple(channels = ['C1', 'C2', 'C3'], num_traces = 2000, threshold = [.5,.2,.2], 
                         fpath=filedirectry, fname=fname, optout1 = True)
