import time

import pyvisa


class Pollux(object):
    """Python class for Pollux motor, by Di Zhu 2016"""

    def __init__(self, visa_name, baud_rate=19200, axis=1):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name, baud_rate=baud_rate)
        self.pyvisa.timeout = 5000  # set response time in milliseconds
        self.axis = str(axis)

    def read(self):
        return self.pyvisa.read()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def position(self):
        self.query(
            self.axis + " npos"
        )  # there's a bug here; you have to ask for the position twice to get the real result
        print("position = " + str(float(self.query(self.axis + " npos"))))

    def status(self):
        return int(self.query(self.axis + " nstatus"))
        # 1 means moving in progress

    def reset(self):
        self.write("*RST")
        self.write(self.axis + " ncal")
        # self.write(self.axis + ' setnpos')
        while self.status() == 1:
            print("moving...")
            time.sleep(0.5)  # wait time in seconds
        self.position()

    # def move_with_speed(self, speed=1.0):
    #     #mm/s; range: +-2000
    #     #this starts a moving with a constant speed
    #     self.write(str(speed) + ' ' + self.axis + ' speed')

    def move_to(self, coordinate):
        self.write(str(float(coordinate)) + " " + self.axis + " nm")
        while self.status() == 1:
            print("moving...")
            time.sleep(0.5)  # wait time in seconds
        self.position()

    def move_by(self, distance):
        self.write(str(float(distance)) + " " + self.axis + " nr")
        while self.status() == 1:
            print("moving...")
            time.sleep(0.5)  # wait time in seconds
        self.position()
