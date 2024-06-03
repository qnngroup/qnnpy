import pyvisa


class Cryocon350(object):
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

    def read_temp(self, channel="A"):
        self.write("KRDG? " + channel + "[term]")  # In form of ":INPUT? A:TEMP", A-D
        t = self.read()
        temperature = float(t[1:8])
        return temperature

        # see manual for other commands
