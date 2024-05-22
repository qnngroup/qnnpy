import pyvisa


class AnritsuMG9638A(object):
    """Python class for Antritsu M9638 tunable laser source, written by Adam McCaughan.  Adapted from
    Mihir's MATLAB code"""

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

    def setup_basic(self):
        self.write("MCW")  # Set laser to CW mode
        self.write("COH ON")  # Set laser to coherent mode
        self.set_power_unit("mW")
        self.set_wavelength(1550)

    def set_power_unit(self, power_unit):
        """power_unit should be either dBm, mW, or uW"""
        self.write("POWU %s" % power_unit)

    def get_power_unit(self, power_unit):
        return self.query("POWU?")

    def get_wavelength(self):
        wavelength_str = self.query("OUTW?")
        return float(wavelength_str)

    def set_output(self, output=False):
        self.write("OUTP %d" % output)

    def get_output(self):
        return bool(self.query("OUTP?"))

    def set_power(self, power, power_unit="uW"):
        """power_unit should be either dBm, mW, or uW"""
        power_str = self.write("POW %0.3d%s" % (power, power_unit))

    def get_power(self):
        power_str = self.query("POW?")
        return float(power_str)

    def set_wavelength(self, lambda_nm):
        self.write("WCNT %0.3fNM" % lambda_nm)


# ls = AnritsuMG9638A('GPIB0::24')

# def setup_4W_source_I_read_V(self):
#     self.write('*RST')
#     self.write(':SOUR:FUNC CURR') # Set operation mode to: source current
#     self.write(':SOUR:CURR:LEVEL 0E-6') # Set current level to 0 uA
#     self.write(':SYST:RSEN 1') # Turn off "Remote Sensing" aka 4-wire measurement mode
#     self.write('SENS:FUNC \"VOLT\", \"CURR\"') # Have it output


# def setup_2W_source_I_read_V(self):
#     self.write('*RST')
#     self.write(':SOUR:FUNC CURR') # Set operation mode to: source current
#     self.write(':SOUR:CURR:LEVEL 0E-6') # Set current level to 0 uA
#     self.write(':SYST:RSEN 0') # Turn off "Remote Sensing" aka 4-wire measurement mode
#     self.write('SENS:FUNC \"VOLT\", \"CURR\"') # Have it output


# def setup_2W_source_V_read_I(self):
#     self.write('*RST')
#     self.write(':SOUR:FUNC VOLT') # Set operation mode to: source voltage
#     self.write(':SOUR:VOLT:LEVEL 0E-3') # Set voltage level to 0 mV
#     self.write(':SYST:RSEN 0') # Turn off "Remote Sensing" aka 4-wire measurement mode
#     self.write('SENS:FUNC \"VOLT\", \"CURR\"') # Have it output


# def set_output(self, output = False):
#     if output is True:  self.write(':OUTP ON')
#     if output is False: self.write(':OUTP OFF')


# def set_compliance_i(self, compliance_i = 10e-6):
#     self.write(':SENS:CURR:PROT %0.3e' % compliance_i)


# def set_compliance_v(self, compliance_v = 10e-6):
#     self.write(':SENS:VOLT:PROT %0.3e' % compliance_v)


# def set_current(self, current = 0e-6):
#     self.write(':SOUR:CURR:LEVEL %0.4e' % current)   # Set current level


# def set_voltage(self, voltage = 0e-6):
#     self.write(':SOUR:VOLT:LEVEL %0.4e' % voltage)   # Set current level


# def read_voltage_and_current(self):
#     read_str = self.query(':READ?')
#     # See page 18-51 of manual, returns: voltage, current, resistance, timestamp, status info
#     # Returns something like '5.275894E-05,-1.508318E-06,+9.910000E+37,+2.562604E+03,+3.994000E+04'
#     data = read_str.split(',')
#     voltage, current = float(data[0]), float(data[1])
#     return voltage, current


# def read_current(self, current = 0e-6):
#     voltage, current = self.read_voltage_and_current()
#     return current


# def read_voltage(self):
#     voltage, current = self.read_voltage_and_current()
#     return voltage
