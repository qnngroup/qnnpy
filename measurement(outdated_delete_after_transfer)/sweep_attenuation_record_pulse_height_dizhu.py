"""
Created on Mon Sep 17 17:10:26 2018

@author: Di Zhu 
@ this code is for testing tapered PNR detectors.
"""
#%%
#sweeping the attenuation and take histogram of the pulse heights

#atts = np.arange(0, 33, 3)

atts = [10]

num_of_samples = 500e3

SRS.set_voltage(3.0)

for att in atts:
    latch_counter = 0
    attenuator.set_attenuation_db(att)
    attenuator.set_beam_block(False)
    SRS.set_output(False)
    sleep(1)
    SRS.set_output(True)
    lecroy.clear_sweeps()
    lecroy.set_trigger_mode('Normal')
    print('\n attenuation: {:d} dB'.format(att))
    while lecroy.get_num_data_points('P10')<num_of_samples:
        print('{:d}'.format(lecroy.get_num_data_points('P10'))),
        sleep(10)
        if k.read_voltage()>.1:
            print('latched, latch counter:{:d}'.format(latch_counter)),
            latch_counter = latch_counter+1
            SRS.set_voltage(0.0); sleep(.1); SRS.set_output(False); sleep(.1); SRS.set_output(True)
    fname = 'hist_PNRv1-b-P5_att={:d}dB_T=1p1_Ib=30uA'.format(att)
    save_traces(channels = ['C2', 'F1'], fname = fname, fpath = fpath)
    lecroy.set_trigger_mode('Stop')
            
#%%

atts = np.arange(0, 33, 3)

num_of_samples = 300e3

SRS.set_voltage(2.75)
for att in atts:
    latch_counter = 0
    attenuator.set_attenuation_db(att)
    SRS.set_output(False)
    sleep(1)
    SRS.set_output(True)
    lecroy.clear_sweeps()
    lecroy.set_trigger_mode('Normal')
    print('\n attenuation: {:d} dB'.format(att))
    while lecroy.get_num_data_points('P10')<num_of_samples:
        print('{:d}'.format(lecroy.get_num_data_points('P10'))),
        sleep(10)
        if k.read_voltage()>.1:
            print('latched, latch counter:{:d}'.format(latch_counter)),
            latch_counter = latch_counter+1
            SRS.set_voltage(0.0); sleep(.1); SRS.set_output(False); sleep(.1); SRS.set_output(True)
    fname = 'hist_PNRv1-b-P5_att={:d}dB_T=1p1_Ib=27p5uA'.format(att)
    save_traces(channels = ['C2', 'F1'], fname = fname, fpath = fpath)
    lecroy.set_trigger_mode('Stop')

SRS.set_output(False)   



#%%
#map dark count

num_of_samples = 10e3

SRS.set_voltage(3.0)

for att in atts:
    latch_counter = 0
    attenuator.set_attenuation_db(30)
    attenuator.set_beam_block(True)
    SRS.set_output(False)
    sleep(1)
    SRS.set_output(True)
    lecroy.clear_sweeps()
    lecroy.set_trigger_mode('Normal')
    print('\n attenuation: {:d} dB'.format(att))
    while lecroy.get_num_data_points('P10')<num_of_samples:
        print('{:d}'.format(lecroy.get_num_data_points('P10'))),
        sleep(10)
        if k.read_voltage()>.1:
            print('latched, latch counter:{:d}'.format(latch_counter)),
            latch_counter = latch_counter+1
            SRS.set_output(False); sleep(.1); SRS.set_output(True)
    fname = 'hist_PNRv1-b-P5_dark_count_T=1p1_Ib=30uA'.format(att)
    save_traces(channels = ['C2', 'F1'], fname = fname, fpath = fpath)
    lecroy.set_trigger_mode('Stop')         

#%%
#sweep counting probability to extract mean photon number

atts = np.arange(20, 30, 1)

num_of_samples = 1e3

photon_count = []
optical_pulse = []

SRS.set_voltage(3)


for att in atts:
    latch_counter = 0
    attenuator.set_attenuation_db(att)
    SRS.set_output(False)
    sleep(1)
    SRS.set_output(True)
    lecroy.clear_sweeps()
    lecroy.set_trigger_mode('Normal')
    print('\n attenuation: {:d} dB'.format(att))
    while lecroy.get_num_data_points('P6')<num_of_samples:
        print('{:d}'.format(lecroy.get_num_data_points('P6'))),
        sleep(10)
        if k.read_voltage()>.1:
            print('latched, latch counter:{:d}'.format(latch_counter)),
            latch_counter = latch_counter+1
            SRS.set_output(False); sleep(.1); SRS.set_output(True)
    lecroy.set_trigger_mode('Stop')      
    optical_pulse.append(lecroy.get_num_data_points('P7'))
    photon_count.append(lecroy.get_num_data_points('P6'))
    

fname = 'counting_probability_PNRv1-b-P2_T=1p1_Ib=30uA_20-27dB'

data_dict = {'atts': atts, 'photon_count':photon_count, 'optical_pulse':optical_pulse}
file_path, file_name  = save_data_dict(data_dict, test_type = '', test_name = fname,
                        filedir = filedirectry)
    
    
        
