# -*- coding: utf-8 -*-
"""
Created on Wed May  6 17:21:25 2020

@author: omedeiro
"""

import signal
import time
from sys import exit
from time import sleep

import numpy as np

import qnnpy.functions.functions as qf


class Snspd:
    """Class for SNSPD measurement. This class handels the instrument
    configuration, measurement, plotting, logging, and saving.
    See qnnpy\examples to see this class in action"""

    def __init__(self, configuration_file):
        #######################################################################
        #       Load .yaml configuraiton file
        #######################################################################

        # qf is a package of base functions that can be used in any class.
        self.properties = qf.load_config(configuration_file)

        self.sample_name = self.properties["Save File"]["sample name"]
        self.device_name = self.properties["Save File"]["device name"]
        self.device_type = self.properties["Save File"]["device type"]

        if self.properties.get("iv_sweep"):
            self.R_srs = self.properties["iv_sweep"]["series_resistance"]

        if self.properties.get("double_sweep"):
            self.R_srs_g = self.properties["double_sweep"]["series_resistance_g"]

        self.isw = 0
        self.instrument_list = []

        #######################################################################
        # Setup instruments
        #######################################################################

        self.inst = qf.Instruments(self.properties)
        # if there are any errors in setting up, compare older versions of
        # snspd on github with qf.Instruments
        signal.signal(signal.SIGINT, self.handler)

    def handler(self, signum, frame):
        """
        Safer exit handling (e.g. on ctrl+c)
        """
        try:
            self.inst.source.set_voltage(0)
            self.inst.source.set_output(False)
        except Exception:
            pass
        try:
            self.inst.awg.set_output(False)
        except Exception:
            pass
        exit(1)

    def get_property(self, property_type, prop):
        return self.properties[property_type][prop]

    def average_counts(self, counting_time, iterations, trigger_v):
        """

        This function sets the counter trigger voltage, integrates the number
        of counts over the counting time. The source is turned on before and turned off after.

        Average COUNT RATE per iteration is returned in [[ [Hz] ]]


        """

        count_rate_temp = []

        for i in range(iterations):
            self.inst.source.set_output(True)
            sleep(0.05)  # bias device
            voltage = self.inst.meter.read_voltage()
            sleep(0.05)
            self.inst.meter.local_key()
            # self.inst.source.set_voltage(np.sign(i)*1e-3); time.sleep(0.05); #reverse bias to unlatch?
            # self.inst.source.set_voltage(i*self.R_srs); time.sleep(0.05)
            try:
                self.inst.counter.set_impedance(self.properties["Counter"]["impedance"])
                self.inst.counter.set_coupling(self.properties["Counter"]["coupling"])
            except Exception:
                pass
            self.inst.counter.set_trigger(trigger_v)
            count_rate = self.inst.counter.count_rate(
                counting_time=counting_time
            )  # obtain counts
            count_rate_temp.append(count_rate)  # append counts for each itteration

            if voltage > 0.005:
                print(str(count_rate) + " wire switched")
            else:
                print(count_rate)

            self.inst.source.set_output(False)
            sleep(0.05)
        count_rate_avg = np.mean(count_rate_temp)  # average of each itteraton
        return count_rate_avg

    def tc_measurement(self, voltage, path):
        """
        Tc measurement for ICE Oxford. Path must include filename.txt
        Bias device at some value much lower than Ic.
        This code will bias device, measure voltage, turn off voltage, every
        two seconds. ICE will measure temp every 10 seconds. Slower sweep is
        better. Keyboard Interrupt to end. File will be saved at path.
        """
        self.inst.source.set_voltage(voltage)
        self.inst.source.set_output(True)
        while True:
            file = open(path, "a")
            if self.properties["Temperature"]["name"] == "ICE":
                temp = qf.ice_get_temp(select=1)
            else:
                temp = self.inst.temp.read_temp(self.inst.temp.channel)
            self.inst.source.set_output(True)
            sleep(1)
            voltage = self.inst.meter.read_voltage()
            line = str(temp) + ", " + str(voltage)
            print(line)
            file.write("\n" + line)
            file.close()
            self.inst.source.set_output(False)

            sleep(1)


###############################################################################
#   _____ __  ______  ________    ___   __________ ___________
#  / ___// / / / __ )/ ____/ /   /   | / ___/ ___// ____/ ___/
#  \__ \/ / / / __  / /   / /   / /| | \__ \\__ \/ __/  \__ \
# ___/ / /_/ / /_/ / /___/ /___/ ___ |___/ /__/ / /___ ___/ /
# /____/\____/_____/\____/_____/_/  |_/____/____/_____//____/
#
###############################################################################

# subclass inherits the properties of snspd


class TriggerSweep(Snspd):
    """Sweeps trigger on counter.

    Configuration : trigger_sweep
    [start: counter trigger start point],
    [stop: counter trigger stop point],
    [step: counter trigger step],
    [bias_voltage: device bias],
    [attenuation_db: optical attenuation],
    [counting_time: integration time on counter]
    """

    def run_sweep(self):
        """Sweep counter voltage start-stop

        (counter_trigger_voltage not used)

        """
        self.inst.meter.local_key()
        self.v_bias = self.properties["trigger_sweep"]["bias_voltage"]
        atten_level = self.properties["trigger_sweep"]["attenuation_db"]
        coupling_setting = self.properties["Counter"]["coupling"]
        impedance_setting = self.properties["Counter"]["impedance"]

        self.inst.source.set_output(False)
        sleep(0.2)
        self.inst.source.set_output(True)
        self.inst.source.set_voltage(0)
        sleep(0.2)
        self.inst.source.set_voltage(self.v_bias)
        sleep(1)
        self.inst.counter.set_impedance(impedance_setting)  # 50Ohm
        self.inst.counter.set_coupling(coupling_setting)  # 50Ohm

        counting_time = self.properties["trigger_sweep"]["counting_time"]
        start = self.properties["trigger_sweep"]["start"]
        stop = self.properties["trigger_sweep"]["stop"]
        step = self.properties["trigger_sweep"]["step"]
        count_rate = []
        atten_list = [atten_level, 100]
        atten_list_bool = [False, True]
        for i in range(2):
            print("\\\\\\\\ BEAM BLOCK: %s \\\\\\\\ " % atten_list_bool[i])
            self.inst.attenuator.set_attenuation_db(atten_list[i])
            self.inst.attenuator.set_beam_block(atten_list_bool[i])
            sleep(5)
            trigger_v, count_rate = self.inst.counter.scan_trigger_voltage(
                voltage_range=[start, stop],
                counting_time=counting_time,
                num_pts=int(np.floor((stop - start) / step)),
            )
            self.trigger_v = trigger_v
            if i == 0:
                self.counts_trigger_light = count_rate
            else:
                self.counts_trigger_dark = count_rate
            sleep(1)
        self.inst.attenuator.set_beam_block(True)

    def plot(self, close=True):
        ydata = [self.counts_trigger_dark, self.counts_trigger_light]
        label = [
            "Beam block: True",
            "Beam block: False",
        ]  # maybe update this to be the attenuation level

        full_path = qf.save(self.properties, "trigger_sweep")[0]
        print(full_path)
        qf.plot(
            self.trigger_v,
            ydata,
            title=self.sample_name + " " + self.device_type + " " + self.device_name,
            xlabel="Trigger Voltage (V)",
            ylabel="Count Rate (Hz)",
            label=label,
            y_scale="log",
            path=full_path,
            close=close,
        )

    def save(self):
        data_dict = {
            "trigger_v": self.trigger_v,
            "counts_trigger_dark": self.counts_trigger_dark,
            "counts_trigger_light": self.counts_trigger_light,
            "v_bias": self.v_bias,
        }
        self.full_path = qf.save(
            self.properties,
            "trigger_sweep",
            data_dict,
            instrument_list=self.instrument_list,
        )


