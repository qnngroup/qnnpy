# Ic measurement code
# Run add_path.py first
from measurement.ic_sweep import *
from useful_functions.save_data_vs_param import *

### Experimental variables: Scope/AWG
R = 10e3
vpp = 8
repetition_hz = 200



### Instrument configuration
lecroy_ip = 'touchlab1.mit.edu'
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
freq_gen = Agilent33250a('GPIB0::10')

### Use SRS
SRS = SIM928(2, 'GPIB0::2')
SRS.reset()


#########################################
#########################################

### Initialize instruments
lecroy.reset()
freq_gen.reset()
time.sleep(5)
setup_ic_measurement(lecroy, freq_gen, vpp = vpp, repetition_hz = repetition_hz, trigger_level = 1e-3, trigger_slope = 'Positive')
time.sleep(5)





############### EXPERIMENT SCRIPT
sample_name = 'NWL016D Device D1 nSQUID Nb memory readout'
test_name = 'Hysteresis test alternate polarity'
test_type = 'Ic Sweep vs Write current'

currents = np.linspace(0,800e-6,801)
R_SRS = 10e3
num_sweeps = 200


### Run experiment!
# Turn off current source
# Turn on, go to 1uA (high)
# Record Ic in ic_high_on list -- just to check
# Turn off
# Record Ic ic_high_off list -- will see if trapped any flux by Ic modulation
# Turn on, go to -1uA (low)
# Record Ic in ic_low_on list -- just to check
# Turn off
# Record Ic ic_low_off list -- will see if trapped any flux by Ic modulation
# Repeat with different current value

ic_high_on = []
ic_high_off = []
ic_low_on = []
ic_low_off = []
sleep_delay = 0.1

start_time = time.time()
for n, i in enumerate(currents):
    print '   ---   Time elapsed for measurement %s of %s: %0.2f min    ---   ' % (n, len(currents), (time.time()-start_time)/60.0)
    SRS.set_output(False); time.sleep(sleep_delay)
    SRS.set_voltage(i*R_SRS); time.sleep(sleep_delay)
    SRS.set_output(True); time.sleep(sleep_delay)
    ic_high_on.append( run_ic_sweeps(lecroy, num_sweeps = num_sweeps)/R_SRS )
    SRS.set_output(False); time.sleep(sleep_delay)
    ic_high_off.append( run_ic_sweeps(lecroy, num_sweeps = num_sweeps)/R_SRS )

    SRS.set_output(False); time.sleep(sleep_delay)
    SRS.set_voltage(-10); time.sleep(sleep_delay)
    SRS.set_output(True); time.sleep(sleep_delay)
    ic_low_on.append( run_ic_sweeps(lecroy, num_sweeps = num_sweeps)/R_SRS )
    SRS.set_output(False); time.sleep(sleep_delay)
    ic_low_off.append( run_ic_sweeps(lecroy, num_sweeps = num_sweeps)/R_SRS )


data_dict =  {'ic_high_on': ic_high_on, 'ic_high_off':ic_high_off, 'ic_low_on':ic_low_on, 'ic_low_off':ic_low_off, 'currents': currents}
file_path, file_name = save_data_dict(data_dict = data_dict, test_type = test_type, test_name = sample_name + ' ' + test_name,
                        filedir = '', zip_file=True)



# Plot histogram vs other things in 2D
for ic_data, title_name in zip([ic_high_off, ic_high_on, ic_low_off, ic_low_on], ['Current HIGH (off)', 'Current HIGH (on)', 'Current LOW (off)', 'Current LOW (on)']):
    num_bins = 100
    range_min = 310e-6; #range_min = None
    range_max = 338e-6; #range_max = None

    x_axis = np.array(currents)*1e6
    ic_hist_list, ic_bins = data_list_to_histogram_list(ic_data, num_bins = num_bins, range_min = range_min, range_max = range_max)
    extent = [x_axis[0], x_axis[-1], ic_bins[0]*1e6, ic_bins[-1]*1e6]

    plt.imshow(np.flipud(np.transpose(ic_hist_list)), extent=extent, aspect = 'auto')
    plt.title(sample_name + '\n' + test_name + '\n' + title_name)
    plt.ylabel('Ic distribution values (uA)'); plt.xlabel('Gate current (uA)')
    plt.savefig(file_name + ' ' + title_name + 'min')
    plt.show()


['ic_low_on', 'ic_high_off', 'ic_high_on', 'currents', 'ic_low_off']
ic_low_on = data['ic_low_on']
ic_high_off = data['ic_high_off']
ic_high_on = data['ic_high_on']
ic_low_off = data['ic_low_off']
currents = data['currents']