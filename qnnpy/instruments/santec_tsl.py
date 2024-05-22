# Controlling the santec tsl 5xx laser
# Copyright (c) 2019 Prashanta Kharel, HyperLight Corporation
import time

import pyvisa


class SantecTSLBase:
    # Base class for controlling Santec TSL laser
    def __init__(self, rsc_name=None):
        self.rsc_name = rsc_name
        self.wav_min = None
        self.wav_max = None

    def initialize(self):
        pass

    def getPowerState(self):
        # return 0 for OFF, 1 for ON
        pass

    def turnLaserDiodeON(self, onoroff):
        # onoroff: True means ON, False means OFF
        pass

    def setAttenuation(self, valuedB):
        pass

    def setWavelength(self, valueWavlength):
        pass

    def setFine(self, valueFine):
        pass

    def openShutter(self, onoroff):
        # onoroff: True means open, False means close
        pass

    def sweepSettings(self, numOfSweeps, triggerOut=True):
        pass

    def setSweepCycles(self, numOfSweeps):
        pass

    def setTriggerOut(self, triggerOut=True):
        pass

    def startSweep(self):
        pass

    def startSweepLoop(self):
        pass

    def stopSweep(self):
        pass

    def setSweepSpeed(self, sweepSpeed_nm):
        pass

    def setStartWavelength(self, startWavelength_nm):
        pass

    def setStopWavelength(self, stopWavelength_nm):
        pass

    def setWavelengthUnit(self, unit):
        pass

    def getInternalPower(self):
        pass

    def close(self):
        pass

    def setSweepMode(self, nmode):
        pass

    def setSweepStep(self, step_nm):
        pass