class TriggerSweepScope(Snspd):
    """Sweeps trigger on scope channel. Noise from counter was switing device.

    FIXME: loop through attenuation on and OFF

    This class uses the scope to output a voltage pulse at the AUX port on each
    scope trigger. The scope trigger is swept instead of the counter and the
    AUX output is connected to the counter.


    Configuration : trigger_sweep:
    [start: counter trigger start point],
    [stop: counter trigger stop point],
    [step: counter trigger step],
    [bias_voltage: device bias],
    [attenuation_db: optical attenuation],
    [counting_time: integration time on counter]
    [counter_trigger_voltage: trigger level set on counter]


    """

    def run_sweep(self):
        """Sweep scope trigger. counter trigger set with
        "counter_trigger_voltage"

        On Lecroy 760Zi: Utilities>Utilities Setup>Aux Output>Trigger Out> 1V into 1MOhm


        """
        self.v_bias = self.properties["trigger_sweep"]["bias_voltage"]
        atten_level = self.properties["trigger_sweep"]["attenuation_db"]

        self.inst.source.set_output(False)
        sleep(0.2)
        self.inst.source.set_output(True)
        self.inst.source.set_voltage(0)
        sleep(0.2)
        self.inst.source.set_voltage(self.v_bias)
        sleep(1)
        self.inst.counter.write(":INP:IMP 1E6")  # 1 MOhm input impedance
        ct_volt = self.properties["trigger_sweep"]["counter_trigger_voltage"]
        self.inst.counter.set_trigger(trigger_voltage=ct_volt)

        counting_time = self.properties["trigger_sweep"]["counting_time"]
        start = self.properties["trigger_sweep"]["start"]
        stop = self.properties["trigger_sweep"]["stop"]
        step = self.properties["trigger_sweep"]["step"]
        trigger_v = np.arange(start, stop, step)

        atten_list = [100, atten_level]
        atten_list_bool = [True, False]
        for a in range(2):
            print("\\\\\\\\ BEAM BLOCK: %s \\\\\\\\ " % atten_list_bool[a])
            self.inst.attenuator.set_attenuation_db(atten_list[a])
            self.inst.attenuator.set_beam_block(atten_list_bool[a])
            counts = []
            for i in trigger_v:
                self.inst.scope.set_trigger(
                    source=self.inst.scope_channel, volt_level=i, slope="positive"
                )
                tv, count_rate = self.inst.counter.scan_trigger_voltage(
                    voltage_range=[ct_volt, ct_volt],
                    counting_time=counting_time,
                    num_pts=1,
                )

                counts.append(count_rate)
                sleep(1)
                print("Scope Trigger: %0.3f" % (i))
            if a == 0:
                # this was added so that qf.plot can accept multiple ydata traces as lists. all single traces need to be arrays
                self.counts_trigger_dark = np.asarray(counts, dtype=np.float32)
            else:
                self.counts_trigger_light = np.asarray(counts, dtype=np.float32)
        self.inst.attenuator.set_beam_block(True)
        self.trigger_v = trigger_v

    def plot(self, close=True):
        ydata = [self.counts_trigger_dark, self.counts_trigger_light]
        label = [
            "Beam block: True",
            "Beam block: False",
        ]  # maybe update this to be the attenuation level

        full_path = qf.save(self.properties, "trigger_sweep")
        qf.plot(
            self.trigger_v,
            ydata,
            title=self.sample_name + " " + self.device_type + " " + self.device_name,
            xlabel="Trigger Voltage (V)",
            ylabel="Count Rate (Hz)",
            label=label,
            y_scale="log",
            path=full_path,
            close=close,
        )

    def save(self):
        data_dict = {
            "trigger_v": self.trigger_v,
            "counts_trigger_dark": self.counts_trigger_dark,
            "counts_trigger_light": self.counts_trigger_light,
            "v_bias": self.v_bias,
        }
        self.full_path = qf.save(
            self.properties,
            "trigger_sweep",
            data_dict,
            instrument_list=self.instrument_list,
        )


