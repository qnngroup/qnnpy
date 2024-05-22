# %%
# set up instrument
import sys
import os
import visa
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
import numpy as np
import scipy
from datetime import datetime
import scipy.io as sio

sys.path.append(r"C:\Users\ICE\Desktop\git-repo\qnn-lab-instr-python")


from qnnpy.instruments.keithley_2700 import Keithley2700
from qnnpy.instruments.srs_sim928 import SIM928
from qnnpy.functions.save_data_vs_param import *
from qnnpy.instruments.lecroy_620zi import LeCroy620Zi
from qnnpy.instruments.jds_ha9 import JDSHA9
from qnnpy.instruments.agilent_53131a import Agilent53131a

# %%
#########################################
### Connect to instruments
#########################################
SRS = SIM928("GPIB0::1", 2)
SRS.reset()
k = Keithley2700("GPIB0::18")
k.reset()
lecroy_ip = "QNN-SCOPE1.MIT.EDU"
lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
attenuator = JDSHA9("GPIB0::7")
counter = Agilent53131a("GPIB0::30")
counter.basic_setup()
# SRS2 = SIM928('GPIB0::1', 4); SRS2.reset()

# %%
# device info
sample_name = "SPF831"
device_name = "ref"
comments = ""
test_name = sample_name + "_" + device_name + "_" + comments
filedirectry = r"C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\20191222_isw_ramp_rate_AQ"

# %%
#########################################
### Setup counter
#########################################
### Scan counter trigger levels - Make sure trigger voltage is well above noise level
counter.write(":EVEN:HYST:REL 100")
# counter.write(':INP:IMP 50')

comments = ""
v_bias = 2.4  # bias voltage
attenuator.set_attenuation_db(0)
attenuator.set_beam_block(False)

SRS.set_output(False)
sleep(0.2)
SRS.set_output(True)
SRS.set_voltage(0)
sleep(0.2)
SRS.set_voltage(v_bias)
sleep(1)
trigger_v, count_rate = counter.scan_trigger_voltage(
    [0, 0.5], counting_time=0.2, num_pts=50
)
plt.semilogy(trigger_v, count_rate + 1, "o")
plt.xlabel("Trigger level (V)")
plt.ylabel("Counts (cps)")
plt.title("Counts vs Bias\n" + test_name)

data_dict = {"trigger_v": trigger_v, "count_rate": count_rate, "v_bias": v_bias}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="trigger_sweep",
    test_name=test_name + comments,
    filedir=filedirectry,
    zip_file=True,
)
plt.savefig(file_path + ".png")
plt.show()

# %%
######################################
# Next, use the above information to set the counter trigger level
#######################################
counter.set_trigger(0.04)
# counter.set_trigger(.2)

# %%
#####################################################################
### Measure and plot dark count rate curve
#####################################################################
R_srs = 100e3


def count_rate_curve(currents, counting_time=0.1):
    count_rate_list = []
    start_time = time.time()
    SRS.set_output(True)
    for n, i in enumerate(currents):
        # print '   ---   Time elapsed for measurement %s of %s: %0.2f min    ---   ' % (n, len(currents), (time.time()-start_time)/60.0)
        SRS.set_voltage(np.sign(i) * 1e-3)
        time.sleep(0.05)
        SRS.set_voltage(i * R_srs)
        time.sleep(0.05)

        count_rate = counter.count_rate(counting_time=counting_time)
        count_rate_list.append(count_rate)
        print(
            "Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)"
            % (i * 1e6, count_rate, n, len(currents), (time.time() - start_time) / 60.0)
        )
    SRS.set_output(False)
    return np.array(count_rate_list)


# %%
# dark count rate
###
# comments = 'T=1p3K'
# currents1 = np.arange(0e-6, 7.99e-6, 2e-6)
# currents2 = np.arange(8e-6, 26e-6, 1e-6)
# currents = np.concatenate([currents1, currents2])
# currents = np.arange(10e-6, 26.5e-6, .5e-6)
currents = np.arange(20e-6, 25e-6, 0.2e-6)
DCR = np.zeros(currents.shape)

iterations = 5
counting_time = 15
attenuator.set_attenuation_db(100)
attenuator.set_beam_block(True)

for i in range(iterations):
    DCR_temp = count_rate_curve(currents, counting_time=counting_time)
    DCR = DCR + np.array(DCR_temp)

DCR = DCR / iterations

