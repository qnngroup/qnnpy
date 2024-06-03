# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 09:40:21 2023

@author: QNN
"""

import datetime

import numpy as np
import pyvisa


# the commonds can be found in the following link
# http://rfmw.em.keysight.com/bihelpfiles/Trueform/webhelp/US/Default.htm?lc=eng&cc=US&id=2197433
class KeysightDSOX(object):
    def __init__(self, visa_name):
        rm = pyvisa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()

    def read_raw(self):
        return self.pyvisa.read_raw()

    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def run(self):
        self.write(":RUN")

    def single(self):
        self.write(":SING")

    def stop(self):
        self.write(":STOP")

    def digitize(self):
        self.write(":DIG")

    def set_trigger_type(self, mode="EDGE"):
        """
        {EDGE | GLITch | PATTern | TV | DELay | EBURst | OR | RUNT | SHOLd | TRANsition | SBUS{1 | 2}}
        """
        self.write(":TRIG:MODE " + mode)

    def set_trigger_mode(self, trigger_mode="Normal"):
        """FAKE"""
        """
        {EDGE | GLITch | PATTern | TV | DELay | EBURst | OR | RUNT | SHOLd | TRANsition | SBUS{1 | 2}}
        """
        self.write(":TRIG:MODE EDGE")

    def set_trigger_source(self, source="CHAN1"):
        """
        {CHANnel<n> |EXTernal | LINE | WGEN | WGEN1 |WGEN2 | WMOD}
        """
        self.write(":TRIG:EDGE:SOUR " + source)

    def set_trigger_level(self, v=0.1):
        self.write(":TRIG:EDGE:LEV " + str(v))

    def set_trigger(self, source="C1", volt_level=0.1, slope="pos"):
        self.write(":TRIG:EDGE:LEV " + str(volt_level))

    def get_trigger_mode(self):
        return  # self.vbs_ask('app.Acquisition.TriggerMode')

        # Max 40e-6

    def set_timebase_scale(self, t=1e-6):
        self.write(":TIM:SCAL " + str(t))

    # test from here
    def set_timebase_mode(self, mode="MAIN"):
        """
        {MAIN | WINDow | XY |ROLL}
        """
        self.write(":TIM:MODE " + mode)

    def set_channel_bwLimit(self, bw="0", channel="1"):
        """'0' is false, '1' is true"""
        self.write(":CHAN" + str(channel) + ":BWL " + str(bw))

    def set_channel_display(self, display="1", channel="1"):
        self.write(":CHAN" + str(channel) + ":DISP " + str(display))

    def set_channel_impedance(self, impedance="ONEM", channel="1"):
        """{ONEMeg | FIFTy}"""
        self.write(":CHAN" + str(channel) + ":IMP " + str(impedance))

    def set_channel_invert(self, invert="0", channel="1"):
        self.write(":CHAN" + str(channel) + ":INV " + str(invert))

    def set_channel_offset(self, offset=0, channel="1"):
        self.write(":CHAN" + str(channel) + ":OFFS " + str(offset))

    def set_channel_scale(self, scale=0.1, channel="1"):
        self.write(":CHAN" + str(channel) + ":SCAL " + str(scale))

    def set_channel_autoScale(self, channel="1"):
        self.write(":AUT CHAN" + str(channel))

    def set_acquire_type(self, typ="HRES"):
        self.write(":ACQ:TYPE " + str(typ))

    def set_acquire_mode(self, mode="RTIM"):
        """{RTIMe | ETIMe |SEGMented}"""
        self.write(":ACQ:MODE " + str(mode))

    def set_segmented_counts(self, count=2):
        """2 to 1000"""
        self.write(":ACQ:MODE SEGM")
        self.write(":ACQ:SEGM:COUN " + str(count))

    def set_awg_arb_data(self, data, output="1"):
        self.write(":WGEN" + str(output) + ":ARB:DATA " + data)

    def set_awg_arb_data_clear(self, output="1"):
        self.write(":WGEN" + str(output) + ":ARB:DATA:CLE")

    def set_awg_freq(self, freq=1e3, output="1"):
        self.write(":WGEN" + str(output) + ":FREQ " + str(freq))

    def set_awg_pulse(self, width=10e-9, output="1"):
        self.write(":WGEN" + str(output) + ":FUNC:PULS:WIDT " + str(width))

    def set_awg_ramp(self, percent=50, output="1"):
        self.write(":WGEN" + str(output) + ":FUNC:RAMP:SYMM " + str(percent))

    def set_awg_square(self, dcycle=20, output="1"):
        self.write(":WGEN" + str(output) + ":FUNC:SQU:DCYC " + str(dcycle))

    def set_awg_output(self, val="1", output="1"):
        """1 for ON, 0 for OFF"""
        self.write(":WGEN" + str(output) + ":OUTP " + str(val))

    def set_awg_output_mode(self, mode="NORM", output="1"):
        """NORM | SING"""
        self.write(":WGEN" + str(output) + ":OUTP:MODE " + str(mode))

    def set_awg_amplitude(self, v=0.1, output=1):
        self.write(":WGEN" + str(output) + ":VOLT " + str(v))

    def set_awg_offset(self, v=0, output=1):
        self.write(":WGEN" + str(output) + ":VOLT:OFFS " + str(v))

    def set_awg_high(self, v=0.1, output=1):
        self.write(":WGEN" + str(output) + ":VOLT:HIGH " + str(v))

    def set_awg_low(self, v=0, output=1):
        self.write(":WGEN" + str(output) + ":VOLT:LOW " + str(v))

    def set_awg_phase(self, phase=0, output=1):
        self.write(":WGEN" + str(output) + ":TRAC:PHAS " + str(phase))

    def get_preamble(self):
        val = self.query(":WAV:PRE?")
        (
            wav_form,
            acq_type,
            wfmpts,
            avgcnt,
            x_increment,
            x_origin,
            x_reference,
            y_increment,
            y_origin,
            y_reference,
        ) = np.array(val.split(","), dtype=np.float32)
        return (
            wav_form,
            acq_type,
            wfmpts,
            avgcnt,
            x_increment,
            x_origin,
            x_reference,
            y_increment,
            y_origin,
            y_reference,
        )

    def save_screenshot(self, file_name=None, white_background=True):
        print("screen shot not saved. need to set up")
        if file_name is None:
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            file_name = time_str

        return file_name

    def get_waveform(self, source="CHAN1", form="ASC", points="MAX"):
        self.write(":WAV:SOUR " + str(source))
        self.write(":WAV:FORM " + str(form))
        self.write(":WAV:POIN " + str(points))

        xorigin = float(self.query(":WAV:XOR?"))
        xinc = float(self.query(":WAV:XINC?"))
        yorigin = float(self.query(":WAV:YOR?"))
        yinc = float(self.query(":WAV:YINC?"))
        raw_data = self.query(":WAV:DATA?")

        data = np.array(raw_data[10:-1].split(","), dtype=np.float32)
        numsamples = len(data)

        x = np.array(range(numsamples)) * xinc + xorigin
        y = data - yorigin
        # y = data*yinc - yorigin
        return x, y

    def get_single_trace(self, channel="CHAN1", form="ASC", points="MAX"):
        self.write(":WAV:SOUR " + str(channel))
        self.write(":WAV:FORM " + str(form))
        self.write(":WAV:POIN " + str(points))

        xorigin = float(self.query(":WAV:XOR?"))
        xinc = float(self.query(":WAV:XINC?"))
        yorigin = float(self.query(":WAV:YOR?"))
        yinc = float(self.query(":WAV:YINC?"))
        raw_data = self.query(":WAV:DATA?")

        data = np.array(raw_data[10:-1].split(","), dtype=np.float32)
        numsamples = len(data)

        x = np.array(range(numsamples)) * xinc + xorigin
        y = data - yorigin
        # y = data*yinc - yorigin
        return x, y

    def set_measurement_clear(self):
        self.write(":MEAS:CLE")

    def set_measurement_stat_disp(self, val=1):
        self.write(":MEAS:STAT:DISP " + str(val))

    def set_measurement_stat_reset(self):
        self.write(":MEAS:STAT:RES")

    def set_measurement_tedge(self):
        self.write(":MEAS:TEDG +1")

    def get_measurement_results(self):
        results = self.query(":MEAS:RES?")
        return results

    """
      self.write(f':WAVeform:SOURce {channel}')
            self.write(f':WAVeform:FORMat {data_type}')
            waveform_data = self.oscilloscope.query_binary_values(':WAVeform:DATA?', datatype=data_type, container=np.array)
    
    """

    ":DIGitize CHANnel1"

    ":WAVeform:SOURce CHANnel1"
