import sys

sys.path.append("Q:\qnnpy")


from time import sleep

# import visa
import numpy as np
from matplotlib import pyplot as plt
from qnnpy.functions.save_data_vs_param import *
from qnnpy.instruments.keithley_2700 import Keithley2700
from qnnpy.instruments.yokogawa_gs200 import YokogawaGS200

#########################################
### Connect to instruments
#########################################
# SRS = SIM928('GPIB0::1', 2); SRS.reset()
# k = Keithley2400("GPIB0::14"); k.reset()
k = Keithley2700("GPIB0::3")
k.reset()
YOKO = YokogawaGS200("GPIB0::20")
YOKO.reset()
# YOKO.setup_source_current()
# YOKO.set_current_range(ran=4)


# raise

# def count_rate_curve(currents, counting_time = 0.1):
#     count_rate_list = []
#     start_time = time.time()
#     SRS.set_output(True)
#     for n, i in enumerate(currents):
#         # print '   ---   Time elapsed for measurement %s of %s: %0.2f min    ---   ' % (n, len(currents), (time.time()-start_time)/60.0)
#         SRS.set_voltage(np.sign(i)*1e-3); time.sleep(0.05); SRS.set_voltage(i*R_srs); time.sleep(0.05)

#         count_rate = counter.count_rate(counting_time=counting_time)
#         count_rate_list.append(count_rate)
#         print 'Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)' % (i*1e6, count_rate, n, len(currents), (time.time()-start_time)/60.0)
#     SRS.set_output(False)
#     return np.array(count_rate_list)

# %%
#########################################
### Sample information
#########################################
sample_name = "MGB255B"
device_name = "p1_4K_0mW"
comments = ""
test_name = sample_name + "_" + device_name + "_" + comments
filedirectry = r"S:\SC\Personal\EB\MgB2\MGB255B\P1_laser"
R_srs = 10e3
# counter.set_trigger(0.04)

Isource_max = 2100e-6
step = 10e-6
# here we go
Isource1 = np.arange(0, Isource_max, step)
Isource2 = np.arange(Isource_max, -Isource_max, -step)
Isource3 = np.arange(-Isource_max, 0, step)
Isource = np.concatenate([Isource1, Isource2, Isource3])
# Isource = np.concatenate([Isource1, Isource2])
V_source = Isource * R_srs
# k.set_output(output = True)
V_device = []
I_device = []
YOKO.set_voltage(0)
YOKO.set_output(True)
k.read_voltage()
sleep(1)


# for i in Isource:
#     YOKO.set_voltage(i*R_srs)
#     sleep(0.1)
#     vread = k.read_voltage()
#     vdev = vread - i*R_srs
#     #iread = (v-vread)/R_srs
#     print('V=%.4f V, R =%.2f' %(vread, vread/i))
#     V_device.append(vdev)
#     I_device.append(i)
# #k.set_output(output = False)

for v in V_source:
    YOKO.set_voltage(v)
    sleep(0.1)
    vread = k.read_voltage()
    iread = (v - vread) / R_srs
    print("V=%.4f V, I=%.2f uA, R =%.2f" % (vread, iread * 1e6, vread / iread))
    V_device.append(vread)
    I_device.append(iread)
    # Temps=ice_get_temp()
YOKO.set_output(False)
# search the switching current in the ramping up
Isw = I_device[np.argmax(np.array(V_device) > 0.005) - 1]

data_dict = {"V_device": V_device, "I_device": I_device, "step": step}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="Isw_curve",
    test_name=test_name,
    filedir=filedirectry,
    zip_file=True,
)

plt.plot(np.array(V_device), np.array(I_device) * 1e6, "-o")
plt.xlabel("Voltage (V)")
plt.ylabel("Current (uA)")
plt.title("I-V " + device_name + ", Isw = %.2f uA" % (Isw * 1e6))
print("Isw = %.2f uA" % (Isw * 1e6))
plt.savefig(file_path + ".png")
plt.show()
