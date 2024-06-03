import numpy as np
import pyvisa


class Agilent33250a(object):
    """Python class for Agilent 33250a 80MHz Frequency Generator, written by Adam McCaughan"""

    # http://rfmw.em.keysight.com/bihelpfiles/Trueform/webhelp/US/Default.htm?lc=eng&cc=US&id=2197433

    # error messages
    # https://rfmw.em.keysight.com/wireless/helpfiles/e4982a/product_information/error_messages/error_messages.htm

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def beep(self):
        self.pyvisa.write("SYST:BEEP")

    def reset(self):
        self.write("*RST")

    def clear_volatile(self):
        self.write(":DATA:VOLatile:CLEar")

    def delete(self, name):
        self.write("DATA:DEL %s" % name)

    def get_catalog(self):
        "List the names of all waveforms in volatile memory currently available for selection."
        return self.query("DATA:CATalog?")

    def get_catalog_int(self):
        "List the names of sequence or arb files in internal memory"
        return self.query("MMEM:CAT:DATA:ARB?")

    def get_error(self):
        # https://rfmw.em.keysight.com/wireless/helpfiles/e4982a/product_information/error_messages/error_messages.htm
        print(self.query("SYST:ERR?"))

    def get_phase(self, chan=1):
        return self.query("SOURCE%s:PHAS?" % chan)

    def get_amplitude(self, chan=1):
        return self.query("SOURCE%s:VOLT?" % (chan))

    def get_freq(self, chan=1):
        return self.query("SOURCE%s:FREQ?" % (chan))

    def set_sin(self, freq=1000, vpp=0.1, voffset=0, chan=1):
        # In a string, %0.6e converts a number to scientific notation like
        # print '%.6e' %(1234.56789) outputs '1.234568e+03'
        self.write(
            "SOURCE%s:APPL:SIN %0.6e HZ, %0.6e VPP, %0.6e V"
            % (chan, freq, vpp, voffset)
        )

    def set_freq(self, freq=1000, chan=1):
        self.write("SOURCE%s:FREQ %0.6e" % (chan, freq))

    def set_high(self, v=0.1, chan=1):
        self.write("SOURCE%s:VOLT:HIGH %0.6e" % (chan, v))

    def set_low(self, v=0, chan=1):
        self.write("SOURCE%s:VOLT:LOW %0.6e" % (chan, v))

    def set_voffset(self, voffset=0.0, chan=1):
        self.write("SOURCE%s:VOLT:OFFS %0.6e" % (chan, voffset))

    def set_vpp(self, vpp=0.1, chan=1):
        self.write("SOURCE%s:VOLT %0.6e" % (chan, vpp))

    def set_arb_freq(self, freq=1e3, chan=1):
        self.write("SOURCE%s:FUNC:ARB:FREQ %0.6e" % (chan, freq))

    def set_arb_sample_rate(self, srate=1e4, chan=1):
        self.write("SOURCE%s:FUNC:ARB:SRAT %0.6e" % (chan, srate))

    def set_arb_sync(self):
        self.write("FUNC:ARB:SYNC")

    def set_vhighlow(self, vlow=0.0, vhigh=1.0):
        if vhigh > vlow:
            self.set_vpp(vhigh - vlow)
            self.set_voffset((vhigh + vlow) / 2.0)
            self.set_polarity(inverted=False)
        elif vhigh < vlow:
            self.set_vpp(vlow - vhigh)
            self.set_voffset((vhigh + vlow) / 2.0)
            self.set_polarity(inverted=True)

    def set_output(self, output=False, chan=1):
        if output is True:
            self.write("OUTPUT%s ON" % chan)
        else:
            self.write("OUTPUT%s OFF" % chan)

    def set_load(self, high_z=False, chan=1):
        if high_z is True:
            self.write("OUTP%s:LOAD INF" % chan)
        else:
            self.write("OUTP%s:LOAD 50" % chan)

    def set_polarity(self, inverted=False):
        if inverted is True:
            self.write("OUTP:POL INV")
        else:
            self.write("OUTP:POL NORM")

    def set_trigger(self, external_trigger=False, delay=0.0):
        if external_trigger:
            self.write("TRIG:SOUR EXT")
        else:
            self.write("TRIG:SOUR IMM")
        self.write("TRIG:DEL %s" % (delay))  # Delay in seconds

    def set_phase(self, value, chan=1, unit="DEG"):
        self.write("SOURCE%s:PHAS %s %s" % (chan, value, unit))

    def set_symmetry(self, value, chan=1):
        self.write("SOURCE%s:FUNCtion:RAMP:SYMMetry %s" % (chan, value))

    def trigger_now(self):
        self.write("*TRG")

    def set_burst_mode(self, burst_enable=True, num_cycles=1, phase=0, period=10e-6):
        if burst_enable:
            self.write("BURS:STAT ON")  # Enables burst state
            self.write("BURS:NCYC %s" % (num_cycles))
            self.write("BURS:PHAS %s" % (phase))  # Phase in degrees
            self.write("BURS:INT:PER %s" % (period))

        else:
            self.write("BURS:STAT OFF")  # Disables burst state

    def set_waveform(self, name="SIN", freq=1000, amplitude=0.1, offset=0, chan=1):
        """
        APPLy
        :SINusoid [<frequency> [,<amplitude> [,<offset>] ]]
        :SQUare [<frequency> [,<amplitude> [,<offset>] ]]
        :RAMP [<frequency> [,<amplitude> [,<offset>] ]]
        :PULSe [<frequency> [,<amplitude> [,<offset>] ]]♠
        :NOISe [<frequency|DEF>1 [,<amplitude> [,<offset>] ]]
        :DC [<frequency|DEF>1 [,<amplitude>|DEF>1 [,<offset>] ]]
        :USER [<frequency> [,<amplitude> [,<offset>] ]]
        """
        self.write(
            "SOURCE%s:APPL:%s %0.6e, %0.6e, %0.6e"
            % (chan, name, freq, amplitude, offset)
        )

    def set_pulse(
        self, freq=1000, vlow=0.0, vhigh=1.0, width=100e-6, edge_time=2.9e-9, chan=1
    ):
        vpp = vhigh - vlow
        voffset = vpp / 2
        self.write(
            "SOURCE%s:APPL:PULS %0.6e HZ, %0.6e VPP, %0.6e V"
            % (chan, freq, vpp, voffset)
        )
        self.write("SOURCE%s:PULS:WIDT %0.6e" % (chan, width))

    def set_pulse_tran(self, edge_time=5e-9, chan=1):
        self.write("SOUR%1.0d:FUNC:PULS:TRAN %0.6e" % (chan, edge_time))

    def set_pulse_width(self, width=1e-6, chan=1):
        self.write("SOURCE%s:PULS:WIDT %0.6e" % (chan, width))

    def set_pulse_lead(self, leading_edge_time=5e-9, chan=1):
        self.write("SOUR%1.0d:FUNC:PULS:TRAN:LEAD %0.6e" % (chan, leading_edge_time))

    # def set_pulse_trail(self, trailing_edge_time=5e-9, chan=1):
    #     self.write('SOUR%1.0d:FUNC:PULS:TRAN:TRAIL %0.6e' % (chan,trailing_edge_time))

    # def set_arb_wf(self, t = [0.0, 1e-3], v = [0.0,1.0], name = 'ARB_PY', num_samples=2**9, chan=1):
    #     """ Input voltage values will be scaled to +/-1.0, you can then adjust the overall
    #     amplitude using the set_vpp function.  The 33250a does not allow the input of time for each
    #     point, so we instead use interpolation here to create waveform of 2^14 equally-spaced
    #     points, after which you can use set_freq to get the desired freq"""

    #     t = np.array(t);  v = np.array(v)

    #     v = v-min(v);  v = 2*v/max(v);  v = v-1
    #     # temp = self.timeout; self.timeout = 60
    #     t_interp = np.linspace(t[0],t[-1],num_samples) # Can be up to 2**14 long
    #     v_interp = np.interp(t_interp, t, v)

    #     data_strings = ['%0.3f' % x for x in v_interp]
    #     data_msg = ', '.join(data_strings)

    #     # self.set_sin(chan=chan) #cannot delete selected waveform
    #     self.delete(name) #for overwriting existing name

    #     self.write('DATA VOLATILE, ' + data_msg) # Form of "DATA VOLATILE, 1, .67, .33, 0, -.33", p200 user's guide
    #     name = name[0:8].upper()
    #     self.write('DATA:COPY %s, VOLATILE' % name)
    #     self.write('SOURCE%s:APPL:USER' % chan)  # Set output to ARB
    #     self.write('FUNC:USER %s' % name) # Select the waveform in the volatile memory
    #     # self.write('APPL:USER')
    #     # self.timeout = temp
    #     # self.write('FUNC USER') # Output the selected waveform

    def set_arb_wf(self, waveform, name="ARB_PY", num_samples=2**9, chan=1):
        t = np.array(range(len(waveform)))
        t_interp = np.linspace(t[0], t[-1], num_samples)
        waveform = np.interp(t_interp, t, waveform)

        self.write("*CLS")  # clear status
        self.write(
            f"SOURce{chan}:DATA:VOLatile:CLEar"
        )  # clears volatile waveform memory
        self.query(
            f"SOUR{chan}:DATA:VOL:FREE?"
        )  # returns number of points available (free) in volatile memory
        # self.get_error() # check for error
        self.write(
            "FORM:BORD SWAP"
        )  # least-significant byte (LSB) of each data point is first. Most computers use this.

        self.query(
            "DATA:CAT?"
        )  # returns the contents of volatile waveform memory, including arbitrary waveforms and sequences

        waveform = waveform.astype("float32")  # set single precision
        mw = np.max(np.abs(waveform))  # find max for normalization
        # waveform = waveform/mw # normalize between +/-1
        arbBytes = str(len(waveform) * 4)  # number of bytes to send
        header = f"SOURce{chan}:DATA:ARBitrary {name}, #{len(arbBytes)}{arbBytes}"

        header = bytes(header, "ascii")
        binblockBytes = waveform.view(
            np.uint8
        )  # waveform as unsigned 8bit interger array
        data_msg = "".join([chr(x) for x in binblockBytes])
        data_msg = data_msg.encode("latin-1")
        message = header + data_msg
        self.pyvisa.write_raw(message)
        self.write("*WAI")

        self.write(f"SOURce{chan}:FUNCtion:ARBitrary {name}")
        self.write(f'MMEM:STOR:DATA{chan} "INT:\\{name}.arb"')
        self.write(f"SOUR{chan}:FUNC ARB")
        self.set_vpp(mw, chan)

    def set_arb_vpeak(self, v, chan):
        self.write(f"SOURce{chan}FUNC:ARBitrary:PTPeak {v}")

    def set_sequence(self, name, chan):
        self.write("*CLS")  # clear status
        self.write(
            f"SOURce{chan}:DATA:VOLatile:CLEar"
        )  # clears volatile waveform memory

        write_start = '"INT:\WRITE0.ARB",0,once,highAtStartGoLow,50'
        write1 = '"INT:\WRITE1.ARB",0,once,maintain,50'
        write0 = '"INT:\WRITE0.ARB",0,once,maintain,50'
        sequence = f'"{name}",' + ",".join(
            [write_start, write0, write0, write1, write1, write0, write1, write1]
        )
        n = str(len(sequence))
        header = f"SOUR{chan}:DATA:SEQ #{len(n)}{n}"
        message = header + sequence

        self.write(f'MMEM:LOAD:DATA{chan} "INT:\WRITE0.arb"')
        self.write(f'MMEM:LOAD:DATA{chan} "INT:\WRITE1.arb"')

        self.pyvisa.write_raw(message)
        self.write(f"SOURce{chan}:FUNCtion:ARBitrary {name}")
        # self.get_error()

    def setup_heartbeat_wf(self):
        heartbeat_t = [0.0, 4.0 / 8, 5.0 / 8, 6.0 / 8, 7.0 / 8, 8.0 / 8]
        heartbeat_v = [0.0, 0.0, 1.0, 0.0, -1.0, 0.0]
        self.set_arb_wf(t=heartbeat_t, v=heartbeat_v, name="HEARTBEA")

    def select_arb_wf(self, name="HEARTBEA"):
        name = name[0:8].upper()
        self.write("APPL:USER")  # Set output to ARB
        self.write("FUNC:USER %s" % name)
        self.write("APPL:USER")  # Set output to ARB

    def setup_pulse_train(
        self, number_of_pulses=6, t_delay=4, t_on=1, t_off=0.2, t_edge=0.01
    ):
        t = [0, t_delay]
        v = [0, 0]
        for i in range(number_of_pulses):
            t.append(round(t[-1] + t_edge, 2))
            t.append(round(t[-1] + t_on, 2))
            t.append(round(t[-1] + t_edge, 2))
            t.append(round(t[-1] + t_off, 2))

            v.extend([1, 1, 0, 0])
        self.get_catalog()
        self.set_arb_wf(t, v, name="PULSE_TR")

    def sync_phase(self, chan):
        # self.write('SOURCE%s:FUNC:ARBitrary:SYNChronize' % chan)
        self.write("SOURCE%s:PHASe:SYNChronize" % chan)