class IvSweep(Snspd):
    """Class object for iv sweeps

    Configuration: iv_sweep:
    [start: initial bias current],
    [stop: final bias current],
    [steps: number of points],
    [sweep: number of itterations],
    [full_sweep: Include both positive and negative bias],
    [series_resistance: resistance at voltage source ie R_srs]

    """

    def run_sweep_fixed(self):
        """Runs IV sweep with config paramters
        This constructs #steps between start and 75% of final current.
        Then, #steps between 75% and 100% of final current.

        np.linspace()
        """
        # self.inst.source.reset()
        # self.inst.meter.reset()

        self.inst.source.set_output(False)

        start = self.properties["iv_sweep"]["start"]
        stop = self.properties["iv_sweep"]["stop"]
        steps = self.properties["iv_sweep"]["steps"]
        sweep = self.properties["iv_sweep"]["sweep"]
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties["iv_sweep"]["full_sweep"]
        Isource1 = np.linspace(start, stop * 0.75, steps)  # Coarse
        Isource2 = np.linspace(stop * 0.75, stop, steps)  # Fine

        if full_sweep:
            Isource = np.concatenate(
                [Isource1, Isource2, Isource2[::-1], Isource1[::-1]]
            )
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = np.concatenate([Isource1, Isource2])
        self.v_set = np.tile(Isource, sweep) * self.R_srs

        self.inst.source.set_output(True)
        sleep(1)
        voltage = []
        current = []

        try:
            if self.inst.meter.name == "Keithley2400":
                self.inst.meter.setup_read_volt()
                self.inst.meter.write("OUTP ON")
        except Exception:
            pass

        for n in self.v_set:
            self.inst.source.set_voltage(n)
            sleep(0.1)  # CHANGE BACK TO 0.1

            vread = self.inst.meter.read_voltage()  # Voltage

            iread = (n - vread) / self.R_srs  # (set voltage - read voltage)

            print("V=%.4f V, I=%.2f uA, R =%.2f" % (vread, iread * 1e6, vread / iread))
            voltage.append(vread)
            current.append(iread)

        self.v_read = voltage
        self.i_read = current

    def run_sweep_sourceMeter(self):
        # self.inst.sourcemeter.reset()

        self.inst.sourcemeter.set_output(False)
        self.inst.sourcemeter.setup_2W_source_I_read_V()

        start = self.properties["iv_sweep"]["start"]
        stop = self.properties["iv_sweep"]["stop"]
        steps = self.properties["iv_sweep"]["steps"]
        sweep = self.properties["iv_sweep"]["sweep"]
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties["iv_sweep"]["full_sweep"]
        Isource1 = np.linspace(start, stop * 0.75, steps)  # Coarse
        Isource2 = np.linspace(stop * 0.75, stop, steps)  # Fine

        if full_sweep:
            Isource = np.concatenate(
                [Isource1, Isource2, Isource2[::-1], Isource1[::-1]]
            )
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = np.concatenate([Isource1, Isource2])
        self.I_set = np.tile(Isource, sweep)

        self.inst.sourcemeter.set_output(True)
        sleep(1)
        voltage = []
        current = []

        for n in self.I_set:
            self.inst.sourcemeter.set_current(n)
            sleep(0.1)  # CHANGE BACK TO 0.1

            vread = self.inst.sourcemeter.read_voltage()  # Voltage

            # iread = (n-vread)/self.R_srs#(set voltage - read voltage)

            # iread = self.inst.sourcemeter.read_current()
            iread = n

            print("V=%.4f V, I=%.2f uA, R =%.2f" % (vread, iread * 1e6, vread / iread))
            voltage.append(vread)
            current.append(iread)

        self.v_read = voltage
        self.i_read = current

    def run_sweep_dynamic(self):
        """Runs IV sweep with config paramters
        This constructs [points_coarse] between start and [percent] of final current.
        Then, [points_fine] between [percent] and 100% of final current.

        uses np.linspace()
        """
        self.inst.source.reset()
        self.inst.meter.reset()

        self.inst.source.set_output(False)

        start = self.properties["iv_sweep"]["start"]
        stop = self.properties["iv_sweep"]["stop"]
        percent = self.properties["iv_sweep"]["percent"]
        num1 = self.properties["iv_sweep"]["points_coarse"]
        num2 = self.properties["iv_sweep"]["points_fine"]

        sweep = self.properties["iv_sweep"]["sweep"]
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties["iv_sweep"]["full_sweep"]
        Isource1 = np.linspace(start, stop * percent, num1)  # Coarse
        Isource2 = np.linspace(stop * percent, stop, num2)  # Fine

        if full_sweep:
            Isource = np.concatenate(
                [Isource1, Isource2, Isource2[::-1], Isource1[::-1]]
            )
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = np.concatenate([Isource1, Isource2])
        self.v_set = np.tile(Isource, sweep) * self.R_srs

        self.inst.source.set_output(True)
        sleep(1)
        voltage = []
        current = []

        for n in self.v_set:
            self.inst.source.set_voltage(n)
            sleep(0.1)

            vread = self.inst.meter.read_voltage()  # Voltage

            iread = (n - vread) / self.R_srs  # (set voltage - read voltage)

            print("V=%.4f V, I=%.2f uA, R =%.2f" % (vread, iread * 1e6, vread / iread))
            voltage.append(vread)
            current.append(iread)

        self.v_read = voltage
        self.i_read = current

    def run_sweep_spacing(self):
        """Runs IV sweep with config paramters
        This constructs [points_coarse] between start and [percent] of final current.
        Then, [points_fine] between [percent] and 100% of final current.

        uses np.arange()
        """
        self.inst.source.reset()
        self.inst.meter.reset()

        self.inst.source.set_output(False)

        start = self.properties["iv_sweep"]["start"]
        stop = self.properties["iv_sweep"]["stop"]
        percent = self.properties["iv_sweep"]["percent"]
        spacing1 = self.properties["iv_sweep"]["spacing_coarse"]
        spacing2 = self.properties["iv_sweep"]["spacing_fine"]

        sweep = self.properties["iv_sweep"]["sweep"]
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties["iv_sweep"]["full_sweep"]
        Isource1 = np.arange(start, stop * percent + spacing1, spacing1)  # Coarse
        Isource2 = np.arange(stop * percent, stop + spacing2, spacing2)  # Fine

        if full_sweep:
            Isource = np.concatenate(
                [Isource1, Isource2, Isource2[::-1], Isource1[::-1]]
            )
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = np.concatenate([Isource1, Isource2])
        self.v_set = np.tile(Isource, sweep) * self.R_srs

        self.inst.source.set_output(True)
        sleep(1)
        voltage = []
        current = []

        for n in self.v_set:
            self.inst.source.set_voltage(n)
            sleep(0.1)

            vread = self.inst.meter.read_voltage()  # Voltage

            iread = (n - vread) / self.R_srs  # (set voltage - read voltage)

            print("V=%.4f V, I=%.2f uA, R =%.2f" % (vread, iread * 1e6, vread / iread))
            voltage.append(vread)
            current.append(iread)

        self.v_read = voltage
        self.i_read = current

    def isw_calc(self):
        """Calculates critical current."""
        """
        Critical current is defined as the current one step before a voltage
        reading greater than 5mV.
        self.isw = self.i_read[np.argmax(np.array(self.v_read) > 0.005)-1]
        print('%.4f uA' % (self.isw*1e6))
        """

        """ New method looks at differential and takes average of points that 
        meet condition. Prints mean() and std().` std should be < 1-2µA
        """
        # isws = abs(self.i_read[np.where(abs(np.diff(self.i_read)/max(np.diff(self.i_read))) > 0.5)])
        # self.isw = self.i_read[np.argmax(np.array(self.v_read) > 0.005)-1]
        # print('%.4f uA' % (self.isw*1e6))

        try:
            switches = np.asarray(
                np.where(abs(np.diff(self.i_read) / max(np.diff(self.i_read))) > 0.8),
                dtype=int,
            ).squeeze()
            isws = abs(np.asarray([self.i_read[i] for i in switches]))
            print(isws)
            self.isw = isws.mean()
            print(
                "Isw_avg = %.4f µA :--: Isw_std = %.4f µA"
                % (self.isw * 1e6, isws.std() * 1e6)
            )
        except Exception:
            print("Could not calculate Isw. Isw set to 0")
            self.isw = 0

    def plot(self):
        full_path = qf.save(self.properties, "iv_sweep")
        qf.plot(
            np.array(self.v_read),
            np.array(self.i_read) * 1e6,
            title=self.sample_name + " " + self.device_type + " " + self.device_name,
            xlabel="Voltage (V)",
            ylabel="Current (uA)",
            path=full_path,
            show=True,
            close=True,
        )

    def save(self, override_vals=None):
        # Set up data dictionary
        data_dict = {
            "V_source": self.v_set,
            "V_device": self.v_read,
            "I_device": self.i_read,
            "Isw": self.isw,
            "R_srs": self.R_srs,
            "temp": self.properties["Temperature"]["initial temp"],
        }

        self.full_path = qf.save(
            self.properties, "iv_sweep", data_dict, instrument_list=self.instrument_list
        )


