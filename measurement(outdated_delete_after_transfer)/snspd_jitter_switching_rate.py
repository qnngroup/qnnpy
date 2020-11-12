# Ic measurement code
# Run add_path.py first
from measurement.ic_sweep import *
from useful_functions.save_data_vs_param import *
from agilent_53131a import Agilent53131a
from jds_ha9 import JDSHA9



#########################################
### Sample information
#########################################
sample_name = 'FIW007A2 Device 2D'
test_name = 'Switching rate'



#########################################
### Connect to instruments
#########################################

lecroy_ip = 'touchlab1.mit.edu'; lecroy_ip = '18.62.30.63' 
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
freq_gen = Agilent33250a('GPIB0::10')
counter = Agilent53131a('GPIB0::3')
counter.basic_setup()
att = JDSHA9('GPIB0::5')
SRS = SIM928(4, 'GPIB0::4'); SRS.reset()
R_srs = 100e3



#########################################
### Setup Ic measurement
#########################################
R_awg = 10e3
vpp = 2
repetition_hz = 200

lecroy.reset()
freq_gen.reset()
time.sleep(5)
setup_ic_measurement(lecroy, freq_gen, vpp = vpp, repetition_hz = repetition_hz, trigger_level = 1e-3, trigger_slope = 'Positive')
time.sleep(5)




#########################################
######    Quick Ic Test  
#########################################

num_sweeps = 500
voltage_data = run_ic_sweeps(lecroy, num_sweeps = num_sweeps)
ic_data = voltage_data/R
print 'Median Ic = %0.2f uA / Std. dev Ic = %0.2f uA' % (np.median(ic_data*1e6), np.std(ic_data*1e6)) + \
        ' [Ramp rate of %0.3f A/s (Vpp = %s V, rate = %s Hz, R = %s kOhms)]' \
            % (calc_ramp_rate(vpp, R, repetition_hz, 'SINE'), vpp, repetition_hz, R/1e3)



#########################################
######    Measure Ic sweep distributions
#########################################

Hz = [100,200,400,800,1600]
num_sweeps = 1e5

ic_data_list = []
for h in Hz:
    freq_gen.set_freq(h)
    voltage_data = run_ic_sweeps(lecroy, num_sweeps = num_sweeps)
    ic_data = voltage_data/R
    ic_data_list.append(voltage_data/R_awg)
    print 'Median Ic = %0.2f uA / Std. dev Ic = %0.2f uA' % (np.median(ic_data*1e6), np.std(ic_data*1e6)) + \
        ' [Ramp rate of %0.3f A/s (Vpp = %s V, rate = %s Hz, R = %s kOhms)]' \
            % (calc_ramp_rate(vpp, R, h, 'SINE'), vpp, h, R/1e3)

file_path, file_name = save_x_vs_param(ic_data_list,  ampspersec, xname = 'ic_data',  pname = 'ampspersec',
                        test_type = 'Ic sweep distribution', test_name = sample_name,
                        comments = '', filedir = '', zip_file=True)




#########################################
### Setup counter
#########################################

### Scan counter trigger levels - Make sure trigger voltage is well above noise level
# trigger_v, count_rate = counter.scan_trigger_voltage([-0.5,0.5], counting_time=0.1, num_pts=200)
# plt.plot(trigger_v, np.log10(count_rate))
# plt.show()

# Next, use the above information to set the counter trigger level
counter.set_trigger(-0.6)




#####################################################################
### Measure and plot dark count rate curve + laser count rate curve
#####################################################################

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


currents = np.linspace(0e-6, 25e-6, 251)
counting_time = .5
# With laser off, measure dark count rate curve (DCR)
att.set_beam_block(True)
DCR = count_rate_curve(currents, counting_time = 0.5)
# Turn on laser, measure laser count curve (LCR)
att.set_beam_block(False)
LCR = count_rate_curve(currents, counting_time = 0.5)


data_dict = {'LCR':LCR, 'DCR':DCR, 'currents':currents}
file_path, file_name  = save_data_dict(data_dict, test_type = 'DCR and LCR', test_name = sample_name,
                        filedir = '', zip_file=True)


plt.semilogy(1e6*currents, LCR, 'o', label='Laser count rate (LCR)')
plt.semilogy(1e6*currents, DCR, 'o', label='Dark count rate (DCR)')
plt.semilogy(1e6*currents, LCR-DCR, 'o', label='LCR - DCR')
plt.legend(loc='upper left')
plt.xlabel('Bias current (uA)'); plt.ylabel('Counts (Hz)'); plt.title('Counts vs Bias\n' + sample_name)
plt.savefig(file_name + '.png')
plt.show()



#########################################
### Setup jitter measurement
#########################################

trigger_level = -200e-3

lecroy.reset()
SRS.set_output(True)
SRS.set_voltage(15e-6*R_srs)
time.sleep(5)

lecroy.set_display_gridmode(gridmode = 'Single')
lecroy.set_coupling(channel = 'C1', coupling = 'DC50')
lecroy.label_channel(channel = 'C1', label = 'SNSPD trace')
lecroy.label_channel(channel = 'C4', label = 'Photodiode reference')
lecroy.view_channel(channel = 'C1', view = True)
lecroy.view_channel(channel = 'C2', view = False)
lecroy.view_channel(channel = 'C3', view = False)
lecroy.view_channel(channel = 'C4', view = True)

