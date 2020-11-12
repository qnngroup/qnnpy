#%%
snspd_traces_x_list = []
snspd_traces_y_list = []
pd_traces_x_list = []
pd_traces_y_list = []
time_start = time.time()

def saveall_traces(file_path = 'myfilename.mat'):

    lecroy.set_trigger_mode('Stop')
    time.sleep(0.1)

    x1,y1 = lecroy.get_wf_data('C1')
    x2,y2 = lecroy.get_wf_data('C2')
    x3,y3 = lecroy.get_wf_data('C3')
    x4,y4 = lecroy.get_wf_data('C4')

    f1x,f1y = lecroy.get_wf_data('F1')
    f2x,f2y = lecroy.get_wf_data('F2')
    f3x,f3y = lecroy.get_wf_data('F3')
    f4x,f4y = lecroy.get_wf_data('F4')

    #data_dict = {'x2' : x2, 'y2' : y2, 'x3' : x3, 'y3' : y3,'f1x' : f1x, 'f1y' : f1y}
    data_dict = {'x1' : x1, 'y1' : y1,'x2' : x2, 'y2' : y2, 'x3' : x3, 'y3' : y3,'x4' : x4, 'y4' : y4,\
    'f1x' : f1x, 'f1y' : f1y,'f2x' : f2x, 'f2y' : f2y,'f3x' : f3x, 'f3y' : f3y,'f4x' : f4x, 'f4y' : f4y  }
    #data_dict = {'x1' : x1, 'y1' : y1, 'x2' : x2, 'y2' : y2, 'x3' : x3, 'y3' : y3 , 'x4' : x4, 'y4' : y4}
    #data_dict = {'x1' : x1, 'y1' : y1, 'x2' : x2, 'y2' : y2, 'x3' : x3, 'y3' : y3 , 'x4' : x4, 'y4' : y4,'f1x' : f1x, 'f1y' : f1y, 'f2x' : f2x, 'f2y' : f2y}
    scipy.io.savemat(file_path, mdict=data_dict)

    lecroy.set_trigger_mode('Stop')


def my_get_single_trace(channel = 'C1'):
    """ Sets scope to "single" trigger mode to acquire one trace, then waits until the trigger has happened
    (indicated by the trigger mode changing to "Stopped").  Returns blank lists if no trigger occurs within 1 second """
    n = 0; x = np.array([]); y = np.array([])
    lecroy.set_trigger_mode(trigger_mode = 'Single')
    if lecroy.get_trigger_mode() == 'Single\n':
        while lecroy.get_trigger_mode() == 'Single\n':
            #SRS.set_output(False)
            time.sleep(1e-4)
            #SRS.set_output(True)
    x,y = lecroy.get_wf_data(channel=channel)
    return x,y


def my_acquisition_3(DL1 = 0, DL2 = 0, DL3 = 0):
    """ Sets scope to "single" trigger mode to acquire one trace, then waits until the trigger has happened
    (indicated by the trigger mode changing to "Stopped").  Returns blank lists if no trigger occurs within 1 second """
    n = 0; 
    x1 = np.array([]); y1 = np.array([]);
    x2 = np.array([]); y2 = np.array([]);
    x3 = np.array([]); y3 = np.array([]);


    lecroy.set_trigger_mode(trigger_mode = 'Single')
    if lecroy.get_trigger_mode() == 'Single\n':
        while lecroy.get_trigger_mode() == 'Single\n':
            #SRS.set_output(False)
            time.sleep(1e-4)
            #SRS.set_output(True)

    x1,y1 = lecroy.get_wf_data(channel='C1')
    x2,y2 = lecroy.get_wf_data(channel='C2')
    x3,y3 = lecroy.get_wf_data(channel='C3')

    if (max(abs(y1)) > DL1) and (max(abs(y2)) > DL2) and (max(abs(y3)) > DL3):

        C1_x_list.append(x1)
        C1_y_list.append(y1)

        C2_x_list.append(x2)
        C2_y_list.append(y2)
        
        C3_x_list.append(x3)
        C3_y_list.append(y3)

        return 0 # a useful sample
    else:
        return 1 # not useful, increase the smapling number



def my_acquisition_2(DL2 = 0, DL3 = 0):

    lecroy.set_trigger_mode('Single')

    x2,y2 = my_get_single_trace('C2')
    x3,y3 = my_get_single_trace('C3')

    if (max(abs(y2)) > DL2) and (max(abs(y3)) > DL3):

        C2_x_list.append(x2)
        C2_y_list.append(y2)
        
        C3_x_list.append(x3)
        C3_y_list.append(y3)

        return 0 # a useful sample
    else:
        return 1 # not useful, increase the smapling number



#%%
###############################################
# sweep currents and save traces
### Use SRS
SRS.reset()
Ib = 22e-6
SRS.set_voltage(Ib*R_SRS)

SRS.set_output(True)
#gathering three traces

C1_x_list = []
C1_y_list = []
C2_x_list = []
C2_y_list = []
C3_x_list = []
C3_y_list = []

samplemax = 50
dl_c1 = 0.05 #threshold of the diode, unit V
dl_c2 = 0.05
dl_c3 = 0.05
print 'Did you change the Threshold setting?'

for n in range(samplemax):
    try:
        aflag = 1
        while  aflag ==1:
            aflag = my_acquisition_3(dl_c1,dl_c2,dl_c3)
            if aflag == 1:
                print 'not_useful'
        if n%100== 0:
            print n,
    except:
        print 'error'
        # n = n - 1


myfilename = '-60uA-1550nm-take-traces-longerwindow-3-'
#myfilename = '-IV-nTron_channel'

