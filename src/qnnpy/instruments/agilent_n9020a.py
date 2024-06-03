from time import sleep

import numpy as np
import pyvisa


class N9020A(object):
    """Python class for Agilent (now Keyseight) N9020A signal analyzer, written by Di Zhu, 2020."""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.rsc = rm.open_resource(visa_name, read_termination="\n")
        self.rsc.timeout = 5000  # Set response timeout (in milliseconds)
        # self.rsc.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.rsc.read()

    def write(self, string):
        self.rsc.write(string)

    def query(self, string):
        return self.rsc.query(string)

    def idn(self):
        self.query("*IDN?")

    def reset(self):
        self.write("*RST")

    def get_freq_start(self):
        string = ":SENSe:FREQuency:STARt?"
        return float(self.query(string).strip())

    def set_freq_start(self, freq):
        string = ":SENSe:FREQuency:STARt {}".format(freq)
        self.write(string)

    def get_freq_stop(self):
        string = ":SENSe:FREQuency:STOP?"
        return float(self.query(string).strip())

    def set_freq_stop(self, freq):
        string = ":SENSe:FREQuency:STOP {}".format(freq)
        self.write(string)

    def set_freq_center(self, freq):
        string = ":SENSe:FREQuency:CENTer {}".format(freq)
        self.write(string)

    def get_freq_center(self):
        string = ":SENSe:FREQuency:CENTer?"
        return float(self.query(string).strip())

    def set_freq_span(self, freq):
        string = ":SENSe:FREQuency:SPAN {}".format(freq)
        self.write(string)

    def get_freq_span(self):
        string = ":SENSe:FREQuency:SPAN?"
        return float(self.query(string).strip())

    def get_avg_count(self):
        string = ":SENSe:AVERage:COUNt?"
        return int(self.query(string).strip())

    def set_avg_count(self, count):
        string = ":SENSe:AVERage:COUNt {}".format(count)
        self.write(string)

    def clear_avg(self):
        self.write(":SENSe:AVERage:CLEar")

    def get_bw(self):
        return float(self.query(":SENSe:BANDwidth:RESolution?").strip())

    def set_bw(self, bw):
        self.write(":SENSe:BANDwidth:RESolution {}".format(bw))

    def set_bw_auto(self, auto="True"):
        if auto:
            self.write(":SENSe:BANDwidth:AUTO ON")
        else:
            self.write(":SENSe:BANDwidth:AUTO OFF")

    def get_bw_auto(self):
        flag = self.query("BWID:AUTO?").strip()
        if flag == "0":
            return False
        if flag == "1":
            return True

    def get_data(self):
        data = self.query("FETCh:SANalyzer?").strip()
        data = data.split(",")
        f = data[0::2]
        f = [float(i) for i in f]
        p = data[1::2]
        p = [float(i) for i in p]
        return f, p

    def single_scan(self):
        self.write(":INIT:CONT OFF")
        self.write(":INITiate:RESTart")
        sleep(self.get_sweep_time())
        f, p = self.get_data()
        return f, p

    def get_sweep_time(self):
        return float(self.query(":SENS:SWE:TIME?").strip())

    def quick_scan(self, freq_center=2e9, freq_span=100e6, bw=100e3, avg=1):
        self.set_freq_center(freq_center)
        self.set_freq_span(freq_span)
        self.set_bw(bw)
        # self.set_avg_count(avg)
        f, p = self.averaged_scan(avg)
        return f, p

    def averaged_scan(self, avg=10):
        for i in range(avg):
            f, p = self.single_scan()
            if i == 0:
                p_total = np.array(p)
            else:
                p_total = p_total + np.array(p)
        return f, p_total / avg
