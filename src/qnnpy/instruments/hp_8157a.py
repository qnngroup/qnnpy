import pyvisa


class HP8157A(object):
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

    def set_attenuation_db(self, attenuation_db=10):
        self.write(("ATT %0.1f dB" % attenuation_db))

    def set_beam_block(self, beam_block=True):
        self.write(("D %0.0f" % beam_block))


# att = JDSHA9('GPIB0::10')
