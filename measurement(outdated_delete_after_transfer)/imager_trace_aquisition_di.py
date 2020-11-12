
# sweep currents and save traces
### Use SRS
comments = '_Ib=14.5uA_1550-calmar_att=30dB_ext=20dB_zoom_in'
#lecroy.set_trigger(source = 'C2', volt_level = -17e-3, slope = 'negative')
R_SRS = 100e3
current_in = 14.5e-6
SRS.set_voltage(current_in*R_SRS)

SRS.set_output(True)
attenuator.set_attenuation_db(30)
attenuator.set_beam_block(False)
#######################
#gathering three traces


C1_x_list = []
C1_y_list = []
C2_x_list = []
C2_y_list = []
C3_x_list = []
C3_y_list = []


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



samplemax = 10000
dl_c1 = 0.3 #threshold of the diode, unit V
dl_c2 = 0.13
dl_c3 = 0.13
print 'Did you change the Threshold setting?'

for n in range(samplemax):
    try:
        aflag = 1
        while  aflag ==1:
            aflag = my_acquisition_3(dl_c1,dl_c2,dl_c3)
            if aflag == 1:
                print 'not_useful',
        if n%100== 0:
            print n,
    except:
        print 'error'
        SRS.set_output(False)
        sleep(0.5)
        SRS.set_output(True)
        sleep(0.5)
        # n = n - 1

time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
myfilename= filedirectry+test_name 
dataFileName = myfilename+'_'+comments+time_str+'.mat'
traceFileName = myfilename+'-all-trace'+comments+time_str+'.mat'
screenshortFileName = myfilename+comments+time_str+'.png'

