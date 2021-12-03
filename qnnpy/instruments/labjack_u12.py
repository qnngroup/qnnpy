# note: need to pip install LabJackPython to use
import u12

class LabJackU12(object):
    """Python class for LabJack U12, written by Emma Batson. 
    https://labjack.com/products/u12
    https://labjack.com/support/software/examples/u12/python
    """
    def __init__(self, debug=False):
        self.device = u12.U12(debug=debug)
        self.read_digital(0)
        # note: may need to collect calibration data?

    def write_digital(self, channel, state):
        self.device.eDigitalOut(channel, state)

    def read_digital(self, channel):
        '''
        note: this operation resets the channel to 0 after readout
        '''
        read_info = self.device.eDigitalIn(channel)
        return read_info['state']

    def read_analog(self, channel):
        read_info = self.device.eAnalogIn(channel)
        return read_info['voltage']

    def set_mux_channel(self, mux_channel):
        '''
        mux_channel: channel to switch mux to (base ten)

        writes the number corresponding to the mux channel
        to LabJack digital outputs in binary, starting from 
        IO0
        '''
        mux_bin = bin(mux_channel)[2:]
        print(mux_bin)
        # reverse endianness (direction)
        mux_bin_little = mux_bin[::-1]
        print(mux_bin_little)
        for i in range(len(mux_bin_little)):
            self.write_digital(i, mux_bin_little[i])