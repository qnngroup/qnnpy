# -*- coding: utf-8 -*-
"""
Library for Keithley 6485 Picoammeter
Author: Dip Joti Paul
Version: 0.1
Date: 15th Feb, 2023
"""

import pyvisa


class Keithley6485(object):
    """Python class for Keithley 6485 Picoammeter"""

    """Allow 6485 to warm up for at least one hour before conducting the measurements for accuracy"""

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

    def set_user_settings(self):
        self.write("SYST:AZER ON")  # enable autozero correction
        self.write("SYST:ZCH ON")
        self.write("CURR:RANG 2e-9")
        self.write("INIT")
        self.write("SYST:ZCOR:ACQ")
        self.write("SYST:ZCOR ON")
        self.write("SYST:ZCH OFF")
        self.write("CURR:RANG 20e-9")  # 2nA, 20nA, 200nA, 2uA, 20uA, 200uA, 2mA, 20mA
        self.write("CURR:NPLC 2")  # Set integration rate to 2 PLC

    def read_current(self):
        read_str = self.query(":READ?")
        print(read_str)
        # # Returns something like '+1.99919507E-01VDC,+6283.313SECS,+60584RDNG#'
        # E_location = read_str.find('E') # Finds location of E in read value
        # current_str = read_str[0 : read_str.find('E')+4]
        # return float(current_str)           # Return just the first number (current)