data_dict = {
    "DCR": DCR,
    "currents": currents,
    "counting_time": counting_time * iterations,
}
file_path, file_name = save_data_dict(
    data_dict, test_type="DCR", test_name=test_name + comments, filedir=filedirectry
)
plt.semilogy(1e6 * currents, DCR, "o", label="Dark count rate (DCR)")
plt.xlabel("Bias current (uA)")
plt.ylabel("Counts (Hz)")
plt.title("Counts vs Bias\n" + test_name)
plt.savefig(file_path + ".png")
plt.show()


# %%
###################################################
####Measure photon count
#####################################################
comments = ""
# currents1 = np.arange(0e-6, 10e-6, 2e-6)
# currents2 = np.arange(10e-6, 19e-6, .2e-6)
# currents = np.concatenate([currents1, currents2])
currents = np.arange(10e-6, 25e-6, 0.5e-6)

counting_time = 2

# load dark count rate measu♣rement
# dcr_fname = 'DCR 2019-12-22 17-26-51 SPF831_ref_'
# dcr_fname = os.path.join(filedirectry, dcr_fname)
# M = sio.loadmat(dcr_fname)
# currents = M['currents'][0]
# DCR = M['DCR'][0]

# Optionally, we can measure the dark count again
attenuator.set_attenuation_db(100)
attenuator.set_beam_block(True)
sleep(1)
DCR = count_rate_curve(currents, counting_time=counting_time)

# photon rate calculation
hbar = 1.05457e-34
lmd = 1550e-9
c = 299792458
Eph = hbar * 2 * np.pi * c / lmd

# Turn on laser, measure laser count curve (LCR)
extra_attenuation = 0
att_db = 0
attenuator.set_beam_block(False)
attenuator.set_attenuation_db(att_db)
sleep(1)
# power = pm.read_value();
power = 10**-5.615  # 0dB power
LCR = count_rate_curve(currents, counting_time=counting_time)

DE = (LCR - DCR) / (power / 10 ** ((att_db + extra_attenuation) / 10.0) / Eph)

data_dict = {
    "LCR": LCR,
    "DCR": DCR,
    "currents": currents,
    "power": power,
    "db_attenuation": att_db,
    "extra_attenuation": extra_attenuation,
    "counting_time": counting_time,
}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="Laser attenuation vs count rate",
    test_name=test_name + comments,
    filedir=filedirectry,
    zip_file=True,
)
plt.figure(1)
plt.plot(1e6 * currents, LCR, "o", label="Laser count rate (LCR)")
plt.plot(1e6 * currents, DCR, "o", label="Dark count rate (DCR)")
plt.plot(1e6 * currents, LCR - DCR, "o", label="LCR - DCR")
plt.legend(loc="upper left")
plt.xlabel("Bias current (uA)")
plt.ylabel("Counts (Hz)")
plt.title("Counts vs Bias\n" + test_name)
plt.savefig(file_path + ".png")
plt.show()

plt.figure(2)

plt.plot(1e6 * currents, DE, "o", label="DE")
plt.savefig(file_path + "DE.png")
plt.show()

plt.figure(3)
plt.semilogy(1e6 * currents, LCR - DCR, "o", label="LCR - DCR")
plt.show()
# %%
# serious dark count measurement
comments = ""
currents1 = np.arange(0e-6, 7.99e-6, 1e-6)
currents2 = np.arange(8e-6, 19e-6, 0.2e-6)
currents = np.concatenate([currents1, currents2])
# currents = np.arange(10e-6, 19e-6, .2e-6)
counting_time = 10
number_of_runs = 5


for i in range(number_of_runs):
    print("{} of {} runs".format(i + 1, number_of_runs))
    attenuator.set_beam_block(True)
    DCR_temp = count_rate_curve(currents, counting_time=counting_time)
    if i == 0:
        DCR = DCR_temp
    else:
        DCR = DCR + DCR_temp

DCR = DCR / number_of_runs


data_dict = {
    "DCR": DCR,
    "currents": currents,
    "counting_time": counting_time,
    "number_of_runs": number_of_runs,
}
file_path, file_name = save_data_dict(
    data_dict, test_type="DCR", test_name=test_name + comments, filedir=filedirectry
)
plt.semilogy(1e6 * currents, DCR, "o", label="Dark count rate (DCR)")
plt.xlabel("Bias current (uA)")
plt.ylabel("Counts (Hz)")
plt.title("Counts vs Bias\n" + test_name)
plt.savefig(file_path + ".png")
plt.show()

SRS.set_output(False)

# %%
#########################################
### Linearity check
#########################################
comments = ""
currents = [10.5e-6]
db_attenuation = np.arange(5, 50, 5)
extra_attenuation = 0
counting_time = 3

attenuator.set_beam_block(False)
attenuator.set_attenuation_db(db_attenuation[0])
sleep(0.1)

