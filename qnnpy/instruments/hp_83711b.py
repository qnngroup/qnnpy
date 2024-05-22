# -*- coding: utf-8 -*-
"""
instrument class for HP 83711B signal generator
Created on Feb 26, 2020
@author: dizhu
"""

import pyvisa


class HP83711B(object):
    """Python class for HP 83711B, written by Di Zhu."""

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

    def idn(self):
        string = "*IDN?"
        return self.query(string)

    def reset(self):
        self.write("*RST")
        self.write(":UNIT:POW DBM")

    def get_freq(self):
        string = "FREQ?"
        return float(self.query(string).strip())

    def set_freq(self, freq=3.0):
        """
        this function sets frequency, in unit of GHz
        """
        string = "FREQ {}".format(freq * 1e9)
        self.write(string)

    def set_power(self, power=-30.0):
        """
        set power, in dBm, in .1 resolution
        """
        string = "POW {:.1f}DBM".format(power)
        self.write(string)

    def get_power(self):
        return float(self.query("POW?").strip())

    def get_output(self):
        state = self.query("OUTP?").strip()
        if state == "+1":
            return True
        else:
            return False

    def set_output(self, state=False):
        if state:
            string = ":OUTP ON"
        else:
            string = ":OUTP OFF"
        self.write(string)
