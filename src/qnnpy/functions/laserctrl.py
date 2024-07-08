"""
Laser control scripts for Santec tunable laser
Scripts from the Loncar group at Harvard.
Consider deleting if not needed.
"""

import os
import time

import nidaqmx
import numpy as np
from nidaqmx.constants import TaskMode

from ..santec_tsl import SantecTSL

# import ..models.modeltools as modeltools


class LaserCtrl:
    """LaserCtrl uses a laser and photodiode to perform monitor and scan
    transmission data.
    """

    def __init__(self):
        self.laser = None  # laser object
        self.config = {}
        self.stop = False
        self.loop_scanning = False
        self.most_recent_scan = "One way"
        self.sweep_task = None
        arr0 = np.array(
            [
                0.0,
            ]
        )
        # initialize empty datasets
        self.scandata = {
            "wav": arr0,
            "V": arr0,
        }
        self.scandata2way = {
            "wavstartstop": arr0,
            "Vstartstop": arr0,
            "wavstopstart": arr0,
            "Vstopstart": arr0,
        }
        self.monitordata = [
            0,
        ]
        self.monitor_nsteps = 10  # number of points to scroll
        path_here = os.path.dirname(__file__)
        self._default_config_path = os.path.join(
            path_here, "config_defaults/laserctrl_default.yml"
        )
        self.loaded_config_path = None

    def load_config(self, fpath=None):
        # load YAML file from fpath or default if fpath=None
        self.config = modeltools.load_config(
            fpath, defaultpath=self._default_config_path
        )
        if fpath is None:
            self.loaded_config_path = self._default_config_path
        else:
            self.loaded_config_path = fpath

    def overwrite_config(self):
        # overwrite YAML file used to load_config with current config
        modeltools.save_config(self.loaded_config_path, self.config)

    def load_laser(self, laser=None):
        # load laser, if None given, autoload from config
        if laser is None:
            kind = self.config["Laser"]["kind"]
            rsc_name = self.config["Laser"]["rsc_name"]
            if kind == "SantecTSLDummy":
                self.laser = SantecTSLDummy(rsc_name)
            elif kind == "SantecTSL":
                self.laser = SantecTSL(rsc_name)
            else:
                raise Exception("Laser kind not recoginized in config")
            self.laser.initialize()
        else:
            self.laser = laser
            self.config["Laser"]["kind"] = str(self.laser)
            self.config["Laser"]["rsc_name"] = self.laser.rsc_name

    def monitor(self):
        """Monitor photoreceiver voltage in time.
        Config Args:
            Monitor.tstep - timestep in sec, float
            Monitor.scroll_time - length of stored data in sec, float
        Updates:
            monitordata - voltage measurements, 1D list
        Notes:
            + This function runs forever. You'll want to run it in a thread
            + Can be stopped during acquisition by self.stop = True
        """
        print("Starting monitoring")
        scroll_time = self.config["Monitor"]["scroll_time"]
        tstep = self.config["Monitor"]["tstep"]
        self.monitor_nsteps = int(scroll_time / tstep)
        # setup analog read daq task
        daqtask = nidaqmx.Task()
        daqtask.ai_channels.add_ai_voltage_chan(self.config["DAQ"]["ai"])
        # init data to empty list
        self.monitordata = []
        self.stop = False
        while not self.stop:
            time.sleep(tstep)
            datum = daqtask.read()  # next measurement
            if len(self.monitordata) < self.monitor_nsteps:
                self.monitordata = self.monitordata + [datum]
            else:
                self.monitordata[:-1] = self.monitordata[1:]
                self.monitordata[-1] = datum
        self.stop = False  # reset stop signal
        daqtask.close()

    def wav_valid(self, wav):
        return self.laser.wav_min <= wav <= self.laser.wav_max

    def _single_scan(self, backwards=False):
        # private single scan function, returns scandata
        scandata = {}
        if not backwards:
            wavstart = self.config["Scan"]["wavstart"]
            wavstop = self.config["Scan"]["wavstop"]
        else:
            wavstart = self.config["Scan"]["wavstop"]
            wavstop = self.config["Scan"]["wavstart"]
        samples = self.config["Scan"]["samples"]
        speed = self.config["Scan"]["speed"]
        t_acq = np.abs(wavstart - wavstop) / speed  # expected acquisition time
        print("tacq: {:.3}".format(t_acq))
        sample_rate = float(samples / t_acq)
        wavs = np.linspace(wavstart, wavstop, samples)
        scandata["wav"] = wavs

        # configure daq task
        self.sweep_task = nidaqmx.Task()
        self.sweep_task.ai_channels.add_ai_voltage_chan(self.config["DAQ"]["ai"])
        max_sample_rate = self.sweep_task.timing.samp_clk_max_rate
        if sample_rate > max_sample_rate:
            self.sweep_task.close()
            msg = "The requested sample rate {} is faster than the max rate {}".format(
                sample_rate, max_sample_rate
            )
            msg += ". Adjust scan settings to lower sample rate."
            raise Exception(msg)
        self.sweep_task.timing.cfg_samp_clk_timing(
            float(sample_rate), samps_per_chan=samples
        )
        self.sweep_task.triggers.reference_trigger.cfg_dig_edge_ref_trig(
            trigger_source=self.config["DAQ"]["trig"], pretrigger_samples=2
        )
        # run scan
        self.sweep_task.start()
        try:
            self.laser.setStartWavelength(wavstart)
            self.laser.setStopWavelength(wavstop)
            self.laser.setSweepSpeed(speed)
            self.laser.setSweepMode(1)
            self.laser.setSweepCycles(numOfSweeps=1)
            self.laser.setTriggerOut(triggerOut=True)
            self.laser.startSweep()
            timeout = self.config["DAQ"]["timeout"]
            voltages = self.sweep_task.read(samples, timeout=t_acq + timeout)
            scandata["wav"] = wavs
            scandata["V"] = voltages
        except nidaqmx.errors.DaqError:
            print("Daq error in LaserCtrl._single_scan")
            # scandata['V'] = np.zeros(len(wavs))
            scandata = self.scandata
        self.sweep_task.close()
        return scandata

    def stop_scan(self):
        # abort scan mid-way
        self.laser.stopSweep()
        self.sweep_task.control(TaskMode.TASK_ABORT)
        print("Scan aborted")

    def scan(self, backwards=False):
        """Perform single continuous wavelength scan
        Args:
            backwards=False: if True, scan from wavstop to wavstart
        Config Args:
            Scan.wavestart - start wavelength in nm, float
            Scan.wavstop - stop wavelength in nm, float
            Scan.samples - number of samples to collect, int
            Scan.speed - scan speed in nm/s
        Updates:
            scandata['wav'] - measured wavelengths in nm, array of float
            scandata['V'] - measured voltages in V, array of float
        Notes:
            Wavelengths are estimated by assuming linear scan in time
        """
        print("Doing a one-way scan!")
        self.scandata = self._single_scan(backwards=backwards)
        self.most_recent_scan = "One way"
        if not self.loop_scanning:
            time.sleep(0.2)
            self.laser.setWavelength(self.config["LaserSettings"]["wavelength"])

    def scan_twoway(self):
        """Perform forward(start>stop) scan, then backwards(stop>start) scan
        Config Args:
            Same as LaserCtrl.scan() above
        Updates:
            scandata['wavstartstop'] - wavelengths in nm, array of float
            scandata['wavstopstart'] - wavelengths in nm, array of float
            scandata['Vstartstop'] - measured voltages in V, array of float
            scandata['Vstopstart'] - measured voltages in V, array of float
        """
        self.stop = False
        print("Doing a two-way scan!")
        data_temp = {}
        # forward scan
        scandata = self._single_scan(backwards=False)
        data_temp["wavstartstop"] = scandata["wav"]
        data_temp["Vstartstop"] = scandata["V"]
        time.sleep(0.3)
        # backward scan
        if not self.stop:
            scandata = self._single_scan(backwards=True)
            data_temp["Vstopstart"] = scandata["V"]
        else:
            data_temp["Vstopstart"] = np.zeros(len(scandata["wav"]))
        data_temp["wavstopstart"] = scandata["wav"]
        # update data
        self.scandata2way = data_temp
        self.most_recent_scan = "Two way"
        if not self.loop_scanning:
            time.sleep(0.2)
            self.laser.setWavelength(self.config["LaserSettings"]["wavelength"])

    def scan_loop(self, two_way=False):
        """Perform scan in a loop
        Config Args:
            same as LaserCtrl.scan
            Scan.loop_delay - wait time between scans
        Args:
            two_way=False - do two-way scan using LaserCtr.scan_twoway
        Updates:
            scandata - see LaserCtrl.scan and LaserCtrl.scan_twoway
        Notes:
            + This function runs forever. You'll want to run it in a thread.
            + Can be stopped during acquisition by self.stop=True
        """
        print("Starting scan loop with two_way={}".format(two_way))
        self.stop = False
        self.loop_scanning = True
        while not self.stop:
            if two_way:
                self.scan_twoway()
            else:
                self.scan()
            time.sleep(self.config["Scan"]["loop_delay"])
        time.sleep(0.2)
        self.laser.setWavelength(self.config["LaserSettings"]["wavelength"])
        self.stop = False
        self.loop_scanning = False

    def clear_data(self, kind="One way"):
        """Reinitilize dataset of a particular type
        Args:
            type - str {One way, Two way, Monitor}
        """
        arr0 = np.array(
            [
                0.0,
            ]
        )
        if kind == "One way":
            self.scandata = {
                "wav": arr0,
                "V": arr0,
            }
        elif kind == "Two way":
            self.scandata2way = {
                "wavstartstop": arr0,
                "Vstartstop": arr0,
                "wavstopstart": arr0,
                "Vstopstart": arr0,
            }
        elif kind == "Monitor":
            self.monitordata = [
                0,
            ]

    def save_scandata(self, save_config=True, overwrite_protect=True, saveplot=True):
        # save data, using dir and fname args in config['Save']
        savedir = self.config["Save"]["dir"]
        fname = self.config["Save"]["fname"]
        fpath = modeltools.overwrite_protection(
            savedir, fname, extension=".dat", overwrite_protect=overwrite_protect
        )
        header = "Data saved by LaserCtrl\n"
        if self.most_recent_scan == "One way":
            modeltools.save_data_dict(
                data_dict=self.scandata,
                fpath=fpath,
                keys=["wav", "V"],
                units=["nm", "V"],
                col_labels=["wavelength", "PD voltage"],
                header=header,
                config_dict=(self.config if save_config else None),
            )
        elif self.most_recent_scan == "Two way":
            modeltools.save_data_dict(
                data_dict=self.scandata2way,
                fpath=fpath,
                keys=["wavstartstop", "Vstartstop", "wavstopstart", "Vstopstart"],
                units=["nm", "V", "nm", "V"],
                col_labels=[
                    "wavelength start2stop",
                    "PD voltage start2stop",
                    "wavelength stop2start",
                    "PD voltage stop2start",
                ],
                header=header,
                config_dict=(self.config if save_config else None),
            )

        print("Data saved to: {}".format(fpath))
        if saveplot:
            if self.most_recent_scan == "One way":
                xs = self.scandata["wav"]
                ys = self.scandata["V"]
                legend = None
            elif self.most_recent_scan == "Two way":
                xs = [
                    self.scandata2way["wavstartstop"],
                    self.scandata2way["wavstopstart"],
                ]
                ys = [self.scandata2way["Vstartstop"], self.scandata2way["Vstopstart"]]
                legend = ["start>stop", "stop>start"]
            xlabel = "Wavelength (nm)"
            ylabel = "PD Voltage (V)"
            modeltools.save_data_fig(xs, ys, fpath, xlabel, ylabel, legend)

    def save_config(self, overwrite_protect=True):
        # save config,using dir and fname args in config['Save']
        fname = self.config["Save"]["fname"]
        savedir = self.config["Save"]["dir"]
        fpath = modeltools.overwrite_protection(
            savedir, fname, extension=".yml", overwrite_protect=overwrite_protect
        )
        modeltools.save_config(fpath, self.config)
