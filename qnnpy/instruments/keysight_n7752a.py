# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 16:12:41 2022

@author: omedeiro
"""

import pyvisa
import numpy as np
import time
from enum import Enum

class PowerUnit(Enum):
    DBM = 0
    WATT = 1

class N7752A(object):
    """
    Python class for Keysight N7752A Optical Attenuator, modfied from JDS by Emma Batson.
    
    Original python class for JDS HJA9 Optical Attenuator, written by Adam McCaughan."""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000 # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands
        self.attenuation = 0

    def read(self):
        return self.pyvisa.read()
    
    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)
    
    def read_power(self, channel=1):
        # returns around -6e1 or -7e1 with laser off
        return self.query('READ{}:POW?'.format(channel))
    
    def get_attenuation(self, channel=1):
        return self.query('INP{}:ATT?'.format(channel))
    
    def get_output_power(self, channel=1):
        return self.query('OUTP{}:POW?'.format(channel))
    
    def get_beam_block(self, channel=1):
        return self.query('OUTP{}:STAT?'.format(channel))
    
    def toggle_power_control(self, pow_control=False, channel=1):
        self.write('OUTP{}:POW:CONTR {}'.format(channel, int(pow_control)))


    def set_attenuation_db(self, attenuation_db = 10, channel=1):
        self.write('INP{}:ATT {}'.format(channel, attenuation_db))
        self.attenuation = attenuation_db

    def set_beam_block(self, beam_block = True, channel=1):
        self.write('OUTP{}:STAT {}'.format(channel, int(not beam_block)))


# att = JDSHA9('GPIB0::10')