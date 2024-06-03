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

#########################################
### Connect to instruments
#########################################

#%%
lecroy_ip = 'QNN-SCOPE1.MIT.EDU'
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
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
    x1list = []; y1list = []
    x2list = []; y2list = []
    x3list = []; y3list = []
    x4list = []; y4list = []
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
fpath = filedirectry

#%%
fname = 'PPNRv2_500MHz_1550nm_no_attenuation'
save_traces(channels = ['C1','C2', 'C3', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10'], fname = fname, fpath = fpath)
lecroy.set_trigger_mode('Normal')


#%%
fname = 'PNRv3_SPDC_fiber_path_only'
save_traces(channels = ['C1','C2', 'F1'], fname = fname, fpath = fpath)
lecroy.set_trigger_mode('Stop')

#%%
#save pulse shapes
fname ='pulse_trace_T=4p5K_Ib=12p8uA'
save_traces_multiple(channels = ['C2'], num_traces = 500, threshold = [0], fpath=fpath, fname=fname)
  
#%%
#save jitter
num_samples = 300e3
while lecroy.get_num_data_points('P1') < num_samples:
    print lecroy.get_num_data_points('P1'), 
    sleep(5)
    if k.read_voltage()>0.5:
        print 'latched'
        SRS.set_output(False); sleep(0.1); SRS.set_output(True)
        
fname = fname = 'ref_jitter_lmd=1550_LNA2500_LNA2000_T=1p3'
save_traces(channels = ['C2', 'C3', 'F2'], fname = fname, fpath = fpath)


#%%
#acquire traces multiple times

###############################################
#Acquire single channel traces
##############################################
x_list = []
y_list = []
channel = 'C2'
samplemax = 10
dl = 0 #height threshold to eliminate dark counts/undesired noise 

for i in range(samplemax):
    try: 
        x,y = my_get_single_trace(channel)
        if max(abs(y)) > dl:
            x_list.append(x)
            y_list.append(y)
        else:
            print('Not useful')
        if i%100== 0:
            print(i),
    except:
        print('error')

t = datetime.now()
tstr = t.strftime('%Y%m%d')+'_%02d%02d%02d_'% (t.hour, t.minute, t.second)

fpath = r'/Users/dizhu/Dropbox (MIT)/QNN lab/Device testing/20180128_Yi_gauge_field/dual_mod'     
fname = 'f1=6000kHz_f2=6000kHz'
fname_full = os.path.join(fpath, tstr+fname)

data_dict = {channel+'_x':x_list, channel+'_y':y_list}

scipy.io.savemat(fname_full+'.mat', mdict=data_dict)
lecroy.save_screenshot(fname_full+'.png')
print('done')
lecroy.set_trigger_mode('Normal')

########################################################
#Acquire two channel traces
############################################################

#%%

#def my_acquisition_3(DL1 = 0, DL2 = 0, DL3 = 0):
#    """ Sets scope to "single" trigger mode to acquire one trace, then waits until the trigger has happened
#    (indicated by the trigger mode changing to "Stopped").  Returns blank lists if no trigger occurs within 1 second """
#    n = 0; 
#    x1 = np.array([]); y1 = np.array([]);
#    x2 = np.array([]); y2 = np.array([]);
#    x3 = np.array([]); y3 = np.array([]);
#
#
#    lecroy.set_trigger_mode(trigger_mode = 'Single')
#    if lecroy.get_trigger_mode() == 'Single\n':
#        while lecroy.get_trigger_mode() == 'Single\n':
#            #SRS.set_output(False)
#            time.sleep(1e-4)
#            #SRS.set_output(True)
#
#    x1,y1 = lecroy.get_wf_data(channel='C1')
#    x2,y2 = lecroy.get_wf_data(channel='C2')
#    x3,y3 = lecroy.get_wf_data(channel='C3')
#
#    if (max(abs(y1)) > DL1) and (max(abs(y2)) > DL2) and (max(abs(y3)) > DL3):
#
#        C1_x_list.append(x1)
#        C1_y_list.append(y1)
#
#        C2_x_list.append(x2)
#        C2_y_list.append(y2)
#        
#        C3_x_list.append(x3)
#        C3_y_list.append(y3)
#
#        return 0 # a useful sample
#    else:
#        return 1 # not useful, increase the smapling number
#
#
#
#def my_acquisition_2(DL2 = 0, DL3 = 0):
#
#    lecroy.set_trigger_mode('Single')
#
#    x2,y2 = my_get_single_trace('C2')
#    x3,y3 = my_get_single_trace('C3')
#
#    if (max(abs(y2)) > DL2) and (max(abs(y3)) > DL3):
#
#        C2_x_list.append(x2)
#        C2_y_list.append(y2)
#        
#        C3_x_list.append(x3)
#        C3_y_list.append(y3)
#
#        return 0 # a useful sample
#    else:
#        return 1 # not useful, increase the smapling number
#
#
#
##%%
################################################
## sweep currents and save traces
#### Use SRS
#SRS.reset()
#Ib = 22e-6
#SRS.set_voltage(Ib*R_SRS)
#
#SRS.set_output(True)
##gathering three traces
#
#C1_x_list = []
#C1_y_list = []
#C2_x_list = []
#C2_y_list = []
#C3_x_list = []
#C3_y_list = []
#
#samplemax = 50
#dl_c1 = 0.05 #threshold of the diode, unit V
#dl_c2 = 0.05
#dl_c3 = 0.05
#print 'Did you change the Threshold setting?'
#
#for n in range(samplemax):
#    try:
#        aflag = 1
#        while  aflag ==1:
#            aflag = my_acquisition_3(dl_c1,dl_c2,dl_c3)
#            if aflag == 1:
#                print 'not_useful'
#        if n%100== 0:
#            print n,
#    except:
#        print 'error'
#        # n = n - 1
#
#
#myfilename = '-60uA-1550nm-take-traces-longerwindow-3-'
##myfilename = '-IV-nTron_channel'
#
#time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
#path_name = 'C:\\Users\\QNN User\\Zhao\\Year-2016\\02252016-SPE829\\0228\\project_image\\metal-mesh\\'
#myfilename_data = path_name+myfilename +time_str  + '.mat'
#myfilename_traces = path_name+myfilename+'last-all-traces' +time_str  + '.mat'
#myfilename_screenshot = path_name +myfilename +'screenshot'+ time_str + '.png'
#
#data_dict = {'C1_x_list':C1_x_list, 'C1_y_list':C1_y_list,\
#'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list,\
#'C3_x_list':C3_x_list, 'C3_y_list':C3_y_list}
#
#scipy.io.savemat(myfilename_data, mdict=data_dict)
#saveall_traces(myfilename_traces)
#lecroy.save_screenshot(myfilename_screenshot)
#
#
##%%
##gathering two traces
#
#C2_x_list = []
#C2_y_list = []
#C3_x_list = []
#C3_y_list = []
#
#samplemax = 500
#
#dl_c2 = 0.02
#dl_c3 = 0.0
#print 'Did you change the Threshold setting?'
#
#for n in range(samplemax):
#    try: 
#        aflag = 1
#        while  aflag ==1:
#            aflag = my_acquisition_2(dl_c2,dl_c3)
#            if aflag == 1:
#                print 'not_useful'
#        if n%100== 0:
#            print n,
#    except:
#        print 'error'
#        # n = n - 1
#
#
#myfilename = 'P1P6_tapered_det_Ib_22uA'
##myfilename = '-IV-nTron_channel'
#
#time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
#path_name = filedirectry
#myfilename_data = path_name+myfilename +time_str  + '.mat'
#myfilename_traces = path_name+myfilename+'last-all-traces' +time_str  + '.mat'
#myfilename_screenshot = path_name +myfilename +'screenshot'+ time_str + '.png'
#
#data_dict = {'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list,\
#'C3_x_list':C3_x_list, 'C3_y_list':C3_y_list}
#
#scipy.io.savemat(myfilename_data, mdict=data_dict)
#saveall_traces(myfilename_traces)
#lecroy.save_screenshot(myfilename_screenshot)
#
##%%

