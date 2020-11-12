import pyvisa

class Keithley2700(object):
    """Python class for Keithley 2700 Data Acquisition System, written by Adam McCaughan"""
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000 # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()
    
    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

        
    def reset(self):
        self.write('*RST')
    def read_voltage(self):
        read_str = self.query(':READ?')
        # Returns something like '+1.99919507E-01VDC,+6283.313SECS,+60584RDNG#'
        E_location = read_str.find('E') # Finds location of E in read value
        voltage_str = read_str[0 : read_str.find('E')+4]
        return float(voltage_str) # Return just the first number (voltage)
        