class IvSweepScope(Snspd):
    def run_sweep(self):
        awg_amp = self.properties["iv_sweep_scope"]["awg_amp"]
        atten = self.properties["iv_sweep_scope"]["atten"]
        freq = self.properties["iv_sweep_scope"]["freq"]

        trigger_v = self.properties["iv_sweep_scope"]["trigger_v"]
        trigger_channel = self.properties["iv_sweep_scope"]["trigger_channel"]
        channels = self.properties["iv_sweep_scope"]["channels"]
        hist_channel = self.properties["iv_sweep_scope"]["hist_channel"]
        num_segments = self.properties["iv_sweep_scope"]["num_segments"]
        self.inst.awg.set_vpp(awg_amp)
        self.inst.awg.set_freq(freq)
        try:
            self.inst.awg.set_ramp(freq=freq, vpp=awg_amp, symm=0)
        except Exception:
            pass
        temperature = self.inst.temp.read_temp()
        # temperature=0
        self.inst.scope.set_trigger(source=trigger_channel, volt_level=trigger_v)
        self.inst.scope.pyvisa.timeout = 10000
        self.inst.scope.clear_sweeps()
        data = self.inst.scope.get_multiple_trace_sequence(
            channels=channels, NumSegments=num_segments
        )
        hist = self.inst.scope.get_wf_data(hist_channel)
        hist_dict = {hist_channel + "x": hist[0], hist_channel + "y": hist[1]}
        self.inst.scope.set_sample_mode()

        data.update(hist_dict)
        data.update(
            {"freq": freq, "awg_amp": awg_amp, "atten": atten, "temp": temperature}
        )

        try:
            self.inst.awg.set_output(False)
        except Exception:
            pass

        self.data_dict_iv_sweep_scope = data

    def save(self):
        self.full_path = qf.save(
            self.properties,
            "iv_sweep_scope",
            self.data_dict_iv_sweep_scope,
            instrument_list=self.instrument_list,
        )
        self.inst.scope.save_screenshot(
            self.full_path + "screen_shot" + ".png", white_background=False
        )


class DoubleSweep(Snspd):
    """Class object for iv sweeps

    Configuration: iv_sweep:
    [start: initial bias current],
    [stop: final bias current],
    [steps: number of points],
    [sweep: number of iterations],
    [full_sweep: Include both positive and negative bias],
    [series_resistance: resistance at voltage source ie R_srs]

    """

    def run_sweep(self):
        """Runs IV sweep with config paramters
        This constructs #steps between start and 75% of final current.
        Then, #steps between 75% and 100% of final current.


        """
        self.inst.source1.reset()
        self.inst.source2.reset()

        self.inst.meter.reset()

        self.inst.source1.set_output(False)
        self.inst.source2.set_output(False)

        start = self.properties["double_sweep"]["start"]
        stop = self.properties["double_sweep"]["stop"]
        steps = self.properties["double_sweep"]["steps"]
        sweep = self.properties["double_sweep"]["sweep"]
        Ig_start = self.properties["double_sweep"]["Ig_start"]
        Ig_stop = self.properties["double_sweep"]["Ig_stop"]
        Ig_steps = self.properties["double_sweep"]["Ig_steps"]

        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties["double_sweep"]["full_sweep"]
        Isource1 = np.linspace(start, stop, steps)  # Coarse
        # Isource2 = np.linspace(stop*0.75, stop, steps) #Fine

        Isource_Ig = np.linspace(Ig_start, Ig_stop, Ig_steps)

        if full_sweep:
            Isource = np.concatenate([Isource1, Isource1[::-1]])
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = Isource1
        self.v_set = np.tile(Isource, sweep) * self.R_srs
        self.v_set_g = np.tile(Isource_Ig, sweep) * self.R_srs_g

        self.inst.source.set_output(True)
        self.inst.source2.set_output(True)
        sleep(1)
        self.v_list = []
        self.i_list = []

        self.ig_list = []
        for m in self.v_set_g:
            voltage = []
            current = []
            self.inst.source2.set_voltage(m)
            sleep(0.1)
            for n in self.v_set:
                self.inst.source.set_voltage(n)
                sleep(0.1)

                vread = self.inst.meter.read_voltage()  # Voltage

                iread = (n - vread) / self.R_srs  # (set voltage - read voltage)

                print(
                    "Vd=%.4f V, Id=%.2f uA, Ig=%.2f uA, R =%.2f"
                    % (vread, iread * 1e6, m * 1e6 / self.R_srs_g, vread / iread)
                )
                voltage.append(vread)
                current.append(iread)

            # ADDED by Andrew...
            # Turn off both voltage sources to provide reset time
            self.inst.source.set_voltage(0.0)
            self.inst.source2.set_voltage(0.0)
            sleep(2)
            #######

            self.v_list.append(np.asarray(voltage, dtype=np.float32))
            self.i_list.append(np.asarray(current, dtype=np.float32))
            self.ig_list.append(m / self.R_srs_g)

    def plot(self):
        full_path = qf.save(self.properties, "double_sweep")
        qf.plot(
            self.v_list,
            self.i_list,
            title=self.sample_name + " " + self.device_type + " " + self.device_name,
            xlabel="Voltage (V)",
            ylabel="Current (A)",
            label=self.ig_list,
            path=full_path,
            show=True,
            linestyle="-o",
            close=True,
        )

    def save(self, extra_values={}):
        # Set up data dictionary

        data_dict = {
            "V_source": self.v_set,
            "V_device": self.v_list,
            "I_device": self.i_list,
            "I_gate": self.ig_list,
            "R_srs": self.R_srs,
            "temp": self.properties["Temperature"]["initial temp"],
        }
        data_dict.update(extra_values)
        self.full_path = qf.save(
            self.properties,
            "double_sweep",
            data_dict,
            instrument_list=self.instrument_list,
        )


