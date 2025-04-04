import numpy as np 
import pyvisa

class BK4060(object):
    """
    Python class for BK4060 AWG, written by Emma Batson 
    """

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands
        self.load = '50'
        self.polarity = 'NOR'
        self.output1 = False
        self.output2 = False

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def reset(self):
        self.write("*RST")

    def sync_phase(self, ch="C1"):
        pass
        # if ch == "C1":
        #     channel = 1
        # else:
        #     channel = 2
        # self.write("SOURce{}:PHASe:SYNChronize".format(channel))

    def set_usual_unit(self):
        pass
        # self.write("SOURce1:APPLy?")
        # self.write("DISP:UNIT:ARBR FREQ")
        # self.write("DISP:UNIT:RATE FREQ")
        # self.write("DISP:UNIT:VOLT HIGH")
        # self.write("DISP:VIEW STAN")

    def set_dual_channel_coupling(self, ch="C1", state="ON"):
        pass
        # if state == "ON":
        #     if ch == "Ch1":
        #         self.write("SOUR1:FREQ:COUP ON")
        #     elif ch == "Ch2":
        #         self.write("SOUR2:FREQ:COUP ON")
        # elif state == "OFF":
        #     if ch == "Ch1":
        #         self.write("SOUR1:FREQ:COUP OFF")
        #     elif ch == "Ch2":
        #         self.write("SOUR2:FREQ:COUP OFF")
        # else:
        #     print("error")

    def set_freq(self, ch='C1', freq=1000):
        self.write(f'{ch}:BaSic_WaVe FRQ,{freq}')

    def set_vpp(self, ch='C1', amp=0.1):
        self.write(f'{ch}:BaSic_WaVe AMP,{amp}')

    def set_voffset(self, ch='C1', voffset=0):
        self.write(f'{ch}:BaSic_WaVe OFST,{voffset}')

    def set_duty(self, ch='C1', duty=50):
        self.write(f'{ch}:BaSic_WaVe DUTY,{duty}')

    def set_phase(self, ch="C1", angle=0):
        # angle in degrees
        self.write(f'{ch}:BaSic_WaVe PHSE,{angle}')

    def set_sin(self, freq=1000, vpp=0.1, voffset=0, ch='C1'):
        # In a string, %0.6e converts a number to scientific notation like
        # print '%.6e' %(1234.56789) outputs '1.234568e+03'
        #self.write("APPL:SIN %0.6e HZ, %0.6e VPP, %0.6e V" % (freq, vpp, voffset))
        self.write(f'{ch}:BaSic_WaVe WVTP,SINE')
        self.set_freq(ch, freq)
        self.set_vpp(ch, vpp)
        self.set_voffset(ch, voffset)

    def set_square(
        self, ch="C1", freq=1000, vpp=0.1, voffset=0, duty_cycle=0.5, phase=0.0
    ):
        # duty cycle limit
        # 20% to 80% (frequency < 25 MHz)
        # 40% to 60% (25 MHz < frequency < 50 MHz)
        # 50% (frequency > 50 MHz)
        self.write(f'{ch}:BaSic_WaVe WVTP,SQUARE')
        self.set_freq(ch, freq)
        self.set_vpp(ch, vpp)
        self.set_voffset(ch, voffset)
        self.set_duty(ch, duty_cycle*100)

    def set_ramp(self, ch="Ch1", freq=1000, vpp=0.1, voffset=0, symm=100):
        self.write(f'{ch}:BaSic_WaVe WVTP,RAMP')
        self.set_freq(ch, freq)
        self.set_vpp(ch, vpp)
        self.write(f'{ch}:BaSic_WaVe SYM,{symm}')
        self.set_voffset(ch, voffset)

    def set_dc(self, ch="C1", voffset=0):
        self.write(f'{ch}:BaSic_WaVe WVTP,DC')
        self.set_voffset(ch, voffset)

    def set_pulse(self, ch='C1', freq=1000, vlow=0, vhigh=1, phase=0, width=100e-6, 
                  leading_edge_time=10e-9, trailing_edge_time=10e-9):
        # width can be between 16.3 ns to 1 Ms
        # rise/falling edges can be between 8.4 ns - 122.4 s
        self.write(f'{ch}:BaSic_WaVe WVTP,PULSE')
        self.set_freq(ch, freq)
        self.write(f'{ch}:BaSic_WaVe LLEV,{vlow}')
        self.write(f'{ch}:BaSic_WaVe HLEV,{vhigh}')
        self.set_phase(ch, phase)
        self.write(f'{ch}:BaSic_WaVe WIDTH,{width}')
        self.write(f'{ch}:BaSic_WaVe RISE,{leading_edge_time}')
        self.write(f'{ch}:BaSic_WaVe FALL,{trailing_edge_time}')

    def set_vhighlow(self, vlow=0.0, vhigh=1.0):
        pass
        # if vhigh > vlow:
        #     self.set_vpp(vhigh - vlow)
        #     self.set_voffset((vhigh + vlow) / 2.0)
        #     self.set_polarity(inverted=False)
        # elif vhigh < vlow:
        #     self.set_vpp(vlow - vhigh)
        #     self.set_voffset((vhigh + vlow) / 2.0)
        #     self.set_polarity(inverted=True)

    def set_output(self, output=False, ch="both", load=None, polarity=None):
        """breaking legacy behavior to make compatible with
        other sources. default behavior is to turn both channels
        on or off
        """
        if load == None:
            load = self.load
        if polarity == None:
            polarity = self.polarity

        if output:
            state = "ON"
            if ch == 'both' or ch == 'C1':
                self.output1 = True
            if ch == 'both' or ch == 'C2':
                self.output2 = True
        else:
            state = "OFF"
            if ch == 'both' or ch == 'C1':
                self.output1 = False
            if ch == 'both' or ch == 'C2':
                self.output2 = False

        if ch == "both" or ch == "C1":
            self.write(f"C1:OUTP {state},LOAD,{load},PLRT,{polarity}")
        if ch == "both" or ch == "C2":
            self.write(f"C2:OUTP {state},LOAD,{load},PLRT,{polarity}")

    def set_output_legacy(self, ch="C1", output="ON"):
        if output in ["on", "ON", "On", "oN"]:
            self.write(f"{ch}:OUTP ON")
        else:
            self.write(f"{ch}:OUTP OFF")

    def set_sync(self, output="ON", phase_dev=0):
        self.write(f"COUP PCOUP,{output}")
        self.write(f"COUP PDEV {phase_dev}")

    def set_load(self, high_z=False):
        if high_z:
            self.load = 'HZ'
        else:
            self.load = '50'
        if self.output1:
            self.set_output(True, ch='C1')
        if self.output2:
            self.set_output(True, ch='C2')

    def set_polarity(self, inverted=False):
        if inverted is True:
            self.polarity = 'INVT'
        else:
            self.polarity = 'NOR'
        if self.output1:
            self.set_output(True, ch='C1')
        if self.output2:
            self.set_output(True, ch='C2')
        

    def set_trigger(self, external_trigger=False, delay=0.0):
        pass
        # if external_trigger:
        #     self.write("TRIG:SOUR EXT")
        # else:
        #     self.write("TRIG:SOUR IMM")
        # self.write("TRIG:DEL %s" % (delay))  # Delay in seconds

    def trigger_now(self):
        pass
        #self.write("*TRG")

    def set_burst_mode(self, ch=1, burst_enable=True, num_cycles=1, phase=0):
        pass
        # if burst_enable:
        #     self.write("SOUR%1.0d:BURS:STAT ON" % (ch))  # Enables burst state
        #     self.write("SOUR%1.0d:BURS:NCYC %s" % (ch, num_cycles))
        #     self.write("SOUR%1.0d:BURS:PHAS %s" % (ch, phase))  # Phase in degrees

        # else:
        #     self.write("SOUR%1.0d:BURS:STAT OFF" % (ch))  # Disables burst state

    def set_arb_wf(self, t=[0.0, 1e-3], v=[0.0, 1.0], name="ARB_PY"):
        """Input voltage values will be scaled to +/-1.0, you can then adjust the overall
        amplitude using the set_vpp function.  The 33250a does not allow the input of time for each
        point, so we instead use interpolation here to create waveform of 2^14 equally-spaced
        points, after which you can use set_freq to get the desired freq"""
        pass
        # t = np.array(t)
        # v = np.array(v)

        # v = v - min(v)
        # v = 2 * v / max(v)
        # v = v - 1
        # temp = self.timeout
        # self.timeout = 60
        # t_interp = np.linspace(t[0], t[-1], 2**14)  # Can be up to 2**14 long
        # v_interp = np.interp(t_interp, t, v)

        # data_strings = ["%0.3f" % x for x in v_interp]
        # data_msg = ", ".join(data_strings)

        # self.write(
        #     "DATA VOLATILE, " + data_msg
        # )  # Form of "DATA VOLATILE, 1, .67, .33, 0, -.33", p200 user's guide
        # name = name[0:8].upper()
        # self.write("DATA:COPY %s, VOLATILE" % name)
        # self.write("APPL:USER")  # Set output to ARB
        # self.write("FUNC:USER %s" % name)  # Select the waveform in the volatile memory
        # self.write("APPL:USER")
        # self.timeout = temp
        # # self.write('FUNC USER') # Output the selected waveform

    def select_arb_wf(self, name="HEARTBEA"):
        pass
        # name = name[0:8].upper()
        # self.write("APPL:USER")  # Set output to ARB
        # self.write("FUNC:USER %s" % name)
        # self.write("APPL:USER")  # Set output to ARB
