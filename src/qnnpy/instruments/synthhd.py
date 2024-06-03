import serial


class SynthHD:
    allowed_chns = [-1, 0, 1]  # -1 means the last one

    def __init__(self, port="auto"):
        self.isinit = False
        self._cur_chn = 0
        self.on = [0, 0]
        self.freqs = [1000.0, 1000.0]
        self.powers = [0.0, 0.0]
        if port == "auto":
            # find if a SynthHD device is in the serial interface
            print("not implemented yet; please specify port manually")
            pass
        else:
            try:
                self.ser = serial.Serial(port)
                self.isinit = True
            except (OSError, serial.SerialException) as err:
                print("An error occurred when trying to connect to %s:\n" % port, err)
                print("Device not initialized")

    def __del__(self):
        if self.initialized():
            self.ser.close()

    def initialized(self):
        """Method to query if the port has been initialized"""
        return self.isinit

    ### channel related methods
    def _chn(self, chn):
        """return corrected channel number"""
        if chn in SynthHD.allowed_chns:
            return self._cur_chn if chn == -1 else chn
        else:
            print("Warning: Channel Invalid. Set to Default Channel " % self._cur_chn)

    def get_channel(self):
        """return the current channel"""
        return self._cur_chn

    def check_channel(self, chn):
        """check if the supplied"""
        return True if chn in SynthHD.allowed_chns else False

    def set_channel(self, chn):
        if self.check_channel(chn):
            self._cur_chn = self._chn(chn)
            self.ser.write(b"C%d" % chn)
        else:
            print("Error: Only Channel A(0) and B(1) are available")

    ### settings
    def _set_output(self, chn, val):
        self.set_channel(chn)
        # set power to high
        self.on[chn] = val
        self.ser.write(b"E%dr%d" % (val, val))

    def open(self, chn=-1):
        """-1 means the current"""
        if self.check_channel(chn):
            self._set_output(chn, 1)
        else:
            print("Channel Invalid: ", chn)

    def close(self, chn=-1):
        """-1 means the current"""
        if self.check_channel(chn):
            self._set_output(chn, 0)
        else:
            print("Channel Invalid: ", chn)

    def open_all(self):
        for chn in SynthHD.allowed_chns[1:]:
            self.open(chn)

    def close_all(self):
        for chn in SynthHD.allowed_chns[1:]:
            self.close(chn)

    def set_freq(self, freq):
        """in MHz"""
        if isinstance(freq, list):
            # validity check
            self.freqs = freq[: len(SynthHD.allowed_chns) - 1]
            for idx, chn in enumerate(SynthHD.allowed_chns[1:]):
                # print(chn, freq[idx])
                self.set_channel(chn)
                self.ser.write(b"f%.5f" % freq[idx])
        else:
            #        elif type(freq) in [float,int]:
            self.freqs[self._cur_chn] = freq  # freq[:len(SynthHD.allowed_chns)-1]
            self.set_channel(self._cur_chn)
            self.ser.write(b"f%.5f" % freq)

    #        else:
    #            print('Error: Frequency not valid. ', freq)

    def set_power(self, power):
        if isinstance(power, list):
            # validity check
            self.powers = power
            for idx, chn in enumerate(SynthHD.allowed_chns[1:]):
                # print(chn, power[idx])
                self.set_channel(chn)
                self.ser.write(b"W%.5f" % power[idx])

        else:  # type(power) in [float,int]:
            self.powers[self._cur_chn] = power  # freq[:len(SynthHD.allowed_chns)-1]
            self.set_channel(self._cur_chn)
            self.ser.write(b"W%.5f" % power)

    #        else:
    #            print('Error: Power not valid. ', power)

    def get_power(self):
        return self.powers


# def serial_ports():
#     """ Lists serial port names

#         :raises EnvironmentError:
#             On unsupported or unknown platforms
#         :returns:
#             A list of the serial ports available on the system
#     """
#     if sys.platform.startswith('win'):
#         ports = ['COM%s' % (i + 1) for i in range(256)]
#     elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
#         # this excludes your current terminal "/dev/tty"
#         ports = glob.glob('/dev/tty[A-Za-z]*')
#     elif sys.platform.startswith('darwin'):
#         ports = glob.glob('/dev/tty.*')
#     else:
#         raise EnvironmentError('Unsupported platform')

#     result = []
#     for port in ports:
#         try:
#             s = serial.Serial(port)
#             s.close()
#             result.append(port)
#         except (OSError, serial.SerialException):
#             pass

# serial_ports()
