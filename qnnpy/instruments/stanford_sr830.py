import pyvisa


class StanfordSR830(object):
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        self.pyvisa.write("OUTX 1")
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def set_ref_freq(self, freq):
        self.pyvisa.write("FREQ %0.6e" % freq)

    def set_ref_amp(self, amp):
        self.pyvisa.write("SLVL %0.6e" % amp)

    # def IV_curve(self, freq, I_max, R_srs, npoints):
    #     self.pyvisa.write('FMOD 1')
    #     self.set_ref_freq(freq)

    def set_ref(self, ref):
        if ref == "INT":
            self.pyvisa.write("FMOD 1")
        if ref == "EXT":
            self.pyvisa.write("FMOD 0")

    def set_input_mode(self, mode):
        "A (0), A-B (1) , I (1 MΩ) (2) or I (100 MΩ) (3)"
        if mode == "A":
            self.pyvisa.write("ISRC 0")
        if mode == "A-B":
            self.pyvisa.write("ISRC 1")
        if mode == "I (1 MΩ)":
            self.pyvisa.write("ISRC 2")
        if mode == "I (100 MΩ)":
            self.pyvisa.write("ISRC 03")

    def set_sensitivity(self, sens):
        "Set (Query) the Sensitivity to 2 nV (0) through 1 V (26) rms full scale"
        self.pyvisa.write("SENS %0.6e" % sens)

    def read_X(self):
        self.pyvisa.write("OUTP? 1")
        return float(self.pyvisa.read())

    def read_Y(self):
        self.pyvisa.write("OUTP? 2")
        return float(self.pyvisa.read())

    def read_R(self):
        self.pyvisa.write("OUTP? 3")
        return float(self.pyvisa.read())

    def read_q(self):
        self.pyvisa.write("OUTP? 4")
        return float(self.pyvisa.read())


# N=40
# Isource_max=400e-9
# Isource1 = np.linspace(0,Isource_max, N+1)
# Isource2 = np.linspace(0, -Isource_max,  N+1)
# Isource3 = np.linspace(-Isource_max, 0,  N+1)
# Isource = np.concatenate([Isource1, Isource2])
# R_srs=2.469135e6
# R_M = 10e9                # R_srs >> Rnw_normal
# V_source = Isource*R_srs
# vread = np.zeros((len(V_source),1))
# iread = np.zeros((len(V_source),1))
# v_d = np.zeros((len(V_source),1))
# i_d = np.zeros((len(V_source),1))

# YOKO.set_voltage(0)
# YOKO.set_output(True)

# voffset = keith.read_voltage()
# # keith.set_output(True)

# sleep(2)
# keith.set_filter(state = 'OFF')
# # ir = - vr / R_srs - 2*vr/R_M


# for k1 in range(len(V_source)):
#     # YOKO.set_voltage(0)
#     # sleep(1)
#     # voffset = keith.read_voltage()

#     YOKO.set_voltage(V_source[k1])
#     if V_source[k1] == 0:
#         sleep(10)
#     sleep(1)
#     vread[k1] = keith.read_voltage()-voffset
#     iread[k1] = (V_source[k1] - vread[k1]) / R_srs - 2*vread[k1]/R_M
#     v_d[k1] = (R_srs/R_M+1)*vread[k1]
#     i_d[k1] = iread[k1]
#     print("I_source :" +str(Isource[k1]*1e9) +" nA, Vd :"+str(v_d[k1]*1e6)+" uV, Rd :"+str(v_d[k1]/i_d[k1])+" ohm")

# YOKO.set_output(False)
# # keith.set_output(False)
# # plt.plot(i_d*1e9,v_d/i_d,'-ob')
# plt.plot(v_d*1e6,i_d*1e9,'-ob')
# temp = ls1.read_temp('D4')
# scipy.io.savemat('S:/SC/Measurements/SPG808/SPG808_IV_340mK_nicelong.mat',{'temp':temp, 'v_device':v_d, 'i_device':i_d, 'v_read':vread})


# pm = Agilent8153A('GPIB0::22')
