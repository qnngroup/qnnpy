import pyvisa
import numpy as np

class Lakeshore121(object):
    """Python class for Lakeshore 121 current source, written by Reed Foster"""
    
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands
        self.name = "Lakeshore121"
    
    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)
    
    def reset(self):
        self.write("*RST")

    def in_compliance(self):
        return bool(int(self.query("COMP?")))

    def enable_current(self):
        self.write("IENBL 1")

    def disable_current(self):
        self.write("IENBL 0")
    
    def is_enabled(self):
        return bool(int(self.query("IENBL?")))

    def set_current(self, current):
        if not(100e-9 <= abs(current) <= 100e-3):
            raise ValueError(f"invalid current {current}, must be between 100 nA and 100 mA")
        self.write(f"SETI {current:.2e}")
        self.write("RANGE 13")

    def get_current(self):
        return float(self.query("SETI?"))
    
    def set_range(self, current_range):
        
        """
        0 = 100 nA
        1 = 300 nA
        2 = 1 uA
        3 = 3 uA
        4 = 10 uA
        ...
        12 = 100 mA
        13 = User current
        """
        current_range = int(current_range)
        if not(0 <= current_range <= 13):
            raise ValueError(f"invalid current range {current_range}, must be between 0 and 13.")
        self.write(f"RANGE {current_range}")

    def get_range(self):
        return int(self.query("RANGE?"))
    
    def set_polarity(self, polarity):
        if not(polarity == 1 or polarity == 0):
            raise ValueError(f"invalid polarity {polarity}, must be 0 (pos) or 1 (neg)")
        self.write(f"IPOL {polarity}")
    
    def get_polarity(self):
        return int(self.query("IPOL?"))