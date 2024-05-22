# -*- coding: utf-8 -*-
"""
instrument class for YOKOGAWA AQ6370 OSA
Created on Fri Dec 27 2019
@author: dizhu
"""

from time import sleep

import numpy as np
import pyvisa


class AQ6370(object):
    """Python class for YOKOGAWA AQ6370 OSA, written by Di Zhu."""

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
        return self.query("*IDN?").strip()

    def opc(self):
        "ask if operation is completed"
        msg = self.query("*OPC?").strip()
        if msg == "1":
            return True
        else:
            return False

    def reset(self):
        self.write("*RST")

    def wait(self):
        self.write("*WAI")

    def repeat_sweep(self):
        self.write(":INITIATE:SMOD REPEAT")
        self.write("INIT")

    def abort(self):
        self.write("ABORt")

    def get_sweep_mode(self):
        """get the sweep mode
        1 = SINGle; 2 = REPeat; 3 = AUTO; 4 = SEGMent
        """
        msg = self.query(":INITiate:SMODe?").strip()
        if msg == "1":
            return "SINGLE"
        if msg == "2":
            return "REPEAT"
        if msg == "3":
            return "AUTO"
        if msg == "4":
            return "SEGMENT"

    def set_average(self, num_avg=1):
        """set the number of averagings"""
        self.write(":SENSE:AVERAGE:COUNT {:d}".format(int(num_avg)))
        pass

    def get_average(self):
        """get the number of averagings"""
        return int(self.query(":SENSE:AVERAGE:COUNT?").strip())

    def set_resolution(self, resolution=0.02e-9):
        """set resolution in nm, choices
        .02 nm, .1 nm, .2 nm, .5 nm, 1.0 nm, 2.0 nm"""
        if resolution not in [0.02e-9, 0.1e-9, 0.2e-9, 0.5e-9, 1.0e-9, 2, 0e-9]:
            print("ERROR: input not valid")
            return
        self.write(":SENSE:BANDWIDTH:RESOLUTION {}".format(resolution))

    def set_wl_center(self, wl=1550e-9):
        self.write(":SENSE:WAVELENGTH:CENTER {}".format(wl))

    def get_wl_center(self):
        """center wavelength in m"""
        return float(self.query(":SENSE:WAVELENGTH:CENTER?").strip())

    def set_wl_span(self, span=5e-9):
        self.write(":SENSE:WAVELENGTH:SPAN {}".format(span))

    def get_wl_span(self):
        return float(self.query(":SENSE:WAVELENGTH:SPAN?").strip())

    def set_wl_start(self, start=1550e-9):
        self.write(":SENSE:WAVELENGTH:START {}".format(start))

    def get_wl_start(self):
        return float(self.query(":SENSE:WAVELENGTH:START?").strip())

    def set_wl_stop(self, start=1550e-9):
        self.write(":SENSE:WAVELENGTH:STOP {}".format(start))

    def get_wl_stop(self):
        return float(self.query(":SENSE:WAVELENGTH:STOP?").strip())

    def get_trace(self):
        return self.query(":TRACE:ACTIVE?").strip()

    def set_trace(self, trace="A"):
        self.write(":TRACE:ACTIVE TR{}".format(trace))

    def single_sweep(self):
        self.write(":INITIATE:SMODE SINGLE")
        self.write("INIT")
        # self.write('*WAI')
        wl = self.query(":TRACE:X? {}".format(self.get_trace())).strip().split(",")
        power = self.query(":TRACE:Y? {}".format(self.get_trace())).strip().split(",")
        wl = [float(w) for w in wl]
        power = [float(p) for p in power]
        return np.array(wl), np.array(power)

    def quick_setup(
        self, wl_center=1550e-9, wl_span=2e-9, resolution=0.02e-9, average=1
    ):
        self.set_wl_center(wl_center)
        self.set_wl_span(wl_span)
        self.set_resolution(resolution)
        self.set_average(average)
        sleep(0.5)

    def quick_scan(self, wl_center=1550e-9, wl_span=2e-9):
        self.set_wl_center(wl_center)
        self.set_wl_span(wl_span)
        wl, power = self.single_sweep()
        return wl, power
