import numpy as np
import pyvisa


class ThorlabsPM100D(object):
    """Python class for Thorlabs PM100, written by Adam McCaughan."""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name, read_termination="\n")
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
        self.set_wavelength(1550)
        self.set_auto_range()

    def set_auto_range(self, state=1):
        self.write("CURR:DC:RANG:AUTO{}".format(state))

    def get_auto_range(self):
        return self.query("CURR:DC:RANG:AUTO?")

    def set_wavelength(self, wl=1550):
        self.write("sense:corr:wav {}".format(wl))

    def get_wavelength(self):
        return float(self.query("sense:corr:wav?").strip())

    def get_power(self, unit="W", repetition=10):
        power = []
        # unit takes W or dBm
        if unit != "W" and unit != "dBm":
            print("invalid unit")
            return 0
        else:
            self.write("power:dc:unit " + unit)
            for i in range(repetition):
                power.append(float(self.query("measure:power?").strip()))

            return np.mean(power)
