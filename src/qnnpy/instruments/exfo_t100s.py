"""
instrument class for EXFO T100S-HP tunable laser
Created on Feb 26, 2020
@author: dizhu
"""

import pyvisa


class EXFOT100S(object):
    """Python class for EXFO T100S-HP, written by Di Zhu."""

    def __init__(self, visa_name, timeout=15000):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = timeout  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def get_wl(self):
        return float(self.query("L?").strip().split("=")[1])

    def get_wl_min(self):
        return float(self.query("L? MIN").strip().split("=")[1])

    def get_wl_max(self):
        return float(self.query("L? MAX").strip().split("=")[1])

    def set_wl(self, wl=1550.0):
        wl_min = self.get_wl_min()
        wl_max = self.get_wl_max()
        if wl >= wl_min and wl <= wl_max:
            self.write("L {}".format(wl))
        else:
            print("wavelength out of range")

    def set_apc(self, apc=True):
        if apc:
            self.write("APCON")
        else:
            self.write("APCOFF")

    def reset(self):
        self.write("INIT")
        self.set_apc(apc=True)
        self.set_power_unit(unit="dBm")

    def set_output(self, output=True):
        if output:
            self.write("ENABLE")
        else:
            self.write("DISABLE")

    def set_power_unit(self, unit="dBm"):
        """set power unit: DBM or MW"""
        if unit == "dBm":
            self.write("DBM")
        if unit == "mW":
            self.write("MW")

    def get_power(self):
        power = self.query("P?").strip()
        if power == "DISABLED":
            print("disabled")
        else:
            return float(power.split("=")[1])

    def set_power(self, power=-20.0):
        self.write("P={:.2f}".format(power))
