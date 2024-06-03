# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:39:04 2023

@author: QNN
"""

import pyvisa

LAKESHORE_MODE_MAP = {
    "0": "Off",
    "1": "Closed Loop PID",
    "2": "Zone",
    "3": "Open Loop",
    "4": "Monitor Out",
    "5": "Warmup Supply",
}


class Lakeshore336(object):
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

    def reset(self):
        self.write("*RST")

    def read_temp(self, channel="A"):
        self.write("KRDG? " + channel + "[term]")  # In form of ":INPUT? A:TEMP", A-D
        t = self.read()
        temperature = float(t[1:8])
        return temperature

    def set_setpoint(self, setpoint=295, output=1, ramp=0, rate_value=10):
        self.write("SETP " + str(output) + "," + str(setpoint))

    def set_ramp(self, output=1, on=1, rate_value=0.1):
        self.write("RAMP " + str(output) + "," + str(on) + "," + str(rate_value))

    def set_range(self, output=1, range_set=1):
        self.write("RANGE " + str(output) + "," + str(range_set))

    def set_output(self, output=1, mode=0, input_sensor=4, enable=0):
        """Specifies the control mode. Valid entries: 0 = Off, 1 = Closed
        Loop PID, 2 = Zone, 3 = Open Loop, 4 = Monitor Out,
        5 = Warmup Supply"""
        self.write(
            "OUTMODE "
            + str(output)
            + ","
            + str(mode)
            + ","
            + str(input_sensor)
            + ","
            + str(enable)
        )

    def get_setpoint(self, output=1):
        s = self.query("SETP? " + str(output))
        return float(s)

    def get_range(self, output=1):
        s = self.query("RANGE? " + str(output))
        return s

    def get_ramp(self, output=1):
        s = self.query("RAMP? " + str(output))
        return s

    def get_output(self, output=1):
        s = self.query("OUTMODE? " + str(output))
        output = s.split(",")
        MODE = str(output[0])
        INPUT = str(output[1])
        ENABLE = str(output[2])
        return s

    def get_formatted_output(self, output=1):
        s = self.query("OUTMODE? " + str(output))
        output = s.split(",")
        MODE = str(output[0])
        INPUT = str(output[1])
        ENABLE = str(output[2])
        print(
            "MODE: "
            + LAKESHORE_MODE_MAP[MODE]
            + "\n INPUT: "
            + INPUT
            + "\n ENABLE: "
            + str(bool(ENABLE))
        )
        return s

    def all_off(self):
        self.set_range(1, 0)
        self.set_range(2, 0)
        self.set_range(3, 0)
        self.set_range(4, 0)
