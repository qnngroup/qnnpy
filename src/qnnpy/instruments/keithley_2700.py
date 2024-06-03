from enum import Enum

import pyvisa


class MeasFunction(Enum):
    VOLT = 1
    VOLTAC = 2
    CURR = 3
    CURRAC = 4
    RES = 5  # 2pt res
    FRES = 6  # 4pt res
    FREQ = 7
    PER = 8
    TEMP = 9


class Keithley2700(object):
    """Python class for Keithley 2700 Data Acquisition System, written by Adam McCaughan"""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 50000000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def local_key(self):
        self.write("SYST:KEY 17")

    def reset(self):
        self.write("*RST")

    def read_voltage(self):
        self.write("FUNC 'VOLT'")
        read_str = self.query(":READ?")
        # Returns something like '+1.99919507E-01VDC,+6283.313SECS,+60584RDNG#'
        E_location = read_str.find("E")  # Finds location of E in read value
        voltage_str = read_str[0 : read_str.find("E") + 4]
        return float(voltage_str)  # Return just the first number (voltage)

    def read_resistance(self):
        self.write("FUNC 'RES'")
        read_str = self.query(":READ?")
        E_location = read_str.find("E")
        res_str = read_str[0 : read_str.find("E") + 4]
        return float(res_str)

    def set_Zin_10Mohm(self):
        self.write("VOLT:IDIV ON")

    def set_Zin_10Gohm(self):
        self.write("VOLT:IDIV OFF")

    def setup_filter(self, filter_type="MOV", window="0.1", count="100"):
        self.write(
            ":VOLT:AVER:TCON " + filter_type
        )  # Select filter type; # <name> = MOVing or REPeat. (Note 2)
        self.write(
            ":VOLT:AVER:WIND " + window
        )  # Set filter window in %; <NRf> = 0 to 10. 0.1
        self.write(
            ":VOLT:AVERage:COUN " + count
        )  # Specify filter count; <n> = 1 to 100. 10

    def set_DCV(self):
        self.write("VOLT:DC")

    def set_filter(self, state="OFF"):
        self.write(":VOLT:AVER:STAT " + state)  # Enable or disable the filter.

    def set_autorange(self, meas_fxn):
        if meas_fxn == MeasFunction.CURRAC:
            meas_str = "CURR:AC"
        elif meas_fxn == MeasFunction.VOLTAC:
            meas_str = "VOLT:AC"
        else:
            meas_str = str(meas_fxn)
        self.write(f"{meas_str}:RANG:AUTO ON")

    def resistance_configure4p(self):
        # Configure the instrument for 4-point resistance measurement
        self.pyvisa.write(
            "ROUTe:SCAN ((@101,102))"
        )  # Configure single channel for 2-point measurement
        self.pyvisa.write("SENS:FUNC 'FRES'")  # Set the function to measure resistance
        self.pyvisa.write("SENS:FRES:NPLC 10")  # Set integration time to 10 PLC
        self.pyvisa.write("SENS:FRES:RANG 10M")  # Enable auto-range

    def read_resistance4p(self):
        # Perform the 4-point measurement
        self.pyvisa.write("INIT")
        self.pyvisa.write("*WAI")  # Wait for the measurement to complete
        read_str = self.pyvisa.query("FETCh?")  # Query the resistance value
        E_location = read_str.find("E")
        res_str = read_str[0 : read_str.find("E") + 4]
        return float(res_str)
