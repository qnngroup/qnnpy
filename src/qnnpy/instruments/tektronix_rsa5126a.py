"""
instrument class for TEKTRONIX RSA5126A
Created on Feb 26, 2020
@author: dizhu
"""

import numpy as np
import pyvisa


class RSA5126A(object):
    """Python class for TEKTRONIX RSA5126A, written by Di Zhu."""

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

    def query_binary_values(self, string):
        return self.pyvisa.query_binary_values(string)

    def idn(self):
        return self.query("*IDN?")

    def reset(self):
        self.write("*RST")

    def get_freq_span(self):
        """return the frequency span in GHz"""
        string = "SENSE:SPECTRUM:FREQUENCY:SPAN?"
        return float(self.query(string).strip()) / 1e9

    def set_freq_span(self, span=1.0):
        """set freq span in GHz"""
        string = "SENSE:SPECTRUM:FREQUENCY:SPAN"
        self.write("{} {}".format(string, span * 1e9))

    def get_freq_center(self):
        """return the frequency span in GHz"""
        string = "SENSE:SPECTRUM:FREQUENCY:CENTER?"
        return float(self.query(string).strip()) / 1e9

    def set_freq_center(self, freq=1.0):
        """set freq span in GHz"""
        string = "SENSE:SPECTRUM:FREQUENCY:CENTER"
        self.write("{} {}".format(string, freq * 1e9))

    def get_spectrum(self, channel=None):
        if channel is None:
            string = "READ:SPEC:TRAC?"
        else:
            string = "READ:SPEC:TRAC{:d}?".format(channel)
        return self.query_binary_values(string)

    def single_scan(self):
        self.write("INITiate:CONTinuous OFF")
        self.write("INITiate:IMMediate")
        s = self.get_spectrum()
        f_start = float(self.query("SPECtrum:FREQuency:STARt?").strip()) / 1e9
        f_stop = float(self.query("SPECtrum:FREQuency:STOP?").strip()) / 1e9
        # f_step = float(self.query('SPECtrum:FREQuency:STEP?').strip())/1e9
        f = np.linspace(f_start, f_stop, len(s))
        return f, s
