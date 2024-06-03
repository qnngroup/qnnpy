import pyvisa


class Keithley6510:
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)

    def reset(self):
        # Reset the instrument
        self.pyvisa.write("*RST")

    def setup_measurement(self):
        # # Set up the measurement configuration
        # self.daq.write(":SENS:FUNC 'RES'")
        # self.daq.write(":SENS:RES:MODE MAN")  # Manual range mode
        # self.daq.write(":SENS:RES:RANG 100")  # Set the range to 100 Ohms
        # self.daq.write(":SENS:RES:NPLC 1")    # Set integration rate to 1 PLC (Power Line Cycles)
        # Configure the instrument
        self.pyvisa.write(":SENS:FUNC 'FRES'")  # Set the function to measure resistance
        self.pyvisa.write(":SENS:FRES:NPLC 10")  # Set integration time to 10 PLC
        self.pyvisa.write(":SENS:FRES:RANG:AUTO ON")  # Enable auto-range
        self.pyvisa.write(":SENS:FRES:OCOM ON")  # Enable offset compensation

    def read_resistance(self):
        # Read the measured resistance value
        resistance = self.pyvisa.query(":MEAS:FRES?")
        return float(resistance)

    def close(self):
        # Close the connection
        self.daq.close()