time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
path_name = 'C:\\Users\\QNN User\\Zhao\\Year-2016\\02252016-SPE829\\0228\\project_image\\metal-mesh\\'
myfilename_data = path_name+myfilename +time_str  + '.mat'
myfilename_traces = path_name+myfilename+'last-all-traces' +time_str  + '.mat'
myfilename_screenshot = path_name +myfilename +'screenshot'+ time_str + '.png'

data_dict = {'C1_x_list':C1_x_list, 'C1_y_list':C1_y_list,\
'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list,\
'C3_x_list':C3_x_list, 'C3_y_list':C3_y_list}

scipy.io.savemat(myfilename_data, mdict=data_dict)
saveall_traces(myfilename_traces)
lecroy.save_screenshot(myfilename_screenshot)


#%%
#gathering two traces

C2_x_list = []
C2_y_list = []
C3_x_list = []
C3_y_list = []

samplemax = 500

dl_c2 = 0.02
dl_c3 = 0.0
print 'Did you change the Threshold setting?'

for n in range(samplemax):
    try: 
        aflag = 1
        while  aflag ==1:
            aflag = my_acquisition_2(dl_c2,dl_c3)
            if aflag == 1:
                print 'not_useful'
        if n%100== 0:
            print n,
    except:
        print 'error'
        # n = n - 1


myfilename = 'P1P6_tapered_det_Ib_22uA'
#myfilename = '-IV-nTron_channel'

time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
path_name = filedirectry
myfilename_data = path_name+myfilename +time_str  + '.mat'
myfilename_traces = path_name+myfilename+'last-all-traces' +time_str  + '.mat'
myfilename_screenshot = path_name +myfilename +'screenshot'+ time_str + '.png'

data_dict = {'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list,\
'C3_x_list':C3_x_list, 'C3_y_list':C3_y_list}

scipy.io.savemat(myfilename_data, mdict=data_dict)
saveall_traces(myfilename_traces)
lecroy.save_screenshot(myfilename_screenshot)

#%%
###############################################
#Single channel  traces
##############################################
C2_x_list = []
C2_y_list = []

samplemax = 500

dl_c2 = 0.025
print 'Did you change the Threshold setting?'


for n in range(samplemax):
    try: 
        lecroy.set_trigger_mode('Single')
        x2,y2 = my_get_single_trace('C2')
        if (max(abs(y2)) > dl_c2):
            C2_x_list.append(x2)
            C2_y_list.append(y2)
        else:
            print 'not_useful'
        
        if n%100== 0:
            print n,
    except:
        print 'error'
        # n = n - 1


myfilename = 'P3_pulse_shape_Mitq_amp'
#myfilename = '-IV-nTron_channel'

time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
path_name = filedirectry
myfilename_data = path_name+myfilename +time_str  + '.mat'
myfilename_traces = path_name+myfilename+'last-all-traces' +time_str  + '.mat'
myfilename_screenshot = path_name +myfilename +'screenshot'+ time_str + '.png'

data_dict = {'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list}

scipy.io.savemat(myfilename_data, mdict=data_dict)
saveall_traces(myfilename_traces)
lecroy.save_screenshot(myfilename_screenshot)

#############################################################

#%%
#save all traces
def saveall_traces(file_path = 'myfilename.mat'):

    lecroy.set_trigger_mode('Stop')
    time.sleep(0.1)

    x1,y1 = lecroy.get_wf_data('C1')
    x2,y2 = lecroy.get_wf_data('C2')
    x3,y3 = lecroy.get_wf_data('C3')
    x4,y4 = lecroy.get_wf_data('C4')

    f4x,f4y = lecroy.get_wf_data('F4')
    f5x,f5y = lecroy.get_wf_data('F5')
    f6x,f6y = lecroy.get_wf_data('F6')
    f7x,f7y = lecroy.get_wf_data('F7')

    #data_dict = {'x2' : x2, 'y2' : y2, 'x3' : x3, 'y3' : y3,'f1x' : f1x, 'f1y' : f1y}
    data_dict = {'x1' : x1, 'y1' : y1,'x2' : x2, 'y2' : y2, 'x3' : x3, 'y3' : y3,'x4' : x4, 'y4' : y4,\
    'f4x' : f4x, 'f4y' : f4y,'f5x' : f5x, 'f5y' : f5y,'f6x' : f6x, 'f6y' : f6y,'f7x' : f7x, 'f7y' : f7y  }
    #data_dict = {'x1' : x1, 'y1' : y1, 'x2' : x2, 'y2' : y2, 'x3' : x3, 'y3' : y3 , 'x4' : x4, 'y4' : y4}
    #data_dict = {'x1' : x1, 'y1' : y1, 'x2' : x2, 'y2' : y2, 'x3' : x3, 'y3' : y3 , 'x4' : x4, 'y4' : y4,'f1x' : f1x, 'f1y' : f1y, 'f2x' : f2x, 'f2y' : f2y}
    scipy.io.savemat(file_path, mdict=data_dict)

    lecroy.set_trigger_mode('Stop')
    
myfilename = 'P1P6_3by3_w_taper_1064nm_30dB_att_Ib=22uA_'
time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
path_name = filedirectry
myfilename_data = path_name+myfilename +time_str  + '.mat'
myfilename_traces = path_name+myfilename+'last-all-traces' +time_str  + '.mat'
myfilename_screenshot = path_name +myfilename +'screenshot'+ time_str + '.png'

saveall_traces(myfilename_traces)
lecroy.save_screenshot(myfilename_screenshot)

