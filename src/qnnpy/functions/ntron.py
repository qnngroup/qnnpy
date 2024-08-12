# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 17:42:10 2020

@author: omedeiro
"""

import time
from time import sleep

import numpy as np

import qnnpy.functions.functions as qf


class nTron:
    """Class for nTron measurement. This class handels the instrument
    configuration, measurement, plotting, logging, and saving.
    """

    def __init__(self, configuration_file):
        #######################################################################
        #       Load .yaml configuraiton file
        #######################################################################

        # qf is a package of base functions that can be used in any class.
        self.properties = qf.load_config(configuration_file)

        self.sample_name = self.properties["Save File"]["sample name"]
        self.device_name = self.properties["Save File"]["device name"]
        self.device_type = self.properties["Save File"]["device type"]

        self.isw = 0
        self.instrument_list = []

        self.R_srs = self.properties["iv_sweep"]["series_resistance"]
        self.R_srs_g = self.properties["iv_sweep"]["series_resistance_g"]

        # set up and store instruments
        self.inst = qf.Instruments(self.properties)

        # if there are any errors in setting up, compare older versions of
        # ntron on github with qf.Instruments

    def voltage2current(
        self, voltage: float, attenuation: float, resistance: float = 50
    ):
        voltage = voltage * 10 ** (attenuation / 20)
        current = voltage / resistance
        return current

    def current2voltage(
        self, current: float, attenuation: float, resistance: float = 50
    ):
        voltage = current * resistance
        voltage = voltage / 10 ** (attenuation / 20)
        return voltage


class IvSweep(nTron):
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
        Isource1 = np.linspace(start, stop, steps)  # Coarse
        # Isource2 = np.linspace(stop*0.75, stop, steps) #Fine

        if full_sweep:
            Isource = np.concatenate([Isource1, Isource1[::-1]])
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = Isource1
        self.v_set = np.tile(Isource, sweep) * self.R_srs

        self.inst.source.set_output(True)
        sleep(1)
        voltage = []
        current = []
        self.i_set = 0
        # self.inst.temp1 = self.inst.temp.read_temp(self.inst.temp.channel)
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

    def run_sweep_basic(self):
        """Runs IV sweep with config paramters


        np.linspace()
        """
        self.inst.source.reset()
        self.inst.meter.reset()

        self.inst.source.set_output(False)

        start = self.properties["iv_sweep"]["start"]
        stop = self.properties["iv_sweep"]["stop"]
        steps = self.properties["iv_sweep"]["steps"]
        sweep = self.properties["iv_sweep"]["sweep"]
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties["iv_sweep"]["full_sweep"]
        Isource1 = np.linspace(start, stop, steps)

        if full_sweep:
            Isource = np.concatenate([Isource1, Isource1[::-1]])
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = np.concatenate([Isource, -Isource])
        self.v_set = np.tile(Isource, sweep) * self.R_srs

        self.inst.source.set_output(True)
        sleep(1)
        voltage = []
        current = []

        self.i_set = 0
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

        self.i_set = 0
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

        self.i_set = 0
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

    def run_sweep_2400(self):
        self.inst.source.setup_2W_source_I_read_V()
        self.inst.source.set_output(False)

        start = self.properties["iv_sweep"]["start"]
        stop = self.properties["iv_sweep"]["stop"]
        steps = self.properties["iv_sweep"]["steps"]
        sweep = self.properties["iv_sweep"]["sweep"]
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties["iv_sweep"]["full_sweep"]
        Isource1 = np.linspace(start, stop, steps)

        if full_sweep:
            Isource = np.concatenate([Isource1, Isource1[::-1]])
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = np.concatenate([Isource, -Isource])
        self.i_set = np.tile(Isource, sweep)

        self.inst.source.set_output(True)
        sleep(1)
        voltage = []
        current = []

        self.v_set = 0
        for n in self.i_set:
            self.inst.source.set_current(n)
            sleep(0.1)
            vread, iread = self.inst.source.read_voltage_and_current()

            print("V=%.4f V, I=%.2f uA, R =%.2f" % (vread, iread * 1e6, vread / iread))
            voltage.append(vread)
            current.append(iread)

        self.v_read = voltage
        self.i_read = current

    # def run_sweep_yoko(self):
    #         self.inst.source.setup_source_current()
    #         self.inst.source.set_output(False)

    #         start = self.properties['iv_sweep']['start']
    #         stop = self.properties['iv_sweep']['stop']
    #         steps = self.properties['iv_sweep']['steps']
    #         sweep = self.properties['iv_sweep']['sweep']
    #         # To select full (positive and negative) trace or half trace
    #         full_sweep = self.properties['iv_sweep']['full_sweep']
    #         Isource1 = np.linspace(start, stop, steps)

    #         if full_sweep == True:
    #             Isource = np.concatenate([Isource1, Isource1[::-1]])
    #             Isource = np.concatenate([Isource, -Isource])
    #         else:
    #             Isource = np.concatenate([Isource, -Isource])
    #         self.i_set = np.tile(Isource, sweep)

    #         self.inst.source.set_output(True)
    #         sleep(1)
    #         voltage = []
    #         current = []

    #         self.v_set=0
    #         for n in self.i_set:
    #             self.inst.source.set_current(n)
    #             sleep(0.1)
    #             vread, iread = self.inst.source.read_voltage_and_current()

    #             print('V=%.4f V, I=%.2f uA, R =%.2f' %(vread, iread*1e6, vread/iread))
    #             voltage.append(vread)
    #             current.append(iread)

    #         self.v_read = voltage
    #         self.i_read = current

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
        if self.properties["Save File"].get("port"):
            qf.plot(
                np.array(self.v_read),
                np.array(self.i_read) * 1e6,
                title=self.sample_name
                + " "
                + self.device_type
                + " "
                + self.device_name
                + " "
                + self.properties["Save File"]["port"],
                xlabel="Voltage (V)",
                ylabel="Current (uA)",
                path=full_path,
                show=True,
                close=True,
            )
        else:
            qf.plot(
                np.array(self.v_read),
                np.array(self.i_read) * 1e6,
                title=self.sample_name
                + " "
                + self.device_type
                + " "
                + self.device_name,
                xlabel="Voltage (V)",
                ylabel="Current (uA)",
                path=full_path,
                show=True,
                close=True,
            )

    def save(self):
        # Set up data dictionary

        data_dict = {
            "V_source": self.v_set,
            "I_source": self.i_set,
            "V_device": self.v_read,
            "I_device": self.i_read,
            "Isw": self.isw,
            "R_srs": self.R_srs,
            "temp": self.properties["Temperature"]["initial temp"],
        }

        self.full_path = qf.save(
            self.properties, "iv_sweep", data_dict, instrument_list=self.instrument_list
        )


class DoubleSweep(nTron):
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
        self.inst.source.reset()
        self.inst.meter.reset()

        self.inst.source.set_output(False)
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
            close=True,
        )

    def save(self):
        # Set up data dictionary

        data_dict = {
            "V_source": self.v_set,
            "V_device": self.v_list,
            "I_device": self.i_list,
            "I_gate": self.ig_list,
            "R_srs": self.R_srs,
            "temp": self.properties["Temperature"]["initial temp"],
        }

        self.full_path = qf.save(
            self.properties,
            "double_sweep",
            data_dict,
            instrument_list=self.instrument_list,
        )


# class DoubleSweepScope(nTron):
#     """ use awg and scope to aquire Ic distributions.
#         Awg settings and scope settings are not currently programmed.

