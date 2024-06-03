import visa
from ThorlabsPM100 import ThorlabsPM100


class ThorlabsPM100Meta(ThorlabsPM100):
    def __init__(self, USB_address, verbose=False):
        rm = visa.ResourceManager()
        inst = rm.open_resource(USB_address)
        self._verbose = verbose
        self._inst = inst

    def reset(self):
        self.status.questionable.preset()

    def set_wavelength(self, wavelength):
        self.sense.correction.wavelength = wavelength
        # wavelength in nm

    def read_value(self):
        # stable = False
        # while not stable:
        #     value = self.read
        #     sleep(0.1)
        #     value1 = self.read
        #     if (value1 - value)/value < 1e-2
        #         stable = True
        self.sense.average.count = 10
        return self.read