lcr_list = []
powers = []
for db in db_attenuation:
    attenuator.set_attenuation_db(db)
    print("attenuation: " + str(db) + " dB")
    sleep(1)
    LCR = count_rate_curve(currents, counting_time=counting_time)
    # powers.append(pm.read_value())
    lcr_list.append(LCR)

attenuator.set_beam_block(True)
print("DCR")
sleep(0.1)
dcr = count_rate_curve(currents, counting_time=10)


data_dict = {
    "LCR": lcr_list,
    "DCR": dcr,
    "currents": currents,
    "db_attenuation": db_attenuation,
    "extra_attenuation": extra_attenuation,
    "powers": powers,
}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="Linearity_check",
    test_name=test_name + comments,
    filedir=filedirectry,
    zip_file=True,
)

# plt.semilogy(db_attenuation, lcr_list-dcr, 'o')
plt.figure(1)
plt.title("Linearity check\n" + test_name)
# plt.subplot(311)
plt.semilogy(db_attenuation, np.array(lcr_list) - dcr, "o")
# plt.legend(loc='upper left')
plt.xlabel("attenuation (db)")
plt.ylabel("Counts (Hz)")
# plt.subplot(312)
# plt.loglog(powers, np.array(lcr_list)-dcr,'o')
##plt.legend(loc='upper left')
# plt.xlabel('powermeter reading (W)'); plt.ylabel('Counts (Hz)')
# plt.subplot(313)
# plt.semilogy(db_attenuation, powers,'o')
##plt.legend(loc='upper left')
# plt.xlabel('attenuation (db)'); plt.ylabel('powermeter reading (W)');


plt.savefig(file_path + ".png")
plt.show()
# %%

#########################################################
# DE curve for muliple attenuation values
####################################################
currents1 = np.arange(0e-6, 5e-6, 1e-6)
currents2 = np.arange(5e-6, 9e-6, 0.1e-6)
currents = np.concatenate([currents1, currents2])

db_attenuation = np.arange(5, 30, 5)
counting_time = 0.5
extra_attenuation = 20


hbar = 1.05457e-34
lmd = 1550e-9
c = 299792458
Eph = hbar * 2 * pi * c / lmd

attenuator.set_beam_block(True)
sleep(10)
DCR = count_rate_curve(currents, counting_time=counting_time)

attenuator.set_beam_block(False)

lcr_list = []
powers = []
de_list = []
for db in db_attenuation:
    attenuator.set_attenuation_db(db)
    sleep(10)
    print("attenuation: " + str(db))
    LCR = count_rate_curve(currents, counting_time=counting_time)
    powers.append(pm.read_value())
    DE = (LCR - DCR) / (power / 10 ** (extra_attenuation / 10.0) / Eph)
    lcr_list.append(LCR)
    de_list.append(DE)

data_dict = {
    "LCR": lcr_list,
    "DCR": DCR,
    "currents": currents,
    "db_attenuation": db_attenuation,
    "powers": powers,
    "extra_attenuation": extra_attenuation,
    "DE": de_list,
}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="Laser attenuation vs count rate",
    test_name=test_name,
    filedir=filedirectry,
    zip_file=True,
)

for n, db in enumerate(db_attenuation):
    plt.semilogy(1e6 * currents, lcr_list[n] + 1, "o-", label=("%0.1f dB" % db))
plt.plot(currents, de_list, "kx-", label="DE")
plt.legend(loc="upper left")
plt.xlabel("Bias current (uA)")
plt.ylabel("DE")
plt.title("DE vs attenuation\n" + test_name)
plt.savefig(file_path + ".png")
plt.show()


#########################################
### Setup jitter measurement
#########################################
#!set your trigger level and bias current here
SRS.set_voltage(6.8e-6 * R_srs)
trigger_level = 100e-3


lecroy.reset()
SRS.set_output(True)
time.sleep(5)

lecroy.set_display_gridmode(gridmode="Single")
lecroy.set_coupling(channel="C2", coupling="DC50")
lecroy.label_channel(channel="C2", label="SNSPD trace")
lecroy.label_channel(channel="C3", label="Photodiode reference")
lecroy.view_channel(channel="C1", view=False)
lecroy.view_channel(channel="C2", view=True)
lecroy.view_channel(channel="C3", view=True)
lecroy.view_channel(channel="C4", view=False)

lecroy.set_vertical_scale(channel="C2", volts_per_div=100e-3, volt_offset=0)
lecroy.set_vertical_scale(channel="C3", volts_per_div=50e-6, volt_offset=0)
lecroy.set_horizontal_scale(time_per_div=10e-9, time_offset=0)