data_dict = {'C1_x_list':C1_x_list, 'C1_y_list':C1_y_list,\
'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list,\
'C3_x_list':C3_x_list, 'C3_y_list':C3_y_list}

scipy.io.savemat(dataFileName, mdict=data_dict)
saveall_traces(traceFileName)
lecroy.save_screenshot(screenshortFileName)



#gathering two traces

comments = 'using_1G-amp_Ib=9p5uA_att=10dB_1um_laser_pulse_shape'

R_SRS = 100e3
current_in = 9.5e-6
SRS.set_voltage(current_in*R_SRS)

SRS.set_output(True)
attenuator.set_attenuation_db(10)
attenuator.set_beam_block(False) 

C2_x_list = []
C2_y_list = []
C3_x_list = []
C3_y_list = []

samplemax = 1000

dl_c2 = 0.05
dl_c3 = 0.05
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

time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
myfilename= filedirectry+test_name 
dataFileName = myfilename+'_'+comments+time_str+'.mat'
traceFileName = myfilename+'-all-trace'+comments+time_str+'.mat'
screenshortFileName = myfilename+comments+time_str+'.png'

data_dict = {'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list,\
'C3_x_list':C3_x_list, 'C3_y_list':C3_y_list}

scipy.io.savemat(dataFileName, mdict=data_dict)
saveall_traces(traceFileName)
lecroy.save_screenshot(screenshortFileName)



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


myfilename = 'Ch1_pulse_shape'
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
lecroy.set_horizontal_scale(time_per_div = 5e-9, time_offset = -15e-9);

#####################################################################
###########################################################################
#save all traces
##########################################################################
##################################################################################
#comments = '_jitter_1550-CALMAR_modulated_1MHz_Ib=14p5uA_att=xxdB_single_photon'
comments = '_single_photon_jitter_calmar_1550nm_att=40dB_Ib=14p5uA_'
time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
myfilename= filedirectry+test_name +comments+time_str
dataFileName = myfilename+'.mat'
screenshortFileName = myfilename+'.png'
saveall_traces(dataFileName)
lecroy.save_screenshot(screenshortFileName)

##################################################################
#scan attenuation vs jitter histogram
###################################################################
comments = '_Ib=14p5uA_sweep_att_1550_picoquant_rep=1MHz_'
awg.set_output(True)
awg.set_freq(1000e3)
#time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
time_str='2017-08-01'
#lecroy.set_trigger(source = 'C2', volt_level = -17e-3, slope = 'negative')
current_in = 14.5e-6
SRS.set_voltage(current_in*R_srs)
SRS.set_output(True)

num_of_sampels = 20000
number_of_sweeps = 5
start_number = 0

atts = [2,4,5,7,8,10,11,13,14,16,17,19,20,22,23,25,26,28,29]

time_start = time.time()
for att in atts:
    awg.set_output(True)
    SRS.set_output(True)
    attenuator.set_attenuation_db(att)
    attenuator.set_beam_block(False)
    SRS.set_output(False)
    SRS.set_output(True)
    sleep(2)
    for i in arange(number_of_sweeps):
        print '\n attenuation = '+str(att)+'dB, file number = ' + str(i+start_number) +', time: '+str((time.time()-time_start)/60)+' min'
        lecroy.clear_sweeps()
        lecroy.set_trigger_mode('Normal')
        sleep(2)
        while lecroy.get_num_data_points('P3') < num_of_sampels:
            print lecroy.get_num_data_points('P3'), 
            sleep(5)
            if k.read_voltage()>0.1:
                print 'latched'
                SRS.set_output(False); sleep(0.1); SRS.set_output(True)
        myfilename= filedirectry+test_name +comments+'att='+str(att)+'dB_'+time_str+'_'+str(i+start_number)
        dataFileName = myfilename+'.mat'
        screenshortFileName = myfilename+'.png'
        saveall_traces(dataFileName)
        lecroy.save_screenshot(screenshortFileName)
        sleep(1)
    awg.set_output(False)
    SRS.set_output(False)
    print '\n taking a rest for 5 min'
    sleep(300) #rest for 5 min

    
#stop everything
SRS.set_output(False)
awg.set_output(False)


##################################################################
#scan attenuation vs pulse traces
###################################################################
comments = '_pulse_shapes_Ib=14p5uA_sweep_att_1550_picoquant_rep=1MHz_'
#time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
time_str='2017-08-01'
#lecroy.set_trigger(source = 'C2', volt_level = -17e-3, slope = 'negative')
current_in = 14.5e-6
SRS.set_voltage(current_in*R_srs)
SRS.set_output(True)

num_of_samples = 100
number_of_sweeps = 5
start_number = 0

atts = arange(0,3,3)

for att in atts:
    attenuator.set_attenuation_db(att)
    print 'attenuation = '+str(att)+'dB'
    attenuator.set_beam_block(False)
    SRS.set_output(False)
    SRS.set_output(True)
    sleep(2)
    for i in arange(number_of_sweeps):
        print 'file number = ' + str(i)
        lecroy.clear_sweeps()
        #######################
        #gathering three traces
        C1_x_list = []
        C1_y_list = []
        C2_x_list = []
        C2_y_list = []
        C3_x_list = []
        C3_y_list = []
        
        samplemax = num_of_samples
        dl_c1 = 0.1 #threshold of the diode, unit V
        dl_c2 = 0.1
        dl_c3 = 0.1
        #print 'Did you change the Threshold setting?'
        for n in range(samplemax):
            try:
                aflag = 1
                while  aflag ==1:
                    aflag = my_acquisition_3(dl_c1,dl_c2,dl_c3)
                    if aflag == 1:
                        print 'not_useful'
                        SRS.set_output(False)
                        sleep(0.5)
                        SRS.set_output(True)
                        sleep(0.5)
                if n%200== 0:
                    print n,
            except:
                print 'error'
                SRS.set_output(False)
                sleep(0.5)
                SRS.set_output(True)
                sleep(0.5)
                # n = n - 1
        
        myfilename= filedirectry+test_name +comments+'att='+str(att)+'dB_'+time_str+'_'+str(i+start_number)
        traceFileName = myfilename+'_all_para.mat'
        screenshortFileName = myfilename+'.png'
        
        data_dict = {'C1_x_list':C1_x_list, 'C1_y_list':C1_y_list,\
        'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list,\
        'C3_x_list':C3_x_list, 'C3_y_list':C3_y_list}
        
        scipy.io.savemat(myfilename+'.mat', mdict=data_dict)
        saveall_traces(traceFileName)
        lecroy.save_screenshot(screenshortFileName)
        sleep(1)
    
    
    

comments = '_traces_Ib=15uA_sweep_att_power_1550_picoquant_rep=400kHz_'
time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
#lecroy.set_trigger(source = 'C2', volt_level = -17e-3, slope = 'negative')
current_in = 15e-6
SRS.set_voltage(current_in*R_srs)
SRS.set_output(True)

num_of_sampels = 10000

atts = [0,1,2,3,4,5,20]

for att in atts:
    attenuator.set_attenuation_db(att)
    print 'attenuation = '+str(att)+'dB'
    attenuator.set_beam_block(False)
    SRS.set_output(False)
    SRS.set_output(True)
    sleep(2)
    lecroy.clear_sweeps()
    #lecroy.set_trigger_mode('Normal')
    #######################
    #gathering three traces
    
    C1_x_list = []
    C1_y_list = []
    C2_x_list = []
    C2_y_list = []
    C3_x_list = []
    C3_y_list = []
    
    samplemax = num_of_sampels
    dl_c1 = 0.00 #threshold of the diode, unit V
    dl_c2 = 0.05
    dl_c3 = 0.05
    #print 'Did you change the Threshold setting?'
    for n in range(samplemax):
        try:
            aflag = 1
            while  aflag ==1:
                aflag = my_acquisition_3(dl_c1,dl_c2,dl_c3)
                if aflag == 1:
                    print 'not_useful'
                    SRS.set_output(False)
                    sleep(0.5)
                    SRS.set_output(True)
                    sleep(0.5)
            if n%200== 0:
                print n,
        except:
            print 'error'
            SRS.set_output(False)
            sleep(0.5)
            SRS.set_output(True)
            sleep(0.5)
            # n = n - 1
    
    myfilename= filedirectry+test_name +comments+'att='+str(att)+'dB_'+time_str
    traceFileName = myfilename+'_all_para.mat'
    screenshortFileName = myfilename+'.png'
    
    data_dict = {'C1_x_list':C1_x_list, 'C1_y_list':C1_y_list,\
    'C2_x_list':C2_x_list, 'C2_y_list':C2_y_list,\
    'C3_x_list':C3_x_list, 'C3_y_list':C3_y_list}
    
    scipy.io.savemat(myfilename+'.mat', mdict=data_dict)
    saveall_traces(traceFileName)
    lecroy.save_screenshot(screenshortFileName)
    sleep(1)

#switch off the awg and put scope to stop mode
lecroy.set_trigger_mode('Stop')
awg.set_output(False)
SRS.set_voltage(0)
SRS.set_output(False)




##################################################################
#take measurement for x number of data points
###################################################################
comments = '_Ib=14p5uA_1550_picoquant_500kHz_att=0dB_threshold=72mV_'
#time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
time_str = '2017-06-15'
#lecroy.set_trigger(source = 'C2', volt_level = -17e-3, slope = 'negative')
num_of_sampels = 10000
number_of_sweeps = 20

start_number = 20

#traching number of latching events per sample period. When this is too high, the EOM could have been drifted.
latch_counter = 0

for i in arange(number_of_sweeps):
    #awg.set_output(True)
    attenuator.set_beam_block(False)
    attenuator.set_attenuation_db(0)
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
            
            #let the EMO to take a rest
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
            
            
            
    myfilename= filedirectry+test_name +comments+time_str+'_'+str(i+start_number)
    dataFileName = myfilename+'.mat'
    screenshortFileName = myfilename+'.png'
    saveall_traces(dataFileName)
    lecroy.save_screenshot(screenshortFileName)
    sleep(1)
    #reset latch counter
    latch_counter = 0    


###############################################
#scan Ib vs dark count distribution
##############################################
comments = 'dark_count_scan'

#time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
time_str='08-01-2017'
#lecroy.set_trigger(source = 'C2', volt_level = -17e-3, slope = 'negative')
current_in = arange(14,14.5,0.5)*1e-6
num_of_sampels = 40000

for Ib in current_in:
    #attenuator.set_beam_block(True)
    print 'Ib = '+str(Ib*1e6)+'uA'
    SRS.set_voltage(Ib*R_srs)
    SRS.set_output(False)
    SRS.set_output(True)
    sleep(2)
    lecroy.clear_sweeps()
    lecroy.set_trigger_mode('Normal')
    while lecroy.get_num_data_points('P5') < num_of_sampels:
        print lecroy.get_num_data_points('P5'), 
        sleep(5)
        if k.read_voltage()>0.1:
            print 'latched'
            SRS.set_output(False); sleep(0.1); SRS.set_output(True)
    myfilename= filedirectry+test_name +comments+'Ib='+str(Ib*1e9)+'nA_'+time_str
    dataFileName = myfilename+'.mat'
    screenshortFileName = myfilename+'.png'
    saveall_traces(dataFileName)
    lecroy.save_screenshot(screenshortFileName)
    sleep(1)

