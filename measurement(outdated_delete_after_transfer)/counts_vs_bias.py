from instruments.agilent_53131a import *
from instruments.srs_sim928 import *
# c = Agilent53131a('GPIB0::10')
# c.basic_setup()
# c.set_trigger(-0.075)


counter = Agilent53131a('GPIB0::3')
counter.basic_setup()

v = SIM928(4, 'GPIB0::4')
v.reset()
v.set_output(True)
R_gate = 100e3


#use this to make sure you're triggering above noise
#trigger_v, count_rate = counter.scan_trigger_voltage([-0.05,0.05], counting_time=0.1, num_pts=500)

#then set the trigger level appropriately
counter.set_trigger(-0.2)

#This defines the current values we use to bias the SNSPD:
currents = np.linspace(50e-6, 80e-6, 100)


#sweep SNSPD bias, measure counts
counts_list = []
I_list = []
#start_time = time.time()

for n in range(len(currents)):

    #print '   ---   Time elapsed for measurement %s of %s: %0.2f min    ---   ' % (n, len(currents), (time.time()-start_time)/60.0)
    # k.set_current(currents[n]); time.sleep(0.01)
    # v,i = k.read_voltage_and_current()
    i = currents[n]; v.set_voltage(0); time.sleep(0.05); v.set_voltage(i*R_gate); time.sleep(0.05);

    counts = counter.count_rate(counting_time=0.1)
    counts_list.append(counts)
    I_list.append(i)
    #print 'Current value %0.2f uA  -  Median Ic = %0.2f uA / Std. dev Ic = %0.2f uA' % (I_list[-1]*1e6, np.median(ic_data*1e6), np.std(ic_data*1e6))


plt.plot(1e6*np.array(I_list), np.log(counts_list), 'o')
plt.xlabel('Bias current (uA)')
plt.ylabel('Counts (#/Sec)')
plt.title('Counts vs Bias')
plt.show()