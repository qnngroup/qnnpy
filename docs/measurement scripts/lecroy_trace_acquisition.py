#%%
import sys
import os

#snspd_measurement_code_dir = r'/Users/dizhu/Dropbox (MIT)/QNN lab/Device testing/snspd_measurement_python_code'
snspd_measurement_code_dir =  r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\snspd-measurement-code'
dir1 = os.path.join(snspd_measurement_code_dir,'instruments')
dir2 = os.path.join(snspd_measurement_code_dir,'useful_functions')
dir3 = os.path.join(snspd_measurement_code_dir,'measurement')

if snspd_measurement_code_dir not in sys.path:
    sys.path.append(snspd_measurement_code_dir)
    sys.path.append(dir1)
    sys.path.append(dir2)
    sys.path.append(dir3)

#import library
from lecroy_620zi import LeCroy620Zi
import visa
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
from datetime import datetime
import scipy
import pyvisa
#########################################
### Connect to instruments
#########################################



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
from Lakeshore350 import Lakeshore350
from datetime import datetime
import datetime as datetime
from lecroy_620zi import *
import scipy.io as sio
import os
from srs_sim928 import *

# #%%

#%%
# lecroy_ip = 'QNN-SCOPE1.MIT.EDU'
lecroy_ip = '18.25.22.73'

lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)


#lecroy_ip = 'QNN-SCOPE1.MIT.EDU'
#lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
# counter = Agilent53131a('GPIB0::4')
# counter.basic_setup()
#cryocon = Cryocon34('GPIB0::5')
# attenuator = JDSHA9('GPIB0::7')
#attenuator = FVA3100('GPIB0::10'); attenuator.set_beam_block(True)
SRS = SIM928('GPIB0::1', 4); SRS.reset()
#initiate the power meter
# pm = ThorlabsPM100Meta('USB0::0x1313::0x8078::P0001093::INSTR')
k = Keithley2700("GPIB0::18"); k.reset()

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

def my_get_single_trace_sequence(channel = 'C1',NumSegments= 1000):
    """ Sets scope to "single" trigger mode to acquire one trace, then waits until the trigger has happened
    (indicated by the trigger mode changing to "Stopped").  """
    lecroy.set_sequence_mode()
    lecroy.set_segments(NumSegments)
    lecroy.set_trigger_mode(trigger_mode = 'Single')
    if lecroy.get_trigger_mode() == 'Single\n':
        while lecroy.get_trigger_mode() == 'Single\n':
            #SRS.set_output(False)
            sleep(1e-4)
            #SRS.set_output(True)
    x,y = lecroy.get_wf_data(channel=channel)
    interval=abs(x[0]-x[1])
    xlist=[]
    ylist=[]
    totdp=np.int(np.size(x)/NumSegments)
    for j in range(NumSegments):
        
        xlist.append(x[0+j*totdp:totdp+j*totdp]-totdp*interval*j)
        ylist.append(y[0+j*totdp:totdp+j*totdp])
    return xlist,ylist
    
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
    t = datetime.datetime.now()
    tstr = t.strftime('%Y%m%d')+'_%02d%02d%02d_'% (t.hour, t.minute, t.second)
    #save matlab file
    ffull = os.path.join(fpath, tstr+fname)
    scipy.io.savemat(ffull, mdict=data_dict)
    #save screen shot
    scname = os.path.join(fpath, tstr+fname.split('.')[0]+'.png')
    lecroy.save_screenshot(scname)
            