class PhotonCounts(Snspd):
    """Class object for PCR and DCR measurments. Configuration data will be
        used for both PCR and DCR

    Configuration: photon_counts:
    [start: initial bias current]
    [stop: final bias current]
    [step: current step size]
    [trigger_v: trigger voltage set on counter]
    [counting_time: integration time on counter]
    [iterations: number of repeated count measurements to average over]
    [attenuation_db: optical attenuation]
    """

    def __init__(self, config):
        """
        initialize optional variables as None type to enable successful
        plotting + saving without them
        """
        self.LCR = []
        self.DCR = []
        self.attenuation = 0
        Snspd.__init__(self, config)

    def dark_counts(self):
        """Dark Count Rate"""

        # Variable Setup
        iterations = self.properties["photon_counts"]["iterations"]
        start = self.properties["photon_counts"]["start"]
        stop = self.properties["photon_counts"]["stop"]
        step = self.properties["photon_counts"]["step"]
        counting_time = self.properties["photon_counts"]["counting_time"]
        trigger_v = self.properties["photon_counts"]["trigger_v"]

        currents = np.arange(start, stop, step)
        self.currents = currents

        # Block light
        self.inst.attenuator.set_attenuation_db(100)
        self.inst.attenuator.set_beam_block(True)

        count_rate_list = []

        print("\\\\\\\\ DARK COUNT RATE \\\\\\\\")
        for n, j in enumerate(currents):  # sweep current
            start_time = time.time()
            self.inst.source.set_voltage(voltage=j * self.R_srs)
            count_rate_avg = Snspd.average_counts(
                self, counting_time, iterations, trigger_v
            )

            count_rate_list.append(
                count_rate_avg
            )  # final countrate at this current is the average of each itteration
            print(
                "Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)"
                % (
                    j * 1e6,
                    count_rate_avg,
                    n + 1,
                    len(currents),
                    (time.time() - start_time) / 60.0,
                )
            )

        self.inst.source.set_output(False)
        self.DCR = np.asarray(count_rate_list, dtype=np.float32)
        #        self.DCR = currents*2  # here for testing

        return self.DCR

    def light_counts(self):
        """Photon Count Rate"""
        # Variable Setup
        iterations = self.properties["photon_counts"]["iterations"]
        start = self.properties["photon_counts"]["start"]
        stop = self.properties["photon_counts"]["stop"]
        step = self.properties["photon_counts"]["step"]
        counting_time = self.properties["photon_counts"]["counting_time"]
        trigger_v = self.properties["photon_counts"]["trigger_v"]
        self.attenuation = self.properties["photon_counts"]["attenuation_db"]

        currents = np.arange(start, stop, step)
        self.currents = currents

        # Shine light
        self.inst.attenuator.set_attenuation_db(self.attenuation)
        self.inst.attenuator.set_beam_block(False)

        count_rate_list = []

        print("\\\\\\\\ LIGHT COUNT RATE \\\\\\\\")
        for n, j in enumerate(currents):  # sweep current
            start_time = time.time()
            self.inst.source.set_voltage(voltage=j * self.R_srs)
            sleep(0.1)
            count_rate_avg = Snspd.average_counts(
                self, counting_time, iterations, trigger_v
            )
            count_rate_list.append(
                count_rate_avg
            )  # final countrate at this current is the average of each itteration
            print(
                "Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)"
                % (
                    j * 1e6,
                    count_rate_avg,
                    n + 1,
                    len(currents),
                    (time.time() - start_time) / 60.0,
                )
            )
        self.inst.attenuator.set_beam_block(True)
        self.inst.source.set_output(False)
        self.LCR = np.asarray(count_rate_list, dtype=np.float32)

        #        self.LCR = currents*3 # here for testing
        return self.LCR

    def dark_counts_noattn(self):
        """Dark Count Rate -- adjust laser manually"""
        # Variable Setup
        iterations = self.properties["photon_counts"]["iterations"]
        start = self.properties["photon_counts"]["start"]
        stop = self.properties["photon_counts"]["stop"]
        step = self.properties["photon_counts"]["step"]
        try:
            mid_start = self.properties["photon_counts"]["mid_start"]
            mid_stop = self.properties["photon_counts"]["mid_stop"]
            high_res_step = self.properties["photon_counts"]["high_res_step"]
            fine_sweep = True
        except Exception:
            fine_sweep = False
        counting_time = self.properties["photon_counts"]["counting_time"]
        trigger_v = self.properties["photon_counts"]["trigger_v"]

        if not fine_sweep:
            currents = np.arange(start, stop, step)
        else:
            currents = np.r_[
                start:mid_start:step,
                mid_start:mid_stop:high_res_step,
                mid_stop:stop:step,
            ]
        self.currents = currents

        count_rate_list = []

        print("\\\\\\\\ DARK COUNT RATE \\\\\\\\")
        for n, j in enumerate(currents):  # sweep current
            start_time = time.time()
            self.inst.source.set_voltage(voltage=j * self.R_srs)
            sleep(0.1)
            counts_at_current = []
            for i in range(self.properties["photon_counts"]["nonavg_iterations"]):
                count_rate_avg = Snspd.average_counts(
                    self, counting_time, iterations, trigger_v
                )
                counts_at_current.append(count_rate_avg)
            count_rate_list.append(
                counts_at_current
            )  # final countrate at this current is the average of each itteration
            print(
                "Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)"
                % (
                    j * 1e6,
                    count_rate_avg,
                    n + 1,
                    len(currents),
                    (time.time() - start_time) / 60.0,
                )
            )

        self.DCR = np.asarray(count_rate_list, dtype=np.float32)
        self.inst.source.set_output(False)

        return self.DCR

    def light_counts_noattn(self):
        """Photon Count Rate -- adjust laser manually"""
        # Variable Setup
        iterations = self.properties["photon_counts"]["iterations"]
        start = self.properties["photon_counts"]["start"]
        stop = self.properties["photon_counts"]["stop"]
        step = self.properties["photon_counts"]["step"]
        try:
            mid_start = self.properties["photon_counts"]["mid_start"]
            mid_stop = self.properties["photon_counts"]["mid_stop"]
            high_res_step = self.properties["photon_counts"]["high_res_step"]
            fine_sweep = True
        except Exception:
            fine_sweep = False
        counting_time = self.properties["photon_counts"]["counting_time"]
        trigger_v = self.properties["photon_counts"]["trigger_v"]
        self.attenuation = self.properties["photon_counts"]["attenuation_db"]

        if not fine_sweep:
            currents = np.arange(start, stop, step)
        else:
            currents = np.r_[
                start:mid_start:step,
                mid_start:mid_stop:high_res_step,
                mid_stop:stop:step,
            ]
        self.currents = currents

        count_rate_list = []

        print("\\\\\\\\ LIGHT COUNT RATE \\\\\\\\")
        for n, j in enumerate(currents):  # sweep current
            start_time = time.time()
            self.inst.source.set_voltage(voltage=j * self.R_srs)
            sleep(0.1)
            counts_at_current = []
            for i in range(self.properties["photon_counts"]["nonavg_iterations"]):
                count_rate_avg = Snspd.average_counts(
                    self, counting_time, iterations, trigger_v
                )
                counts_at_current.append(count_rate_avg)
            count_rate_list.append(
                counts_at_current
            )  # final countrate at this current is the average of each itteration
            print(
                "Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)"
                % (
                    j * 1e6,
                    count_rate_avg,
                    n + 1,
                    len(currents),
                    (time.time() - start_time) / 60.0,
                )
            )
        self.LCR = np.asarray(count_rate_list, dtype=np.float32)

        return self.LCR

    def plot(self):
        """Plots DCR, LCR, and LCR-DCR"""
        full_path = qf.save(self.properties, "photon_counts")[0]

        ydata = []
        label = []
        if self.DCR is not None and self.DCR != []:
            ydata.append(self.DCR)
            label.append("DCR")
        if self.LCR is not None and self.LCR != []:
            ydata.append(self.LCR)
            label.append("LCR")
        if (
            self.DCR is not None
            and self.LCR is not None
            and self.DCR != []
            and self.LCR != []
        ):
            ydata.append(self.LCR - self.DCR)
            label.append("LCR-DCR")
        if self.properties["Laser"]["wavelength_nm"]:
            device_name = (
                self.device_name
                + " "
                + str(self.properties["Laser"]["wavelength_nm"])
                + "nm"
                + " "
                + str(self.properties["photon_counts"]["attenuation_db"])
                + "dB"
            )
        qf.plot(
            self.currents * 1e6,
            ydata,
            title=self.sample_name + " " + self.device_type + " " + device_name,
            xlabel="Current (uA)",
            ylabel="Count Rate (Hz)",
            label=label,
            path=full_path,
            show=True,
            close=True,
        )

    def save(self):
        """If LCR was not measured, attunation is 100dB for dark counts"""
        if self.LCR is None or self.LCR == []:
            self.attenuation = 100

        self.instrument_list.append("Laser")

        data_dict = {
            "LCR": self.LCR,
            "DCR": self.DCR,
            "currents": self.currents,
            "wavelength": self.properties["Laser"]["wavelength_nm"],
            "attenuation": self.attenuation,
        }

        full_path = qf.save(
            self.properties,
            "photon_counts",
            data_dict,
            instrument_list=self.instrument_list,
        )


