#%%
import sys
import os

sys.path.append('C:\Users\ICE\Desktop\git-repo\qnn-lab-instr-python')


from qnnpy.instruments.keithley_2700 import Keithley2700
from qnnpy.instruments.srs_sim928 import SIM928
from qnnpy.functions.save_data_vs_param import *

import visa
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
import numpy as np
from datetime import datetime
import scipy


#import library
from qnnpy.instruments.lecroy_620zi import LeCroy620Zi
from qnnpy.instruments.agilent_33250a import Agilent33250a
#########################################
### Connect to instruments
#########################################

#%%
#lecroy_ip = 'QNN-SCOPE1.MIT.EDU'
lecroy_ip = '18.62.7.103'
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
awg = Agilent33250a( u'GPIB0::10::INSTR')

#%%
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
    
def save_traces_multiple(channels = ['C1', 'C2'], num_traces = 20, threshold = [0,0], fpath='', fname='myfile'):
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
                    print('Not useful')
            if num_ch>1:
                x,y = my_get_single_trace(channels[1])
                if max(abs(y))>threshold[1]:
                    x2list.append(x)
                    y2list.append(y)
                else:
                    q = q+1
                    print('Not useful')
            if num_ch>2:
                x,y = my_get_single_trace(channels[2])
                if max(abs(y))>threshold[2]:
                    x3list.append(x)
                    y3list.append(y)
                else:
                    q = q+1
                    print('Not useful')
            if num_ch>3:
                x,y = my_get_single_trace(channels[3])
                if max(abs(y))>threshold[3]:
                    x4list.append(x)
                    y4list.append(y)
                else:
                    q = q+1
                    print('Not useful')
            if i%100 == 0:
                print(i),
        except:
            print('error')
    
    data_dict = {}
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
#fpath = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\SPF190B\20180131'
#fname = 'jitter_lmd=1550_att=0dB_Ib=22uA_10x10_taper_C2-P2_C3-P5'

#filedirectry = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\SPF831_PNR_v3\SPDC'
fpath = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\20191222_isw_ramp_rate_AQ'




#%%
Isw = 27e-6;
Rb = 100e3;

freq = 200
#vpp = Isw*Rb*(1+2*.9)
#v_offset = Isw*Rb*.9
vpp = Isw*Rb*6
v_offset = 0

awg.set_freq(freq)
awg.set_vpp(vpp)
awg.set_voffset(v_offset)
awg.set_output(True)

#%%

freq_list = np.arange(10, 1000,10)

for f in freq_list:
    awg.set_freq(f)
    print(f)
    fname = 'f={}Hz_two_filters_bias_T_open_both'.format(int(f))
    lecroy.set_horizontal_scale(time_per_div = 2.0/f/10.0, time_offset = 0)
    sleep(2.0/freq)
    save_traces(channels = ['C2','C3', 'F2', 'F3'], fname = fname, fpath = fpath)
    lecroy.set_trigger_mode('Normal')


    



#%%
save_traces(channels = ['C2','C3', 'F2', 'F3'], fname = fname, fpath = fpath)
lecroy.set_trigger_mode('Normal')
#
#
##%%
#fname = 'PNRv3_SPDC_fiber_path_only'
#save_traces(channels = ['C1','C2', 'F1'], fname = fname, fpath = fpath)
#lecroy.set_trigger_mode('Stop')
#
##%%
##save pulse shapes
#fname ='pulse_trace_T=4p5K_Ib=12p8uA'
#save_traces_multiple(channels = ['C2'], num_traces = 500, threshold = [0], fpath=fpath, fname=fname)
#  
##%%
##save jitter
#num_samples = 300e3
#while lecroy.get_num_data_points('P1') < num_samples:
#    print lecroy.get_num_data_points('P1'), 
#    sleep(5)
#    if k.read_voltage()>0.5:
#        print 'latched'
#        SRS.set_output(False); sleep(0.1); SRS.set_output(True)
#        
#fname = fname = 'ref_jitter_lmd=1550_LNA2500_LNA2000_T=1p3'
#save_traces(channels = ['C2', 'C3', 'F2'], fname = fname, fpath = fpath)
#
#
##%%
##acquire traces multiple times
#
################################################
##Acquire single channel traces
###############################################
#x_list = []
#y_list = []
#channel = 'C2'
#samplemax = 10
#dl = 0 #height threshold to eliminate dark counts/undesired noise 
#
#for i in range(samplemax):
#    try: 
#        x,y = my_get_single_trace(channel)
#        if max(abs(y)) > dl:
#            x_list.append(x)
#            y_list.append(y)
#        else:
#            print('Not useful')
#        if i%100== 0:
#            print(i),
#    except:
#        print('error')
#
#t = datetime.now()
#tstr = t.strftime('%Y%m%d')+'_%02d%02d%02d_'% (t.hour, t.minute, t.second)
#
#fpath = r'/Users/dizhu/Dropbox (MIT)/QNN lab/Device testing/20180128_Yi_gauge_field/dual_mod'     
#fname = 'f1=6000kHz_f2=6000kHz'
#fname_full = os.path.join(fpath, tstr+fname)
#
#data_dict = {channel+'_x':x_list, channel+'_y':y_list}
#
#scipy.io.savemat(fname_full+'.mat', mdict=data_dict)
#lecroy.save_screenshot(fname_full+'.png')
#print('done')
#lecroy.set_trigger_mode('Normal')
