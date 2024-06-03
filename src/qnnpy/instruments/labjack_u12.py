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
        """
        note: this operation may reset the channel to 0 after readout
        """
        read_info = self.device.eDigitalIn(channel)
        return read_info["state"]

    def read_analog(self, channel):
        read_info = self.device.eAnalogIn(channel)
        return read_info["voltage"]

    def set_mux_channel(self, mux_channel, mapping, mux_names):
        """
        mux_channel: channel to switch mux to (base ten)
        mapping: mapping of LabJack digital outputs to
        control device input labels
        mux_names: list of mux channel names used in mapping, in order

        writes the number corresponding to the mux channel
        to LabJack digital outputs
        """
        mux_bin = bin(mux_channel)[2:]
        # prepend 0s for any unused control bits
        while len(mux_bin) < len(mux_names):
            mux_bin.insert(0, 0)
        # reverse endianness so it makes sense
        mux_bin_little = mux_bin[::-1]

        # enable mux
        enable_channel = mapping["EN"]
        self.write_digital(enable_channel, 0)

        # apply digital output according to mapping
        for mux_in, bit in zip(mux_names, mux_bin_little):
            digital_channel = mapping[mux_in]
            self.write_digital(digital_channel, int(bit))

        """mux_bin = bin(mux_channel)[2:]
        print(mux_bin)
        # reverse endianness (direction)
        mux_bin_little = mux_bin[::-1]
        print(mux_bin_little)
        for i in range(len(mux_bin_little)):
            self.write_digital(i, mux_bin_little[i])"""
