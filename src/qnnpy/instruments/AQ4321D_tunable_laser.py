# This file contains the class for the Keithley 2001 Multimeter
import pyvisa


class Keithley2001(object):
    """Python class for Keithley 2001 Multimeter, written by Adam McCaughan"""

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

        # Anything else here that needs to happen on initialization

    def reset(self):
        self.write("*RST")

    def set_voltage_range(self, ran=10):
        self.write(":VOLT:RANG %0.1e" % ran)

    def set_current_range(self, ran=10e-3):
        self.write(":CURR:RANG %0.1e" % ran)

    def set_voltage_rate(
        self, nplcs=1
    ):  # specify read speed in terms of NPLCs. 1 PLC = 1/60th of a second
        self.write(":VOLT:NPLC %0.1e" % nplcs)

    def set_current_rate(
        self, nplcs=1
    ):  # specify read speed in terms of NPLCs. 1 PLC = 1/60th of a second
        self.write(":CURR:NPLC %0.1e" % nplcs)

    def read_voltage(self):
        read_str = self.query(":READ?")
        # Returns something like '+1.99919507E-01VDC,+6283.313SECS,+60584RDNG#'
        E_location = read_str.find("E")  # Finds location of E in read value
        voltage_str = read_str[0 : read_str.find("E") + 4]
        return float(voltage_str)  # Return just the first number (voltage)
