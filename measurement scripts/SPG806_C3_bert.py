# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 18:28:03 2023

@author: QNN
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 13:01:57 2023

@author: QNN
"""

import sys

sys.path.append(r"Q:\qnnpy")
import numpy as np
import qnnpy.functions.snspd as snspd
import qnnpy.functions.ntron as nt
from qnnpy.instruments.lakeshore336 import Lakeshore336
import qnnpy.functions.functions as qf

config = r"S:\SC\Measurements\SPG806\SPG806_config.yml"

import time
from time import sleep

from matplotlib import pyplot as plt
import random

# %% CREATE WAVEFORMS
plt.close()
num_samples = 200

write_0 = np.zeros(num_samples)
write_1 = np.zeros(num_samples)
enable_signal = np.zeros(num_samples)


channel_level = 1
read_level = 1.5
wr_ratio = read_level / channel_level

enable_level_write = 1
enable_level_read = 1

channel_start = 50
channel_width = 25

enable_start = 45
enable_width = 20

read_delay = 100
read_width = 50

# write 1
write_1[channel_start : channel_start + channel_width] = channel_level
enable_signal[enable_start : enable_start + enable_width] = enable_level_write

# read 1
# channel_signal[read_delay:read_delay+read_width] = np.linspace(0,read_level,read_width)
write_1[read_delay : read_delay + read_width] = read_level
enable_signal[read_delay : read_delay + read_width] = enable_level_read


# write 0
write_0[channel_start : channel_start + channel_width] = -channel_level
enable_signal[enable_start : enable_start + enable_width] = enable_level_write

# read 0
# channel_signal[read_delay:read_delay+read_width] = np.linspace(0,read_level,read_width)
write_0[read_delay : read_delay + read_width] = read_level
enable_signal[read_delay : read_delay + read_width] = enable_level_read


plt.plot(write_0, label="write_0")
plt.plot(write_1, label="write_1")

plt.plot(enable_signal, label="enable")
plt.legend()
plt.ylabel("amplitude")
plt.xlabel("points")

plt.show()
plt.close()

b = nt.nTron(config)
b.inst.awg.set_arb_wf(write_0, name="WRITE0", num_samples=2**8, chan=1)
b.inst.awg.set_arb_wf(write_1, name="WRITE1", num_samples=2**8, chan=1)
b.inst.awg.set_arb_wf(enable_signal, name="ENAB", num_samples=2**8, chan=1)


# %%
startTime = time.time()


byte_list = [f"{x:08b}" for x in range(0, 256)]

chan = 1
name = "CHAN"
b.inst.awg.write("*CLS")  # clear status
b.inst.awg.write(f"SOURce{chan}:DATA:VOLatile:CLEar")  # clears volatile waveform memory

write1 = '"INT:\WRITE1.ARB"'
write0 = '"INT:\WRITE0.ARB"'

b.inst.awg.set_output(False, 1)
b.inst.awg.set_output(False, 2)

for j in range(0, 10000):
    i = random.randint(0, 255)
    write_string = []
    start_flag = True
    for c in byte_list[i]:
        if start_flag == True:
            suffix = ",0,once,highAtStartGoLow,50"
        else:
            suffix = ",0,once,maintain,50"

        if c == "0":
            write_string.append(write0 + suffix)
        if c == "1":
            write_string.append(write1 + suffix)

        start_flag = False
    write_string = ",".join(write_string)

    print(byte_list[i])
    print(write_string)

    chan = 1
    name = "CHAN"
    sequence = f'"{name}",{write_string}'
    n = str(len(sequence))
    header = f"SOUR{chan}:DATA:SEQ #{len(n)}{n}"
    message = header + sequence
    b.inst.awg.write(
        f"SOURce{chan}:DATA:VOLatile:CLEar"
    )  # clears volatile waveform memory

    b.inst.awg.write(f"MMEM:LOAD:DATA{chan} {write0}")
    b.inst.awg.write(f"MMEM:LOAD:DATA{chan} {write1}")

    b.inst.awg.pyvisa.write_raw(message)
    b.inst.awg.write(f"SOURce{chan}:FUNCtion:ARBitrary {name}")
    b.inst.awg.get_error()

    chan = 2
    name = "ENAB"
    b.inst.awg.write(
        f"SOURce{chan}:DATA:VOLatile:CLEar"
    )  # clears volatile waveform memory

    enab_start = '"INT:\ENAB.ARB",0,once,highAtStartGoLow,50'
    enab_string = '"INT:\ENAB.ARB",0,once,maintain,50'
    write_string = []
    write_string.append(enab_start)
    write_string.extend(list(np.tile(enab_string, 7)))
    write_string = ",".join(write_string)
    sequence = f'"{name}",{write_string}'
    n = str(len(sequence))
    header = f"SOUR{chan}:DATA:SEQ #{len(n)}{n}"
    message = header + sequence

    b.inst.awg.write(f'MMEM:LOAD:DATA{chan} "INT:\ENAB.ARB"')

    b.inst.awg.pyvisa.write_raw(message)
    b.inst.awg.write(f"SOURce{chan}:FUNCtion:ARBitrary {name}")
    b.inst.awg.get_error()

    b.inst.awg.set_arb_sync()
    channel_voltage = 10e-3 * wr_ratio
    enable_voltage = 160e-3
    b.inst.awg.set_vpp(channel_voltage, 1)
    b.inst.awg.set_vpp(enable_voltage, 2)

    b.inst.awg.set_output(True, 1)
    b.inst.awg.set_output(True, 2)

    sleep(1)
    b.inst.scope.set_trigger_mode("Single")

    byte_meas = []
    byte_meas.append(b.inst.scope.get_parameter_value("P3"))
    byte_meas.append(b.inst.scope.get_parameter_value("P4"))
    byte_meas.append(b.inst.scope.get_parameter_value("P5"))
    byte_meas.append(b.inst.scope.get_parameter_value("P6"))
    byte_meas.append(b.inst.scope.get_parameter_value("P7"))
    byte_meas.append(b.inst.scope.get_parameter_value("P8"))
    byte_meas.append(b.inst.scope.get_parameter_value("P9"))
    byte_meas.append(b.inst.scope.get_parameter_value("P10"))
    byte_meas = np.array(byte_meas)
    byte_meas = "".join((byte_meas > 5e-3).astype(int).astype(str))

    # b0 = b.inst.scope.get_parameter_value('P3')
    # b1 = b.inst.scope.get_parameter_value('P4')
    # b2 = b.inst.scope.get_parameter_value('P5')
    # b3 = b.inst.scope.get_parameter_value('P6')
    # b4 = b.inst.scope.get_parameter_value('P7')
    # b5 = b.inst.scope.get_parameter_value('P8')
    # b6 = b.inst.scope.get_parameter_value('P9')
    # b7 = b.inst.scope.get_parameter_value('P10')
    if byte_meas != byte_list[i]:
        print("ERROR")
        sleep(1)
        data1 = b.inst.scope.get_wf_data("C2")
        data2 = b.inst.scope.get_wf_data("C4")

        plt.plot(data1[0] * 1e6, data1[1] * 1e3, label="channel")
        plt.plot(data2[0] * 1e6, data2[1] * 1e3, label="enable")
        plt.legend()
        plt.title(f"Byte written {byte_list[i]}, Byte read {byte_meas}")
        plt.show()
        sleep(1)

        data_dict = {
            "channel_voltage": channel_voltage,
            "enable_voltage": enable_voltage,
            "trace_chan": data1,
            "trace_enab": data2,
            "bit_string": byte_list[i],
            "byte_meas": byte_meas,
        }
        file_path = qf.save(b.properties, "nMem_bert_test_prbs2", data_dict)
        plt.savefig(file_path + ".png")
        b.inst.scope.save_screenshot(
            file_path + "screen_shot" + ".png", white_background=False
        )

    else:
        print("Correct!")

    # b.inst.scope.set_trigger_mode('Normal')

    b.inst.awg.set_output(False, 1)
    b.inst.awg.set_output(False, 2)

executionTime = time.time() - startTime
print("Execution time in seconds: " + str(executionTime))