lecroy.set_trigger(source="C2", volt_level=trigger_level, slope="Positive")
lecroy.set_trigger_mode(trigger_mode="Normal")
lecroy.set_parameter(parameter="P1", param_engine="Skew", source1="C3", source2="C2")
lecroy.setup_math_trend(math_channel="F1", source="P1", num_values=100e3)
lecroy.setup_math_histogram(math_channel="F2", source="P1", num_values=500)
lecroy.set_parameter(
    parameter="P2", param_engine="FullWidthAtHalfMaximum", source1="F2", source2=None
)

# One more thing to do:  Set trigger voltage levels for the P1 skew function


#########################################
### Setup jitter measurement
#########################################

# Review the laser count rate graph, and determine
# the range of currents with LCR > ~100, and DCR << LCR
comments = "1G-amp_35db_var_att_15db_extra"
attenuator.set_attenuation_db(35)
currents = np.linspace(6.5e-6, 7.2e-6, 4)
num_sweeps = (
    1e4  # For some reason if this is == 10e3, reading the data crashes occasionally
)
num_bins = 500  # 5000 is max

jitter_data_list = []
start_time = time.time()
SRS.set_output(True)
for n, i in enumerate(currents):
    SRS.set_voltage(i * R_srs)
    jitter_data = lecroy.collect_sweeps(channel="F2", num_sweeps=num_sweeps)
    jitter_data_list.append(jitter_data)


file_path, file_name = save_x_vs_param(
    jitter_data_list,
    currents,
    xname="jitter_data",
    pname="currents",
    test_type="Jitter IRF data",
    test_name=sample_name,
    comments="",
    filedir="",
    zip_file=True,
)


for n, data in enumerate(jitter_data_list):
    n, bins, patches = plt.hist(
        data * 1e12,
        bins=num_bins,
        normed=True,
        histtype="stepfilled",
        label="%0.1f uA" % (currents[n] * 1e6),
    )
    plt.setp(patches, "alpha", 0.5)
plt.xlabel("Time delay (ps)")
plt.ylabel("Counts")
plt.title("Jitter distributions\n" + sample_name)
plt.savefig(file_path + ".png")
plt.legend()
plt.show()


#########################################
### Trace acquistion of pulses
#########################################

### First adjust scope to include whole pulse shape

# simple single trace of the pulse shape
channel = "C2"
x, y = lecroy.get_single_trace(channel=channel)
plt.plot(x, y)
data_dict = {"x": x, "y": y}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="pulse_shape",
    test_name="5F1",
    filedir=filedirectry,
    zip_file=False,
)
plt.savefig(file_path + ".png")
plt.show()


### First adjust scope to include whole pulse shape

num_traces = 1
currents = np.linspace(14e-6, 21e-6, 8)

snspd_traces_x_list = []
snspd_traces_y_list = []
pd_traces_x_list = []
pd_traces_y_list = []
start_time = time.time()
SRS.set_output(True)
for n, i in enumerate(currents):
    print(
        "   ---   Time elapsed for measurement %s of %s: %0.2f min    ---   "
        % (n, len(currents), (time.time() - start_time) / 60.0)
    )
    SRS.set_voltage(i * R_srs)
    pd_traces_x = []  # Photodiode pulses
    pd_traces_y = []
    snspd_traces_x = []  # Device pulses
    snspd_traces_y = []
    lecroy.clear_sweeps()
    for n in range(num_traces):
        x, y = lecroy.get_single_trace(channel="C2")
        snspd_traces_x.append(x)
        snspd_traces_y.append(y)
        x, y = lecroy.get_single_trace(channel="C3")
        pd_traces_x.append(x)
        pd_traces_y.append(y)

    snspd_traces_x_list.append(snspd_traces_x)
    snspd_traces_y_list.append(snspd_traces_y)
    pd_traces_x_list.append(pd_traces_x)
    pd_traces_y_list.append(pd_traces_y)


data_dict = {
    "snspd_traces_x_list": snspd_traces_x_list,
    "snspd_traces_y_list": snspd_traces_y_list,
    "pd_traces_x_list": pd_traces_x_list,
    "pd_traces_y_list": pd_traces_y_list,
    "currents": currents,
}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="SNSPD trace acquisition",
    test_name=sample_name,
    filedir=filedirectry,
    zip_file=True,
)


# save screenshots
lecroy.save_screenshot(
    filename="test",
    filepath="C:\\Users\\LeCroyUser\\Dropbox\\dizhu\\screenshots\\",
    grid_area_only=False,
)
