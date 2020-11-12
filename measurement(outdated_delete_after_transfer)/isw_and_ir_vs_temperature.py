# Ic measurement code
# Run add_path.py first

#This is add_path.py copied here for convenience:
import sys
import os

snspd_measurement_code_dir = r'C:\Users\quu optics\Desktop\python code on the electronics lab computer\snspd-measurement-code'
dir1 = os.path.join(snspd_measurement_code_dir,'instruments')
dir2 = os.path.join(snspd_measurement_code_dir,'useful_functions')
dir3 = os.path.join(snspd_measurement_code_dir,'measurement')

if snspd_measurement_code_dir not in sys.path:
    sys.path.append(snspd_measurement_code_dir)
    sys.path.append(dir1)
    sys.path.append(dir2)
    sys.path.append(dir3)

#end add_path.py


from measurement.ic_sweep import *
from cryocon34 import *

from measurement.remove_outliers import *
from measurement.goto_temp import *


### Experimental variables: Scope/AWG and SRS or Keithley
sample_name = 'SPE995_F6'
R = 10e3
vpp = 0.7
repetition_hz = 100
trigger_level = 10e-3
num_sweeps = 500


### Instrument configuration
freq_gen = Agilent33250a('GPIB0::10')
lecroy_ip = '18.62.7.103'
#lecroy_ip = 'QNN-SCOPE1.mit.edu'
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
tempcon = Cryocon34('GPIB0::5')

lecroy.reset()
freq_gen.reset()
time.sleep(5)

#TO-DO: setup and intialize the cryocon
#tempcon.stop_heater()
#tempcon.setup_heater(load = 50, range='5W', source_channel = 'C')
#tempcon.set_pid(P=10, I=30, D=0.0)
#tempcon.set_setpoint(0)
#tempcon.start_heater()

isw_median_list = []
isw_stdev_list = []
ir_median_list = []
ir_stdev_list = []
temp_median_list = []
temp_stdev_list = []


temperatures = np.arange(2.8, 3.0, 0.3)

#NOTE!!!! Thepython code doesn't seem to care when the scope returns it's data- I just saw the temp change in the middle of recording the retrapping histogram.. wtf!?

for t in range(len(temperatures)):

    gototemp (tempcon, 'C', temperatures[t], 60)

    temp_list = []

    for num in range(0,10):
        thistemp = tempcon.read_temp('C')
        temp_list.append(thistemp)
        print 'Temperature measurement %i was %0.4fK' % (num+1,thistemp)
        time.sleep(2)
        
    temp_mean = np.mean(temp_list)
    temp_stdev = np.std(temp_list)
    print 'The measured temperature was %0.4fK +/- %0.5fK' % (temp_mean, temp_stdev)
    setup_ic_measurement(lecroy, freq_gen, vpp = vpp, repetition_hz = repetition_hz, trigger_level = trigger_level, trigger_slope = 'Positive', coupling_ch1 = 'DC1M', coupling_ch2 = 'DC1M')

    time.sleep(5)

    ### Run Isw experiment!
    voltage_switch_data = run_ic_sweeps(lecroy, num_sweeps = num_sweeps)

    time.sleep(num_sweeps/repetition_hz)
    isw_data = voltage_switch_data/R
    print 'Median Isw = %0.2f uA / Std. dev Isw = %0.2f uA' % (np.median(isw_data*1e6), np.std(isw_data*1e6)) + \
        	' [Ramp rate of %0.3f A/s (Vpp = %s V, rate = %s Hz, R = %s kOhms)]' \
            	% (calc_ramp_rate(vpp, R, repetition_hz, 'SINE'), vpp, repetition_hz, R/1e3)

    #prepare for retrapping measurment:
    setup_ic_measurement(lecroy, freq_gen, vpp = vpp, repetition_hz = repetition_hz,
                 trigger_level = trigger_level, trigger_slope = 'Negative',
                 coupling_ch1 = 'DC1M', coupling_ch2 = 'DC1M')
    time.sleep(5)

    voltage_retrap_data = run_ic_sweeps(lecroy, num_sweeps = num_sweeps)
    time.sleep(num_sweeps/repetition_hz)
    ir_data = voltage_retrap_data/R

    filtered_ir = remove_outliers(ir_data)

    print 'Median Ir = %0.2f uA / Std. dev Ir = %0.2f uA' % (np.median(filtered_ir*1e6), np.std(filtered_ir*1e6)) + \
    	    ' [Ramp rate of %0.3f A/s (Vpp = %s V, rate = %s Hz, R = %s kOhms)]' \
            	% (calc_ramp_rate(vpp, R, repetition_hz, 'SINE'), vpp, repetition_hz, R/1e3)

    time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    data_dir = 'C:\\Users\\quu optics\\Desktop\\aedata\\'
    filename =  data_dir +'isw_and_ir_hist_data %s %s temperature %0.3fK +- %0.4fK' % (time_str, sample_name, temp_mean, temp_stdev)
    scipy.io.savemat(filename + '.mat', mdict={'isw': isw_data, 'ir' : ir_data, 'filtered_ir': filtered_ir})

    isw_median_list.append(np.median(isw_data*1e6))
    isw_stdev_list.append(np.std(isw_data*1e6))
    ir_median_list.append(np.median(ir_data*1e6))
    ir_stdev_list.append(np.std(ir_data*1e6))
    temp_median_list.append(temp_mean)
    temp_stdev_list.append(temp_stdev)

time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
data_dir = 'C:\\Users\\quu optics\\Desktop\\aedata\\'
filename =  data_dir +'median temperature Isw and Ir %s' % (time_str)
scipy.io.savemat(filename + '.mat', mdict={'isw_med_ua' : isw_median_list, 'isw_stdev_ua' : isw_stdev_list , 'ir_med_ua' : ir_median_list, 'ir_stdev_ua' : ir_stdev_list , 'temp_med_K' : temp_median_list, 'temp_stdev_K' : temp_stdev_list})


gototemp (tempcon, 'C', 0.0, 1)



# Plot histogram data
# plt.hist(ic_data*1e6, bins = 50)
# plt.xlabel('Switching current (uA)')
# plt.ylabel('Frequency (#)')
# plt.show()


#tempcon.stop_heater()


# Save data
#TODO add nominal temperature to file name
#TODO add retrapping data to file

# f = open(filename + '.pickle', 'wb')
# pickle.dump(experiments, f)
# f.close()