class LinearityCheck(Snspd):
    """Class object for Linearity Measurement.
    Sweeps atteunation and measures count rate.
    Assumes R_srs has already been defined.

    Configuration: linearity_check:
    [bias: current bias]
    [start: initial optical attenuation in dB]
    [stop: final optical attenuation in dB]
    [step: step size of optical attenuation in dB]
    [counting_time: integration time on counter]
    [iterations: number of repeated count measurements to average over]

    FIXME: Trigger voltage on counter. Passed from self?
    """

    def run_sweep(self):
        bias = self.properties["linearity_check"]["bias"]
        start = self.properties["linearity_check"]["start"]
        stop = self.properties["linearity_check"]["stop"]
        step = self.properties["linearity_check"]["step"]
        trigger_v = self.properties["linearity_check"]["trigger_v"]
        counting_time = self.properties["linearity_check"]["counting_time"]
        iterations = self.properties["linearity_check"]["iterations"]

        dbs = np.arange(start, stop, step)
        self.inst.source.set_output(True)
        self.inst.source.set_voltage(voltage=bias * self.R_srs)

        # add current loop if desired
        self.inst.attenuator.set_beam_block(False)

        counts_per_atten = []
        start_time = time.time()
        for i in dbs:
            self.inst.attenuator.set_attenuation_db(i)
            sleep(0.1)
            count_rate_avg = Snspd.average_counts(
                self, counting_time, iterations, trigger_v
            )
            counts_per_atten.append(count_rate_avg)
            print(
                "Attenuation: %.1f dB \\\\ Counts: %.0f \\\\ Elapsed Time: %.2f"
                % (i, count_rate_avg, time.time() - start_time)
            )
        self.inst.attenuator.set_beam_block(True)

        self.counts_per_atten = np.asarray(counts_per_atten, dtype=np.float32)
        self.attenuation_levels = np.asarray(dbs, dtype=np.float32)
        self.linearity_bias = bias

    def run_manual_sweep(self):
        bias = self.properties["linearity_check"]["bias"]
        trigger_v = self.properties["linearity_check"]["trigger_v"]
        counting_time = self.properties["linearity_check"]["counting_time"]
        iterations = self.properties["linearity_check"]["iterations"]

        self.inst.source.set_output(True)
        self.inst.source.set_voltage(voltage=bias * self.R_srs)

        continue_sweep = True
        counts_per_atten = []
        dbs = []
        start_time = time.time()
        while continue_sweep:
            sleep(0.1)
            db = float(input("Attenuation?"))
            count_rate_avg = Snspd.average_counts(
                self, counting_time, iterations, trigger_v
            )
            counts_per_atten.append(count_rate_avg)
            print(
                "Attenuation: %.1f dB \\\\ Counts: %.0f \\\\ Elapsed Time: %.2f"
                % (db, count_rate_avg, time.time() - start_time)
            )
            dbs.append(db)
            continue_sweep = int(input("Continue sweep?"))
            print(continue_sweep)
        self.counts_per_atten = np.asarray(counts_per_atten, dtype=np.float32)
        self.attenuation_levels = np.asarray(dbs, dtype=np.float32)
        self.linearity_bias = bias

    def plot(self):
        full_path = qf.save(self.properties, "linearity_check")
        device_name = (
            self.device_name
            + " "
            + str(self.properties["Laser"]["wavelength_nm"])
            + "nm"
        )
        qf.plot(
            self.attenuation_levels,
            self.counts_per_atten,
            title=self.sample_name + " " + self.device_type + " " + device_name,
            xlabel="Attenuation (dB)",
            ylabel="Count Rate (Hz)",
            y_scale="log",
            path=full_path,
            show=True,
            close=True,
        )

    def save(self):
        data_dict = {
            "attenuation": self.attenuation_levels,
            "counts": self.counts_per_atten,
            "bias": self.linearity_bias,
        }

        self.full_path = qf.save(
            self.properties,
            "linearity_check",
            data_dict,
            instrument_list=self.instrument_list,
        )


class PulseTraceSingle(Snspd):
    """Single trace acquistion for LeCroy620Zi.
    no pulse_trace configuration required.

    Sadly, this will reset instruments when initializing the Snspd class.
    So be sure to 'stop' the scope before running.
    """

    def trace_data(self, channels=None, trigger_source=None):
        """Returns x,y of scope_channel in configuration file"""

        bias = self.properties["pulse_trace"]["bias_voltage"]
        self.inst.scope.set_trigger_mode(trigger_mode="Stop")
        self.inst.source.set_output(True)
        self.inst.source.set_voltage(voltage=bias)

        if channels:
            channels = channels
        else:
            channels = self.properties["pulse_trace"]["channel"]

        xlist = []
        ylist = []
        tlist = []

        trigger_v = self.properties["pulse_trace"]["trigger_level"]
        if trigger_source:
            self.inst.scope.set_trigger(
                source=trigger_source, volt_level=trigger_v, slope="positive"
            )
        else:
            self.inst.scope.set_trigger(
                source=channels[0], volt_level=trigger_v, slope="positive"
            )

        if self.properties.get("Attenuator"):
            attenuation = self.properties["pulse_trace"]["attenuation"]
            self.inst.attenuator.set_attenuation_db(attenuation)
            if attenuation == 100:
                self.inst.attenuator.set_beam_block(True)
            else:
                self.inst.attenuator.set_beam_block(False)

        sleep(0.1)
        self.inst.scope.set_trigger_mode(trigger_mode="Single")
        while self.inst.scope.get_trigger_mode() == "Single\n":
            sleep(0.1)

        for i in range(len(channels)):
            x, y = self.inst.scope.get_single_trace(channel=channels[i])
            xlist.append(x)
            ylist.append(y)

        self.trace_x = xlist
        self.trace_y = ylist
        self.inst.source.set_output(False)
        return self.trace_x, self.trace_y

    def plot(self):
        """Grabs new trace from scope and plots. Figure is saved to path"""
        # x,y = self.inst.scope.get_single_trace(channel= self.inst.scope_channel)
        channels = self.properties["pulse_trace"]["channel"]
        full_path, time_str = qf.save(self.properties, "pulse_trace")
        #        data_dict = {'x':x,'y':y}
        x = self.trace_x
        y = self.trace_y
        qf.plot(
            x,
            y,
            title=self.sample_name + " " + self.device_type + " " + self.device_name,
            # xlabel = '',
            # ylabel = '',
            path=full_path,
            show=True,
            linestyle="-",
            label=channels,
            close=True,
        )

    def save(self):
        data_dict = {"x": self.trace_x, "y": self.trace_y}
        file_path, time_str = qf.save(
            self.properties,
            "pulse_trace",
            data_dict,
            instrument_list=self.instrument_list,
        )
        self.inst.scope.save_screenshot(file_path + ".png")


