import pyvisa

class Keithley2700(object):
    """Python class for Keithley 2700 Data Acquisition System, written by Adam McCaughan"""
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 50000000 # Set response timeout (in milliseconds)
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
    
    # def set_compliance_v(self, compliance_v = 10e-6):
    #     self.write(':SENS:VOLT:PROT %0.3e' % compliance_v)
    def set_Zin_10Mohm(self):
        self.write('VOLT:IDIV ON')
        
    def set_Zin_10Gohm(self):
        self.write('VOLT:IDIV OFF')
        
    def setup_filter(self, filter_type = 'MOV', window = '0.1', count = '100'):
        self.write(':VOLT:AVER:TCON '+ filter_type) #Select filter type; # <name> = MOVing or REPeat. (Note 2)
        self.write(':VOLT:AVER:WIND '+ window) # Set filter window in %; <NRf> = 0 to 10. 0.1
        self.write(':VOLT:AVERage:COUN '+ count)  # Specify filter count; <n> = 1 to 100. 10

    def set_DCV(self):
        self.write('VOLT:DC')
    
    def set_filter(self, state = 'OFF'):
        self.write(':VOLT:AVER:STAT ' + state) # Enable or disable the filter. 


