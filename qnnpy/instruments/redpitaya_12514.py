# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 15:02:29 2022

@author: QNN_LabUser
"""

import visa


class RedPitaya(object):
    """

    Python Class for RedPitaya. Created by Owen Medeiros 2022.

    example visa_name 'TCPIP::18.25.31.186::5000::SOCKET'

    """

    def __init__(self, visa_name):
        rm = visa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name, read_termination="\r\n")
        self.pyvisa.timeout = 10000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        text = self.pyvisa.read()
        text = text.replace("ERR!", "")
        return text

    def read_raw(self):
        return self.pyvisa.read_raw()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def get_buffer_size(self):
        return int(self.query("ACQ:BUF:SIZE?"))

    def set_output(self, output=True, chan=1):
        if output:
            self.write("OUTPUT%s:STATE ON" % chan)
        else:
            self.write("OUTPUT%s:STATE OFF" % chan)

    def set_freq(self, freq, chan=1):
        print("SOUR%s:FREQ:FIX %s" % (chan, freq))
        self.write("SOUR%s:FREQ:FIX %s" % (chan, freq))

    def set_waveform(self, wf="SINE", chan=1):
        """{SINE, SQUARE, TRIANGLE, SAWU, SAWD, PWM, ARBITRARY, DC, DC_NEG}"""
        self.write("SOUR%s:FUNC %s" % (chan, wf))

    def set_amplitude(self, voltage, chan=1):
        self.write("SOUR%s:VOLT %s" % (chan, voltage))

    def send_waveform(self, string, chan=1):
        self.write("SOUR%s:TRAC:DATA:DATA " % (chan) + string)


# rm = visa.ResourceManager()
# IP = '18.25.31.186' ## your Red Pitaya's IP
# PORT = 5000
# RP = rm.open_resource('TCPIP::' + IP + '::' + str(PORT) + '::SOCKET', read_termination='\r\n')
# for i in range(1, 8):
#     RP.write('DIG:PIN LED' + str(i) + ',' + str(1))
#     time.sleep(0.1)
#     RP.write('DIG:PIN LED' + str(i) + ',' + str(0))
#     time.sleep(0.1)

# print(RP.query('*IDN?'))
