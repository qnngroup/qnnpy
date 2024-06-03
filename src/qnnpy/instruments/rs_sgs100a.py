import pyvisa


class SGS100A(object):
    """Python class for Agilent 53131a counter, written by Adam McCaughan
    Use like c = Agilent53131a('GPIB0::3')"""

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
        self.write("*CLS")

    def basic_setup(self):
        self.reset()
        self.write(":SOURce:OPMode NORMal")
        self.write(":SOURce:FREQuency:CW 2 GHz")
        self.write(":SOURce:POWer -10dBm")
        self.write(":OUTPut:STATe OFF")

    def set_output_attenautor_mode(self, mode="AUTO"):
        """set the attenautor mode on the output
        AUTO | FIXed | APASsive"""
        self.write(":OUTPut:AMODe {}".format(mode))

    def set_output(self, state="OFF"):
        """activates/deactivates the rf output
        parameters: 0, 1, OFF, ON"""
        self.write(":OUTPut:STATe {}".format(state))

    def set_frequency(self, freq=2.0):
        """set frequency in GHz"""
        self.write(":SOURce:FREQuency:CW {:f} GHz".format(freq))

    def set_power(self, power=-30):
        """set power in dBm
        the manual says range: -20 to 25, increment: 0.01, *RST -10"""

        self.write(":SOURce:POWer {}dBm".format(power))
