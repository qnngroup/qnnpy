# Ic measurement code
# Run add_path.py first
from measurement.ic_sweep import *


### Experimental variables: Scope/AWG and SRS or Keithley
sample_name = 'NWL017A Device F2c'
R = 10e3
vpp = 10
repetition_hz = 100
trigger_level = 1e-3
num_sweeps = 1000


### Instrument configuration
freq_gen = Agilent33250a('GPIB0::10')
lecroy_ip = '18.62.10.141'
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)


### Initialize instruments
lecroy.reset()
freq_gen.reset()
time.sleep(5)
setup_ic_measurement(lecroy, freq_gen, vpp = vpp, repetition_hz = repetition_hz,
                     trigger_level = trigger_level, trigger_slope = 'Positive',
                     coupling_ch1 = 'DC1M', coupling_ch2 = 'DC1M')
time.sleep(5)


### Run experiment!
voltage_data = run_ic_sweeps(lecroy, num_sweeps = num_sweeps)
ic_data = voltage_data/R
print 'Median Ic = %0.2f uA / Std. dev Ic = %0.2f uA' % (np.median(ic_data*1e6), np.std(ic_data*1e6)) + \
        ' [Ramp rate of %0.3f A/s (Vpp = %s V, rate = %s Hz, R = %s kOhms)]' \
            % (calc_ramp_rate(vpp, R, repetition_hz, 'SINE'), vpp, repetition_hz, R/1e3)


# Plot histogram data
plt.hist(ic_data*1e6, bins = 50)
plt.xlabel('Switching current (uA)')
plt.ylabel('Frequency (#)')
plt.show()






# # Save data
# time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
# filename =  'ic_sweep data %s %s' % (time_str, sample_name)
# # scipy.io.savemat(filename + '.mat', mdict={'igg': igg, 'icg': icg, 'Iin_g' : Iin_g, 'Iin_c' : Iin_c, 'Vout_g' : Vout_g, 'Vout_c' : Vout_c})
# f = open(filename + '.pickle', 'wb')
# pickle.dump(experiments, f)
# f.close()


# # Generate histogram data
# ic_hist, bin_edges = np.histogram(a = ic_data, bins = 50)
# ic_hist_x = bin_edges[:-1] + (bin_edges[1]-bin_edges[0])/2.0
# plt.plot(ic_hist_x*1e6, ic_hist)
# plt.show()