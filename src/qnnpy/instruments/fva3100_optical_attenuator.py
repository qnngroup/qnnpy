import time

import pyvisa


class FVA3100(object):
    """Python class for FVA3100 Optical Attenuator, written by Adam McCaughan."""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        self.wait_time = 5  # in second #this optical attenuator switches very slowly
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def set_attenuation_db(self, attenuation_db=-10):
        self.write(
            ("ATT %0.1f dB" % -attenuation_db)
        )  # this attenuator has a different convention; it takes negative value as attenuation
        time.sleep(self.wait_time)

    def set_beam_block(self, beam_block=True):
        # self.write(('D %0.0f' % beam_block))  #it appears that the beam blocker for this attenuator is broken. Instead, we set -80 dB attenuation
        if beam_block:
            self.write("ATT -80")
            time.sleep(self.wait_time)


# att = JDSHA9('GPIB0::10')
