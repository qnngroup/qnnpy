from time import sleep

import pyvisa


class Cryocon34(object):
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

    def read_temp(self, channel="A"):
        self.write(":INPUT? " + channel + ":TEMP")  # In form of ":INPUT? A:TEMP", A-D
        try:
            temperature = float(self.read())
        except Exception:
            temperature = "no reading"

        return temperature

    def setup_heater(self, load=25, range="25W", source_channel="A"):
        self.write("LOOP 1:SETPT 10")
        self.write("LOOP 1:LOAD " + str(load))
        self.write("LOOP 1:RANGE " + range)
        self.write("LOOP 1:SOUR CH" + str(source_channel))
        self.write("LOOP 1:TYPE OFF")  # Default to off in case of trouble
        self.write("LOOP 1:PMAN 0")  # Default to zero manual power in case of trouble
        # Range can be 50W, 5.0W, 0.5W and 0.05W
        # or for 25ohm load 25W, 2.5W, 0.3W and 0.03W

    def set_pid(self, proportional_gain=0.5, integral_gain=5.0, derivative_gain=0.0):
        self.write("LOOP 1:PGAIN " + str(proportional_gain))
        self.write("LOOP 1:IGAIN " + str(integral_gain))
        self.write("LOOP 1:DGAIN " + str(derivative_gain))

    def set_setpoint(self, setpoint=5):
        self.write("LOOP 1:SETPT " + str(setpoint))
        print("- Changing heater setpoint to " + str(setpoint) + "K")
        sleep(1)

    def set_control_type_rampp(self, ramp_rate=1.0):
        """Ramps at a rate of ramp_rate kelvin per minute using PID control"""
        self.write("LOOP 1:TYPE RAMPP")
        ramp_rate_rounded = float(round(ramp_rate * 10)) / 10
        self.write("LOOP 1:RATE " + str(ramp_rate_rounded))  # Ramp rate in K/min

    def set_control_type_pid(self):
        """Goes to setpoint value using PID control"""
        self.write("LOOP 1:TYPE PID")

    def start_heater(self):
        self.write("SYSTEM:BEEP 1")
        self.write("CONTROL")

    def stop_heater(self):
        self.write("STOP")
        self.write("SYSTEM:BEEP 1")
        sleep(0.5)

    def heat_up(
        self,
        load=50,
        range="50W",
        source_channel="B",
        setpoint=293,
        proportional_gain=0.5,
        integral_gain=5.0,
        derivative_gain=0.0,
    ):
        self.set_pid(proportional_gain, integral_gain, derivative_gain)
        self.write("LOOP 1:SETPT " + str(setpoint))
        self.write("LOOP 1:LOAD " + str(load))
        self.write("LOOP 1:RANGE " + range)
        self.write("LOOP 1:SOUR CH" + str(source_channel))
        self.write("LOOP 1:TYPE Rampp")  # Default to off in case of trouble
        self.write("LOOP 1:PMAN 5")
        self.start_heater()

    # *CLS
    # *IDN?
    # SYSTEM:BEEP 1;*OPC?
    # LOOP 2:TYPE OFF;*OPC? # Turns off analog heater in loop 2
    # LOOP 1:TYPE PID;*OPC? # Sets PID mode
    # LOOP 1:TYPE RAMPP;*OPC? # Sets PID ramp mode
    # LOOP 1:SOUR CHD;*OPC? # Sets heater ("loop 1") channel e.g. CHB = Channel B
    # LOOP 1:SETPT 10;*OPC? # Sets desired temp set point
    # LOOP 1:RANGE 0.5W;*OPC?
    # LOOP 1:RANGE 5.0W;*OPC?
    # HEATER:AUTOTUNE:START # Must be in TYPE PID mode to run
    # LOOP 1:PGAIN 0.5;*OPC?
    # LOOP 1:IGAIN 5;*OPC?
    # LOOP 1:DGAIN 0;*OPC?
    # LOOP 1:SOURCE?
    # LOOP 1:SOUR CHA
    # LOOP 1:SETPT?
    # LOOP 1:TYPE?
    # LOOP 1:RANGE?
    # LOOP 1:LOAD?
    # LOOP 1:RAMP?
    # LOOP 1:RATE? # A rate of 0.02 means the heater will do 0.02K/min (if using Kelvin units)
    # CONTROL;*OPC?
    # STOP;*OPC?
