"""
Author: Reed Foster
"""

import csv
import re
import time
from pathlib import Path

import LabJackPython as ljpy
import numpy as np
import u6
import yaml

import qnnpy.functions.functions as qf
from qnnpy.instruments.cryocon34 import Cryocon34
from qnnpy.instruments.lakeshore121 import Lakeshore121


# pretty-printing utility
def eng_string(x, sig_figs=3):
    """
    Returns float/int value <x> formatted in a simplified engineering format -
    using an exponent that is a multiple of 3.

    sig_figs: number of significant figures
    """
    sign = "-" if x < 0 else " "
    x = abs(float(x))
    if x == 0:
        return "0"
    log10 = int(np.floor(np.log10(x)))
    log10_nearest_3 = 3 * ((log10) // 3)
    x_mantissa = x / (10**log10_nearest_3)
    x_mantissa = round(
        x_mantissa, -int(np.floor(np.log10(x_mantissa)) - (sig_figs - 1))
    )
    if x_mantissa >= -24 and x_mantissa <= 24:
        exp_text = "yzafpnum kMGTPEZY"[log10_nearest_3 // 3 + 8]
    else:
        exp_text = "e%s" % log10_nearest_3
    mantissa_text = str(x_mantissa)
    mantissa_text = mantissa_text[:-1] if mantissa_text[-2:] == ".0" else mantissa_text
    return ("%s%s%s") % (sign, mantissa_text, exp_text)


class TcCryo:
    """Class for measurements with TcCryo. This class handles setup of the instruments,
    measurement, plotting, and saving of data
    """

    def __init__(self, configuration_file):
        self.properties = qf.load_config(configuration_file)

        self.tc_T_min = self.properties["Tc measurement"]["T_min"]
        self.tc_T_max = self.properties["Tc measurement"]["T_max"]
        self.tc_T_step = self.properties["Tc measurement"]["T_step"]
        self.tc_t_dwell = self.properties["Tc measurement"]["t_dwell"]
        self.tc_current = self.properties["Tc measurement"]["current"]
        self.tc_n_repeat = self.properties["Tc measurement"]["repeat"]

        self.cool_warm_current = self.properties["Cooldown-Warmup measurement"][
            "current"
        ]
        self.cool_warm_n_repeat = self.properties["Cooldown-Warmup measurement"][
            "repeat"
        ]
        self.cool_warm_sleep = self.properties["Cooldown-Warmup measurement"]["sleep"]
        self.cool_warm_save_interval = self.properties["Cooldown-Warmup measurement"][
            "save interval"
        ]
        self.cool_warm_T_base = self.properties["Cooldown-Warmup measurement"]["T_base"]
        self.cool_warm_T_max = self.properties["Cooldown-Warmup measurement"]["T_max"]

        samples = self.properties["Sample Mapping"]
        # verify samples
        self.samples = {}
        expr = re.compile(r"^[A-Z]+[0-9]{3}$")
        for key in samples:
            if not expr.match(samples[key]):
                raise ValueError(f"invalid sample ID {samples[key]}")
            if int(key) < 0 or int(key) > 5:
                raise ValueError(
                    f"invalid sample position {key}, must be an int between 0 and 5"
                )
            self.samples[int(key)] = samples[key]

        # set up temp controller
        self.temp = Cryocon34(self.properties["Cryocon34"]["port"])
        self.temp_channel = self.properties["Cryocon34"]["channel"]
        # set up current source
        self.isrc = Lakeshore121(self.properties["Lakeshore121"]["port"])
        # set up labjack
        self.lj_device = u6.U6()

        # range setting (from labjack.m, and section 4.3.3 of U6 datasheet)
        # LJ_rgBIP10V = 2;  % -10V to +10V
        # LJ_rgBIP1V = 8;   % -1V to +1V
        # LJ_rgBIPP1V = 10; % -0.1V to +0.1V
        # LJ_rgBIPP01V = 11; % -0.01V to +0.01V
        self.labjack_ranges = {
            10: ljpy.LJ_rgBIP10V,
            1: ljpy.LJ_rgBIP1V,
            0.1: ljpy.LJ_rgBIPP1V,
            0.01: ljpy.LJ_rgBIPP01V,
        }

    def select_mux(self, position):
        """Selects a position between 0 and 7"""
        for b in range(3):
            ljpy.eDO(Handle=self.lj_device.handle, Channel=b, State=position & (2**b))

    def read_voltage(self, channels=(0, 1), vrange="auto"):
        """
        Reads voltage using eAIN on differential pair AIN2-3.
        Only works on windows

        Default autoranges gain setting to the optimal value.
        """
        # SettlingFactor parameter is 0=Auto, 1=20us, 2=50us, 3=100us, 4=200us, 5=500us, 6=1ms, 7=2ms, 8=5ms, 9=10ms
        # resolution setting: 8 is maximum for non-pro version of U6

        # Lakeshore121 compliance limit is +/-11V up to 30 mA and +/-10V up to 100 mA.
        # realistically at these high currents, there will be some drop from the cables
        # Autorange starting with BIP10V (+/-10V), working downwards if voltage is within next range down
        if (vrange not in self.labjack_ranges.keys()) and not (
            isinstance(vrange, str) and vrange.lower() == "auto"
        ):
            raise ValueError(
                f'invalid range {vrange}, please specify "auto" or a numeric voltage range ',
                "that is one of 10, 1, 0.1, 0.01",
            )
        ranges = [10, 1, 0.1, 0.01] if vrange == "auto" else [vrange]
        for lj_range in ranges:
            vdevice = ljpy.eAIN(
                Handle=self.lj_device.handle,
                ChannelP=channels[0],
                ChannelN=channels[1],
                Range=self.labjack_ranges[lj_range],
                Resolution=8,  # maximum
                Settling=9,  # 10 ms
                Binary=False,
            )
            # range down if vdevice < 0.1 * lj_range
            # set threshold to 0.099 so we're not right at the range limit
            if abs(vdevice) >= 0.099 * lj_range:
                return vdevice, lj_range
        return vdevice, lj_range

    def check_resistances(self, current=100e-6, n_measurements=10):
        """
        Checks resistance for multiple positions, averaging over n_measurements
        """
        self.isrc.enable_current()
        time.sleep(0.1)
        self.isrc.set_current(current)
        voltages_4p = np.zeros(n_measurements)
        ranges = np.zeros(n_measurements)
        for pos in self.samples.keys():
            self.select_mux(pos)
            time.sleep(0.5)
            for i in range(len(voltages_4p)):
                voltages_4p[i], ranges[i] = self.read_voltage(self.lj_device)
                time.sleep(0.01)
            if self.isrc.in_compliance():
                print("WARNING: COMPLIANCE")
            print(
                "4P: ",
                np.mean(voltages_4p) / current,
                " +/- ",
                np.std(voltages_4p) / current,
                " range = ",
                ranges,
            )
        self.isrc.disable_current()

    def pretty_print(self, sample_indices, temperatures, voltages, current, n_avg):
        text = [["", ""], ["", ""], ["", ""]]
        positions = [[2, 3], [1, 4], [0, 5]]
        for row in range(3):
            for col in range(2):
                pos = positions[row][col]
                if pos not in self.samples:
                    text[row][col] = ["---".center(15)] * 4
                    continue
                sample_idx = sample_indices[pos]
                t = temperatures[sample_idx][-n_avg:]
                r = voltages[sample_idx][-n_avg:] / current
                r_mean = np.mean(r)
                r_std = np.std(r)
                t_str = eng_string(t)
                r_mean_str = eng_string(r_mean)
                r_std_str = eng_string(r_std)
                # width = 1(sign)+3 or 4(mantissa)+1(exponent)
                # budget width of 8 for eng_str
                text[row][col] = (
                    self.samples[pos].center(15),
                    "T  = %s K" % t_str.rjust(8),
                    "Rμ = %s Ω" % r_mean_str.rjust(8),
                    "Rσ = %s Ω" % r_std_str.rjust(8),
                )
        # print rows
        for row in range(3):
            print("+", "-" * 15, "+", "-" * 15, "|")
            for i in range(4):
                print("|", text[row][0][i], "|", text[row][1][i], "|")
        print("+", "-" * 15, "+", "-" * 15, "|")

    def set_heater(self, temperature):
        """Sets heater to specified temperature"""
        # lookup range, P/I for different ranges
        if temperature > 15:
            power = "25W"
        else:
            power = "2.5W"
        proportional = 2
        integral = 1
        self.temp.setup_heater(load=25, range=power, source_channel=self.temp_channel)
        time.sleep(0.1)
        self.temp.set_pid(proportional, integral, 0.0)
        self.temp.set_setpoint(temperature)  # Setpoint in Kelvin
        self.temp.set_control_type_pid()
        time.sleep(0.1)
        self.temp.start_heater()

    def get_save_dirs(self):
        save_dirs = {}
        for pos in self.samples.keys():
            save_dir = Path(f"S:/SC/Measurements/{self.samples[pos]}/tc")
            save_dir.mkdir(parents=True, exist_ok=True)
            save_dirs[pos] = save_dir
        return save_dirs

    def save_data(self, tstart, measurement_type, num_rows, sample_indices, data_dict):
        # save data
        fname = lambda file_type: time.strftime(
            f"{measurement_type}_%Y-%m-%d_%H-%M-%S.{file_type}", tstart
        )
        save_dirs = self.get_save_dirs()
        for pos in self.samples.keys():
            # append to CSV
            with open(save_dirs[pos] / fname("csv"), "a") as csvfile:
                writer = csv.writer(csvfile)
                for i in range(num_rows[pos]):
                    s_idx = sample_indices[pos]
                    row = [
                        data_dict['timestamps'][s_idx, i],
                        data_dict['compliance'][s_idx, i],
                        data_dict['temperatures'][s_idx, i],
                        data_dict['voltages'][s_idx, i],
                        data_dict['vranges'][s_idx, i],
                    ]
                    writer.writerow(row)
            with open(save_dirs[pos] / fname("mat"), "w") as f:
                yaml.dump(self.properties, f, default_flow_style=False)

    def measure_tc(
        self,
    ):
        """Ramp temperature up slowly and then back down slowly"""
        t_min = self.tc_T_min
        t_max = self.tc_T_max
        t_step = self.tc_T_step
        tlist = np.concatenate(
            (np.linspace(t_min, t_max, t_step), np.linspace(t_max, t_min, -t_step))
        )
        sample_indices = {pos: i for i, pos in enumerate(self.samples.keys())}
        n_samples = len(self.samples)
        temperatures = np.zeros((n_samples, len(tlist) * self.tc_n_repeat))
        voltages = np.zeros(temperatures.shape)
        vranges = np.zeros(temperatures.shape)
        compliance = np.zeros(temperatures.shape)
        timestamps = np.zeros(temperatures.shape)
        self.isrc.enable_current()
        time.sleep(0.1)
        self.isrc.set_current(self.tc_current)
        time.sleep(0.1)
        tstart = time.time()
        fname = lambda ftype: time.strftime(f"tc_%Y-%m-%d_%H-%M-%S.{ftype}", tstart)
        try:
            # loop
            for ti, t in enumerate(tlist):
                self.set_heater(t)
                print(f"set heater to T = {t} K")
                time.sleep(self.tc_t_dwell)
                # measure
                for pos, sample_idx in sample_indices.items():
                    self.select_mux(pos)
                    time.sleep(0.5)
                    for n in range(self.tc_n_repeat):
                        w_idx = n + ti * self.tc_n_repeat
                        timestamps[sample_idx, w_idx] = time.time()
                        compliance[sample_idx, w_idx] = self.isrc.in_compliance()
                        T = self.temp.read_temp(channel=self.temp_channel)
                        v, vr = self.read_voltage(self.lj_device)
                        temperatures[sample_idx, w_idx] = T
                        voltages[sample_idx, w_idx] = v
                        vranges[sample_idx, w_idx] = vr
                        time.sleep(0.01)
                    self.pretty_print(
                        sample_indices,
                        temperatures,
                        voltages,
                        self.tc_current,
                        self.tc_n_repeat,
                    )
                    print("")
            self.temp.stop_heater()
            self.isrc.disable_current()
            # save data
            data_dict = dict(
                timestamps=timestamps,
                compliance=compliance,
                temperatures=temperatures,
                voltages=voltages,
                vranges=vranges
            )
            self.save_data(
                tstart,
                "cooldown_warmup",
                {pos: timestamps.shape[1] for pos in self.samples.keys()},
                sample_indices,
                data_dict
            )
        except:
            self.temp.stop_heater()
            self.isrc.disable_current()
            raise

    def measure_cooldown_warmup(
        self,
    ):
        """
        Repeatedly measure multiple samples during warmup or cooldown.
        Saves meausrements at regular intervals to ensure data is saved.
        """
        n_samples = len(self.samples)
        temperatures = np.zeros(
            (n_samples, self.cool_warm_save_interval * self.cool_warm_n_repeat)
        )
        voltages = np.zeros(temperatures.shape)
        vranges = np.zeros(temperatures.shape)
        compliance = np.zeros(temperatures.shape)
        timestamps = np.zeros(temperatures.shape)
        sample_indices = {pos: i for i, pos in enumerate(self.samples.keys())}
        min_temp = np.inf
        max_temp = -np.inf
        # do measurement
        self.isrc.enable_current()
        time.sleep(0.1)
        self.isrc.set_current(self.cool_warm_current)
        time.sleep(0.1)
        tstart = time.time()
        fname = lambda ftype: time.strftime(
            f"cooldown_warmup_%Y-%m-%d_%H-%M-%S.{ftype}", tstart
        )
        rows_written = {pos: 0 for pos in self.samples.keys()}
        try:
            while True:
                for pos, sample_idx in sample_indices.items():
                    rows_written[pos] = 0
                for save_iter in range(self.cool_warm_save_interval):
                    for pos, sample_idx in sample_indices.items():
                        self.select_mux(pos)
                        time.sleep(0.5)
                        for n in range(self.cool_warm_n_repeat):
                            w_idx = n + save_iter * self.cool_warm_n_repeat
                            timestamps[sample_idx, w_idx] = time.time()
                            compliance[sample_idx, w_idx] = self.isrc.in_compliance()
                            T = self.temp.read_temp(channel=self.temp_channel)
                            v, vr = self.read_voltage(self.lj_device)
                            temperatures[sample_idx, w_idx] = T
                            voltages[sample_idx, w_idx] = v
                            vranges[sample_idx, w_idx] = vr
                            time.sleep(0.01)
                            min_temp = min(min_temp, T)
                            max_temp = max(max_temp, T)
                            rows_written[pos] += 1
                    self.pretty_print(
                        sample_indices,
                        temperatures,
                        voltages,
                        self.cool_warm_current,
                        self.cool_warm_n_repeat,
                    )
                    print("")
                    # pretty-print measured resistances and temperatures
                    time.sleep(self.cool_warm_sleep)
                    # check stopping condition
                    if min_temp < self.cool_warm_T_base:
                        raise Exception
                    if max_temp > self.cool_warm_T_max:
                        raise Exception
                data_dict = dict(
                    timestamps=timestamps,
                    compliance=compliance,
                    temperatures=temperatures,
                    voltages=voltages,
                    vranges=vranges
                )
                self.save_data(
                    tstart,
                    "cooldown_warmup",
                    rows_written,
                    sample_indices,
                    data_dict
                )
        except Exception:
            self.isrc.disable_current()
            data_dict = dict(
                timestamps=timestamps,
                compliance=compliance,
                temperatures=temperatures,
                voltages=voltages,
                vranges=vranges
            )
            self.save_data(
                tstart,
                "cooldown_warmup",
                rows_written,
                sample_indices,
                data_dict
            )
