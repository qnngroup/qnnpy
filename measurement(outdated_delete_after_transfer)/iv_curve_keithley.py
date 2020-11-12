# Written by Adam McCaughan Jan 17, 2014
# Run add_path.py first

from keithley_2400 import Keithley2400
import numpy as np
from pyvisa import visa
import time
import scipy.io
import datetime
from matplotlib import pyplot as plt
import cPickle as pickle


def iv_curve(k, voltages = [0,1e-3,2e-3], compliance_i = 1e-3, step_delay = 0.05):
    k.setup_2W_source_V_read_I() # k = Keithley attached to channel
    k.set_compliance_i(compliance_i)
    k.set_output(True)
    k.set_voltage(voltages[0]); time.sleep(0.1)
    v_list = []
    i_list = []
    print 'This IV curve will take (optimistically): %0.1f min' % (len(voltages)*step_delay/60.0)
    for v in voltages:
        try:
            k.set_voltage(v)
            time.sleep(step_delay)
            vout, iout = k.read_voltage_and_current()
            v_list.append(vout)
            i_list.append(iout)
        except KeyboardInterrupt:
            break
    k.set_output(False)
    return np.array(v_list), np.array(i_list)


def vi_curve(k, currents = [0,1e-3,2e-3], compliance_v = 1, step_delay = 0.05):
    k.setup_2W_source_I_read_V() # k = Keithley attached to channel
    k.set_compliance_v(compliance_v)
    k.set_output(True)
    k.set_current(currents[0]); time.sleep(0.1)
    v_list = []
    i_list = []
    print 'This IV curve will take (optimistically): %0.1f min' % (len(currents)*(step_delay+0.1)/60.0)
    for i in currents:
        try:
            k.set_current(i)
            time.sleep(step_delay)
            vout, iout = k.read_voltage_and_current()
            v_list.append(vout)
            i_list.append(iout)
        except KeyboardInterrupt:
            break
    k.set_output(False)
    return np.array(v_list), np.array(i_list)


def save_IV(I,V, test_name = 'Test01', plot_results = False):
    """ Save data as MATLAB .mat file and Python .pickle file """
    data_dict = {'I':I, 'V':V}
    time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    filename =  'IV Curve %s %s' % (time_str, test_name)
    scipy.io.savemat(filename + '.mat', mdict=data_dict)
    f = open(filename + '.pickle', 'wb'); pickle.dump(data_dict, f); f.close()

    # Plot data
    plt.plot(np.transpose(np.array(V)),np.transpose(np.array(I))*1e6)
    plt.xlabel('Voltage (V)'); plt.ylabel('Current (uA)')
    plt.savefig(filename)
    if plot_results is True: plt.show()
    else: plt.close()
    print 'Saving IV curve with filename: %s' % filename
    return filename



### Experimental variables
voltages = np.linspace(0, .2, 201); compliance_i = 200e-6
voltages = np.concatenate([voltages, voltages[::-1]])
voltages = np.concatenate([voltages, -voltages])
num_sweeps = 1
test_name = 'NWL028D Device 3wx 1V %s sweeps' % num_sweeps


### Setup instruments
k = Keithley2400('GPIB0::14')
k.reset()


### Run experiment with multiple sweeps
V_list = []; I_list = []
start_time = time.time()
for n in range(num_sweeps):
    print 'Time elapsed for measurement %s: %0.2f min' % (n, (time.time()-start_time)/60.0)
    V, I = iv_curve(k, voltages = voltages, compliance_i = compliance_i, step_delay = 0.05)
    V_list.append(V)
    I_list.append(I)
    plt.plot(V,I)
save_IV(I_list,V_list, test_name = test_name, plot_results = True)
plt.show()


# # Replot 
# for n in range(len(V_list)/2):
#     plt.plot(V_list[n*2],I_list[n*2]*1e6)
#     plt.ylim((0,5))
# plt.show()

### Run "VI Curve" e.g. with current bias
num_pts = 100
currents = np.linspace(0,100e-6,num_pts+1)
currents = np.concatenate([currents, currents[::-1]])
compliance_v = 0.2
V, I = vi_curve(k, currents, compliance_v, step_delay = 0.05)
V = np.array(V); I = np.array(I)
V1 = V[0:num_pts]; V2 = V[num_pts:]
I1 = I[0:num_pts]; I2 = I[num_pts:]
plt.plot(V1*1e3,I1*1e6,'.-')
plt.plot(V2*1e3,I2*1e6,'.-')
plt.xlabel('Voltage (mV)')
plt.ylabel('Current (uA)')
plt.title('Port 3')
plt.show()