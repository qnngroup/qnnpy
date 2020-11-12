# Ic measurement code
# Run add_path.py first
from measurement.ic_sweep import *
from useful_functions.save_data_vs_param import *


### Experimental variables: Scope/AWG
R = 10e3
vpp = 10
repetition_hz = 200


### Instrument configuration
lecroy_ip = 'touchlab1.mit.edu'
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
freq_gen = Agilent33250a('GPIB0::10')

#########################################
# ######## Choose current source ########
#########################################

### Use Keithley
# k = Keithley2400('GPIB0::14')
# k.reset()
# k.setup_2W_source_I_read_V()
# time.sleep(1)
# use_keithley = True

### Use SRS
SRS = SIM928(2, 'GPIB0::2')
SRS.reset()
R_gate = 100e3
use_keithley = False


#########################################
### Initialize instruments
#########################################

lecroy.reset()
freq_gen.reset()
time.sleep(5)
setup_ic_measurement(lecroy, freq_gen, vpp = vpp, repetition_hz = repetition_hz, trigger_level = 1e-3, trigger_slope = 'Positive')
time.sleep(5)


#########################################
######    Quick Ic Test  ####
#########################################


### Quick Ic Test
num_sweeps = 500
voltage_data = run_ic_sweeps(lecroy, num_sweeps = num_sweeps)
ic_data = voltage_data/R
print 'Median Ic = %0.2f uA / Std. dev Ic = %0.2f uA' % (np.median(ic_data*1e6), np.std(ic_data*1e6)) + \
        ' [Ramp rate of %0.3f A/s (Vpp = %s V, rate = %s Hz, R = %s kOhms)]' \
            % (calc_ramp_rate(vpp, R, repetition_hz, 'SINE'), vpp, repetition_hz, R/1e3)






############### EXPERIMENT SCRIPT
sample_name = 'NWL016F D2cd nMEM structures'
test_name = 'Fine sweep'
test_type = 'Ic Sweep vs Write current'

### Experimental variables: about 4 tests/min for 1000 sweeps
# currents = np.arange(0e-6, 45e-6, 1000e-9)
# currents = np.linspace(-.5, .5, 151)
currents = np.linspace(-200e-6,200e-6,401)
# currents[::10] =  currents[::10] + .1
# currents[0] = 1
# currents = np.concatenate([currents, currents[::-1]])
# currents = np.concatenate([currents, currents[::-1]])
num_sweeps = 100


### Run experiment!
ic_data_list = []
I_list = []
start_time = time.time()
if use_keithley is True: k.set_output(True)
if use_keithley is False: SRS.set_output(True)
for n in range(len(currents)):
    print '   ---   Time elapsed for measurement %s of %s: %0.2f min    ---   ' % (n, len(currents), (time.time()-start_time)/60.0)

    if use_keithley is True: k.set_current(currents[n]); v,i = k.read_voltage_and_current()
    if use_keithley is False: i = currents[n]; SRS.set_voltage(np.sign(i)*1e-3); time.sleep(0.05); SRS.set_voltage(i*R_gate); time.sleep(0.05)

    voltage_data = run_ic_sweeps(lecroy, num_sweeps = num_sweeps)
    ic_data = voltage_data/R
    ic_data_list.append(ic_data.tolist())
    I_list.append(i)
    print 'Current value %0.2f uA  -  Median Ic = %0.2f uA / Std. dev Ic = %0.2f uA' % (i*1e6, np.median(ic_data*1e6), np.std(ic_data*1e6))
if use_keithley is True: k.set_current(0); k.set_output(False)
if use_keithley is False: SRS.set_output(False)


file_path, file_name = save_x_vs_param(ic_data_list,  I_list, xname = 'ic_data',  pname = 'currents',
                        test_type = test_type, test_name = sample_name + ' ' + test_name,
                        comments = '', filedir = '', zip_file=True)





# Plot histogram vs other things in 2D
num_bins = 100
range_min = 75e-6; # range_min = None
ic_data_list_toplot = np.array(ic_data_list)

# Take ic values and subtract off current (in case they're directly added)
# ic_data_list_toplot += np.transpose(np.tile(currents, [ic_data_list_toplot.shape[1],1]))

x_axis = np.array(currents)*1e6
ic_hist_list, ic_bins = data_list_to_histogram_list(ic_data_list_toplot, num_bins = num_bins, range_min = range_min)
extent = [x_axis[0], x_axis[-1], ic_bins[0]*1e6, ic_bins[-1]*1e6]

plt.imshow(np.flipud(np.transpose(ic_hist_list)), extent=extent, aspect = 'auto')
plt.title(sample_name + '\n' + test_name)
plt.ylabel('Ic distribution values (uA)'); plt.xlabel('Write port current (uA)')
plt.savefig(file_name)
plt.show()




# Two subplots: (1) histogram vs run # and (2) solenoid value vs run #
# num_bins = 100
# range_min = 140e-6 ; range_min = None

# ic_hist_list, ic_bins = data_list_to_histogram_list(ic_data_list, num_bins = num_bins, range_min = range_min)

# extent = [0, len(I_list), ic_bins[0]*1e6, ic_bins[-1]*1e6]

# f, (ax1, ax2) = plt.subplots(2)

# ax1.imshow(np.flipud(np.transpose(ic_hist_list)), extent=extent, aspect = 'auto')
# ax1.set_ylabel('Ic distribution values (uA)'); ax1.set_xlabel('Histogram/Run #')
# ax2.plot(np.array(I_list)*1e3,'o-')
# ax2.set_xlim((0, len(I_list)))
# ax2.set_ylabel('Write current (mA)'); ax2.set_xlabel('Histogram/Run #')
# #plt.savefig(file_name)
# plt.show()
