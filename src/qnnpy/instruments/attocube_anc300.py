import time

import pyvisa


class AttocubeANC300(object):
    """Python class for Attocube ANC300 peizo controller, by Di Zhu 2016"""

    """functions follow the user manual """

    def __init__(self, visa_name, baud_rate=38400):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name, baud_rate=baud_rate)
        self.pyvisa.timeout = 5000  # set response time in milliseconds

    def reset(self):
        for i in range(1, 4):
            self.setf(i, 1000)
            self.setv(i, 10)
            self.setm(i, "stp")

    def read(self):
        results = ""
        readline = self.pyvisa.read()
        while readline[0:2] != "OK" and readline[0:4] != "ERROR":
            results = results + readline
            readline = self.pyvisa.read()
        return results

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        self.write(string)
        return self.read()

    def help(self):
        self.write("help")
        print(self.read())

    def ver(self):
        self.write("ver")
        print(self.read())

    def setm(self, axis=1, amode="stp"):
        # <amode> ext, stp, gnd cap
        self.write("setm " + str(axis) + " " + amode)
        self.read()  # clear out the buffer

    def stop(self, axis=1):
        # <amode> ext, stp, gnd cap
        self.write("stop " + str(axis))
        print(self.read())  # clear out the buffer

    def stepu(self, axis=1, steps=1):
        # step up
        self.write("stepu " + str(axis) + " " + str(steps))
        self.read()  # clear out the buffer

    def contu(self, axis=1):
        # continuous travel up
        self.write("stepu " + str(axis) + " c")
        self.read()  # clear out the buffer

    def stepd(self, axis=1, steps=1):
        # step down
        self.write("stepd " + str(axis) + " " + str(steps))
        self.read()  # clear out the buffer

    def contd(self, axis=1):
        # conitnous drive down
        self.write("stepd " + str(axis) + " c")
        self.read()  # clear out the buffer

    def setf(self, axis=1, freq=1000):
        # set frequency
        self.write("setf " + str(axis) + " " + str(freq))
        self.read()

    def setv(self, axis=1, voltage=10):
        # set voltage
        self.write("setv " + str(axis) + " " + str(voltage))
        self.read()

    def getf(self, axis=1):
        # read frequency
        return self.query("getf " + str(axis))

    def getv(self, axis=1):
        # read voltage
        return self.query("getv " + str(axis))

    def getc(self, axis=1):
        # read capacitance
        self.setm(axis, "cap")
        time.sleep(2)
        # time.sleep(1)
        c = self.query("getc " + str(axis))

        self.setm(axis, "stp")
        time.sleep(1)
        return float(c.split(" ")[4])

    def reset(self):
        for i in range(1, 4):
            self.setm(axis=i, amode="stp")
            self.setv(i, 10)
            self.setf(i, 1000)


# ac = AttocubeANC150(u'ASRL5::INSTR')
# ac.reset()

# ac.write('help')
# print ac.read()
# ac.query('help')
