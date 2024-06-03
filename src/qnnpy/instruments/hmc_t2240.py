# -*- coding: utf-8 -*-
"""
instrument class for HMC0T2240 singal gnerator
Created on Fri Dec 27 12:16:08 2019
@author: dizhu
"""

import pyvisa


class TMC_T2240(object):
    """Python class for HMC0T2240 singal gnerator, written by Di Zhu."""

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

    def idn(self):
        return self.query("*IDN?").strip()

    def reset(self):
        self.write("*CLS;*SRE 0; *ESE 0; STATus:PRESet")

    def set_output(self, state=False):
        """turn on/off the output"""
        if not state:
            self.write("OUTP OFF")
        else:
            self.write("OUTP ON")

    def get_output(self):
        """get the status of the output"""
        result = self.query("OUTP?").strip()
        if result == "0":
            return "OFF"
        else:
            return "True"

    def set_freq(self, freq):
        """set frequency in GHz"""
        self.write("freq {}".format(freq * 1e9))

    def get_freq(self):
        """get frequency in GHz"""
        return float(self.query("freq?").strip()) / 1e9

    def set_power(self, power=-60, max_power=-12):
        """set power in dBm"""
        if power < max_power:
            self.write("POW {}".format(power))
        else:
            print(
                "Warning: set power exceeded preset limit, double confirm amplifier specs and explicitly adjust 'max_power'"
            )

    def get_power(self):
        """get power in dBm"""
        return float(self.query("POW?").strip())
