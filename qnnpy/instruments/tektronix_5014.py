# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 22:19:54 2022

@author: omedeiro
"""

import pyvisa


class Tektronix5014(object):
    """"""

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

    def set_amplitude(self, v=0.02, chan=1):
        self.write("SOUR%s:VOLT %s" % (chan, v))

    def set_high(self, v=0.02, chan=1):
        self.write("SOUR%s:VOLT %s" % (chan, v))
        self.write("SOUR%s:VOLT:OFFS %s" % (chan, v / 2))
