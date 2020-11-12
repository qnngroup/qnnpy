import visa
import numpy as np
import time
import datetime

class LeCroy620Zi(object):
    """Python class for LeCroy Oscilloscope, written by Adam McCaughan.  Most of these commands
    originate from the Automation Command Reference Manual for WaveRunner Oscilloscopes"""

    def __init__(self, visa_name):
        rm = visa.ResourceManager()
        self.pyvisa = rm.open_resource(visa_name)
        self.pyvisa.timeout = 10000 # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands
        self.write('COMM_HEADER OFF') # Get rid of the leading 'VBS ' crap
        self.write('COMM_FORMAT DEF9,WORD,BIN') # Set output to 16 bits of information (a 'word') per datapoint

    def read(self):
        return self.pyvisa.read()

    def read_raw(self):
        return self.pyvisa.read_raw()
    
    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)


    def round_up_lockstep(self, x):
        """ Some functions on the LeCroy require numbers to be rounded up to nearest 1,2 or 5
        e.g. 1.2e-6 -> 5e-6 and 4.7e0 -> 5e0 """
        x_str = '%0.9e' % x  # Takes 1234.24e-10 -> '1.234240000e-07'
        x_digits = x_str[:-4] #  Takes '1.234240000e-07' -> '1.234240000'
        x_exp = x_str[-4:]
        if float(x_digits) <= 1:      locked_x = '1'
        elif float(x_digits) <= 2:    locked_x = '2'
        elif float(x_digits) <= 5:    locked_x = '5'
        else:                         locked_x = '10'
        return float(locked_x + x_exp)



    def vbs_ask(self,message):
        vbs_msg = 'VBS? \'return = %s\'' % message
        # print 'Sending command:  ' + vbs_msg
        return self.query(vbs_msg)


    def vbs_write(self,message):
        vbs_msg = 'VBS \'%s\'' % message
        # print 'Sending command:  ' + vbs_msg
        self.write(vbs_msg)


    def reset(self):
        self.write('*RST')
        self.write('COMM_HEADER OFF') # Get rid of the leading 'VBS ' crap
        self.write('COMM_FORMAT DEF9,WORD,BIN') # Set output to 16 bits of information (a word) per sample
        time.sleep(1)


    def clear_sweeps(self):
        self.vbs_write('app.ClearSweeps') #
        time.sleep(0.2) # Necessary to allow the scope time to reset all values

    
    def view_channel(self, channel = 'C1', view = True):
        if channel[0] == 'C':  # If it's C1, C3, etc
            self.vbs_write('app.Acquisition.%s.View = %s' % (channel, view))
        elif channel[0] == 'F': # If it's F1, F2...
            self.vbs_write('app.Math.%s.View = %s' % (channel, view))

        
    def set_coupling(self, channel = 'C1', coupling = 'DC1M'):
        """ Coupling should be either AC1M, DC1M, DC50, or Gnd """
        self.vbs_write('app.Acquisition.%s.Coupling = "%s"' % (channel, coupling))

        
    def get_coupling(self, channel = 'C1'):
        """ Coupling should be either AC1M, DC1M, DC50, or Gnd """
        return self.vbs_ask('app.Acquisition.%s.Coupling' % (channel))
        

    def set_bandwidth(self, channel = 'C1', bandwidth = 'Full'):
        """ Bandwidth should be either 1GHz, 200MHz, 20MHz, 3GHz, 4GHz, Full """
        self.vbs_write('app.Acquisition.%s.BandwidthLimit = "%s"' % (channel, bandwidth))


    def set_vertical_scale(self, channel = 'C1', volts_per_div = 1, volt_offset = 0):
        # Lecroy only allows digits 1, 2, and 5.  e.g. 5e-6 is acceptable, 4e-6 is not
        volts_per_div = self.round_up_lockstep(volts_per_div)
        self.vbs_write('app.Acquisition.%s.VerScale = %0.0e' % (channel, volts_per_div))
        self.vbs_write('app.Acquisition.%s.VerOffset = %0.0e' % (channel, volt_offset))

    def find_vertical_scale(self, channel = 'C1'):
        self.vbs_write('app.Acquisition.%s.FindScale' % channel)


    def set_horizontal_scale(self, time_per_div = 1e-6, time_offset = 0):
        self.vbs_write('app.Acquisition.Horizontal.HorScale = %0.6e' % time_per_div)
        self.vbs_write('app.Acquisition.Horizontal.HorOffset = %0.6e' % time_offset)

    def set_memory_samples(self, num_samples = 1e6):
        self.vbs_write('app.Acquisition.Horizontal.MaxSamples = %0.3e' % num_samples)


    def set_trigger(self, source = 'C1', volt_level = 0.1, slope = 'positive'):
        """ Slope should be "Either" / "Negative" / "Positive" """
        self.vbs_write('app.Acquisition.Trigger.Source = "%s"' % source)
        self.vbs_write('app.Acquisition.Trigger.%s.Level = %0.4e' % (source, volt_level))
        self.vbs_write('app.Acquisition.Trigger.%s.Slope = "%s"' % (source, slope))


    def set_trigger_mode(self, trigger_mode = 'Normal'):
        """ trigger_mode should be set to Auto/Normal/Single/Stop """
        self.vbs_write('app.Acquisition.TriggerMode = "%s"' % trigger_mode)


    def set_persistence(self, channel = 'C1', persistence = False, monochrome = False):
        self.vbs_write('app.Display.LockPersistence = "PerTrace"')
        self.vbs_write('app.Acquisition.%s.Persisted = %s' % (channel, persistence))
        self.vbs_write('app.Acquisition.%s.PersistenceMonochrome = %s' % (channel, monochrome))


    def label_channel(self, channel = 'C1', label = 'Channel 1 label text'):
        if (label == '') or (label == False) or (label == None):
            self.vbs_write('app.Acquisition.%s.ViewLabels = False' % channel)
        else:
            self.vbs_write('app.Acquisition.%s.LabelsText = "%s"' % (channel, label))
            self.vbs_write('app.Acquisition.%s.ViewLabels = True' % channel)


    def set_display_gridmode(self, gridmode = 'Auto'):
        """ gridmode should be Auto / Dual / Octal / Quad / Single / XY / XYDual / XYSingle """
        self.vbs_write('app.Display.GridMode = "%s"' % gridmode)



    def set_parameter(self, parameter = 'P1', param_engine = 'Maximum', source1 = 'C1', source2 = None, show_table=True):
        """ Possible param_engine values listed in a table on page 1-151 of the automation manual.
        Some sample param_engine values are:
        Frequency / LevelAtX / Fall / Maximum / Mean / Median / Minimum / PeakToPeak """
        self.vbs_write('app.Measure.ShowMeasure = %s' % show_table)
        self.vbs_write('app.Measure.%s.ParamEngine = "%s"' % (parameter, param_engine))
        if source1 is not None:
            self.vbs_write('app.Measure.%s.Source1 = "%s"' % (parameter, source1))
        if source2 is not None:
            self.vbs_write('app.Measure.%s.Source2 = "%s"' % (parameter, source2))
        self.vbs_write('app.Measure.%s.View = True' % parameter)


    def set_math(self, math_channel = 'F1', operator = 'AbsoluteValue', source1 = 'C1', source2 = None):
        """ Possible operator values listed in a table on page 1-151 of the automation manual.
        Sample values include: Average / Trend / Histogram / FFT / Integral / etc """
        self.vbs_write('app.Math.%s.Operator1 = "%s"' % (math_channel, operator))
        if source1 is not None:
            self.vbs_write('app.Math.%s.Source1 = "%s"' % (math_channel, source1))
        if source2 is not None:
            self.vbs_write('app.Math.%s.Source1 = "%s"' % (math_channel, source2))


    def get_parameter_value(self, parameter = 'P1'):
        return float(self.vbs_ask('app.Measure.%s.Out.Result.Value' % parameter))



    def get_trigger_mode(self):
        return self.vbs_ask('app.Acquisition.TriggerMode')


    def get_wf_data(self,channel='C1'):  # e.g. channel = C1 or F3 etc
        ADDR_VGAIN = 156
        ADDR_VOFFSET = 160
        ADDR_HINTERVAL = 176
        ADDR_HOFFSET = 180
        self.write(channel + ':WAVEFORM? DAT1') # Contains waveform data
        databytes = self.read_raw()
        databytes = databytes[16:]  # Strips leading header data
        if len(databytes) == 0:
            return np.array([]), np.array([])
        if len(databytes) % 2 == 1: # Sometimes accidentally returns an extra byte
            databytes = databytes[:-1]
        data = np.frombuffer(databytes, np.int16)
        # DESC contains info about vertical/horiz scaling, etc,
        # see P280, Appendix II Remote Control Manual for byte addresses
        self.write(channel + ':WAVEFORM? DESC') # Contains waveform data
        desc = self.read_raw()
        desc = desc[16:]
        vgain = float(np.frombuffer(desc[ADDR_VGAIN:ADDR_VGAIN+4], np.float32))
        voffset = float(np.frombuffer(desc[ADDR_VOFFSET:ADDR_VOFFSET+4], np.float32))
        hinterval = float(np.frombuffer(desc[ADDR_HINTERVAL:ADDR_HINTERVAL+4], np.float32))
        hoffset = float(np.frombuffer(desc[ADDR_HOFFSET:ADDR_HOFFSET+8], np.double))
        num_samples = len(data)
        x = np.array(range(num_samples))*hinterval + hoffset 
        # yscale = float(2**16)/(vf_stop - vf_start)  # Scale the data, it's output as ints from -2^16 to 2^16
        y = data*vgain - voffset
        return x,y



    def get_single_trace(self, channel = 'C1'):
        """ Sets scope to "single" trigger mode to acquire one trace, then waits until the trigger has happened
        (indicated by the trigger mode changing to "Stopped").  Returns blank lists if no trigger occurs within 1 second """
        n = 0; x = np.array([]); y = np.array([])
        self.set_trigger_mode(trigger_mode = 'Single')
        while self.get_trigger_mode() == 'Single' or n > 1e10:
            time.sleep(1e-4)
            n = n+1
        x,y = self.get_wf_data(channel=channel)
        return x,y


    # def get_math_data(self,channel='C1'):  # e.g. channel = C1 or F3 etc
        # return self.vbs_ask('app.Math.%s.Out.Result.Sweeps' % channel)


    def get_num_sweeps(self,channel='F1'):  # For use with histograms, trends, etc
        return int(self.vbs_ask('app.Math.%s.Out.Result.Sweeps' % channel))

    def get_num_data_points(self, channel = 'P1'):
        return int(self.vbs_ask('app.Measure.%s.num.REsult.Value' % channel))
        

    # def save_screenshot(self, filename = 'Hellokitty', filepath = 'C:\\LecroyScreenshots\\', grid_area_only = True):
    #     self.vbs_write('app.Hardcopy.Destination = "File"')
    #     if grid_area_only is True:
    #         self.vbs_write('app.Hardcopy.HardcopyArea = "GridAreaOnly"')
    #     else: 
    #         self.vbs_write('app.Hardcopy.HardcopyArea = "DSOWindow"')
    #     self.vbs_write('app.Hardcopy.PreferredFilename = "%s"' % filename)
    #     self.vbs_write('app.Hardcopy.ImageFileFormat = "PNG"')
    #     self.vbs_write('app.Hardcopy.Directory = "%s"' % filepath)
    #     self.vbs_write('app.Hardcopy.Print')


    def setup_math_trend(self, math_channel = 'F1', source = 'P1', num_values = 10e3):
        self.set_math(math_channel = math_channel, operator = 'Trend', source1 = source)
        self.vbs_write('app.Math.%s.Operator1Setup.Values = %s' % (math_channel, num_values))
        self.view_channel(channel = math_channel, view = True)


    def setup_math_wf_average(self, math_channel = 'F1', source = 'C1', num_sweeps = 100):
        self.set_math(math_channel = math_channel, operator = 'Average', source1 = source)
        self.vbs_write('app.Math.%s.Operator1Setup.Sweeps = %s' % (math_channel, num_sweeps))
        self.view_channel(channel = math_channel, view = True)


    def setup_math_histogram(self, math_channel = 'F1', source = 'P1', num_values = 10e3,
                            num_bins = 100, center = 0, width_per_div = 1, auto_scale = True):
        self.set_math(math_channel = math_channel, operator = 'Histogram', source1 = source)
        self.vbs_write('app.Math.%s.Operator1Setup.Values = %s' % (math_channel, num_values))
        self.vbs_write('app.Math.%s.Operator1Setup.AutoFindScale = %s' % (math_channel, auto_scale))
        self.vbs_write('app.Math.%s.Operator1Setup.Bins = %s' % (math_channel, num_bins))
        self.vbs_write('app.Math.%s.Operator1Setup.Center = %s' % (math_channel, center))
        width_per_div = self.round_up_lockstep(width_per_div)
        self.vbs_write('app.Math.%s.Operator1Setup.HorScale = %s' % (math_channel, width_per_div))
        self.view_channel(channel = math_channel, view = True)


    def collect_sweeps(self, channel = 'F1', num_sweeps = 1000):
        self.clear_sweeps()
        time.sleep(0.1)
        while (self.get_num_sweeps(channel = channel) < num_sweeps+1):
            time.sleep(0.1)
        x, ic_values = self.get_wf_data(channel=channel)
        while len(ic_values) < num_sweeps:
            time.sleep(0.05)
            x, ic_values = self.get_wf_data(channel=channel)
        return ic_values[:num_sweeps] # will occasionally return 1-2 more than num_sweeps



    def save_screenshot(self, file_name = None, white_background = True):
        if file_name == None:
            time_str = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            file_name = time_str + ' lecroy screenshot.png'


        # lecroy.query('HCSU?') # Asks what the current hard copy setup is (useful for reference)
        if white_background: self.write('HCSU BCKG,WHITE') # Sets background to white
        if white_background is False: self.write('HCSU BCKG,BLACK') # Sets background to black
        self.write('HCSU DEV,PNG')
        self.write('HCSU FORMAT,LANDSCAPE')
        self.write('HCSU DEST,REMOTE')
        self.write('HCSU AREA,DSOWINDOW')
        self.write('SCREEN_DUMP') # Takes the screenshot
        newFileBytes = self.read_raw()

        with open(file_name, "wb") as newFile:
            newFileByteArray = bytearray(newFileBytes)
            newFile.write(newFileByteArray)

        return file_name


# lecroy_ip = '18.62.10.141'
# lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % lecroy_ip)
# x,y = lecroy.get_wf_data('F1')
# from matplotlib import pyplot as plt
# plt.plot(x,y)
# plt.show()