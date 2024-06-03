import pyvisa


class Agilent8153A(object):
    """Python class for Agilent 8153A power meter, written by Adam McCaughan"""

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

    def setup_basic(self, lambda_nm=1550, averaging_time=0.1):
        self.write("*RST")
        self.write("INIT1:CONT 1")
        self.set_averaging_time(
            averaging_time=averaging_time
        )  # Sets averaging time, 20ms < value < 3600s
        self.set_wavelength(lambda_nm=lambda_nm)
        # self.write('OUTP 1')

    def set_averaging_time(self, averaging_time=0.1):
        self.write(
            "SENS1:POW:ATIME %0.3e" % averaging_time
        )  # Sets averaging time, 20ms < value < 3600s

    def read_power(self):
        power = float(self.query("READ1:POW?"))  # Returns power in watts
        return power

    def set_wavelength(self, lambda_nm):
        self.write("SENS1:POW:WAVE %0.6e" % (lambda_nm * 1e-9))


# pm = Agilent8153A('GPIB0::22')