#     """
#     def run_sweep(self):
#         'runs the sweep'

#         self.inst.source.reset()
#         self.inst.source.set_output(False)
#         self.R_srs = self.properties['double_sweep_scope']['series_resistance_srs']
#         start = self.properties['double_sweep_scope']['start']
#         stop = self.properties['double_sweep_scope']['stop']
#         steps = self.properties['double_sweep_scope']['steps']
#         sweep = self.properties['double_sweep_scope']['sweep']

#         trace_signal = self.properties['double_sweep_scope']['trace_signal']
#         trace_trigger = self.properties['double_sweep_scope']['trace_trigger']
#         trace_hist = self.properties['double_sweep_scope']['trace_hist']

#         Isource = np.linspace(start, stop, steps)

#         self.v_set = np.tile(Isource, sweep) * self.R_srs


#         for i in self.v_set:
#             self.inst.source.set_voltage(i)
#             self.inst.source.set_output(True)
#             print('Voltage:%0.2f ' % i)
#             sleep(0.1)

#             self.inst.scope.set_trigger_mode(trigger_mode = 'Stop')
#             self.inst.scope.math_histogram_clear_sweeps()

#             self.data_dict = self.inst.scope.save_traces_multiple_sequence(
#                 channels = [trace_signal, trace_trigger],
#                 num_traces = 1,
#                 NumSegments = 1000)
#             hist = self.inst.scope.get_wf_data(trace_hist)
#             self.data_dict['hist'] = hist
#             self.data_dict['i_bias'] = i/self.R_srs

#             self.full_path = qf.save(self.properties, 'double_sweep_scope', self.data_dict,
#                                      instrument_list = self.instrument_list)
#             self.inst.scope.save_screenshot(file_name=self.full_path+'.png', white_background=False)

#         self.inst.scope.set_segments(2)


