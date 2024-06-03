from time import sleep

import numpy as np

import qnnpy.functions.functions as qf

# note: instrument libraries are imported within the class as needed from config file


class Resonators:
    """
    class for measuring superconducting resonators
    """

    def __init__(self, config_file):
        # Load config file
        self.properties = qf.load_config(config_file)

        self.sample_name = self.properties["Save File"]["sample name"]
        self.device_name = self.properties["Save File"]["device name"]
        self.device_type = self.properties["Save File"]["device type"]
        self.R_srs = self.properties["iv_sweep"]["series_resistance"]

        self.instrument_list = []

        ### Set up instruments ###
        if self.properties.get("PNA"):
            self.instrument_list.append("PNA")

            if self.properties["PNA"]["name"] == "KeysightN5224a":
                from qnnpy.instruments.keysight_n5224a import KeysightN5224a

                try:
                    self.pna = KeysightN5224a(self.properties["PNA"]["port"])
                    # self.pna.set_power(0)
                    self.pna.set_scale_auto()
                    print("PNA: connected")
                except Exception:
                    print("PNA: failed to connect")
            else:
                qf.lablog(
                    'Invalid PNA. PNA name: "%s" is not'
                    "configured" % self.properties["PNA"]["name"]
                )
                raise NameError("Invalide PNA. PNA name is not configured")

        # Meter
        if self.properties.get("Meter"):
            self.instrument_list.append("Meter")

            if self.properties["Meter"]["name"] == "Keithley2700":
                from qnnpy.instruments.keithley_2700 import Keithley2700

                try:
                    self.meter = Keithley2700(self.properties["Meter"]["port"])
                    self.meter.reset()
                    print("METER: connected")
                except Exception:
                    print("METER: failed to connect")

            elif self.properties["Meter"]["name"] == "Keithley2400":
                # this is a source meter
                from qnnpy.instruments.keithley_2400 import Keithley2400

                try:
                    self.meter = Keithley2400(self.properties["Meter"]["port"])
                    self.meter.reset()
                    print("METER: connected")
                except Exception:
                    print("METER: failed to connect")

            elif self.properties["Meter"]["name"] == "Keithley2001":
                from qnnpy.instruments.keithley_2001 import Keithley2001

                try:
                    self.meter = Keithley2001(self.properties["Meter"]["port"])
                    self.meter.reset()
                    print("METER: connected")
                except Exception:
                    print("METER: failed to connect")
            else:
                qf.lablog(
                    'Invalid Meter. Meter name: "%s" is not configured'
                    % self.properties["Meter"]["name"]
                )
                raise NameError(
                    'Invalid Meter. Meter name: "%s" is not configured'
                    % self.properties["Meter"]["name"]
                )

        # Source
        if self.properties.get("Source"):
            self.instrument_list.append("Source")

            if self.properties["Source"]["name"] == "SIM928":
                from qnnpy.instruments.srs_sim928 import SIM928

                try:
                    self.source = SIM928(
                        self.properties["Source"]["port"],
                        self.properties["Source"]["port_alt"],
                    )
                    self.source.reset()

                    try:
                        self.properties.get("Source")["port_alt2"]
                        self.source2 = SIM928(
                            self.properties["Source"]["port"],
                            self.properties["Source"]["port_alt2"],
                        )
                    except Exception:
                        print("No second SRS specified")

                    print("SOURCE: connected")
                except Exception:
                    print("SOURCE: failed to connect")
            else:
                qf.lablog(
                    'Invalid Source. Source name: "%s" is not configured'
                    % self.properties["Source"]["name"]
                )
                raise NameError(
                    'Invalid Source. Source name: "%s" is not configured'
                    % self.properties["Source"]["name"]
                )

        # Temperature Controller
        if self.properties.get("Temperature"):
            self.instrument_list.append("Temperature")

            if self.properties["Temperature"]["name"] == "Cryocon350":
                from qnnpy.instruments.cryocon350 import Cryocon350

                try:
                    self.temp = Cryocon350(self.properties["Temperature"]["port"])
                    self.temp.channel = self.properties["Temperature"]["channel"]
                    self.properties["Temperature"]["initial temp"] = (
                        self.temp.read_temp(self.temp.channel)
                    )
                    print("TEMPERATURE: connected")
                except Exception:
                    print("TEMPERATURE: failed to connect")

            elif self.properties["Temperature"]["name"] == "Cryocon34":
                from qnnpy.instruments.cryocon34 import Cryocon34

                try:
                    self.temp = Cryocon34(self.properties["Temperature"]["port"])
                    self.temp.channel = self.properties["Temperature"]["channel"]
                    self.properties["Temperature"]["initial temp"] = (
                        self.temp.read_temp(self.temp.channel)
                    )
                    print("TEMPERATURE: connected")
                except Exception:
                    print("TEMPERATURE: failed to connect")

            elif self.properties["Temperature"]["name"] == "ICE":
                try:
                    self.properties["Temperature"]["initial temp"] = qf.ice_get_temp(
                        select=1
                    )
                    print("TEMPERATURE: connected")
                except Exception:
                    print("TEMPERATURE: failed to connect")

            elif self.properties["Temperature"]["name"] == "DEWAR":
                try:
                    self.properties["Temperature"]["initial temp"] = 4.2
                    print("TEMPERATURE: ~connected~ 4.2K")
                except Exception:
                    print("TEMPERATURE: failed to connect")

            else:
                qf.lablog(
                    'Invalid Temperature Controller. TEMP name: "%s" is not configured'
                    % self.properties["Temperature"]["name"]
                )
                raise NameError(
                    'Invalid Temperature Controller. TEMP name: "%s" is not configured'
                    % self.properties["Temperature"]["name"]
                )
        else:
            self.properties["Temperature"] = {"initial temp": "None"}
            # print('TEMPERATURE: Not Specified')

    def configure_pna(
        self, start_freq, stop_freq, num_points, power=0, if_bandwidth=100
    ):
        # self.pna.reset(measurement='S21', if_bandwidth = 20, start_freq = 200E6,
        #     stop_freq = 20E9, power = -40)

        self.pna.set_start(start_freq)
        self.pna.set_stop(stop_freq)
        self.pna.set_points(num_points)
        self.pna.set_power(power)
        self.pna.set_if_bw(if_bandwidth)
        sleep(5)
        self.pna.set_scale_auto()

    def S21_measurement(
        self, start_freq, stop_freq, num_points, power=0, if_bandwidth=100
    ):
        """
        measure the S21 data on a superconducting resonator using a VNA
        start_freq, stop_freq = start/end points of frequency sweep (Hz)
        num_points = number of points in frequenyc sweep
        if_bandwidth = if_bandwidth (Hz)
        power = output power of VNA (dBm)

        class stores the measured source attenuation, the frequency points
        swept over, and resulting S21 values
        """
        self.configure_pna(start_freq, stop_freq, num_points, power, if_bandwidth)

        self.f, self.S21 = self.pna.single_sweep()
        self.att = self.pna.get_source_attenuation()

    def phase_measurement(
        self, start_freq, stop_freq, num_points, power=0, if_bandwidth=100
    ):
        self.configure_pna(start_freq, stop_freq, num_points, power, if_bandwidth)

        self.f, self.phase = self.pna.single_sweep_phase()
        self.att = self.pna.get_source_attenuation()

    def power_characterization(
        self, start_freq, stop_freq, num_points, powers, if_bandwidth=100
    ):
        for power in powers:
            self.S21_measurement(start_freq, stop_freq, num_points, power, if_bandwidth)
            self.save()
            self.plot()

    def S21_to_dBm(self):
        return 20 * np.log10(np.abs(self.S21))

    def plot(self, close=True):
        full_path = qf.save(self.properties, "S21_measurement")
        qf.plot(
            self.f,
            self.S21_to_dBm(),
            title=self.sample_name
            + " "
            + self.device_type
            + " "
            + self.device_name
            + " "
            + str(self.pna.get_power())
            + "dB",
            xlabel="Frequency (Hz)",
            ylabel="S21 (dBm)",
            path=full_path,
            close=close,
        )

    def save(self):
        data_dict = {
            "S21": self.S21_to_dBm(),
            "pna_power": self.pna.get_power(),
            "f": self.f,
            "pna_att": self.att,
        }
        self.full_path = qf.save(
            self.properties,
            "S21_measurement",
            data_dict,
            instrument_list=self.instrument_list,
        )


class IvSweep(Resonators):
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
        self.source.reset()
        self.meter.reset()

        self.source.set_output(False)

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

        self.source.set_output(True)
        sleep(1)
        voltage = []
        current = []

        for n in self.v_set:
            self.source.set_voltage(n)
            sleep(0.1)

            vread = self.meter.read_voltage()  # Voltage

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
        self.source.reset()
        self.meter.reset()

        self.source.set_output(False)

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

        self.source.set_output(True)
        sleep(1)
        voltage = []
        current = []

        for n in self.v_set:
            self.source.set_voltage(n)
            sleep(0.1)

            vread = self.meter.read_voltage()  # Voltage

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
        self.source.reset()
        self.meter.reset()

        self.source.set_output(False)

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

        self.source.set_output(True)
        sleep(1)
        voltage = []
        current = []

        for n in self.v_set:
            self.source.set_voltage(n)
            sleep(0.1)

            vread = self.meter.read_voltage()  # Voltage

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
            xlabel="Voltage (mV)",
            ylabel="Current (uA)",
            path=full_path,
            show=True,
            close=True,
        )

    def save(self):
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
