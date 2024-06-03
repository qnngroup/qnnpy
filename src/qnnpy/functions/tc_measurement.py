# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 12:50:01 2020

@author: omedeiro
"""

import qnnpy.functions.functions as qf


class TcMeasurement:
    def __init__(self, configuration_file):
        #######################################################################
        #       Load .yaml configuraiton file
        #######################################################################

        # qf is a package of base functions that can be used in any class.
        self.properties = qf.load_config(configuration_file)

        # Temperature Controller
        if self.properties.get("Temperature"):
            ###################################################################
            if self.properties["Temperature"]["name"] == "Cryocon350":
                from qnnpy.instruments.cryocon350 import Cryocon350

                try:
                    self.temp = Cryocon350(self.properties["Temperature"]["port"])
                    channel = self.properties["Temperature"]["channel"]
                    self.properties["Temperature"]["initial temp"] = (
                        self.temp.read_temp(channel)
                    )
                    print("TEMPERATURE: connected")
                except Exception:
                    print("TEMPERATURE: failed to connect")
            ###################################################################
            elif self.properties["Temperature"]["name"] == "Cryocon34":
                from qnnpy.instruments.cryocon34 import Cryocon34

                try:
                    self.temp = Cryocon34(self.properties["Temperature"]["port"])
                    channel = self.properties["Temperature"]["channel"]
                    self.properties["Temperature"]["initial temp"] = (
                        self.temp.read_temp(channel)
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

    def run_sweep(self):
        """Sweep temperature and record voltage

        Configuration : tc_measurement:
        [start: initial temperature setpoint],
        [stop: final temperature setpoint],
        [itterations: number of start-stop-start sweeps]

        If start is left blank then current temperature will be used as initial
        setpoint.
        """

        if self.properties["Temperature"]["name"] == "ICE":
            qf.ice_get_temp(select=1)

    def plot(self):
        NotImplemented("Plotting function not implemented yet.")

    def save(self):
        NotImplemented("Saving function not implemented yet.")
