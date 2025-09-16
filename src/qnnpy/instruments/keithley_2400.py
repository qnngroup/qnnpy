import pyvisa
import time


class Keithley2400(object):
    """Python class for Keithley 2400 Sourcemeter, written by Adam McCaughan"""

    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands
        self.name = "Keithley2400"

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def reset(self):
        self.write("*RST")

    def local_key(self):
        self.write("SYST:KEY 23")

    def setup_read_volt(self):
        self.write("*RST")
        self.write(":SOUR:FUNC CURR")
        self.write(":SOUR:CURR:LEVEL 0E-6")
        self.write('SENS:FUNC "VOLT"')

    def setup_4W_source_I_read_V(self):
        """current level in microamps"""
        self.write("*RST")
        self.write(":SOUR:FUNC CURR")  # Set operation mode to: source current
        self.write(":SOUR:CURR:LEVEL 0E-6")
        self.write(":SYST:RSEN 1")  # Turn on remote sensing for 4w measurement
        self.write('SENS:FUNC "VOLT", "CURR"')  # Have it output

    def setup_2W_source_I_read_V(self):
        self.write("*RST")
        self.write(":SOUR:FUNC CURR")  # Set operation mode to: source current
        self.write(":SOUR:CURR:LEVEL 0E-6")  # Set current level to 0 uA
        self.write(":SYST:RSEN 0")  # Turn off remote sense
        self.write('SENS:FUNC "VOLT", "CURR"')  # Have it output

    def setup_2W_source_V_read_I(self):
        self.write("*RST")
        self.write(":SOUR:FUNC VOLT")  # Set operation mode to: source voltage
        self.write(":SOUR:VOLT:LEVEL 0E-3")  # Set voltage level to 0 mV
        self.write(":SYST:RSEN 0")  # Turn off remote sense
        self.write('SENS:FUNC "VOLT", "CURR"')  # Have it output

    def set_output(self, output=False):
        if output is True:
            self.write(":OUTP ON")
        if output is False:
            self.write(":OUTP OFF")

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
        self.write(":SENS:CURR:PROT %0.3e" % compliance_i)

    def set_compliance_v(self, compliance_v=10e-6):
        self.write(":SENS:VOLT:PROT %0.3e" % compliance_v)

    def set_current(self, current=0e-6):
        self.write(":SOUR:CURR:LEVEL %0.4e" % current)  # Set current level

    def set_voltage(self, voltage=0e-6):
        self.write(":SOUR:VOLT:LEVEL %0.4e" % voltage)  # Set current level

    def read_voltage_and_current(self):
        # See page 18-51 of manual, returns: voltage, current, resistance, timestamp, status info
        # Returns something like '5.275894E-05,-1.508318E-06,+9.910000E+37,+2.562604E+03,+3.994000E+04'
        return [float(d) for d in self.query(":READ?").split(",")[:2]]

    def read_current(self, current=0e-6):
        _, current = self.read_voltage_and_current()
        return current

    def read_voltage(self):
        voltage, _ = self.read_voltage_and_current()
        return voltage

    def switch_front(self):
        self.write(":ROUT:TERM FRON")

    def switch_rear(self):
        self.write(":ROUT:TERM REAR")
    
    def iv_linsweep(self, i_list, delay):
        # runs a sweep
        if len(i_list) > 2500:
            raise ValueError("lists longer than 2500 are not supported")
        num_points = len(i_list) 
        # see pg 171 of manual
        self.write(f'TRAC:CLE')
        self.write(f'TRAC:FEED SENS')
        self.write(f'TRAC:POIN {num_points}')
        self.write(f'TRAC:FEED:CONT NEXT')
        sublists = []
        while len(i_list) > 10:
            sublists.append([str(i) for i in i_list[:10]])
            i_list = i_list[10:]
        sublists.append([str(i) for i in i_list])
        for n, sublist in enumerate(sublists):
            self.write(f'SOUR:LIST:CURR{":APP" if n > 0 else ""} {", ".join(sublist)}')
        self.write('SOUR:CURR:MODE LIST')
        self.write(f'TRIG:COUN {num_points}')
        self.write(f'SOUR:DEL {delay}')
        self.write('INIT')
        # wait for measurement to finish
        time.sleep(num_points * (delay + 0.08))
        while (int(self.query('STAT:OPER:COND?')) & 1024) == 0:
            time.sleep(self.pyvisa.timeout)
        raw_data = self.query('TRAC:DATA?')
        data = [float(d) for d in raw_data.split(',')]
        return data[1::5], data[::5]
