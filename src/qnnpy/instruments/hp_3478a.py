import pyvisa


class HP3748A(object):
    """Python class for HP 3478A Multimeter, written by Adam McCaughan"""

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
        # Anything else here that needs to happen on initialization

    # def reset(self):
    # self.write('*RST')
    # def read_volt(self):
    # self.query('VOLT %0.6e' %(vpp))
    # def set_output(self,message='OFF'):
    # self.write_simport('OP' + message[0:2])  # Only uses "OPOF" or "OPON": "OPOFF" does not work
