import time
from time import sleep

import numpy as np
import pyvisa


class Keysight53230a(object):
    """Python class for Agilent 53131a counter, written by Adam McCaughan
    Use like c = Agilent53131a('GPIB0::3')"""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def reset(self):
        self.write("*RST")

    def basic_setup(self):
        self.write("*RST")
        self.write("*CLS")
        self.write("CONFigure:TOTalize:TIMed")

        # input
        self.write(":INP1:SLOP POS")
        self.write(":INP1:COUP DC")
        self.write(":INP1:IMP 50")
        self.write(":INP1:LEV 50e-3")
        self.write(":INP1:NREJ OFF")
        # gate
        self.write("SENS:GATE:STAR:SOUR IMM")
        self.write("SENS:TOT:GATE:TIME 10")

        # trigger
        self.write("TRIG:DEL 1e-6")

    def set_impedance(self, value=0):
        """
        VALUE=0 : IMPEDANCE IS 50OHMS
        VALUE=1 : IMPEDANCE IS 1MOHM

        """
        if value == 0:
            self.write(":INP1:IMP 50")
        else:
            self.write(":INP1:IMP 1E6")

    def set_coupling(self, value="AC"):
        if value == "AC":
            self.write(":INP1:COUP AC")
        else:
            self.write(":INP1:COUP DC")

    def count_rate_setup(self, counting_time=0.1):
        stringset = "SENS:TOT:GATE:TIME %0.3f" % counting_time
        self.write(stringset)

    def count_rate(self, counting_time=0.1):
        self.count_rate_setup(counting_time)
        sleep(0.1)
        dcr = self.query(":READ?")
        dcr = float(dcr) / counting_time
        # time.sleep(counting_time + 0.1)
        return dcr

    def set_trigger(self, trigger_voltage=-0.075, trigger_slope=None):
        if trigger_slope == "POS" or trigger_slope == "NEG":
            self.write(
                ":INP1:SLOP %s" % trigger_slope
            )  # Or POS. Trigger on negative slope
        self.write(":INP1:LEV %0.3fV" % trigger_voltage)  # Set trigger level

    def counts_vs_time(self, trigger_voltage=-0.075, counting_time=0.1, total_time=2):
        self.set_trigger(trigger_voltage)
        num_tests = int(total_time / counting_time)
        dcr = []
        t = []
        start_time = time.time()
        for n in range(num_tests):
            dcr.append(self.get_dcr(counting_time))
            t.append(time.time() - start_time)

        return t, dcr

    def scan_trigger_voltage(
        self, voltage_range=[-0.2, 0.2], counting_time=0.1, num_pts=40
    ):
        v = np.linspace(voltage_range[0], voltage_range[1], num_pts)
        dcr = []
        for trigger_voltage in v:
            self.set_trigger(trigger_voltage)
            dcr.append(self.count_rate(counting_time))
            print(
                "Trigger voltage = %0.3f  /  Count rate %0.1f"
                % (trigger_voltage, dcr[-1])
            )
        return v, np.array(dcr) / float(counting_time)
