import time

import numpy as np
import pyvisa


class Agilent53131a(object):
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

    def basic_setup(self, coupling="AC", impedance="1M"):
        self.write("*RST")
        self.write("*CLS")

        self.write(":EVEN:LEV:AUTO OFF")  # Turn off auto trigger level
        self.write(":EVEN:LEV -0.200V")  # Set trigger level
        self.write(":EVEN:SLOP POS")  # Or POS. Trigger on negative slope
        self.write(":EVEN:HYST:REL 0")  # Set hysteresis 0 indicates high sensitivity
        if coupling == "AC":
            self.write(":INP:COUP AC")  # Or DC.  Input coupling
        elif coupling == "DC":
            self.write(":INP:COUP DC")

        if impedance == "1M":
            self.write(":INP:IMP 1E6")  # Set input impedance to 1 MOhms
        elif impedance == "50":
            self.write(":INP:IMP 50")  # Set input impedance to 50ohms

        self.write(":INP:FILT OFF")  # Turn off 100kHz lowpass filter
        self.write(':FUNC "TOT 1"')  # Totalize on channel 1
        self.write(
            ":TOT:ARM:STAR:SOUR IMM"
        )  # Set start source to immediate (run on command)
        self.write(
            ":TOT:ARM:STOP:SOUR TIM"
        )  # Set stop source to time (wait certain time)
        self.write(":TOT:ARM:STOP:TIM 0.1")  # Set stop time to 100 ms
        self.write(":INP:ATT 1")  # Or 10. Set attenuation factor

    def set_impedance(self, value=0):
        """
        VALUE=0 : IMPEDANCE IS 50OHMS
        VALUE=1 : IMPEDANCE IS 1MOHM

        """
        if value == 0:
            self.write(":INP:IMP 50")
        else:
            self.write(":INP:IMP 1E6")

    def set_coupling(self, value="AC"):
        if value == "AC":
            self.write(":INP:COUP AC")
        else:
            self.write(":INP:COUP DC")

    def set_trigger(self, trigger_voltage=-0.075, trigger_slope=None):
        if trigger_slope == "POS" or trigger_slope == "NEG":
            self.write(
                ":EVEN:SLOP %s" % trigger_slope
            )  # Or POS. Trigger on negative slope
        self.write(":EVEN:LEV %0.3fV" % trigger_voltage)  # Set trigger level

    def count_rate(self, counting_time=0.1):
        self.write(
            ":TOT:ARM:STOP:TIM %0.3f" % counting_time
        )  # Set stop time to # of seconds
        dcr = self.query(":READ?")
        dcr = float(dcr) / counting_time
        # time.sleep(counting_time + 0.1)
        return dcr

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
        return v, np.array(dcr)