class PulseTraceMultiple(Snspd):
    def trace_data(self, channels=None, trigger_source=None):
        """Returns x,y of scope_channel in configuration file"""

        if channels:
            channels = channels
        else:
            channels = self.properties["pulse_trace"]["channel"]

        """ Option for attenuator control. Set to 100dB for beam block. """
        if self.properties.get("pulse_trace").get("attenuation"):
            self.inst.attenuator.set_attenuation_db(
                self.properties["pulse_trace"]["attenuation"]
            )
            self.inst.attenuator.set_beam_block(False)
            if self.properties["pulse_trace"]["attenuation"] == 100:
                self.inst.attenuator.set_beam_block(True)

        total_xlist = []
        total_ylist = []
        trigger_v = self.properties["pulse_trace"]["trigger_level"]
        number_of_traces = self.properties["pulse_trace"]["number_of_traces"]

        if trigger_source:
            self.inst.scope.set_trigger(
                source=trigger_source, volt_level=trigger_v, slope="positive"
            )
        else:
            self.inst.scope.set_trigger(
                source=channels[0], volt_level=trigger_v, slope="positive"
            )

        self.inst.source.set_voltage(self.properties["pulse_trace"]["bias_voltage"])
        self.inst.source.set_output(True)
        for n in range(number_of_traces):
            self.inst.meter.read_voltage()
            self.inst.scope.set_trigger_mode(trigger_mode="Single")
            while self.inst.scope.get_trigger_mode() != "Stopped\n":
                sleep(0.001)

            xlist = []
            ylist = []
            for i in range(len(channels)):
                x, y = self.inst.scope.get_single_trace(channel=channels[i])
                xlist.append(x)  # keep all x data the same.
                ylist.append(y)

            total_xlist.append(np.asarray(xlist, dtype=np.float32))
            total_ylist.append(np.asarray(ylist, dtype=np.float32))

            print("Acquired Trace %0.f of %0.f" % (n + 1, number_of_traces))

        self.trace_x = np.asarray(total_xlist, dtype=np.float32)
        self.trace_y = np.asarray(total_ylist, dtype=np.float32)
        self.inst.source.set_output(False)

        return self.trace_x, self.trace_y

    def plot(self):
        """Grabs new trace from scope and plots. Figure is saved to path"""
        # x,y = self.inst.scope.get_single_trace(channel= self.inst.scope_channel)

        full_path = qf.save(self.properties, "pulse_trace")
        #        data_dict = {'x':x,'y':y}
        qf.plot(
            self.trace_x,
            self.trace_y,
            title=self.sample_name + " " + self.device_type + " " + self.device_name,
            # xlabel = '',
            # ylabel = '',
            path=full_path,
            show=True,
            linestyle="-",
            close=True,
        )

    def save(self):
        data_dict = {"x": self.trace_x, "y": self.trace_y}
        qf.save(
            self.properties,
            "pulse_trace",
            data_dict,
            instrument_list=self.instrument_list,
        )


class PulseTraceSegments(Snspd):
    def trace_data(self, channels=None, trigger_source=None, bias_voltage=None):
        """Returns x,y of scope_channel in configuration file"""

        if channels:
            channels = channels
        else:
            channels = self.properties["pulse_trace"]["channel"]

        """ Option for attenuator control. Set to 100dB for beam block. """
        if self.properties.get("Attenuator"):
            attenuation = self.properties["pulse_trace"]["attenuation"]
            self.inst.attenuator.set_attenuation_db(attenuation)
            if attenuation == 100:
                self.inst.attenuator.set_beam_block(True)
            else:
                self.inst.attenuator.set_beam_block(False)

        total_ylist = []
        trigger_v = self.properties["pulse_trace"]["trigger_level"]
        number_of_traces = self.properties["pulse_trace"]["number_of_traces"]

        if trigger_source:
            self.inst.scope.set_trigger(
                source=trigger_source, volt_level=trigger_v, slope="positive"
            )
        else:
            self.inst.scope.set_trigger(
                source=channels[0], volt_level=trigger_v, slope="positive"
            )

        if bias_voltage:
            self.inst.source.set_voltage(bias_voltage)
        else:
            self.inst.source.set_voltage(self.properties["pulse_trace"]["bias_voltage"])
        self.inst.source.set_output(True)

        if trigger_source:
            self.inst.scope.set_trigger(
                source=trigger_source, volt_level=trigger_v, slope="positive"
            )
        else:
            self.inst.scope.set_trigger(
                source=channels[0], volt_level=trigger_v, slope="positive"
            )

        self.inst.scope.pyvisa.timeout = 10000
        self.inst.scope.clear_sweeps()
        data = self.inst.scope.get_multiple_trace_sequence(
            channels=channels, NumSegments=number_of_traces
        )

        self.inst.scope_data = data
        self.inst.scope.set_sample_mode()
        self.inst.scope.set_trigger_mode()
        self.inst.source.set_output(False)

        return self.inst.scope_data

    def plot(self):
        """Grabs new trace from scope and plots. Figure is saved to path"""
        # x,y = self.inst.scope.get_single_trace(channel= self.inst.scope_channel)
        full_path = qf.save(self.properties, "pulse_trace")
        self.inst.scope.set_trigger_mode("Single")
        self.inst.scope.save_screenshot(full_path + ".png")
        self.inst.scope.set_trigger_mode()

    # #        data_dict = {'x':x,'y':y}
    #         qf.plot(self.trace_x, self.trace_y,
    #                 title=self.sample_name+" "+self.device_type+" "+
    #                       self.device_name,
    #                 # xlabel = '',
    #                 # ylabel = '',
    #                 path=full_path,
    #                 show=True,
    #                 linestyle='-',
    #                 close=True)

    def save(self, data=None):
        data_dict = {
            "data": self.inst.scope_data,
            "atten": self.properties["pulse_trace"]["attenuation"],
            "vbias": self.properties["pulse_trace"]["bias_voltage"],
        }

        if data:
            data_dict.update(data)
        qf.save(
            self.properties,
            "pulse_trace",
            data_dict,
            instrument_list=self.instrument_list,
        )


