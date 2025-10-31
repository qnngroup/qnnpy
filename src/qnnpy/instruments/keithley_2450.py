import pyvisa
import time

class Keithley2450(object):
    """Python class for Keithley 2450 Sourcemeter, written by Dip Joti Paul and Reed Foster"""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands
        self.isrc = True # if True, source is current, sense is voltage. if false, is the opposite

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def reset(self):
        self.write("*RST")

    def setup_read_volt(self):
        self.write("*RST")
        self.write(":SOUR:FUNC CURR")
        self.write(":SOUR:CURR:LEVEL 0E-6")
        self.write(':SENS:FUNC "VOLT"')

    def setup_4W_source_I_read_V(self):
        self.write("*RST")
        self.write(":SOUR:FUNC CURR")  # Set operation mode to: source current
        self.write(":SOUR:CURR:LEVEL 0E-6")  # Set current level to 0 uA
        self.write(":SENS:VOLT:UNIT VOLT")  # measure voltage
        self.write(":SENS:VOLT:RSEN ON")  # Turn on 4-wire measurement
        self.write(":SOUR:CURR:READ:BACK ON") # enable readback of current
        self.write(':SENS:FUNC "VOLT"') # set sense function to voltage
        self.isrc = True

    def setup_2W_source_I_read_V(self):
        self.write("*RST")
        self.write(":SOUR:FUNC CURR")  # Set operation mode to: source current
        self.write(":SOUR:CURR:LEVEL 0E-6")  # Set current level to 0 uA
        self.write(":SENS:VOLT:UNIT VOLT")  # measure voltage
        self.write(":SENS:VOLT:RSEN OFF")  # Turn off 4-wire measurement
        self.write(":SOUR:CURR:READ:BACK ON") # enable readback of current
        self.write(':SENS:FUNC "VOLT"') # set sense function to voltage
        self.isrc = True

    def setup_2W_source_V_read_I(self):
        self.write("*RST")
        self.write(":SOUR:FUNC VOLT")  # Set operation mode to: source voltage
        self.write(":SOUR:VOLT:LEVEL 0E-3")  # Set voltage level to 0 mV
        self.write(":SENS:CURR:UNIT AMP")  # measure current
        self.write(":SENS:CURR:RSEN OFF")  # Turn off 4-wire measurement
        self.write(":SOUR:VOLT:READ:BACK ON") # enable readback of voltage
        self.write(':SENS:FUNC "CURR"') # set sense function to current
        self.isrc = False

    def set_output(self, output=False):
        if output is True:
            self.write(":OUTPut:STATe ON")
        if output is False:
            self.write(":OUTPut:STATe OFF")

    def set_measurement_time(self, plc_cycles=1.0):
        """plc_cycles Sets integration time Keithley.  Each cycle corresponds to
        1/60th of a second.  Default is 1.0, Max is 10.0. Min is 0.01.  See Keithley
        manual p18-70 for more details"""
        self.write(":NPLCycles %0.2f" % plc_cycles)

    def disable_remote(self):
        """Simulates the pressing of the "LOCAL" button on the Keithley
        which will take the keithley out of remote mode"""
        self.write(":SYST:KEY 23")

    def set_compliance_i(self, compliance_i=10e-6):
        self.write(f":SOUR:VOLT:ILIM:LEV %0.3e" % compliance_i)

    def set_compliance_v(self, compliance_v=10e-6):
        self.write(f":SOUR:CURR:VLIM:LEV %0.3e" % compliance_v)

    def set_current(self, current=0e-6):
        self.write(":SOUR:CURR:LEVEL %0.4e" % current)  # Set current level

    def set_voltage(self, voltage=0e-6):
        self.write(":SOUR:VOLT:LEVEL %0.4e" % voltage)  # Set current level
    
    def set_sense_range(self, upper):
        self.write(f':SENS:{"VOLT" if self.isrc else "CURR"}:RANG {upper}')
    
    def set_source_range(self, upper):
        self.write(f':SOUR:{"CURR" if self.isrc else "VOLT"}:RANG {upper}')

    def get_sense_range(self):
        return float(self.query(f':SENS:{"VOLT" if self.isrc else "CURR"}:RANG?'))

    def get_source_range(self):
        return float(self.query(f':SENS:{"CURR" if self.isrc else "VOLT"}:RANG?'))

    def read_voltage_and_current(self, delay=0):
        source_mode = "CURR" if self.isrc else "VOLT"
        setting = self.query(f'SOUR:{source_mode}?')
        self.write(f'SOUR:LIST:{source_mode} {setting}')
        self.write(f'SOUR:SWE:{source_mode}:LIST 1, {delay}')
        self.write('INIT')
        self.write('*WAI')
        raw_data = self.query('TRAC:DATA? 1, 1, "defbuffer1", SOUR, READ')
        source, sense = [float(d) for d in raw_data.split(',')]
        if self.isrc:
            current, voltage = source, sense
        else:
            voltage, current = source, sense
        return voltage, current

    def read_current(self):
        return float(self.query("READ?"))

    def read_voltage(self):
        return float(self.query("READ?"))
    
    def iv_linsweep(self, i_list, delay, failabort=False):
        if len(i_list) > 2500:
            raise ValueError("lists longer than 2500 are not supported")
        sublists = []
        while len(i_list) > 10:
            sublists.append([str(i) for i in i_list[:10]])
            i_list = i_list[10:]
        sublists.append([str(i) for i in i_list])
        for n, sublist in enumerate(sublists):
            self.write(f'SOUR:LIST:CURR{":APP" if n > 0 else ""} {", ".join(sublist)}')
            self.write('*WAI')
        self.write(f'SOUR:SWE:CURR:LIST 1, {delay}, 1, {"ON" if failabort else "OFF"}')
        num_points = int(self.query('SOUR:LIST:CURR:POIN?'))
        self.write('INIT')
        self.write('*WAI')
        # wait for measurement to finish
        time.sleep(num_points * (delay + 0.08))
        while self.query('TRIG:STATE?').startswith('RUNNING'):
            time.sleep(self.pyvisa.timeout)
        raw_data = self.query(f'TRAC:DATA? 1, {num_points}, "defbuffer1", SOUR, READ')
        data = [float(d) for d in raw_data.split(',')]
        return data[::2], data[1::2]
