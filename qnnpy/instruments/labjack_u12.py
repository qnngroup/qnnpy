# note: need to pip install LabJackPython to use
import u12

class LabJackU12(object):
    """Python class for LabJack U12, written by Emma Batson. 
    https://labjack.com/products/u12
    https://labjack.com/support/software/examples/u12/python
    """
    def __init__(self, debug=False):
        self.device = u12.U12(debug)

    def write_digital(self, channel, state):
        self.device.eDigitalOut(channel, state)

    def read_digital(self, channel):
        read_info = self.device.eDigitalIn(channel)
        return read_info['state']

    def read_analog(self, channel):
        read_info = self.device.eAnalogIn(channel)
        return read_info['voltage']