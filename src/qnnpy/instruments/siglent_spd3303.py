import pyvisa


class SPD3303(object):
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # set response timeout (in milliseconds)

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        return self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    #### implement functions specific to this machine ####

    # turn on channel
    def set_channel_on(self, channel):
        # input: channel number as string or int
        string = "OUTPut CH{},ON"
        self.write(string.format(channel))

    # turn off channel
    def set_channel_off(self, channel):
        # input: channel number (str or int)
        string = "OUTPut CH{},OFF"
        self.write(string.format(channel))

    # set selected channel
    def set_selected_channel(self, channel):
        # input: channel number (str or int)
        string = "INSTrument CH{}"
        self.write(string.format(channel))

    # get selected channel
    def get_selected_channel(self):
        # return: currently selected channel (str)
        string = "INSTrument?"
        return self.query(string)

    # set current
    def set_current(self, channel, current):
        # inputs: channel number (str or int), current (str or float or int)
        string = "CH{}:CURRent {}"
        self.write(string.format(channel, current).strip())

    # get current
    def get_current(self, channel):
        # inputs: channel number (str or int)
        string = "CH{}:CURRent?"
        return self.query(string.format(channel).strip())

    # set voltage
    def set_voltage(self, channel, voltage):
        # inputs: channel number (str or int), voltage (str or float or int)
        string = "CH{}: VOLTage {}"
        self.write(string.format(channel, voltage).strip())

    # get voltage
    def get_voltage(self, channel):
        # inputs: channel number (str or int)
        string = "CH{}: VOLTage?"
        return self.query(string.format(channel).strip())

    # query for errors (returns 0 if no error)
    def query_error(self):
        string = "SYSTem: ERRor?"
        return self.query(string)
