# %%
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append("/Users/dizhu/Documents/github_repo/qnn-lab-instr-python")

from qnnpy.functions.save_data_vs_param import *
from qnnpy.instruments.keysight_n5224a import KeysightN5224a

# %%
# connect PNA
pna = KeysightN5224a("GPIB0::16::INSTR")

pna.reset(
    measurement="S21", if_bandwidth=1e3, start_freq=200e6, stop_freq=15e9, power=-30
)

# connect signal generator
# sg = SGS100A('USB0::0x0AAD::0x0088::110963::INSTR')
# %%

filedirectry = (
    r"C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\LC11\20190404_LC11_3rd_cooldown"
)
sample_name = "LC11"
device_name = "HFB"

comments = "T=1p2K"
power = -30
test_type = "single_sweep"

#
pna.set_measurement("S21")  # measurement type
pna.set_start(5.5e9)  # starting frequency in Hz
pna.set_stop(8e9)  # stop freq
pna.set_points(4001)  # number of points
pna.set_if_bw(100)  # if bandwidth
pna.set_power(power)  # power in dBm

pna.set_sweep_mode("CONT")
# pna.set_sweep_mode('HOLD')


f, S21 = pna.single_sweep()
att = pna.get_source_attenuation()

data_dict = {"power": power, "f": f, "S21": S21, "att": att}
file_path, file_name = save_data_dict(
    data_dict,
    test_type=test_type,
    test_name=sample_name + "_" + device_name + comments,
    filedir=filedirectry,
    zip_file=True,
)

plt.plot(f / 1e9, 20 * np.log10(abs(S21)))
plt.xlabel("Frequency (GHz)")
plt.ylabel("S21 (dB)")
plt.title(file_name)
plt.savefig(file_path + ".png")
plt.show()


# for i in range(len(S21)):
#    S = S21[i]
#    a = att[i]
#    plt.plot(f/1e9, 20*np.log10(abs(np.array(S)))+a)
# plt.savefig(file_path + '.png')
# plt.show()


# %%
# power sweep
filedirectry = r"C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\LC11"
sample_name = "LC11_LF"
device_name = "NbN_LN_resonator"

T = 1.2

test_type = "vary_VNA_power_T={}K".format(T)
test_type = test_type.replace(".", "p")

pna.set_measurement("S21")  # measurement type
pna.set_start(1.5e9)  # starting frequency in Hz
pna.set_stop(3.5e9)  # stop freq
pna.set_points(2001)  # number of points
pna.set_if_bw(100)  # if bandwidth
pna.set_power(power)  # power in dBm

pna_power = np.arange(-50, 10, 3)

S21 = []
VNA_att = []
for p in pna_power:
    print("VNA power = {}dBm".format(p))
    pna.set_power(p)
    f, S = pna.single_sweep()
    S21.append(S)
    VNA_att.append(float(pna.query("SOUR:POW:ATT?").strip()))

for i in range(len(S21)):
    plt.plot(
        f / 1e9,
        20 * np.log10(np.abs(S21[i]) - VNA_att[i]),
        label="P = {}dBm".format(pna_power[i]),
    )
plt.legend()
plt.title("VNA power sweep, temperature = {}K".format(T))
plt.xlabel("Frequency (GHz)")
plt.ylabel("S21 (dB)")

data_dict = {"S21": S21, "pna_power": pna_power, "f": f, "T": T, "VNA_att": VNA_att}
file_path, file_name = save_data_dict(
    data_dict,
    test_type=test_type,
    test_name=sample_name + "_" + device_name,
    filedir=filedirectry,
    zip_file=True,
)
plt.savefig(file_path + ".png")
plt.show()

pna.set_sweep_mode("HOLD")

# %%

filedirectry = r"C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\LC11"
sample_name = "LC11_HF"
device_name = "NbN_LN_resonator"

T = 6

test_type = "vary_temsperature_T={}K".format(T)
test_type = test_type.replace(".", "p")

#
power = -30
# pna.set_measurement('S21') #measurement type
pna.set_start(5.5e9)  # starting frequency in Hz
pna.set_stop(11e9)  # stop freq
pna.set_points(2001)  # number of points
pna.set_if_bw(100)  # if bandwidth
pna.set_power(power)  # power in dBm


f, S21 = pna.single_sweep()
att = pna.get_source_attenuation()


plt.plot(f / 1e9, 20 * np.log10(np.abs(S21)))
plt.title("PNA power = {}, temperature = {}K".format(pna_power, T))
plt.xlabel("Frequency (GHz)")
plt.ylabel("S21 (dB)")

data_dict = {"S21": S21, "power": power, "f": f, "T": T, "att": att}
file_path, file_name = save_data_dict(
    data_dict,
    test_type=test_type,
    test_name=sample_name + "_" + device_name,
    filedir=filedirectry,
    zip_file=True,
)
plt.savefig(file_path + ".png")
plt.show()