def save_traces_multiple_sequence(channels = ['C1', 'C2'], num_traces = 20, NumSegments = 1000, threshold = [0,0], fpath='', fname='myfile'):
    """save multiple traces multiple times, threshold is set for each channel to eliminate false counts (set to )
    0 if unused"""
    num_ch = len(channels)
    x1list = []; y1list = []
    x2list = []; y2list = []
    x3list = []; y3list = []
    x4list = []; y4list = []
    q = 0 #number of not useless points
    for i in range(num_traces):
        print('Trace %d of %d' % (i, num_traces))
        try:
            if num_ch>0:
                x,y = my_get_single_trace_sequence(channels[0],NumSegments)
                if max(abs(y[0]))>threshold[0]:
                    x1list.append(x)
                    y1list.append(y)
                else:
                    q = q+1
                    print('Not useful')
            if num_ch>1:
                x,y = my_get_single_trace_sequence(channels[1],NumSegments)
                if max(abs(y[0]))>threshold[1]:
                    x2list.append(x)
                    y2list.append(y)
                else:
                    q = q+1
                    print('Not useful')
            if num_ch>2:
                x,y = my_get_single_trace_sequence(channels[2],NumSegments)
                if max(abs(y[0]))>threshold[2]:
                    x3list.append(x)
                    y3list.append(y)
                else:
                    q = q+1
                    print('Not useful')
            if num_ch>3:
                x,y = my_get_single_trace_sequence(channels[3],NumSegments)
                if max(abs(y[0]))>threshold[3]:
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
        x1list=np.reshape(x1list, (len(x1list)*len(x1list[0]),len(x1list[0][0])))
        y1list=np.reshape(y1list, (len(y1list)*len(y1list[0]),len(y1list[0][0])))
        data_dict[channels[0]+'x']=x1list
        data_dict[channels[0]+'y']=y1list
    if num_ch>1:
        x2list=np.reshape(x2list, (len(x2list)*len(x2list[0]),len(x2list[0][0])))
        y2list=np.reshape(y2list, (len(y2list)*len(y2list[0]),len(y2list[0][0])))
        data_dict[channels[1]+'x']=x2list
        data_dict[channels[1]+'y']=y2list
    if num_ch>2:
        x3list=np.reshape(x3list, (len(x3list)*len(x3list[0]),len(x3list[0][0])))
        y3list=np.reshape(y3list, (len(y3list)*len(y3list[0]),len(y3list[0][0])))
        data_dict[channels[2]+'x']=x3list
        data_dict[channels[2]+'y']=y3list
    if num_ch>3:
        x4list=np.reshape(x4list, (len(x4list)*len(x4list[0]),len(x4list[0][0])))
        y4list=np.reshape(y4list, (len(y4list)*len(y4list[0]),len(y4list[0][0])))
        data_dict[channels[3]+'x']=x4list
        data_dict[channels[3]+'y']=y4list
    
    if '.' in fname:
        if fname.split('.')[1] != 'mat':
            print('file extension error') 
    else:
        fname = fname+'.mat'
    #add time to the file name
    t = datetime.datetime.now()
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

fpath = r'S:\SC\Measurements\SPG667\snspd\P1\jitter'

#%%
R_srs = 100e3

Isource_max =9.4e-6
step = 0.2e-6
#here we go
Isource = np.arange(9e-6, Isource_max, step)

V_source = Isource*R_srs


SRS.set_voltage(0)
SRS.set_output(True)
k.read_voltage()
sleep(1)

for v in V_source:
    SRS.set_voltage(v)
    sleep(0.1)
    fname = '1550nm_jitter_'+str(int(v*100))
    save_traces_multiple(channels = ['C2','C3'],num_traces = 50000 , fname = fname, fpath = fpath)



# save_traces(channels = ['C2','C3', 'C3', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10'], fname = fname, fpath = fpath)
# save_traces_multiple_sequence(channels = ['C2','C3'],num_traces = 100 , NumSegments=500, fname = fname, fpath = fpath)
# ave_traces_multiple(channels = ['C2', 'C3'], num_traces = 1000, threshold = [0, 0, 0], fpath=fpath, fname=fname)

# lecroy.set_trigger_mode('Stop')

#%%
#save pulse shapes
fname ='pulse_shape_30dB'
save_traces_multiple(channels = ['C1', 'C2', 'C3'], num_traces = 1000, threshold = [0, 0, 0], fpath=fpath, fname=fname)
  
#%%
#save jitter
num_samples = 5e4
while lecroy.get_num_data_points('P1') < num_samples:
    print lecroy.get_num_data_points('P1'), 
    sleep(5)
    if k.read_voltage()>0.5:
        print 'latched'
        SRS.set_output(False); sleep(0.1); SRS.set_output(True)
        
fname = fname = 'jitter_lmd=1550_att=0dB_Ib=22uA_10x10_taper_C2-P2_C3-P5_1Gamp'
save_traces(channels = ['C1','C2', 'C3', 'F1', 'F2', 'F3', 'F4', 'F5', 'F5','F6','F7', 'F8'], fname = fname, fpath = fpath)


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