lecroy.set_vertical_scale(channel = 'C1', volts_per_div = 500e-3, volt_offset = 0)
lecroy.set_vertical_scale(channel = 'C4', volts_per_div = 1, volt_offset = 0)
lecroy.set_horizontal_scale(time_per_div = 100e-9, time_offset = 0)

lecroy.set_trigger(source = 'C1', volt_level = trigger_level, slope = 'Negative')
lecroy.set_trigger_mode(trigger_mode = 'Normal')
lecroy.set_parameter(parameter = 'P1', param_engine = 'Skew', source1 = 'C4', source2 = 'C1')
lecroy.setup_math_trend(math_channel = 'F1', source = 'P1', num_values = 100e3)
lecroy.setup_math_histogram(math_channel = 'F2', source = 'P1', num_values = 500)
lecroy.set_parameter(parameter = 'P2', param_engine = 'FullWidthAtHalfMaximum', source1 = 'F2', source2 = None)

# One more thing to do:  Set trigger voltage levels for the P1 skew function



#########################################
### Setup jitter measurement
#########################################

# Review the laser count rate graph, and determine 
# the range of currents with LCR > ~100, and DCR << LCR

currents = np.linspace(15e-6, 21e-6, 7)
num_sweeps = 100e3 # For some reason if this is == 10e3, reading the data crashes occasionally
num_bins = 500

jitter_data_list = []
start_time = time.time()
SRS.set_output(True)
for n, i in enumerate(currents):
    SRS.set_voltage(i*R_srs)
    jitter_data = lecroy.collect_sweeps(channel = 'F1', num_sweeps = num_sweeps)
    jitter_data_list.append(jitter_data)


file_path, file_name = save_x_vs_param(jitter_data_list,  currents, xname = 'jitter_data',  pname = 'currents',
                        test_type = 'Jitter IRF data', test_name = sample_name,
                        comments = '', filedir = '', zip_file=True)


for n, data in enumerate(jitter_data_list):
    n, bins, patches = plt.hist(data*1e12, bins = num_bins, normed=True, histtype='stepfilled', label = '%0.1f uA' % (currents[n]*1e6))
    plt.setp(patches, 'alpha', 0.5)
plt.xlabel('Time delay (ps)'); plt.ylabel('Counts'); plt.title('Jitter distributions\n' + sample_name)
plt.savefig(file_name + '.png')
plt.legend()
plt.show()





#########################################
### Laser attenuation vs count rate curves
#########################################

currents = np.linspace(18e-6, 20e-6, 81)
db_attenuation = np.linspace(0, 12, 5)
counting_time = 1

att = JDSHA9('GPIB0::5')
att.set_beam_block(False)

lcr_list = []
for db in db_attenuation:
    att.set_attenuation_db(db)
    LCR = count_rate_curve(currents, counting_time = counting_time)
    lcr_list.append(LCR)
att.set_beam_block(True)
DCR = count_rate_curve(currents, counting_time = counting_time)


data_dict = {'LCR':lcr_list, 'DCR':DCR, 'currents':currents, 'db_attenuation':db_attenuation}
file_path, file_name  = save_data_dict(data_dict, test_type = 'Laser attenuation vs count rate', test_name = sample_name,
                        filedir = '', zip_file=True)


for n, db in enumerate(db_attenuation): plt.semilogy(1e6*currents, lcr_list[n]+1, 'o-', label=('%0.1f dB' % db))
plt.semilogy(1e6*currents, DCR+1, 'kx-', label='DCR')
plt.legend(loc='upper left')
plt.xlabel('Bias current (uA)'); plt.ylabel('Counts (Hz)'); plt.title('Counts vs Bias\n' + sample_name)
plt.savefig(file_name + '.png')
plt.show()





#########################################
### Trace acquistion of pulses
#########################################

### First adjust scope to include whole pulse shape

num_traces = 5000
currents = np.linspace(14e-6, 21e-6, 8)

snspd_traces_x_list = []
snspd_traces_y_list = []
pd_traces_x_list = []
pd_traces_y_list = []
start_time = time.time()
SRS.set_output(True)
for n, i in enumerate(currents):
    print '   ---   Time elapsed for measurement %s of %s: %0.2f min    ---   ' % (n, len(currents), (time.time()-start_time)/60.0)
    SRS.set_voltage(i*R_srs)
    pd_traces_x = [] # Photodiode pulses
    pd_traces_y = []
    snspd_traces_x = [] # Device pulses
    snspd_traces_y = []
    lecroy.clear_sweeps()
    for n in range(num_traces):
        x,y = lecroy.get_single_trace(channel = 'C1')
        snspd_traces_x.append(x);  snspd_traces_y.append(y)
        x,y = lecroy.get_single_trace(channel = 'C4')
        pd_traces_x.append(x);  pd_traces_y.append(y)

    snspd_traces_x_list.append(snspd_traces_x)
    snspd_traces_y_list.append(snspd_traces_y)
    pd_traces_x_list.append(pd_traces_x)
    pd_traces_y_list.append(pd_traces_y)


data_dict = {'snspd_traces_x_list':snspd_traces_x_list, 'snspd_traces_y_list':snspd_traces_y_list, \
             'pd_traces_x_list':pd_traces_x_list, 'pd_traces_y_list':pd_traces_y_list, \
             'currents':currents}
file_path, file_name  = save_data_dict(data_dict, test_type = 'SNSPD trace acquisition', test_name = sample_name,
                        filedir = '', zip_file=True)