class SantecTSL(SantecTSLBase):
    def __init__(self, rsc_name=None):
        self.rsc_name = rsc_name
        rm = pyvisa.ResourceManager()
        if rsc_name is not None:
            self.rsc_name = rsc_name
        self.rsc = rm.open_resource(self.rsc_name)
        print("IDN: " + self.rsc.query("*IDN?"))
        # wavelength limits
        self.wav_min = None
        self.wav_max = None

    def initialize(self):
        self.setWavelengthUnit("nm")
        time.sleep(0.3)
        self.openShutter(False)
        self.wav_min, self.wav_max = self.getWavlengthLimits()
        # check to power state and turn it ON if it is OFF
        if self.getPowerState() == 0:
            self.turnLaserDiodeON(True)
            print("Waiting for laser to warm up...", end="")
            while not self.getPowerState():
                print(".", end="")
                time.sleep(1)
            print("Done!")
        self.setAttenuation(30)
        time.sleep(0.3)
        self.openShutter(1)  # open the shutter 1: shutter is on
        print(
            "min wavelength: {} nm, max wavelength: {} nm".format(
                self.wav_min, self.wav_max
            )
        )

    def checkWavelength(self, wavelength):
        if not (self.wav_min <= wavelength <= self.wav_max):
            error_msg = "Wavelength {} is outside my range".format(wavelength)
            raise Exception(error_msg)

    def getPowerState(self):
        # return 0 for OFF, 1 for ON
        return int(self.rsc.query(":POWer:STATe?"))

    def turnLaserDiodeON(self, onoroff):
        # onoroff: True means ON, False means OFF
        if onoroff:
            self.rsc.write(":POWer:STATe 1")
        else:
            self.rsc.write(":POWer:STATe 0")

    def setAttenuation(self, valuedB):
        self.rsc.write(":POW:ATT " + str(valuedB))

    def setWavelength(self, valueWavlength):
        self.checkWavelength(valueWavlength)
        self.rsc.write(":WAVelength " + str(valueWavlength))

    def setFine(self, valueFine):
        if -100.0 < valueFine < 100.0:
            self.rsc.write("WAVelength:FINe {:.2f}".format(valueFine))
        else:
            print("Fine tuning value {:.3} is out of range".format(float(valueFine)))

    def openShutter(self, onoroff):
        # onoroff: True means open, False means close
        if onoroff:
            self.rsc.write(":POW:SHUT 0")
            print("Shutter is now open!")
        else:
            self.rsc.write(":POW:SHUT 1")
            print("Shutter is now closed!")

    def sweepSettings(self, numOfSweeps, triggerOut=True):
        # write sweep settings to laser. numOfSweeps=0 for continous
        self.rsc.write(":WAVelength:SWEep:MODe 1")  # sweep mode: 1way continuous
        time.sleep(0.3)
        # use cycles if Range 0~999. 0 means infinite sweep
        self.rsc.write(":WAVelength:SWEep:CYCLes " + str(numOfSweeps))
        if numOfSweeps == 0:
            self.rsc.write(":WAV:SWE:REP")  # continuously repeat the sweeps
        time.sleep(0.3)
        if triggerOut:
            # sends a trigger out at the start of a sweep
            self.rsc.write(":TRIGger: OUTPut 2")
        time.sleep(0.5)
        # self.startSweep()       # start the sweep

    def setSweepCycles(self, numOfSweeps):
        self.rsc.write(
            ":WAVelength:SWEep:CYCLes " + str(numOfSweeps)
        )  # if Range 0~999. 0 means infinite sweep
        if numOfSweeps == 0:
            self.rsc.write(":WAV:SWE:REP")  # continuously repeat the sweeps

    def setTriggerOut(self, triggerOut=True):
        if triggerOut:
            # sends a trigger out at the start of a sweep
            self.rsc.write(":TRIGger: OUTPut 2")
        else:
            self.rsc.write(":TRIGger: OUTPut 0")

    def startSweep(self):
        # start the wavelength sweep
        # time.sleep(0.5)
        self.rsc.write(":WAVelength:SWEep 1")

    def startSweepLoop(self):
        self.rsc.write(":WAVelength:SWEep:STATe:REPeat")

    def stopSweep(self):
        # stop the wavelength sweep
        # for some reason must first pause, then stop it.
        self.rsc.write(":WAVelength:SWEep 2")
        time.sleep(0.1)
        self.rsc.write(":WAVelength:SWEep 0")

    def setSweepSpeed(self, sweepSpeed_nm):
        self.rsc.write(":WAVelength:SWEep:SPEed " + str(sweepSpeed_nm))

    def setStartWavelength(self, startWavelength_nm):
        # speed_light_vacuum = 299792458
        # startfrequency = 299792458 / startWavelength_nm * 1.0e-3  # in THz
        self.checkWavelength(startWavelength_nm)
        self.rsc.write(":WAVelength:SWEep:STARt %.5f" % startWavelength_nm)

    def setStopWavelength(self, stopWavelength_nm):
        # speed_light_vacuum = 299792458
        # stopfrequency = 299792458 / stopWavelength_nm * 1.0e-3  # in THz
        self.checkWavelength(stopWavelength_nm)
        self.rsc.write(":WAVelength:SWEep:STOP %.5f" % stopWavelength_nm)
        # self.laser.write(':FREQuency:SWEep:STOP %.5f' % stopfrequency)

    def setWavelengthUnit(self, unit):
        if unit == "nm":
            self.rsc.write(":WAVelength:UNIT 0")  # 0 means in nm
        elif unit == "THz" or unit == "thz":
            self.rsc.write(":WAVelength:UNIT 1")  # 1 means in  THz
        else:
            raise Exception("Unrecognized unit")

    def getInternalPower(self):
        return self.rsc.query(":POWer:ACTual?")

    def setSweepMode(self, nmode):
        self.rsc.write("WAVelength:SWEep:MODe " + str(nmode))

    def setSweepStep(self, step_nm):
        self.rsc.write("WAVelength:SWEep:STEp " + str(step_nm))

    def getWavlengthLimits(self):
        wav_min = float(self.rsc.query("WAV:MIN?"))
        wav_max = float(self.rsc.query("WAV:MAX?"))
        return wav_min, wav_max

    def close(self):
        self.stopSweep()  # stop the sweep
        time.sleep(0.3)
        self.setAttenuation(30)
        time.sleep(0.3)
        self.openShutter(0)
        # self.turnLaserDiodeON(0)
        self.rsc.close()


class SantecTSLDummy(SantecTSLBase):
    # Dummy class for controlling Santec TSL laser
    def __init__(self, rsc_name=None):
        super().__init__(rsc_name)
        self.already_on = False

    def initialize(self, rsc_name=None):
        self.wav_min = 1480.0  # nm
        self.wav_max = 1630.0  # nm
        if rsc_name is not None:
            self.rsc_name = rsc_name
        if not self.already_on:
            print("Waiting for dummy TSL to warm up...")
            time.sleep(1)
            print("Warmup complete")

    def getPowerState(self):
        # return 0 for OFF, 1 for ON
        return 1

    def getInternalPower(self):
        return 2.000