class PulseTraceCurrentSweep(Snspd):
    """UNFINISHED Sweep current and acquire trace. Configuration requires
    pulse_trace section: {start, stop, steps}"""

    def trace_data(self):
        start = self.properties["pulse_trace"]["start"]
        stop = self.properties["pulse_trace"]["stop"]
        steps = self.properties["pulse_trace"]["steps"]
        num_traces = 1
        currents = np.linspace(start, stop, steps)

        snspd_traces_x_list = []
        snspd_traces_y_list = []
        pd_traces_x_list = []
        pd_traces_y_list = []
        start_time = time.time()
        self.inst.source.set_output(True)
        for n, i in enumerate(currents):
            print(
                "   ---   Time elapsed for measurement %s of %s: %0.2f "
                "min    ---   " % (n, len(currents), (time.time() - start_time) / 60.0)
            )
            self.inst.source.set_voltage(i * self.R_srs)
            pd_traces_x = []  # Photodiode pulses
            pd_traces_y = []
            snspd_traces_x = []  # Device pulses
            snspd_traces_y = []
            self.inst.scope.clear_sweeps()
            for n in range(num_traces):
                x, y = self.inst.scope.get_single_trace(channel="C2")
                snspd_traces_x.append(x)
                snspd_traces_y.append(y)
                x, y = self.inst.scope.get_single_trace(channel="C3")
                pd_traces_x.append(x)
                pd_traces_y.append(y)

            snspd_traces_x_list.append(snspd_traces_x)
            snspd_traces_y_list.append(snspd_traces_y)
            pd_traces_x_list.append(pd_traces_x)
            pd_traces_y_list.append(pd_traces_y)


class KineticInductancePhase(Snspd):
    def run_sweep_current(self, Ic_break=None, save=None, plot=None):
        self.inst.VNA.write("CALC:FORM SMITh")
        start = self.properties["kinetic_inductance_phase"]["start"]
        stop = self.properties["kinetic_inductance_phase"]["stop"]
        steps = self.properties["kinetic_inductance_phase"]["steps"]

        currents = np.linspace(start, stop, steps)

        self.if_bandwidth = self.inst.VNA.get_if_bw()
        self.fspan = self.inst.VNA.get_span()
        sweep_time = self.fspan / (self.if_bandwidth**2)

        self.rf_power = self.inst.VNA.get_power()

        self.inst.VNA.select_measurement()

        for current in currents:
            print("Bias set to %0.3f uA" % (current * 1e6))
            self.inst.source.set_voltage(current * self.R_srs)
            self.inst.source.set_output(True)
            self.current = current * 1e6

            if self.properties["Temperature"]["name"] == "ICE":
                self.currentTemp = qf.ice_get_temp(select=1)
            else:
                self.currentTemp = self.inst.temp.read_temp(self.inst.temp.channel)

            self.voltage = self.inst.meter.read_voltage()
            if Ic_break:
                if self.voltage > 0.01:
                    print("Wire Switched")
                    self.inst.meter.reset()
                    break
            t = sweep_time + 10
            # print('Waiting %0.1f seconds for vna averging' % t)
            print("Waiting 10 seconds for vna averging")

            sleep(10)  # vna averging

            self.f, self.re, self.im = self.inst.VNA.get_freq_real_imag()
            self.log_mag = 20 * np.log10(
                np.sqrt(np.square(self.re) + np.square(self.im))
            )
            self.phase = np.angle(self.re + self.im * 1j, deg=True)

            if plot:
                self.plot()
            if save:
                self.save()
        self.inst.source.set_output(False)
        self.inst.VNA.write("CALC:FORM MLOG")

    def plot(self):
        full_path = qf.save(self.properties, "kinetic_inductance_phase")
        qf.plot(
            self.f,
            self.phase,
            title=self.sample_name
            + " "
            + self.device_type
            + " "
            + self.device_name
            + ": "
            + str(round(self.current, 2))
            + " uA, "
            + str(self.rf_power)
            + " dB",
            xlabel="Frequency (Hz)",
            ylabel="Phase (°)",
            path=full_path,
            show=True,
            linestyle="-",
            close=True,
        )

    def save(self):
        data_dict = {
            "freq": self.f,
            "re": self.re,
            "im": self.im,
            "log_mag": self.log_mag,
            "phase": self.phase,
            "Ibias": self.current,
            "voltage": self.voltage,
            "if_bandwidth": self.if_bandwidth,
            "R_srs": self.R_srs,
            "temp": self.currentTemp,
        }
        qf.save(
            self.properties,
            "kinetic_inductance_phase",
            data_dict,
            instrument_list=self.instrument_list,
        )


class PulseTraceFFT_CurrentSweep(Snspd):
    """((NO PLOT. ONLY SAVE)) Sweep current and acquire traces C1(signal) and F1(FFT) . Configuration requires
    pulse_trace section: {start, stop, steps}"""

    def trace_data(self):
        start = self.properties["pulse_trace"]["start"]
        stop = self.properties["pulse_trace"]["stop"]
        steps = self.properties["pulse_trace"]["steps"]

        num_traces = 1
        currents = np.linspace(start, stop, steps)

        self.FFT = []
        self.FREQ = []
        self.VIN = []
        self.T1 = []
        self.VOUT = []
        start_time = time.time()
        self.inst.source.set_output(True)

        self.inst.scope.clear_sweeps()
        time.sleep(1)

        for n, i in enumerate(currents):
            print(
                "   ---   Time elapsed for measurement %s of %s: %0.2f "
                "min    ---   " % (n, len(currents), (time.time() - start_time) / 60.0)
            )
            self.inst.source.set_voltage(i * self.R_srs)

            time.sleep(1)

            self.inst.scope.label_channel("C1", "V_device")

            self.inst.scope.set_math("F1", "FFT", "C1")
            self.inst.scope.view_channel("F1")

            t1, C1 = self.inst.scope.get_wf_data("C1")
            tf, Ft = self.inst.scope.get_wf_data("F1")
            self.FFT.append(Ft)
            self.FREQ.append(tf)
            self.T1.append(t1)
            self.VOUT.append(C1)
            self.Ibias = currents

            time.sleep(1)

        self.inst.source.set_voltage(0)
        self.inst.source.set_output(False)

    def save(self):
        data_dict = {
            "FFT": self.FFT,
            "FREQ": self.FREQ,
            "T2": self.T1,
            "VOUT": self.VOUT,
            "Ibias": self.Ibias,
        }

        qf.save(
            self.properties,
            "pulse_trace",
            data_dict,
            instrument_list=self.instrument_list,
        )
