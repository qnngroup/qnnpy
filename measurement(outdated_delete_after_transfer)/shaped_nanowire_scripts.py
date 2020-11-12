# Ic measurement code

from pyvisa import visa
import numpy as np
import time
import datetime
from matplotlib import pyplot as plt
from scipy.optimize import fmin
import scipy.io
import cPickle as pickle

def setup_ic_measurement(lecroy, freq_gen, vpp = 1, repetition_hz = 100, trigger_level = 0.1, trigger_slope = 'Positive'):

    # Setup frequency generator to have heartbeat shape for Ic sweeping --'\,---
    freq_gen.set_load(high_z = True)
    freq_gen.select_arb_wf(name = 'HEARTBEA')

    # Change repetition rate and voltage amplitude
    freq_gen.set_freq(repetition_hz)
    freq_gen.set_vpp(vpp)
    freq_gen.set_output(True)

    # Setup LeCroy scope:
    lecroy.set_coupling(channel = 'C1', coupling = 'DC1M')
    lecroy.set_coupling(channel = 'C2', coupling = 'DC1M')
    lecroy.label_channel(channel = 'C1', label = 'AWG input waveform')
    lecroy.label_channel(channel = 'C2', label = 'Device output')
    lecroy.label_channel(channel = 'F1', label = 'Per-sweep Ic values')
    lecroy.label_channel(channel = 'F2', label = 'Ic values histogram')
    lecroy.set_vertical_scale(channel = 'C1', volts_per_div = vpp/10.0, volt_offset = 0)
    lecroy.set_horizontal_scale(time_per_div = (1.0/repetition_hz)/10.0, time_offset = 0)
    lecroy.set_trigger(source = 'C2', volt_level = trigger_level, slope = trigger_slope)
    lecroy.set_trigger_mode(trigger_mode = 'Auto')
    lecroy.set_parameter(parameter = 'P1', param_engine = 'LevelAtX', source1 = 'C1', source2 = None)
    lecroy.setup_math_trend(math_channel = 'F1', source = 'P1', num_values = 100e3)
    lecroy.setup_math_histogram(math_channel = 'F2', source = 'P1', num_values = 100e3)
    lecroy.set_display_gridmode(gridmode = 'Single')


def measure_ic_values(lecroy, num_sweeps):
    lecroy.clear_sweeps()
    time.sleep(0.1)
    while (lecroy.get_num_sweeps(channel = 'F1') < num_sweeps):
        time.sleep(0.1)
    x, ic_values = lecroy.get_wf_data(channel='F1')
    return ic_values



class IcExperiment:
    data = np.array([]) # Observation data (typically Gumbel distributed)
    ic = 0
    delta_ic = 0
    description = ''


def gumbel_pdf(theta, x):
    a = theta[0]; b = theta[1]
    return 1.0/b*np.exp((x-a)/b - np.exp((x-a)/b))


def gumbel_dist_error_fun(theta, data, min_prob = 1e-2):
    pdf_fun = gumbel_pdf
    prob = pdf_fun(theta = theta, x = data)
    prob[prob<min_prob] = min_prob  # Otherwise any datapoint with probability zero returns log(P(x)=0) = -Inf
    log_likelihood = np.sum(np.log(prob))
    return -log_likelihood


def analyze_ic_values(ic_values):
    theta0 = [np.median(ic_values), np.std(ic_values)*10]
    thetaopt = fmin(gumbel_dist_error_fun, theta0, [ic_values])
    ic = thetaopt[0]
    delta_ic = thetaopt[1]
    return ic, delta_ic


def fit_ic_histogram(ic_values, bins = 100, binrange = None, plot = False):
    ic_hist, bin_edges = np.histogram(a = ic_values, bins = bins)
    ic_hist_x = bin_edges[:-1] + (bin_edges[1]-bin_edges[0])/2.0

    ic, delta_ic = analyze_ic_values(ic_values)
    ic_hist_fit_x = np.linspace(min(ic_values), max(ic_values), bins)
    ic_hist_fit = gumbel_pdf([ic, delta_ic], ic_hist_fit_x)
    ic_hist_fit = ic_hist_fit/float(np.max(ic_hist_fit))
    ic_hist = ic_hist/float(np.max(ic_hist))
    if plot:
        plt.bar(ic_hist_x, ic_hist, width=(ic_hist_x[1]-ic_hist_x[0]))
        plt.plot(ic_hist_x, ic_hist_fit, 'r')
        plt.show()
    return ic_hist_x, ic_hist, ic_hist_fit