class ProbeStationDoubleSweep(nTron):
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
        self.inst.source.reset()
        self.inst.meter.reset()
        self.inst.meter2.setup_read_volt()
        self.inst.meter2.set_output(output=True)

        self.inst.source.set_output(False)
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
        self.g_vlist = []
        self.g_ilist = []
        for m in self.v_set_g:
            voltage = []
            current = []
            v_g = []
            i_g = []
            self.inst.source2.set_voltage(m)
            sleep(0.1)
            for n in self.v_set:
                self.inst.source.set_voltage(n)
                sleep(0.1)

                vread = self.inst.meter.read_voltage()  # Voltage
                vgread = self.inst.meter2.read_voltage()

                iread = (n - vread) / self.R_srs  # (set voltage - read voltage)
                # igread = (m-vgread)/self.R_srs_g

                print(
                    "Vd=%.4f V, Id=%.2f uA, Ig=%.2f uA, R =%.2f"
                    % (vread, iread * 1e6, m * 1e6 / self.R_srs_g, vread / iread)
                )
                voltage.append(vread)
                current.append(iread)
                v_g.append(vgread)
                # i_g.append(igread)

            # ADDED by Andrew...
            # Turn off both voltage sources to provide reset time
            self.inst.source.set_voltage(0.0)
            self.inst.source2.set_voltage(0.0)
            sleep(2)
            #######

            self.v_list.append(np.asarray(voltage, dtype=np.float32))
            self.i_list.append(np.asarray(current, dtype=np.float32))
            self.g_vlist.append(np.asarray(v_g, dtype=np.float32))
            # self.g_ilist.append(np.asarray(i_g, dtype=np.float32))
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
            close=True,
        )
        qf.plot(
            self.i_list,
            self.g_vlist,
            title=self.sample_name + " " + self.device_type + " " + self.device_name,
            xlabel="Voltage (V)",
            ylabel="Current (A)",
            label=self.ig_list,
            path=full_path,
            show=True,
            close=True,
        )

    def save(self):
        # Set up data dictionary

        data_dict = {
            "V_source": self.v_set,
            "V_device": self.v_list,
            "I_device": self.i_list,
            "I_gate": self.ig_list,
            "R_srs": self.R_srs,
            "temp": self.properties["Temperature"]["initial temp"],
        }

        self.full_path = qf.save(
            self.properties,
            "double_sweep",
            data_dict,
            instrument_list=self.instrument_list,
        )


class IvSweepScope(nTron):
    """
    iv_sweep_scope:
      awg_amp: 0.06
      atten: 0
      freq: 100
      trigger_v: 0.1
      trigger_channel: 'C4'
      channels: [C2,F1, F2]
      hist_channel: 'F3'
      num_segments: 500
    """

    def run_sweep(self, wf="RAMP"):
        awg_amp = self.properties["iv_sweep_scope"]["awg_amp"]
        atten = self.properties["iv_sweep_scope"]["atten"]
        freq = self.properties["iv_sweep_scope"]["freq"]

        trigger_v = self.properties["iv_sweep_scope"]["trigger_v"]
        trigger_channel = self.properties["iv_sweep_scope"]["trigger_channel"]
        channels = self.properties["iv_sweep_scope"]["channels"]
        num_segments = self.properties["iv_sweep_scope"]["num_segments"]

        if wf == "RAMP":
            self.inst.awg.set_waveform("RAMP", freq=freq, amplitude=awg_amp)
            self.inst.awg.write("FUNCtion:RAMP:SYMM 50")
        if wf == "PULSE":
            self.inst.awg.set_pulse(
                freq=freq, vlow=0.0, vhigh=awg_amp, width=6.6e-6, chan=1
            )

        temperature1 = self.inst.temp.read_temp()
        self.inst.scope.set_trigger(source=trigger_channel, volt_level=trigger_v)
        self.inst.scope.pyvisa.timeout = 10000
        self.inst.scope.clear_sweeps()
        data = self.inst.scope.get_multiple_trace_sequence(
            channels=channels, NumSegments=num_segments
        )

        key = self.properties.get("iv_sweep_scope")
        if key.get("hist_channel"):
            hist_channel = self.properties["iv_sweep_scope"]["hist_channel"]
            hist = self.inst.scope.get_wf_data(hist_channel)
            hist_dict = {hist_channel + "x": hist[0], hist_channel + "y": hist[1]}
            data.update(hist_dict)

        temperature2 = self.inst.temp.read_temp()

        self.inst.scope.set_sample_mode()
        self.inst.scope.set_trigger_mode()

        data.update(
            {
                "freq": freq,
                "awg_amp": awg_amp,
                "atten": atten,
                "temp1": temperature1,
                "temp2": temperature2,
            }
        )

        self.data_dict_iv_sweep_scope = data

        self.inst.scope.set_trigger_mode()

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


class PulseTraceCurrentSweep(nTron):
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
                x, y = self.inst.source.get_single_trace(channel="C2")
                snspd_traces_x.append(x)
                snspd_traces_y.append(y)
                x, y = self.inst.source.get_single_trace(channel="C3")
                pd_traces_x.append(x)
                pd_traces_y.append(y)

            snspd_traces_x_list.append(snspd_traces_x)
            snspd_traces_y_list.append(snspd_traces_y)
            pd_traces_x_list.append(pd_traces_x)
            pd_traces_y_list.append(pd_traces_y)

    def save(self):
        """write"""
