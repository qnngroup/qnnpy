# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 12:50:01 2020

@author: omedeiro & emmabat
"""

from time import sleep

import qnnpy.functions.functions as qf


class TcMeasurement:
    def __init__(self, configuration_file):
        #######################################################################
        #       Load .yaml configuraiton file
        #######################################################################

        # qf is a package of base functions that can be used in any class.
        self.properties = qf.load_config(configuration_file)

        # LabJack U12
        from qnnpy.instruments.labjack_u12 import LabJackU12

        self.mux = LabJackU12()
        self.mux_names = ["S0", "S1", "S2"]
        self.mapping = {"EN": 3, "S0": 2, "S1": 1, "S2": 0}

        # Temperature Controller
        if self.properties.get("Temperature"):
            ###################################################################
            if self.properties["Temperature"]["name"] == "Cryocon350":
                from qnnpy.instruments.cryocon350 import Cryocon350

                try:
                    self.temp = Cryocon350(self.properties["Temperature"]["port"])
                    self.channel = self.properties["Temperature"]["channel"]
                    self.properties["Temperature"]["initial temp"] = (
                        self.temp.read_temp(self.channel)
                    )
                    print("TEMPERATURE: connected")
                except Exception as e:
                    print("TEMPERATURE: failed to connect")
            ###################################################################
            elif self.properties["Temperature"]["name"] == "Cryocon34":
                from qnnpy.instruments.cryocon34 import Cryocon34

                try:
                    self.temp = Cryocon34(self.properties["Temperature"]["port"])
                    self.channel = self.properties["Temperature"]["channel"]
                    self.properties["Temperature"]["initial temp"] = (
                        self.temp.read_temp(self.channel)
                    )
                    print("TEMPERATURE: connected")
                except Exception:
                    print("TEMPERATURE: failed to connect")
            ###################################################################
            elif self.properties["Temperature"]["name"] == "ICE":
                try:
                    self.properties["Temperature"]["initial temp"] = qf.ice_get_temp()
                    print("TEMPERATURE: connected")
                except Exception:
                    print("TEMPERATURE: failed to connect")
            ###################################################################
            else:
                qf.lablog(
                    'Invalid Temperature Controller. TEMP name: "%s" is not configured'
                    % self.properties["Temperature"]["name"]
                )
                raise NameError(
                    'Invalid Temperature Controller. TEMP name: "%s" is not configured'
                    % self.properties["Temperature"]["name"]
                )

    def run_sweep(self, min_temp, num_channels, wait_time=1):
        """Sweep temperature and record voltage

        Configuration : tc_measurement:
        [start: initial temperature setpoint],
        [stop: final temperature setpoint],
        [iterations: number of start-stop-start sweeps]
        """
        temp = self.get_temp()

        # initialize storage variables
        self.temps = []
        self.all_voltages = []
        for channel in range(num_channels):
            self.all_voltages.append([])

        # while ICE cools to min_temp, read vals
        while temp > min_temp:
            # read temperature
            temp = self.get_temp()
            self.temps.append(temp)

            # read voltage from each analog channel
            for channel in range(num_channels):
                # LabJack functions execute in 20 ms or less
                # and set_mux_channel calls 4 LabJack functions
                self.mux.set_mux_channel(channel, self.mapping, self.mux_names)
                sleep(0.1)
                voltage = self.mux.read_analog(channel)
                sleep(0.05)
                self.all_voltages[channel - 1].append(voltage)
            sleep(wait_time)
        return self.temps, self.all_voltages

    def get_temp(self):
        if self.properties["Temperature"]["name"] == "ICE":
            return qf.ice_get_temp(select=1)
        else:
            return self.temp.read_temp(self.channel)

    def plot(self):
        full_path = qf.save(self.properties, "temperature sweep")
        qf.plot(
            self.temps,
            self.all_voltages,
            title=self.sample_name + " " + self.device_type,
            xlabel="Temperature [K]",
            ylabel="Voltage [V]",
            path=full_path,
            show=True,
            linestyle="-",
            close=True,
        )

    def save(self):
        data_dict = {
            "temps": self.temps,
            "voltages": self.all_voltages,
        }
        qf.save(
            self.properties,
            "temperature sweep",
            data_dict,
            instrument_list=self.instrument_list,
        )
