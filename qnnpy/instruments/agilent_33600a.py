import pyvisa
import numpy as np

#the commonds can be found in the following link
#http://rfmw.em.keysight.com/bihelpfiles/Trueform/webhelp/US/Default.htm?lc=eng&cc=US&id=2197433
class Agilent33600a(object):
    """Python class for Agilent 33600a 80MHz Frequency Generator, written by Adam McCaughan"""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000 # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()
    
    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string) 
    
    def reset(self):
        self.write('*RST')
    
    def set_usual_unit(self):
        self.write('SOURce1:APPLy?')
        self.write('DISP:UNIT:ARBR FREQ')
        self.write('DISP:UNIT:RATE FREQ')
        self.write('DISP:UNIT:VOLT HIGH')
        self.write('DISP:VIEW STAN')

    def set_dual_channel_coupling(self, ch='Ch1', state='ON'):
        if state is 'ON':
                if ch is 'Ch1':  
                    self.write('SOUR1:FREQ:COUP ON')
                elif ch is 'Ch2':  
                    self.write('SOUR2:FREQ:COUP ON')
        elif state is 'OFF':
                if ch is 'Ch1':  
                    self.write('SOUR1:FREQ:COUP OFF')
                elif ch is 'Ch2':  
                    self.write('SOUR2:FREQ:COUP OFF')
        else: print ('error')               

    def set_sin(self, freq=1000, vpp=0.1, voffset=0):
        # In a string, %0.6e converts a number to scientific notation like
        # print '%.6e' %(1234.56789) outputs '1.234568e+03'
        self.write('APPL:SIN %0.6e HZ, %0.6e VPP, %0.6e V' % (freq,vpp,voffset))

    def set_square(self, freq = 1000, vpp = 0.1, voffset = 0, duty_cycle = 0.5):
        #duty cycle limit
        #20% to 80% (frequency < 25 MHz)
        #40% to 60% (25 MHz < frequency < 50 MHz)
        #50% (frequency > 50 MHz)
        self.write('APPLy:SQUare %0.6e Hz, %0.6e VPP, %.6e V' %(freq, vpp, voffset))
        self.write('FUNCtion:SQUare:DCYCle %0.2e' %duty_cycle)


    def set_pulse(self, ch = 'Ch1', freq=1000, vlow=0.0, vhigh=1.0, phase = 1.0, width = 100e-6, leading_edge_time = 2.9E-9, trailing_edge_time = 2.9E-9):
        if ch is'Ch1':
                channel = 1
        elif ch is 'Ch2':
                channel = 2

        vpp = vhigh-vlow
        voffset = (vhigh+vlow)/2.0

        self.write('SOUR%1.0d:APPL:PULS %d,%0.6e,%0.6e' % (channel,freq,vpp,voffset))
        self.write('SOUR%1.0d:FUNC:PULS:WIDT %0.6e' % (channel,width))
        self.write('SOUR%1.0d:FUNC:PULS:TRAN:LEAD %0.6e' % (channel,leading_edge_time))
        self.write('SOUR%1.0d:FUNC:PULS:TRAN:TRA %0.6e' % (channel,trailing_edge_time))
        self.write('SOUR%1.0d:PHAS %0.3e' % (channel,phase))

    def set_freq(self, freq=1000):
        self.write('FREQ %0.6e' % (freq))

    def set_vpp(self, vpp=0.1):
        self.write('VOLT %0.6e' % (vpp))

    def set_voffset(self, voffset = 0.0):
        self.write('VOLT:OFFS %0.6e' % (voffset))

    def set_vhighlow(self, vlow=0.0, vhigh=1.0):
        if vhigh > vlow:
            self.set_vpp(vhigh-vlow)
            self.set_voffset((vhigh+vlow)/2.0)
            self.set_polarity(inverted = False)
        elif vhigh < vlow:
            self.set_vpp(vlow-vhigh)
            self.set_voffset((vhigh+vlow)/2.0)
            self.set_polarity(inverted = True)

    def set_output(self,ch = 'Ch1', output='ON'):
        if ch is'Ch1':
                channel = 1
        elif ch is 'Ch2':
                channel = 2
        
        if output in ['on','ON','On','oN']:   self.write('OUTP%1.0d ON' % (channel))
        else:                self.write('OUTP%1.0d OFF' % (channel))

    def set_sync(self, output='ON'):
        self.write('OUTP:SYNC:MODE NORM')
        self.write('OUTP:SYNC:POL NORM')
        if output in ['on','ON','On','oN']:   self.write('OUTP:SYNC ON')
        else:                self.write('OUTP:SYNC OFF')
    

    def set_load(self, high_z=False):
        if high_z is True:  self.write('OUTP:LOAD INF')
        else:               self.write('OUTP:LOAD 50')

    def set_polarity(self, inverted = False):
        if inverted is True:  self.write('OUTP:POL INV')
        else:               self.write('OUTP:POL NORM')

    def set_trigger(self, external_trigger = False, delay = 0.0):
        if external_trigger:    self.write('TRIG:SOUR EXT' )
        else:                   self.write('TRIG:SOUR IMM' )
        self.write('TRIG:DEL %s' % (delay)) # Delay in seconds


    def trigger_now(self):
        self.write('*TRG')


    def set_burst_mode(self, burst_enable = True, num_cycles = 1, phase = 0):
        if burst_enable:
            self.write('BURS:STAT ON') # Enables burst state
            self.write('BURS:NCYC %s' % (num_cycles))
            self.write('BURS:PHAS %s' % (phase)) # Phase in degrees

        else:
            self.write('BURS:STAT OFF')  # Disables burst state
        

    def set_arb_wf(self, t = [0.0, 1e-3], v = [0.0,1.0], name = 'ARB_PY'):
        """ Input voltage values will be scaled to +/-1.0, you can then adjust the overall
        amplitude using the set_vpp function.  The 33250a does not allow the input of time for each
        point, so we instead use interpolation here to create waveform of 2^14 equally-spaced 
        points, after which you can use set_freq to get the desired freq"""

        t = np.array(t);  v = np.array(v)

        v = v-min(v);  v = 2*v/max(v);  v = v-1
        temp = self.timeout; self.timeout = 60
        t_interp = np.linspace(t[0],t[-1],2**14) # Can be up to 2**14 long
        v_interp = np.interp(t_interp, t, v)

        data_strings = ['%0.3f' % x for x in v_interp]
        data_msg = ', '.join(data_strings)

        self.write('DATA VOLATILE, ' + data_msg) # Form of "DATA VOLATILE, 1, .67, .33, 0, -.33", p200 user's guide
        name = name[0:8].upper()
        self.write('DATA:COPY %s, VOLATILE' % name)
        self.write('APPL:USER')  # Set output to ARB
        self.write('FUNC:USER %s' % name) # Select the waveform in the volatile memory
        self.write('APPL:USER')
        self.timeout = temp
        # self.write('FUNC USER') # Output the selected waveform

    def setup_heartbeat_wf(self):
        heartbeat_t = [0.0, 4.0/8, 5.0/8, 6.0/8,  7.0/8, 8.0/8]
        heartbeat_v = [0.0,   0.0,   1.0,   0.0,   -1.0,   0.0]
        freq_gen.set_arb_wf(t = heartbeat_t, v = heartbeat_v, name = 'HEARTBEA')


    def select_arb_wf(self, name = 'HEARTBEA'):
        name = name[0:8].upper()
        self.write('APPL:USER')  # Set output to ARB
        self.write('FUNC:USER %s' % name)
        self.write('APPL:USER')  # Set output to ARB