from enum import Enum, auto

import pyvisa


class MeasType(Enum):
    def __str__(self):
        name = str(self.name)
        if name.isupper():
            return name
        elif "DC" or "AC" in name:
            return name[:-2].upper() + ":" + name[-2:].upper()
        else:
            return name[:-4].upper() + ":" + name[-4:].upper()

    VoltDC = auto()  # VOLT:DC
    CurrDC = auto()  # CURR:DC
    VoltAC = auto()  # VOLT:AC
    CurrAC = auto()  # CURR:AC
    RES = auto()  # 2-pt res
    FRES = auto()  # 4-pt res
    TEMP = auto()  # temp
    FREQ = auto()  # freq
    VoltFreq = auto()  # VOLT:FREQ
    CurrFreq = auto()  # CURR:FREQ


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

    def local_key(self):
        self.write("SYST:KEY 7")

    def read_voltage(self):
        self.write(":CONF:VOLT:DC")
        read_str = self.query(":READ?")
        # Returns something like '+1.99919507E-01VDC,+6283.313SECS,+60584RDNG#'
        E_location = read_str.find("E")  # Finds location of E in read value
        voltage_str = read_str[0 : read_str.find("E") + 4]
        return float(voltage_str)  # Return just the first number (voltage)

    def read_value(self, value=MeasType.VoltDC):
        self.write(":CONF:" + str(value))
        read_str = self.query(":READ?")
        # Returns something like '+1.99919507E-01VDC,+6283.313SECS,+60584RDNG#'
        E_location = read_str.find("E")  # Finds location of E in read value
        value_str = read_str[0 : read_str.find("E") + 4]
        return float(value_str)  # Return just the first number (voltage)
