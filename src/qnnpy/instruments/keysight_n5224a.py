from time import sleep

import numpy as np
import pyvisa


class KeysightN5224a(object):
    """Python class for KeysightN5224a network analyzer, written by Di Zhu/Owen Medeiros.
    Connect the GPIB cable to GPIB1 (talker and listener)

    http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/SCPI_Command_Tree.htm
    https://helpfiles.keysight.com/csg/N52xxB/Programming/New_Programming_Commands.htm


    """

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands
        # set the data format; this seems to be the only format recognizable
        self.pyvisa.write("FORM ASCii,0")

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def reset(
        self,
        measurement="S21",
        if_bandwidth=1e3,
        start_freq=100e6,
        stop_freq=15e9,
        power=-30,
    ):
        # these two lines delete the calibration.
        # self.write('SYST:PRES')
        # self.write("CALC:PAR:DEL:ALL")

        # self.write("CALC:PAR:DEL") #this command deletes the measurement before setting the measurement below
        # self.set_measurement(measurement)
        self.set_start(start_freq)
        self.set_stop(stop_freq)
        self.set_if_bw(if_bandwidth)
        self.set_sweep_mode("CONT")
        self.set_power(power)

    def set_measurement(self, measurement="S21"):
        current_trace = self.get_trace_catalog()
        if current_trace == "NO CATALOG":
            self.write('CALC:PAR:DEF "{}", {}'.format(measurement, measurement))
            self.write('CALC:PAR:SEL "{}"'.format(measurement))
        self.write('CALC:PAR:MOD:EXT "{}"'.format(measurement))
        trace_name = self.get_trace_catalog()
        trace_name = trace_name.split(",")[0]
        self.write("DISPlay:WINDow1:TRACe1:FEED '{}'".format(trace_name))

    def set_basic(
        self,
        cnum,
        start_freq=100e6,
        stop_freq=15e9,
        power=-30,
        if_bandwidth=1e3,
        points=1001,
    ):
        self.write("SENS{}:FREQ:STAR {}".format(cnum, start_freq))
        self.write("SENS{}:FREQ:STOP {}".format(cnum, stop_freq))
        self.write("SOUR{}:POW {:.2f}".format(cnum, power))
        self.write("SENS{}:BAND {:.2f}".format(cnum, if_bandwidth))
        self.write("SENS{}:SWE:POIN {}".format(cnum, points))

    def set_Sparam(
        self, start_freq=100e6, stop_freq=15e9, power=-30, if_bandwidth=1e3, points=1001
    ):
        self.write("CALC:PAR:DEL:ALL")
        self.write("CALCulate1:PARameter:DEFine:EXT 'Meas1','S11'")
        self.write("CALCulate1:PARameter:DEFine:EXT 'Meas2','S21'")
        self.write("CALCulate1:PARameter:DEFine:EXT 'Meas3','S12'")
        self.write("CALCulate1:PARameter:DEFine:EXT 'Meas4','S22'")

        self.write("DISPlay:WINDow1:STATE ON")
        self.write("DISPlay:WINDow2:STATE ON")
        self.write("DISPlay:WINDow3:STATE ON")
        self.write("DISPlay:WINDow4:STATE ON")

        self.write("DISPlay:WINDow1:TRACe1:FEED 'Meas1'")
        self.write("DISPlay:WINDow2:TRACe1:FEED 'Meas2'")
        self.write("DISPlay:WINDow3:TRACe1:FEED 'Meas3'")
        self.write("DISPlay:WINDow4:TRACe1:FEED 'Meas4'")

        self.set_basic(1, start_freq, stop_freq, power, if_bandwidth, points)
        # self.set_basic(2, start_freq, stop_freq, power, if_bandwidth, points)
        # self.set_basic(3, start_freq, stop_freq, power, if_bandwidth, points)
        # self.set_basic(4, start_freq, stop_freq, power, if_bandwidth, points)

        self.set_sweep_mode("SING")
        # self.write("INITiate:IMMediate")
        while self.get_sweep_mode() != "HOLD":
            sleep(0.1)
        self.set_sweep_mode("CONT")
        self.set_scale_auto_all()

    def set_Sparam2(
        self, start_freq=100e6, stop_freq=15e9, power=-30, if_bandwidth=1e3, points=1001
    ):
        self.write("CALC:PAR:DEL:ALL")
        self.write("CALCulate1:PARameter:DEFine:EXT 'Meas1','S21'")

        self.write("DISPlay:WINDow1:STATE ON")

        self.write("DISPlay:WINDow1:TRACe1:FEED 'Meas1'")

        self.set_basic(1, start_freq, stop_freq, power, if_bandwidth, points)
        self.set_basic(2, start_freq, stop_freq, power, if_bandwidth, points)
        self.set_basic(3, start_freq, stop_freq, power, if_bandwidth, points)
        self.set_basic(4, start_freq, stop_freq, power, if_bandwidth, points)

        self.set_sweep_mode("SING")
        # self.write("INITiate:IMMediate")
        while self.get_sweep_mode() != "HOLD":
            sleep(0.1)
        self.set_sweep_mode("CONT")
        self.set_scale_auto_all()

    def single_sweep(self, channel=1):
        """run a single sweep and get f in Hz, S in real + i*imag form"""
        # self.write("INITiate:CONTinuous OFF")
        self.set_sweep_mode("SING", channel)
        # self.write("INITiate:IMMediate")
        while self.get_sweep_mode() != "HOLD":
            sleep(0.1)
        print(1)
        f = self.get_frequency(channel)
        S = self.read_channel(channel)
        return f, S

    def read_channel(self, channel=1):
        val = self.query("CALC{}:DATA? SDATA".format(channel))
        val = [x.strip() for x in val.split(",")]
        val = [float(x) for x in val]
        real_part = np.array(val[0::2])
        imag_part = np.array(val[1::2])
        S = real_part + 1j * imag_part
        return S

    # strip \n and return a float. OM - i think float() handles \n
    def _pna_getter(self, s):
        return float(s.strip())

    def get_frequency(self, channel=1):
        print(11)
        freq = self.query("CALC{}:X?".format(channel))
        print(12)
        freq = [x.strip() for x in freq.split(",")]
        print(13)
        freq = [float(x) for x in freq]
        print(14)
        return np.array(freq)

    def select_measurement(self, measurement_name="CH1_S11_1"):
        self.write("CALCulate:PARameter:SELect '" + measurement_name + "'")

    # IF bandwidth
    def get_if_bw(self):
        cmd = "SENS:BAND?"
        return self._pna_getter(self.query(cmd))

    def set_if_bw(self, bandwidth=1000):
        self.write("SENS:BAND {:.2f}".format(bandwidth))

    # power
    def get_power(self):
        cmd = "SOUR:POW?"
        return self._pna_getter(self.query(cmd))

    def set_power(self, power=-10):
        """set power in dbm"""
        self.write("SOUR:POW {:.2f}".format(power))

    # frequency range
    def set_start(self, frequency=100e6):
        cmd = "SENS:FREQ:STAR {}".format(frequency)
        self.write(cmd)

    def set_stop(self, frequency=20e9):
        cmd = "SENS:FREQ:STOP {}".format(frequency)
        self.write(cmd)

    def set_center(self, frequency=5e9):
        cmd = "SENS:FREQ:CENT {}".format(frequency)
        self.write(cmd)

    def set_span(self, frequency=5e9):
        cmd = "SENS:FREQ:SPAN {}".format(frequency)
        self.write(cmd)

    def set_points(self, points=201):
        cmd = "SENS:SWE:POIN {}".format(points)
        self.write(cmd)

    def set_calibration(self, state=1):
        """Set measurement must be run first.
        Note: Before using this command you must select a measurement using
        CALC:PAR:SEL. You can select one measurement for each channel.
        """
        cmd = "SENS:CORR {}".format(state)
        self.write(cmd)

    def set_scale_auto(self, window=1):
        cmd = "DISP:WIND{}:Y:AUTO".format(window)
        self.write(cmd)

    def set_scale_auto_all(self):
        """Scales all windows"""
        win = self.query("DISPlay:CATalog?")
        win = win[1:-2]
        for w in win.split(","):
            self.write("DISP:WIND{}:Y:AUTO".format(w))

    def get_start(self):
        cmd = "SENS:FREQ:STAR?;"
        return self._pna_getter(self.query(cmd))

    def get_stop(self):
        cmd = "SENS:FREQ:STOP?;"
        return self._pna_getter(self.query(cmd))

    def get_center(self):
        cmd = "SENS:FREQ:CENT?;"
        return self._pna_getter(self.query(cmd))

    def get_span(self):
        cmd = "SENS:FREQ:SPAN?;"
        return self._pna_getter(self.query(cmd))

    def get_sweep_time(self):
        cmd = "SENS:SWE:TIME?;"
        return self._pna_getter(self.query(cmd))

    # number of points in a sweep
    def get_points(self):
        cmd = "SENS:SWE:POIN?"
        return self._pna_getter(self.query(cmd))

    def get_trace_catalog(self):
        """
        Get the trace catalog, that is a list of trace and sweep types
        from the Pself.
        The format of the returned trace is:
            trace_name,trace_type,trace_name,trace_type...
        """
        return self.query("CALC:PAR:CAT:EXT?").strip().strip('"')

    def get_window_catalog(self):
        return self.query("DISPlay:CATalog?").strip().strip('"')

    # electrical delay
    # def get_electrical_delay():
    #    '''unit s'''
    #    get_cmd='CALC:CORR:EDEL:TIME?'
    #    return pna_getter(self.query(get_cmd))
    #
    # def set_electrical_delay(delay=0):
    #    set_cmd='CALC:CORR:EDEL:TIME {:.6e}'.format(delay)
    #    self.write(set_cmd)

    # sweep mode
    def set_sweep_mode(self, mode="CONT", cnum=1):
        """vals=Enum("HOLD", "CONT", "GRO", "SING"))"""
        set_cmd = "SENS{}:SWE:MODE {}".format(cnum, mode)
        self.write(set_cmd)

    def get_sweep_mode(self, cnum=1):
        """vals=Enum("HOLD", "CONT", "GRO", "SING"))"""
        get_cmd = "SENS{}:SWE:MODE?".format(cnum)
        return self.query(get_cmd).strip()

    def get_source_attenuation(self):
        get_cmd = "SOUR:POW:ATT?"
        return self._pna_getter(self.query(get_cmd))

    def get_freq_real_imag(self):
        # change to polar coordinates
        # here I assume the measurment is #1 (MNUM=1)
        # self.write('CALC:PAR:MNUM:SEL 1')
        # self.write('CALC:FORM POL')

        f_start = self.get_start()
        f_stop = self.get_stop()
        num_pts = self.get_points()

        print(
            "Sweeping from %0.0d MHz to %0.0d MHz, with %0.0d points"
            % (f_start / 1e6, f_stop / 1e6, num_pts)
        )

        # self.write('FORM:DATA REAL,64')
        # F = np.linspace(f_start, f_stop, num_pts, endpoint = True)
        # GET FREQUENCIES!

        # self.write('FORM:DATA ASC') #this is in _init_
        try:
            raw_f = self.query("CALC:X?")
            raw = self.query("CALC:DATA? FDATA")
        except Exception as e:
            print(
                'If SCPI command "unterminated", check that measurement has been selected'
            )

        f = str(raw_f).split(",")
        data = str(raw).split(",")

        real_arr = data[::2]  # Every other element starting with element 0
        imag_arr = data[1::2]

        freq = np.asarray(np.float_(f))
        real = np.asarray(np.float_(real_arr))
        imag = np.asarray(np.float_(imag_arr))

        return freq, real, imag
