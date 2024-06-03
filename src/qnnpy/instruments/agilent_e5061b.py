import pyvisa


class AgilentE5061B(object):
    """Python class for Agilent E5061B Network Analyzer, written by Adam McCaughan"""

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

    def reset(self):
        self.write("*RST")
        self.timeout = 1

    def get_channel_data(self, channel=1):
        self.write(":FORM:DATA ASC")
        m = self.ask_for_values(":CALC1:DATA:FDAT?")
        m = m[::2]
        f = self.ask_for_values(":SENS1:FREQ:DATA?")
        return f, m


# na = AgilentE5061B('GPIB0::17')
# def freq_range(self, f_start = 0.1e9, f_stop = 1.0e9, num_pts = 400):

#     self.write('POIN %0.0i;' % num_pts)
#     self.write('STAR %0.6e;' % f_start)
#     self.write('STOP %0.6e;' % f_stop)

# def fixed_freq(self, f = 10e6):
#     self.write('CWFREQ%0.6eHZ;' % f)

# def power(self, power = -20):
#     if (power < -60) or (power > 0):
#         print 'Out of range value'; return
#     if   power >=  -5:  power_range = '01' # Only available below 26 GHz
#     elif power >= -20:  power_range = '02'
#     elif power >= -35:  power_range = '05'
#     elif power >= -50:  power_range = '08'
#     elif power >= -60:  power_range = '10'

#     self.write('PRAN%s' % power_range)
#     self.write('POWE %0.0d' % power)  # Sets power (in dBm)

# def s_mode(self, s_mode = 'S11'):
#     self.write('%s;' % s_mode)

# def format_polar(self):
#     self.write('POLA') # Set to polar coordinates

# def format_logarithmic(self):
#     self.write('LOGM') # Set to polar coordinates

# def run_sweep_ri(self):
#     """ Runs a sweep using whatever settings are currently on the NA and returns the real
#     and imaginary components of each data point """
#     self.format_polar() # Set to polar coordinates
#     f_start = float(self.query('STAR?;'))
#     f_span = float(self.query('SPAN?;'))
#     f_stop = float(self.query('STOP?;'))
#     num_pts = int(float(self.query('POIN?;')))

#     print 'Sweeping from %0.0d to %0.0d, with %0.0d points' % (f_start/1e6, f_stop/1e6, num_pts)
#     # FIXME: Waiting loop here
#     # while (self.no bits are waiting):
#     #     sleep(1)
#     #     print 'Operation not yet complete, waiting 1s'

#     self.write('FORM4;') # Make the data output in ASCII
#     data = self.ask_for_values('OUTPFORM;')

#     f = np.linspace(f_start, f_stop, num_pts)
#     R = data[::2] # Every other element starting with element 0
#     I = data[1::2]
#     return f, R, I
