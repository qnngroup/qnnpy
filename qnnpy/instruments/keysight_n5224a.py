import pyvisa
from time import sleep
import numpy as np

class KeysightN5224a(object):
    """Python class for KeysightN5224a network analyzer, written by Di Zhu. 
    Connet the GPIB cable to GPIB1 (talker and listener)
    
    http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/SCPI_Command_Tree.htm
            
    
    """
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000 # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands
        #set the data format; this seems to be the only format recognizable
        self.pyvisa.write('FORM ASCii,0') 
    
    def read(self):
        return self.pyvisa.read()
    
    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)
    
    def reset(self, measurement = 'S21', if_bandwidth = 1e3, start_freq=100e6,
              stop_freq = 15e9, power = -30):
        self.write('SYST:PRES')
        self.write("CALC:PAR:DEL:ALL")
        self.set_measurement(measurement)
        self.set_start(start_freq)
        self.set_stop(stop_freq)
        self.set_if_bw(if_bandwidth)
        self.set_sweep_mode('CONT')
        self.set_power(power)
        
    
    def set_measurement(self, measurement = 'S21'):
        current_trace = self.get_trace_catalog()
        if current_trace == 'NO CATALOG':
            self.write("CALC:PAR:DEF \"{}\", {}".format(measurement, measurement))
            self.write("CALC:PAR:SEL \"{}\"".format(measurement))
        self.write("CALC:PAR:MOD:EXT \"{}\"".format(measurement))
        trace_name = self.get_trace_catalog()
        trace_name = trace_name.split(',')[0]
        self.write("DISPlay:WINDow1:TRACe1:FEED \'{}\'".format(trace_name))
        
    def single_sweep(self):
        '''run a single sweep and get f in Hz, S in real + i*imag form'''
        #self.write("INITiate:CONTinuous OFF") 
        self.set_sweep_mode('SING')
        #self.write("INITiate:IMMediate")
        while self.get_sweep_mode() !='HOLD':
            sleep(.1)
        f = self.get_frequency()
        S = self.read_channel()
        return f, S
    
    def read_channel(self):
        val = self.query("CALC:DATA? SDATA")
        val = [x.strip() for x in val.split(',')]
        val = [float(x) for x in val]
        real_part = np.array(val[0::2])
        imag_part = np.array(val[1::2])
        S = real_part+1j*imag_part
        return S
        
    def get_frequency(self):
        freq = self.query("CALC:X?")
        freq = [x.strip() for x in freq.split(',')]
        freq = [float(x) for x in freq]
        return np.array(freq)
        
    def select_measurement(self, measurement_name="CH1_S11_1"):
        self.write("CALCulate:PARameter:SELect '"+ measurement_name+"'")
    
    # strip \n and return a float. OM - i think float() handles \n
    def _pna_getter(self, s):
        return float(s.strip())
    #IF bandwidth
    def get_if_bw(self):
        cmd = 'SENS:BAND?'
        return self._pna_getter(self.query(cmd))
    
    def set_if_bw(self, bandwidth = 1000):
        self.write('SENS:BAND {:.2f}'.format(bandwidth))
        
    #power
    def get_power(self):
        cmd = 'SOUR:POW?'
        return self._pna_getter(self.query(cmd))
    def set_power(self, power = -10):
        '''set power in dbm'''
        self.write('SOUR:POW {:.2f}'.format(power))
    
    #frequency range
    def set_start(self, frequency = 100e6):
        cmd = 'SENS:FREQ:STAR {}'.format(frequency)
        self.write(cmd)
    
    def set_stop(self, frequency = 20e9):
        cmd ='SENS:FREQ:STOP {}'.format(frequency)
        self.write(cmd)
        
    def set_center(self, frequency = 5e9):
        cmd ='SENS:FREQ:CENT {}'.format(frequency)
        self.write(cmd)
        
    def set_span(self, frequency = 5e9):
        cmd ='SENS:FREQ:SPAN {}'.format(frequency)
        self.write(cmd)


    def get_start(self):
        cmd ='SENS:FREQ:STAR?;'
        return self._pna_getter(self.query(cmd))
        
    def get_stop(self):
        cmd ='SENS:FREQ:STOP?;'
        return self._pna_getter(self.query(cmd))
        
    def get_center(self):
        cmd ='SENS:FREQ:CENT?;'
        return self._pna_getter(self.query(cmd))
        
    def get_span(self):
        cmd ='SENS:FREQ:SPAN?;'
        return self._pna_getter(self.query(cmd))
        
    
    #number of points in a sweep
    def get_points(self):
        cmd = 'SENS:SWE:POIN?'
        return self._pna_getter(self.query(cmd))
    def set_points(self, points = 201):
        cmd ='SENS:SWE:POIN {}'.format(points)
        self.write(cmd)
    
             
    def get_trace_catalog(self):
        """
        Get the trace catalog, that is a list of trace and sweep types
        from the Pself.
        The format of the returned trace is:
            trace_name,trace_type,trace_name,trace_type...
        """
        return self.query("CALC:PAR:CAT:EXT?").strip().strip('"')
    
    #electrical delay
    #def get_electrical_delay():
    #    '''unit s'''
    #    get_cmd='CALC:CORR:EDEL:TIME?'
    #    return pna_getter(self.query(get_cmd))
    #    
    #def set_electrical_delay(delay=0):
    #    set_cmd='CALC:CORR:EDEL:TIME {:.6e}'.format(delay)
    #    self.write(set_cmd)
    
    #sweep mode
    def set_sweep_mode(self, mode = 'CONT'):
        '''vals=Enum("HOLD", "CONT", "GRO", "SING"))'''
        set_cmd='SENS:SWE:MODE {}'.format(mode)
        self.write(set_cmd)
        
    def get_sweep_mode(self):
        '''vals=Enum("HOLD", "CONT", "GRO", "SING"))'''
        get_cmd='SENS:SWE:MODE?'
        return self.query(get_cmd).strip()
    
    
    def get_source_attenuation(self):
        get_cmd = 'SOUR:POW:ATT?'
        return self._pna_getter(self.query(get_cmd))
    

    def get_freq_real_imag(self):
        #change to polar coordinates
        #here I assume the measurment is #1 (MNUM=1)
        # self.write('CALC:PAR:MNUM:SEL 1')
        #self.write('CALC:FORM POL')
        
        f_start = self.get_start()
        f_stop = self.get_stop()
        num_pts = self.get_points()
        
        print('Sweeping from %0.0d MHz to %0.0d MHz, with %0.0d points' % (f_start/1e6, f_stop/1e6, num_pts))
        
        #self.write('FORM:DATA REAL,64')
        #F = np.linspace(f_start, f_stop, num_pts, endpoint = True)
        #GET FREQUENCIES!
        
        # self.write('FORM:DATA ASC') #this is in _init_
        try:
            raw_f = self.query('CALC:X?')
            raw = self.query('CALC:DATA? FDATA')
        except:
            print('If SCPI command "unterminated", check that measurement has been selected')    
        
        f = str(raw_f).split(",")
        data = str(raw).split(",")
        
        R = data[::2] # Every other element starting with element 0
        I = data[1::2]
        
        freq = np.asarray(np.float_(f))
        real = np.asarray(np.float_(R))
        imag = np.asarray(np.float_(I))
        
        return freq, real, imag

