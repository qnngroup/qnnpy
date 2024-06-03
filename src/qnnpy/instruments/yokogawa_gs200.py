# -*- coding: utf-8 -*-
"""
Library for Yokogawa GS-200 DC Voltage/Current Source
Author: Luca Camellini
Version: 0.2
Date: 17th July, 2018

Inspired by amcc's Keithley2400 library

"""

import pyvisa


class YokogawaGS200(object):
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def reset(self):
        self.write("*RST")

    def setup_source_current(self):
        self.write("*RST")
        # Set current source mode
        self.write(":SOUR:FUNC CURR")
        self.write(":SOUR:LEV:AUTO 0E-6")
        # Enable measurement mode
        self.write(":SENS:REM OFF")  # 2 wire
        # self.write(':SENS ON')

    def setup_source_voltage(self):
        self.write("*RST")
        # Set voltage source mode
        self.write(":SOUR:FUNC VOLT")
        self.write(":SOUR:LEV:AUTO 0E-3")
        # Enable measurement mode
        self.write(":SENS:REM OFF")  # 2 wire
        # self.write(':SENS ON')

    # def setup_4W_source_I_read_V(self):
    #     self.write('*RST')
    #     #Set current source mode
    #     self.write(':SOUR:FUNC CURR')
    #     self.write(':SOUR:LEV:AUTO 0E-6')
    #     #Enable measurement mode
    #     self.write(':SENS:REM ON') #4 wire
    #     self.write(':SENS ON')

    #    def set_measurement_time(self, integration_time = 1):
    #        # Set integration time in terms of power line cycle. 1 = 1/60th of a second
    #        # Min = 1, Default = 1, Max = 25
    #        self.write(':SENS :NPLC %i' %integration_time)

    # Need setup_read_volt first
    #    def read_volt(self):
    #        voltage = self.query(':MEAS?')
    #        return voltage #returns real number - see 13-17
    #
    #    #Need setup_read_curr first
    #    def read_curr(self):
    #        current = self.query(':MEAS?')
    #        return current #returns real number - see 13-17

    def set_current_range(self, ran=1):
        # Remember: Yokogawa has no auto-range feature!
        # 1 -> 1mA
        # 2 -> 10mA
        # 3 -> 100mA
        # 4 -> 200mA
        # You can also let the instrument choose the range for the current value you apply
        # Use set_current_autorange
        if ran == 1:
            self.write(":SOUR:RANG 1E-3")
        elif ran == 2:
            self.write(":SOUR:RANG 10E-3")
        elif ran == 3:
            self.write(":SOUR:RANG 100E-3")
        elif ran == 4:
            self.write(":SOUR:RANG 200E-3")

    def set_voltage_range(self, ran=1):
        # Remember: Yokogawa has no auto-range feature!
        # 1 -> 10mV
        # 2 -> 100mV
        # 3 -> 1V
        # 4 -> 10V
        # 5 -> 30V
        # You can also let the instrument choose the range for the current value you apply
        # Use set_voltage_autorange
        if ran == 1:
            self.write(":SOUR:RANG 10E-3")
        elif ran == 2:
            self.write(":SOUR:RANG 100E-3")
        elif ran == 3:
            self.write(":SOUR:RANG 1E+0")
        elif ran == 4:
            self.write(":SOUR:RANG 10E+0")
        elif ran == 5:
            self.write(":SOUR:RANG 30E+0")

    def set_current(self, current=0e-6):
        self.write(":SOUR:LEV %0.4e" % current)  # Set current level

    def set_voltage(self, voltage=0e-6):
        self.write(":SOUR:LEV %0.4e" % voltage)  # Set voltage level

    def set_guard(self, guard=False):
        # Guard terminal is used to reduce common ground noise - see page 4-6 of the manual
        if guard is True:
            self.write(":SENS:GUAR ON")
        else:
            self.write(":SENS:GUAR OFF")

    def set_current_autorange(self, current=0e-6):
        self.write(":SOUR:LEV:AUTO %0.4e" % current)  # Set current level

    def set_voltage_autorange(self, voltage=0e-6):
        self.write(":SOUR:LEV:AUTO %0.4e" % voltage)  # Set voltage level

    def set_compliance_i(self, compliance_i=1e-3):
        # Limit value for current when used in voltage source mode
        # from 1 mA to 200 mA
        self.write(":SOUR:PROT:CURR %0.3e" % compliance_i)

    def set_compliance_v(self, compliance_v=1):
        # Limit value for voltage when used in current source mode
        # from 1 V to 30 V
        self.write(":SOUR:PROT:VOLT %0.3e" % compliance_v)

    def read_voltage(self):
        read_str = self.query(":READ?")
        # Returns something like '+1.99919507E-01VDC,+6283.313SECS,+60584RDNG#'
        E_location = read_str.find("E")  # Finds location of E in read value
        voltage_str = read_str[0 : read_str.find("E") + 4]
        return float(voltage_str)  # Return just the first number (voltage)

    def set_output(self, output=False):
        if output is True:
            self.write(":OUTP ON")
        if output is False:
            self.write(":OUTP OFF")