def calc_ramp_rate(vpp, R, repetition_hz):
    # Assumes you're using a heartbeat waveform
    T = 1.0/repetition_hz
    T_ramp = T/8.0
    I_max = (vpp/2.0)/R
    return I_max/T_ramp




############### EXPERIMENT SCRIPT

### Experimental variables
output_rise_time = 20e-9
repetition_hz = 100
vpp = 10
R = 100e3
trigger_level = 0.1
sample_name = 'SPE048 Device N11'


### Setup instruments
lecroy_ip = '18.62.12.250'
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
freq_gen = Agilent33250a('GPIB0::11')
na = HP8722C('GPIB0::7')

lecroy.reset()
freq_gen.reset()
na.reset()
time.sleep(5)
setup_ic_measurement(lecroy, freq_gen, vpp = vpp, repetition_hz = 100, trigger_level = trigger_level, trigger_slope = 'Positive')
time.sleep(5)
lecroy.set_horizontal_scale(time_per_div = output_rise_time, time_offset = 0)
na.fixed_freq(1e9)
na.power(-60)


### Run experiment!
F = np.linspace(1e9,30e9,30)
P = np.linspace(-60, 0, 7)
num_sweeps = 10000

raw_input('About to wipe all previous experiments in memory! Press enter to continue')
experiments = []

for f in F:
    for p in P:
        try:
            ic_exp = IcExperiment()
            ic_exp.description = 'Microwave-enhancement of Ic Constriction: %0.1f MHz / %0.1f dBm' % (f*1e-6, p)
            print ic_exp.description
            ic_exp.f = f; ic_exp.p = p
            ic_exp.ramp_rate = calc_ramp_rate(vpp, R, repetition_hz)
            ic_exp.time = time.time()
            ic_exp.sample = sample_name

            na.fixed_freq(f)
            na.power(p)
            time.sleep(1)
            
            # Get Ic data / analyze / append to big list of experiments
            ic_exp.data = measure_ic_values(lecroy, num_sweeps = num_sweeps)
            ic_exp.ic, ic_exp.delta_ic = analyze_ic_values(ic_exp.data)
            experiments.append(ic_exp)
            print 'Experiment complete:  %0.2f mins elapsed (%0.2f mins to run whole series)' \
                    % ((time.time()-ic_exp.time)/60, (time.time()-ic_exp.time)*len(F)*len(P)/60)
        except KeyboardInterrupt:
            break



# Save data
time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
filename =  'Ic_microwave_enhance %s %s' % (time_str, sample_name)
# scipy.io.savemat(filename + '.mat', mdict={'igg': igg, 'icg': icg, 'Iin_g' : Iin_g, 'Iin_c' : Iin_c, 'Vout_g' : Vout_g, 'Vout_c' : Vout_c})
f = open(filename + '.p', 'wb')
pickle.dump(experiments, f)
f.close()



# Plot histogram data
for e in experiments:
e.data = e.data[e.data>0]
ic_hist_x, ic_hist, ic_hist_fit = fit_ic_histogram(e.data, bins=20, plot=False)
plt.plot(ic_hist_x, ic_hist)
plt.plot(ic_hist_x, ic_hist_fit)
plt.show()


# Plot as image
ic_list = []
delta_ic_list = []
for e in experiments:
    ic_list.append(np.median(e.data))
    delta_ic_list.append(np.std(e.data))
IC = np.reshape(np.array(ic_list), [len(F), len(P)])
IC = np.flipud(np.transpose(IC/R*1e6))
plt.imshow(IC, extent=[F[0]/1e9,F[-1]/1e9,P[0],P[-1]], aspect='auto')
plt.xlabel('Frequency (GHz)'); plt.ylabel('Power (dBm)'); plt.title('Ic (uA) for ' + sample_name)
plt.colorbar()
plt.savefig(filename)
plt.show()

ic_list = []
delta_ic_list = []
f_list = []
p_list = []
    # ic_list.append(e.ic)
    # delta_ic_list.append(e.delta_ic)
    # p_list.append(e.p)
    # f_list.append(e.f)