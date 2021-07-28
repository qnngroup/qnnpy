# -*- coding: utf-8 -*-
"""
Created on Wed May  6 17:21:25 2020

@author: omedeiro
"""
import qnnpy.functions.functions as qf
import time
from time import sleep
import numpy as np

class Snspd:
    """ Class for SNSPD measurement. This class handels the instrument
    configuration, measurement, plotting, logging, and saving.
    See qnnpy\examples to see this class in action  """
    def __init__(self, configuration_file):

        #######################################################################
        #       Load .yaml configuraiton file
        #######################################################################

        # qf is a package of base functions that can be used in any class.
        self.properties = qf.load_config(configuration_file)


        self.sample_name = self.properties['Save File']['sample name']
        self.device_name = self.properties['Save File']['device name']
        self.device_type = self.properties['Save File']['device type']

        self.R_srs = self.properties['iv_sweep']['series_resistance']
        self.isw = 0
        self.instrument_list = []

        #######################################################################
        # Setup instruments
        #######################################################################

        # Counter
        if self.properties.get('Counter'):
            self.instrument_list.append('Counter')
            if self.properties['Counter']['name']:
                if self.properties['Counter']['name'] == 'Agilent53131a':
                    from qnnpy.instruments.agilent_53131a import Agilent53131a
                    try:
                        self.counter = Agilent53131a(self.properties['Counter']['port'])
                        #without the reset command this section will evaluate connected
                        #even though the GPIB could be wrong
                        #similary story for the other insturments
                        self.counter.reset()
                        self.counter.basic_setup()
                        # self.counter.write(':EVEN:HYST:REL 100')
                        print('COUNTER: connected')
                    except:
                        print('COUNTER: failed to connect')
                else:
                    qf.lablog('Invalid counter. Counter name: "%s" is not ' \
                              'configured' 
                              % self.properties['Counter']['name'])
                    raise NameError('Invalid counter. Counter name is not '\
                                    'configured')




        # Attenuator
        if self.properties.get('Attenuator'):
            self.instrument_list.append('Attenuator')

            if self.properties['Attenuator']['name'] == 'JDSHA9':
                from qnnpy.instruments.jds_ha9 import JDSHA9
                try:
                    self.attenuator = JDSHA9(self.properties['Attenuator']['port'])
                    self.attenuator.set_beam_block(True)
                    print('ATTENUATOR: connected')
                except:
                    print('ATTENUATOR: failed to connect')
            else:
                qf.lablog('Invalid Attenuator. Attenuator name: "%s" is not '\
                          'configured' % self.properties['Attenuator']['name'])
                raise NameError('Invalid Attenuator. Attenuator name is not configured')




        # Scope
        if self.properties.get('Scope'):
            self.instrument_list.append('Scope')

            if self.properties['Scope']['name'] == 'LeCroy620Zi':
                from qnnpy.instruments.lecroy_620zi import LeCroy620Zi
                try:
                    self.scope = LeCroy620Zi("TCPIP::%s::INSTR" % self.properties['Scope']['port'])
                    self.scope_channel = self.properties['Scope']['channel']
                    print('SCOPE: connected')
                except:
                    print('SCOPE: failed to connect')
            else:
                qf.lablog('Invalid Scope. Scope name: "%s" is not configured' % self.properties['Scope']['name'])
                raise NameError('Invalid Scope. Scope name is not configured')




        # Meter
        if self.properties.get('Meter'):
            self.instrument_list.append('Meter')

            if self.properties['Meter']['name'] == 'Keithley2700':
                from qnnpy.instruments.keithley_2700 import Keithley2700
                try:
                    self.meter = Keithley2700(self.properties['Meter']['port'])
                    self.meter.reset()
                    print('METER: connected')
                except:
                    print('METER: failed to connect')

            elif self.properties['Meter']['name'] == 'Keithley2400':
                # this is a source meter
                from qnnpy.instruments.keithley_2400 import Keithley2400
                try:
                    self.meter = Keithley2400(self.properties['Meter']['port'])
                    self.meter.reset()
                    print('METER: connected')
                except:
                    print('METER: failed to connect')

            elif self.properties['Meter']['name'] == 'Keithley2001':
                from qnnpy.instruments.keithley_2001 import Keithley2001
                try:
                    self.meter = Keithley2001(self.properties['Meter']['port'])
                    self.meter.reset()
                    print('METER: connected')
                except:
                    print('METER: failed to connect')
            else:
                qf.lablog('Invalid Meter. Meter name: "%s" is not configured' % self.properties['Meter']['name'])
                raise NameError('Invalid Meter. Meter name: "%s" is not configured' % self.properties['Meter']['name'])




        # Source
        if self.properties.get('Source'):
            self.instrument_list.append('Source')

            if self.properties['Source']['name'] == 'SIM928':
                from qnnpy.instruments.srs_sim928 import SIM928
                try:
                    self.source = SIM928(self.properties['Source']['port'], self.properties['Source']['port_alt'])
                    # self.source.reset()
                    self.source.set_output(False)
                    print('SOURCE: connected')
                except:
                    print('SOURCE: failed to connect')
                    
            elif self.properties['Source']['name'] == 'YokogawaGS200':
                from qnnpy.instruments.yokogawa_gs200 import YokogawaGS200
                try:
                    self.source = YokogawaGS200(self.properties['Source']['port'])
                    # self.source.reset()
                    self.source.set_output(False)
                    self.source.set_voltage_range(5)
                    print('SOURCE: connected')
                except:
                    print('SOURCE: failed to connect')
            else:
                qf.lablog('Invalid Source. Source name: "%s" is not configured' % self.properties['Source']['name'])
                raise NameError('Invalid Source. Source name: "%s" is not configured' % self.properties['Source']['name'])



        # AWG
        if self.properties.get('AWG'):
            self.instrument_list.append('AWG')

            if self.properties['AWG']['name'] == 'Agilent33250a':
                from qnnpy.instruments.agilent_33250a import Agilent33250a
                try:
                    self.awg = Agilent33250a(self.properties['AWG']['port'])
                    self.awg.beep()
                    print('AWG: connected')
                except:
                    print('AWG: failed to connect')
            else:
                qf.lablog('Invalid AWG. AWG name: "%s" is not configured' % self.properties['AWG']['name'])
                raise NameError('Invalid AWG. AWG name: "%s" is not configured' % self.properties['AWG']['name'])

        # VNA
        if self.properties.get('VNA'):
            self.instrument_list.append('VNA')

            if self.properties['VNA']['name'] == 'KeysightN5224a':
                from qnnpy.instruments.keysight_n5224a import KeysightN5224a
                try:
                    self.VNA = KeysightN5224a(self.properties['VNA']['port'])
                    # self.VNA.reset()
                    print('VNA: connected')
                except:
                    print('VNA: failed to connect')
            else:
                qf.lablog('Invalid VNA. VNA name: "%s" is not configured' % self.properties['VNA']['name'])
                raise NameError('Invalid VNA. VNA name: "%s" is not configured' % self.properties['VNA']['name'])



        # Temperature Controller
        if self.properties.get('Temperature'):
            self.instrument_list.append('Temperature')

            if self.properties['Temperature']['name'] == 'Cryocon350':
                from qnnpy.instruments.cryocon350 import Cryocon350
                try:
                    self.temp = Cryocon350(self.properties['Temperature']['port'])
                    self.temp.channel = self.properties['Temperature']['channel']
                    self.properties['Temperature']['initial temp'] = self.temp.read_temp(self.temp.channel)
                    print('TEMPERATURE: connected')
                except:
                    print('TEMPERATURE: failed to connect')

            elif self.properties['Temperature']['name'] == 'Cryocon34':
                from qnnpy.instruments.cryocon34 import Cryocon34
                try:
                    self.temp = Cryocon34(self.properties['Temperature']['port'])
                    self.temp.channel = self.properties['Temperature']['channel']
                    self.properties['Temperature']['initial temp'] = self.temp.read_temp(self.temp.channel)
                    print('TEMPERATURE: connected')
                except:
                    print('TEMPERATURE: failed to connect')

            elif self.properties['Temperature']['name'] == 'ICE':
                try:
                    self.properties['Temperature']['initial temp'] = qf.ice_get_temp(select=1)
                    print('TEMPERATURE: connected')
                except:
                    print('TEMPERATURE: failed to connect')
                    
            elif self.properties['Temperature']['name'] == 'DEWAR':
                try:
                    self.properties['Temperature']['initial temp'] = 4.2
                    print('TEMPERATURE: ~connected~ 4.2K')
                except:
                    print('TEMPERATURE: failed to connect')

            else:
                qf.lablog('Invalid Temperature Controller. TEMP name: "%s" is not configured' % self.properties['Temperature']['name'])
                raise NameError('Invalid Temperature Controller. TEMP name: "%s" is not configured' % self.properties['Temperature']['name'])
        else:
            self.properties['Temperature'] = {'initial temp': 'None'}
            # print('TEMPERATURE: Not Specified')


    def average_counts(self, counting_time, iterations, trigger_v):
        """

        This function sets the counter trigger voltage, integrates the number
        of counts over the counting time. The source is turned on before and turned off after.

        Average COUNT RATE per iteration is returned in [[ [Hz] ]]


        """

        count_rate_temp = []

        for i in range(iterations):
            self.source.set_output(True); sleep(0.05) # bias device
            voltage = self.meter.read_voltage(); sleep(0.05)
            # self.source.set_voltage(np.sign(i)*1e-3); time.sleep(0.05); #reverse bias to unlatch?
            # self.source.set_voltage(i*self.R_srs); time.sleep(0.05)
            self.counter.set_trigger(trigger_v)
            count_rate = self.counter.count_rate(counting_time=counting_time) #obtain counts
            count_rate_temp.append(count_rate) #append counts for each itteration

            if voltage > 0.005:
                print(str(count_rate)+ " wire switched")
            else:
                print(count_rate)
                
            self.source.set_output(False); sleep(0.05)
        count_rate_avg = np.mean(count_rate_temp) #average of each itteraton
        return count_rate_avg


    def tc_measurement(self, voltage, path):
        """
        Tc measurement for ICE Oxford. Path must include filename.txt
        Bias device at some value much lower than Ic. 
        This code will bias device, measure voltage, turn off voltage, every 
        two seconds. ICE will measure temp every 10 seconds. Slower sweep is 
        better. Keyboard Interrupt to end. File will be saved at path. 
        """
        self.source.set_voltage(voltage)
        self.source.set_output(True)
        while True:
            file = open(path, 'a')
            temp = qf.ice_get_temp(select=1)
            # temp = self.temp.read_temp(self.temp.channel)
            self.source.set_output(True)
            sleep(1)
            voltage = self.meter.read_voltage()
            line =str(temp)+', '+str(voltage)
            print(line)
            file.write('\n'+line)
            file.close()
            self.source.set_output(False)

            sleep(1)
            

###############################################################################
#   _____ __  ______  ________    ___   __________ ___________
#  / ___// / / / __ )/ ____/ /   /   | / ___/ ___// ____/ ___/
#  \__ \/ / / / __  / /   / /   / /| | \__ \\__ \/ __/  \__ \
# ___/ / /_/ / /_/ / /___/ /___/ ___ |___/ /__/ / /___ ___/ /
#/____/\____/_____/\____/_____/_/  |_/____/____/_____//____/
#
###############################################################################

#subclass inherits the properties of snspd

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
        self.v_bias = self.properties['trigger_sweep']['bias_voltage']
        atten_level = self.properties['trigger_sweep']['attenuation_db']

        self.source.set_output(False); sleep(.2)
        self.source.set_output(True)
        self.source.set_voltage(0)
        sleep(.2)
        self.source.set_voltage(self.v_bias)
        sleep(1)


        counting_time = self.properties['trigger_sweep']['counting_time']
        start = self.properties['trigger_sweep']['start']
        stop = self.properties['trigger_sweep']['stop']
        step = self.properties['trigger_sweep']['step']
        count_rate = []
        atten_list = [100, atten_level]
        atten_list_bool = [True, False]
        for i in range(2):
            print('\\\\\\\\ BEAM BLOCK: %s \\\\\\\\ ' % atten_list_bool[i])
            self.attenuator.set_attenuation_db(atten_list[i])
            self.attenuator.set_beam_block(atten_list_bool[i])
            trigger_v, count_rate = self.counter.scan_trigger_voltage(voltage_range=[start, stop],
                                                                      counting_time=counting_time,
                                                                      num_pts=int(np.floor((stop-start)/step)))
            self.trigger_v = trigger_v
            if i == 0:
                self.counts_trigger_dark = count_rate
            else:
                self.counts_trigger_light = count_rate
            sleep(1)
        self.attenuator.set_beam_block(True)


    def plot(self, close=True):
        ydata = [self.counts_trigger_dark, self.counts_trigger_light]
        label = ['Beam block: True', 'Beam block: False'] #maybe update this to be the attenuation level

        full_path = qf.save(self.properties, 'trigger_sweep')
        qf.plot(self.trigger_v, ydata,
                title=self.sample_name+" "+self.device_type+" "+self.device_name,
                xlabel='Trigger Voltage (V)',
                ylabel='Count Rate (Hz)',
                label=label,
                y_scale='log',
                path=full_path,
                close=close)

    def save(self):
        data_dict = {'trigger_v':self.trigger_v,
                     'counts_trigger_dark':self.counts_trigger_dark,
                     'counts_trigger_light':self.counts_trigger_light,
                     'v_bias':self.v_bias}
        self.full_path = qf.save(self.properties, 'trigger_sweep', data_dict, 
                                 instrument_list = self.instrument_list)


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
        self.v_bias = self.properties['trigger_sweep']['bias_voltage']
        atten_level = self.properties['trigger_sweep']['attenuation_db']

        self.source.set_output(False); sleep(.2)
        self.source.set_output(True)
        self.source.set_voltage(0)
        sleep(.2)
        self.source.set_voltage(self.v_bias)
        sleep(1)
        self.counter.write(':INP:IMP 1E6') #1 MOhm input impedance
        ct_volt = self.properties['trigger_sweep']['counter_trigger_voltage']
        self.counter.set_trigger(trigger_voltage=ct_volt)

        counting_time = self.properties['trigger_sweep']['counting_time']
        start = self.properties['trigger_sweep']['start']
        stop = self.properties['trigger_sweep']['stop']
        step = self.properties['trigger_sweep']['step']
        trigger_v = np.arange(start, stop, step)

        atten_list = [100, atten_level]
        atten_list_bool = [True, False]
        for a in range(2):
            print('\\\\\\\\ BEAM BLOCK: %s \\\\\\\\ ' % atten_list_bool[a])
            self.attenuator.set_attenuation_db(atten_list[a])
            self.attenuator.set_beam_block(atten_list_bool[a])
            counts = []
            for i in trigger_v:
                self.scope.set_trigger(source=self.scope_channel, volt_level=i, slope='positive')
                tv, count_rate = self.counter.scan_trigger_voltage(voltage_range=[ct_volt, ct_volt],
                                                                   counting_time=counting_time,
                                                                   num_pts=1)
                counts.append(count_rate)
                sleep(1)
                print('Scope Trigger: %0.3f' %(i))
            if a == 0:
                #this was added so that qf.plot can accept multiple ydata traces as lists. all single traces need to be arrays
                self.counts_trigger_dark = np.asarray(counts, dtype=np.float32)
            else:
                self.counts_trigger_light = np.asarray(counts, dtype=np.float32)
        self.attenuator.set_beam_block(True)
        self.trigger_v = trigger_v



    def plot(self, close=True):
        ydata = [self.counts_trigger_dark, self.counts_trigger_light]
        label = ['Beam block: True', 'Beam block: False'] #maybe update this to be the attenuation level

        full_path = qf.save(self.properties, 'trigger_sweep')
        qf.plot(self.trigger_v, ydata,
                title=self.sample_name+" "+self.device_type+" "+self.device_name,
                xlabel='Trigger Voltage (V)',
                ylabel='Count Rate (Hz)',
                label=label,
                y_scale='log',
                path=full_path,
                close=close)


    def save(self):
        data_dict = {'trigger_v':self.trigger_v,
                     'counts_trigger_dark':self.counts_trigger_dark,
                     'counts_trigger_light':self.counts_trigger_light,
                     'v_bias':self.v_bias}
        self.full_path = qf.save(self.properties, 'trigger_sweep', data_dict, 
                                 instrument_list = self.instrument_list)


class IvSweep(Snspd):
    """ Class object for iv sweeps

    Configuration: iv_sweep:
    [start: initial bias current],
    [stop: final bias current],
    [steps: number of points],
    [sweep: number of itterations],
    [full_sweep: Include both positive and negative bias],
    [series_resistance: resistance at voltage source ie R_srs]
    
    """
    def run_sweep_fixed(self):
        """ Runs IV sweep with config paramters
        This constructs #steps between start and 75% of final current.
        Then, #steps between 75% and 100% of final current.
        
        np.linspace()
        """
        self.source.reset()
        self.meter.reset()

        self.source.set_output(False)

        start = self.properties['iv_sweep']['start']
        stop = self.properties['iv_sweep']['stop']
        steps = self.properties['iv_sweep']['steps']
        sweep = self.properties['iv_sweep']['sweep']
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties['iv_sweep']['full_sweep']
        Isource1 = np.linspace(start, stop*0.75, steps) #Coarse
        Isource2 = np.linspace(stop*0.75, stop, steps) #Fine

        if full_sweep == True:
            Isource = np.concatenate([Isource1, Isource2, Isource2[::-1], Isource1[::-1]])
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

            vread = self.meter.read_voltage() # Voltage

            iread = (n-vread)/self.R_srs#(set voltage - read voltage)

            print('V=%.4f V, I=%.2f uA, R =%.2f' %(vread, iread*1e6, vread/iread))
            voltage.append(vread)
            current.append(iread)

        self.v_read = voltage
        self.i_read = current
        
        
    def run_sweep_dynamic(self):
        """ Runs IV sweep with config paramters
        This constructs [points_coarse] between start and [percent] of final current.
        Then, [points_fine] between [percent] and 100% of final current.

        uses np.linspace()
        """
        self.source.reset()
        self.meter.reset()

        self.source.set_output(False)

        start = self.properties['iv_sweep']['start']
        stop = self.properties['iv_sweep']['stop']
        percent = self.properties['iv_sweep']['percent']
        num1 = self.properties['iv_sweep']['points_coarse']
        num2 = self.properties['iv_sweep']['points_fine']
        
        sweep = self.properties['iv_sweep']['sweep']
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties['iv_sweep']['full_sweep']
        Isource1 = np.linspace(start, stop*percent, num1) #Coarse
        Isource2 = np.linspace(stop*percent, stop, num2) #Fine

        if full_sweep == True:
            Isource = np.concatenate([Isource1, Isource2, Isource2[::-1], Isource1[::-1]])
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

            vread = self.meter.read_voltage() # Voltage

            iread = (n-vread)/self.R_srs#(set voltage - read voltage)

            print('V=%.4f V, I=%.2f uA, R =%.2f' %(vread, iread*1e6, vread/iread))
            voltage.append(vread)
            current.append(iread)

        self.v_read = voltage
        self.i_read = current

    def run_sweep_spacing(self):
        """ Runs IV sweep with config paramters
        This constructs [points_coarse] between start and [percent] of final current.
        Then, [points_fine] between [percent] and 100% of final current.
        
        uses np.arange()
        """
        self.source.reset()
        self.meter.reset()

        self.source.set_output(False)

        start = self.properties['iv_sweep']['start']
        stop = self.properties['iv_sweep']['stop']
        percent = self.properties['iv_sweep']['percent']
        spacing1 = self.properties['iv_sweep']['spacing_coarse']
        spacing2 = self.properties['iv_sweep']['spacing_fine']
        
        sweep = self.properties['iv_sweep']['sweep']
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties['iv_sweep']['full_sweep']
        Isource1 = np.arange(start, stop*percent+spacing1, spacing1) #Coarse
        Isource2 = np.arange(stop*percent, stop+spacing2, spacing2) #Fine

        if full_sweep == True:
            Isource = np.concatenate([Isource1, Isource2, Isource2[::-1], Isource1[::-1]])
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

            vread = self.meter.read_voltage() # Voltage

            iread = (n-vread)/self.R_srs#(set voltage - read voltage)

            print('V=%.4f V, I=%.2f uA, R =%.2f' %(vread, iread*1e6, vread/iread))
            voltage.append(vread)
            current.append(iread)

        self.v_read = voltage
        self.i_read = current



    def isw_calc(self):
        """ Calculates critical current.
        """
        '''
        Critical current is defined as the current one step before a voltage
        reading greater than 5mV.
        self.isw = self.i_read[np.argmax(np.array(self.v_read) > 0.005)-1]
        print('%.4f uA' % (self.isw*1e6))
        '''

        ''' New method looks at differential and takes average of points that 
        meet condition. Prints mean() and std().` std should be < 1-2µA
        '''
        #isws = abs(self.i_read[np.where(abs(np.diff(self.i_read)/max(np.diff(self.i_read))) > 0.5)])
        # self.isw = self.i_read[np.argmax(np.array(self.v_read) > 0.005)-1]
        # print('%.4f uA' % (self.isw*1e6))
        
        
        
        try:
            switches = np.asarray(np.where(abs(np.diff(self.i_read)/max(np.diff(self.i_read))) > 0.8),dtype=int).squeeze()
            isws = abs(np.asarray([self.i_read[i] for i in switches]))
            print(isws)
            self.isw = isws.mean()
            print('Isw_avg = %.4f µA :--: Isw_std = %.4f µA' % (self.isw*1e6, isws.std()*1e6))
        except:
            print('Could not calculate Isw. Isw set to 0')
            self.isw = 0
    
    def plot(self):
        full_path = qf.save(self.properties, 'iv_sweep')
        qf.plot(np.array(self.v_read), np.array(self.i_read)*1e6,
                title=self.sample_name+" "+self.device_type+" "+self.device_name,
                xlabel='Voltage (mV)',
                ylabel='Current (uA)',
                path=full_path,
                show=True,
                close=True)
    
    def save(self):

        #Set up data dictionary

        data_dict = {'V_source': self.v_set,
                 'V_device': self.v_read,
                 'I_device': self.i_read,
                 'Isw': self.isw,
                 'R_srs': self.R_srs,
                 'temp': self.properties['Temperature']['initial temp']}


        self.full_path = qf.save(self.properties, 'iv_sweep', data_dict, 
                                 instrument_list = self.instrument_list)


class IvSweepScope(Snspd):
    
    def run_sweep(self):
        awg_amp = self.properties['iv_sweep_scope']['awg_amp']
        atten = self.properties['iv_sweep_scope']['atten']
        freq = self.properties['iv_sweep_scope']['freq']
        
        trigger_v = self.properties['iv_sweep_scope']['trigger_v']
        trigger_channel = self.properties['iv_sweep_scope']['trigger_channel']
        channels = self.properties['iv_sweep_scope']['channels']
        hist_channel = self.properties['iv_sweep_scope']['hist_channel']
        num_segments = self.properties['iv_sweep_scope']['num_segments']
        self.awg.set_vpp(awg_amp)
        self.awg.set_freq(freq)
        # temperature = self.temp.read_temp()
        temperature=0
        self.scope.set_trigger(source=trigger_channel, volt_level=trigger_v)
        self.scope.pyvisa.timeout = 10000
        self.scope.clear_sweeps()
        data = self.scope.get_multiple_trace_sequence(channels=channels, NumSegments=num_segments)
        hist = self.scope.get_wf_data(hist_channel)
        hist_dict = {hist_channel+'x': hist[0], hist_channel+'y':hist[1]}
        self.scope.set_sample_mode()

        data.update(hist_dict)    
        data.update({'freq': freq, 'awg_amp':awg_amp, 'atten':atten, 'temp':temperature})
        
        self.data_dict_iv_sweep_scope = data
        
        
    def save(self):
        
        
        self.full_path = qf.save(self.properties, 'iv_sweep_scope', self.data_dict_iv_sweep_scope, instrument_list = self.instrument_list)    
        self.scope.save_screenshot(self.full_path+'screen_shot'+'.png', white_background=False)

        

class PhotonCounts(Snspd):
    """ Class object for PCR and DCR measurments. Configuration data will be
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


    def dark_counts(self):
        """ Dark Count Rate"""

        #Variable Setup
        iterations = self.properties['photon_counts']['iterations']
        start = self.properties['photon_counts']['start']
        stop = self.properties['photon_counts']['stop']
        step = self.properties['photon_counts']['step']
        counting_time = self.properties['photon_counts']['counting_time']
        trigger_v = self.properties['photon_counts']['trigger_v']

        currents = np.arange(start, stop, step)
        self.currents = currents

        #Block light
        self.attenuator.set_attenuation_db(100)
        self.attenuator.set_beam_block(True)

        count_rate_list = []

        print('\\\\\\\\ DARK COUNT RATE \\\\\\\\')
        for n, j in enumerate(currents): #sweep current
            start_time = time.time()
            self.source.set_voltage(voltage=j*self.R_srs)
            count_rate_avg = Snspd.average_counts(self, counting_time, iterations, trigger_v)

            count_rate_list.append(count_rate_avg) #final countrate at this current is the average of each itteration
            print('Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)' % (j*1e6, count_rate_avg, n+1, len(currents), (time.time()-start_time)/60.0))

        self.DCR = np.asarray(count_rate_list, dtype=np.float32)
#        self.DCR = currents*2  # here for testing

        return self.DCR

    def light_counts(self):
        """ Photon Count Rate"""
        #Variable Setup
        iterations = self.properties['photon_counts']['iterations']
        start = self.properties['photon_counts']['start']
        stop = self.properties['photon_counts']['stop']
        step = self.properties['photon_counts']['step']
        counting_time = self.properties['photon_counts']['counting_time']
        trigger_v = self.properties['photon_counts']['trigger_v']
        self.attenuation = self.properties['photon_counts']['attenuation_db']

        currents = np.arange(start, stop, step)
        self.currents = currents

        #Shine light
        self.attenuator.set_attenuation_db(self.attenuation)
        self.attenuator.set_beam_block(False)

        count_rate_list = []
        
        print('\\\\\\\\ LIGHT COUNT RATE \\\\\\\\')
        for n, j in enumerate(currents): #sweep current
            start_time = time.time()
            self.source.set_voltage(voltage=j*self.R_srs)
            sleep(0.1)
            count_rate_avg = Snspd.average_counts(self, counting_time, iterations, trigger_v)
            count_rate_list.append(count_rate_avg) #final countrate at this current is the average of each itteration
            print('Current value %0.2f uA - Count rate = %0.2e   (%s of %s: %0.2f min)' % (j*1e6, count_rate_avg, n+1, len(currents), (time.time()-start_time)/60.0))
        self.attenuator.set_beam_block(True)
        self.LCR = np.asarray(count_rate_list, dtype=np.float32)

#        self.LCR = currents*3 # here for testing
        return self.LCR


    def plot(self):
        """ Plots DCR, LCR, and LCR-DCR """
        full_path = qf.save(self.properties, 'photon_counts')

        ydata = []
        label = []
        if not self.DCR == []:
            ydata.append(self.DCR)
            label.append('DCR')
        if not self.LCR == []:
            ydata.append(self.LCR)
            label.append('LCR')
        if not self.DCR == [] and not self.LCR == []:
            ydata.append(self.LCR-self.DCR)
            label.append('LCR-DCR')
        if self.properties['Laser']['wavelength_nm']:
            device_name = self.device_name+" "+str(self.properties['Laser']['wavelength_nm'])+'nm'+" "+str(self.properties['photon_counts']['attenuation_db'])+"dB"
        qf.plot(self.currents * 1e6, ydata,
                title=self.sample_name+" "+self.device_type+" "+device_name,
                xlabel='Current (uA)',
                ylabel='Count Rate (Hz)',
                label=label,
                path=full_path,
                show=True,
                close=True)
        
    def save(self):
        """If LCR was not measured, attunation is 100dB for dark counts"""
        if self.LCR == []:
            self.attenuation = 100

        self.instrument_list.append('Laser')

        data_dict = {'LCR': self.LCR,
                     'DCR': self.DCR,
                     'currents': self.currents,
                     'wavelength': self.properties['Laser']['wavelength_nm'],
                     'attenuation': self.attenuation}

        full_path = qf.save(self.properties, 'photon_counts', data_dict, 
                            instrument_list = self.instrument_list)


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
        bias = self.properties['linearity_check']['bias']
        start = self.properties['linearity_check']['start']
        stop = self.properties['linearity_check']['stop']
        step = self.properties['linearity_check']['step']
        trigger_v = self.properties['linearity_check']['trigger_v']
        counting_time = self.properties['linearity_check']['counting_time']
        iterations = self.properties['linearity_check']['iterations']

        dbs = np.arange(start, stop, step)
        self.source.set_output(True)
        self.source.set_voltage(voltage=bias*self.R_srs)

        #add current loop if desired
        self.attenuator.set_beam_block(False)

        counts_per_atten = []
        start_time = time.time()
        for i in dbs:
            self.attenuator.set_attenuation_db(i)
            sleep(.1)
            count_rate_avg = Snspd.average_counts(self, counting_time, iterations, trigger_v)
            counts_per_atten.append(count_rate_avg)
            print('Attenuation: %.1f dB \\\\ Counts: %.0f \\\\ Elapsed Time: %.2f' %(i, count_rate_avg, time.time()-start_time))
        self.attenuator.set_beam_block(True)

        self.counts_per_atten = np.asarray(counts_per_atten, dtype=np.float32)
        self.attenuation_levels = np.asarray(dbs, dtype=np.float32)
        self.linearity_bias = bias


    def plot(self):
        full_path = qf.save(self.properties, 'linearity_check')
        device_name = self.device_name+" "+str(self.properties['Laser']['wavelength_nm'])+'nm'
        qf.plot(self.attenuation_levels, self.counts_per_atten,
                title=self.sample_name+" "+self.device_type+" "+device_name,
                xlabel='Attenuation (dB)',
                ylabel='Count Rate (Hz)',
                y_scale='log',
                path=full_path,
                show=True,
                close=True)
        
    def save(self):
        data_dict = {'attenuation': self.attenuation_levels,
                     'counts': self.counts_per_atten,
                     'bias': self.linearity_bias
                     }

        self.full_path = qf.save(self.properties, 'linearity_check', data_dict, 
                                 instrument_list = self.instrument_list)


class PulseTraceSingle(Snspd):
    """ Single trace acquistion for LeCroy620Zi.
    no pulse_trace configuration required.
    
    Sadly, this will reset instruments when initializing the Snspd class. 
    So be sure to 'stop' the scope before running. 
    """
    def trace_data(self, channels=None):
        """ Returns x,y of scope_channel in configuration file"""
        
        bias = self.properties['pulse_trace']['bias_voltage']
        self.scope.set_trigger_mode(trigger_mode='Stop')
        self.source.set_output(True)
        self.source.set_voltage(voltage=bias)
        
        if channels:
            channels = channels
        else:
            channels = self.properties['pulse_trace']['channel']

        xlist = []; ylist = [];
        tlist = []
        
        trigger_v = self.properties['pulse_trace']['trigger_level']
        self.scope.set_trigger(source = channels[0], volt_level = trigger_v, slope = 'positive')
        
        attenuation = self.properties['pulse_trace']['attenuation']
        self.attenuator.set_attenuation_db(attenuation)
        if attenuation == 100:
            self.attenuator.set_beam_block(True)
        else:
            self.attenuator.set_beam_block(False)
            
        sleep(0.1)
        self.scope.set_trigger_mode(trigger_mode='Single')
        while (self.scope.get_trigger_mode() == 'Single\n'):
            sleep(0.1)
            
        for i in range(len(channels)):
            x, y = self.scope.get_single_trace(channel=channels[i])
            # xlist.append(x);  #keep all x data the same.
            ylist.append(y);

        self.trace_x = x
        self.trace_y = ylist
        return self.trace_x, self.trace_y

    def plot(self):
        """ Grabs new trace from scope and plots. Figure is saved to path """
        # x,y = self.scope.get_single_trace(channel= self.scope_channel)
        channels = self.properties['pulse_trace']['channel']
        full_path = qf.save(self.properties, 'pulse_trace')
#        data_dict = {'x':x,'y':y}
        x = self.trace_x
        y = self.trace_y
        qf.plot(x, y,
                title=self.sample_name+" "+self.device_type+" "+self.device_name,
                # xlabel = '',
                # ylabel = '',
                path=full_path,
                show=True,
                linestyle='-',
                label=channels,
                close=True)

    def save(self):
        data_dict = {'x':self.trace_x, 'y':self.trace_y}
        qf.save(self.properties, 'pulse_trace', data_dict, 
                instrument_list = self.instrument_list)

class PulseTraceMultiple(Snspd):

    def trace_data(self, channels=None):
        """ Returns x,y of scope_channel in configuration file"""

        if channels:
            channels = channels
        else:
            channels = self.properties['pulse_trace']['channel']
         
        ''' Option for attenuator control. Set to 100dB for beam block. '''    
        if self.properties.get('pulse_trace').get('attenuation'):
            self.attenuator.set_attenuation_db(self.properties['pulse_trace']['attenuation'])
            self.attenuator.set_beam_block(False)
            if self.properties['pulse_trace']['attenuation'] == 100:
                self.attenuator.set_beam_block(True)
        
        
        total_ylist = []
        trigger = self.properties['pulse_trace']['trigger_level']
        number_of_traces = self.properties['pulse_trace']['number_of_traces']
        
        self.scope.set_trigger(source=channels[0], volt_level=trigger)

            
        self.source.set_voltage(self.properties['pulse_trace']['bias_voltage'])
        self.source.set_output(True)    
        for n in range(number_of_traces):
            self.meter.read_voltage()
            self.scope.set_trigger_mode(trigger_mode='Single')
            while self.scope.get_trigger_mode() != 'Stopped\n':
                sleep(0.001)
            
            ylist = [];
            for i in range(len(channels)):
                x, y = self.scope.get_single_trace(channel=channels[i])
                # xlist.append(x);  #keep all x data the same.
                ylist.append(y);

            total_ylist.append(np.asarray(ylist, dtype=np.float32))
            print('Acquired Trace %0.f of %0.f' %(n+1, number_of_traces))
            
        self.trace_x = x
        self.trace_y = np.asarray(total_ylist, dtype=np.float32)
        self.source.set_output(False)    

        return self.trace_x, self.trace_y

    def plot(self):
        """ Grabs new trace from scope and plots. Figure is saved to path """
        # x,y = self.scope.get_single_trace(channel= self.scope_channel)

        full_path = qf.save(self.properties, 'pulse_trace')
#        data_dict = {'x':x,'y':y}
        qf.plot(self.trace_x, self.trace_y,
                title=self.sample_name+" "+self.device_type+" "+
                      self.device_name,
                # xlabel = '',
                # ylabel = '',
                path=full_path,
                show=True,
                linestyle='-',
                close=True)

    def save(self):
        data_dict = {'x':self.trace_x, 'y':self.trace_y}
        qf.save(self.properties, 'pulse_trace', data_dict, 
                instrument_list = self.instrument_list)
        
        
class PulseTraceCurrentSweep(Snspd):
    """ UNFINISHED Sweep current and acquire trace. Configuration requires
    pulse_trace section: {start, stop, steps}  """
    def trace_data(self):
        start = self.properties['pulse_trace']['start']
        stop = self.properties['pulse_trace']['stop']
        steps = self.properties['pulse_trace']['steps']
        num_traces = 1
        currents = np.linspace(start, stop, steps)

        snspd_traces_x_list = []
        snspd_traces_y_list = []
        pd_traces_x_list = []
        pd_traces_y_list = []
        start_time = time.time()
        self.source.set_output(True)
        for n, i in enumerate(currents):
            print('   ---   Time elapsed for measurement %s of %s: %0.2f '\
                  'min    ---   ' % (n, len(currents), 
                                     (time.time()-start_time)/60.0))
            self.source.set_voltage(i*self.R_srs)
            pd_traces_x = [] # Photodiode pulses
            pd_traces_y = []
            snspd_traces_x = [] # Device pulses
            snspd_traces_y = []
            self.scope.clear_sweeps()
            for n in range(num_traces):
                x, y = self.scope.get_single_trace(channel='C2')
                snspd_traces_x.append(x);  snspd_traces_y.append(y)
                x, y = self.scope.get_single_trace(channel='C3')
                pd_traces_x.append(x);  pd_traces_y.append(y)

            snspd_traces_x_list.append(snspd_traces_x)
            snspd_traces_y_list.append(snspd_traces_y)
            pd_traces_x_list.append(pd_traces_x)
            pd_traces_y_list.append(pd_traces_y)
            
            
            
class KineticInductancePhase(Snspd):
     
    def run_sweep_current(self, Ic_break=None, save=None, plot=None):
        self.VNA.write('CALC:FORM SMITh')
        start = self.properties['kinetic_inductance_phase']['start']
        stop = self.properties['kinetic_inductance_phase']['stop']
        steps = self.properties['kinetic_inductance_phase']['steps']

        currents = np.linspace(start, stop, steps)
            
        self.if_bandwidth = self.VNA.get_if_bw()
        self.fspan = self.VNA.get_span()
        sweep_time = self.fspan/(self.if_bandwidth**2)
        
        self.rf_power = self.VNA.get_power()
        
        self.VNA.select_measurement()
        
        for current in currents:
            print('Bias set to %0.3f uA' % (current*1e6))
            self.source.set_voltage(current*self.R_srs)
            self.source.set_output(True)
            self.current = current*1e6
            
            if self.properties['Temperature']['name'] == 'ICE':
                self.currentTemp = qf.ice_get_temp(select=1)
            else:
                self.currentTemp = self.temp.read_temp(self.temp.channel)

            self.voltage = self.meter.read_voltage()
            if Ic_break:
                if(self.voltage>0.01):
                    print('Wire Switched')
                    self.meter.reset()
                    break
            t = sweep_time+10
            # print('Waiting %0.1f seconds for vna averging' % t)
            print('Waiting 10 seconds for vna averging')

            sleep(10) #vna averging
        
            self.f,self.re,self.im = self.VNA.get_freq_real_imag()
            self.log_mag = 20*np.log10(np.sqrt(np.square(self.re)+
                                               np.square(self.im)))
            self.phase = np.angle(self.re+self.im*1j,deg=True)
            
            if plot:
                self.plot()
            if save:
                self.save()
        self.source.set_output(False)
        self.VNA.write('CALC:FORM MLOG')


             
    def plot(self):
        full_path = qf.save(self.properties, 'kinetic_inductance_phase')
        qf.plot(self.f, self.phase,
                title=self.sample_name+" "+self.device_type+" "+
                      self.device_name+": "+str(round(self.current,2))+" uA, "
                      +str(self.rf_power)+" dB",
                xlabel = 'Frequency (Hz)',
                ylabel = 'Phase (°)',
                path=full_path,
                show=True,
                linestyle='-',
                close=True)           
 

    def save(self):
        data_dict = {'freq': self.f,
                     're': self.re,
                     'im': self.im,
                     'log_mag': self.log_mag,
                     'phase': self.phase,
                     'Ibias': self.current,
                     'voltage': self.voltage,
                     'if_bandwidth': self.if_bandwidth,
                     'R_srs': self.R_srs,
                     'temp': self.currentTemp}
        qf.save(self.properties, 'kinetic_inductance_phase', data_dict, 
                instrument_list = self.instrument_list)
   
    
class PulseTraceFFT_CurrentSweep(Snspd):
    """ ((NO PLOT. ONLY SAVE)) Sweep current and acquire traces C1(signal) and F1(FFT) . Configuration requires
    pulse_trace section: {start, stop, steps}  """
    def trace_data(self):
        start = self.properties['pulse_trace']['start']
        stop = self.properties['pulse_trace']['stop']
        steps = self.properties['pulse_trace']['steps']
        
        num_traces = 1
        currents = np.linspace(start, stop, steps)

        self.FFT = []
        self.FREQ = []
        self.VIN = []
        self.T1 = []
        self.VOUT = []
        start_time = time.time()
        self.source.set_output(True)
        
        self.scope.clear_sweeps()
        time.sleep(1)

        
        for n, i in enumerate(currents):
            print('   ---   Time elapsed for measurement %s of %s: %0.2f '\
                  'min    ---   ' % (n, len(currents), 
                                     (time.time()-start_time)/60.0))
            self.source.set_voltage(i*self.R_srs)
            
            time.sleep(1)
           
            self.scope.label_channel('C1', 'V_device')

            self.scope.set_math('F1','FFT','C1')
            self.scope.view_channel('F1')
            
            
       
            t1,C1 = self.scope.get_wf_data('C1')
            tf,Ft = self.scope.get_wf_data('F1')
            self.FFT.append(Ft)
            self.FREQ.append(tf)
            self.T1.append(t1)
            self.VOUT.append(C1)
            self.Ibias = currents
         
            time.sleep(1)

            
        self.source.set_voltage(0)
        self.source.set_output(False)   
            
    def save(self):
        data_dict = {'FFT':self.FFT,'FREQ':self.FREQ,'T2':self.T1,'VOUT':self.VOUT, 'Ibias':self.Ibias}
        
        qf.save(self.properties, 'pulse_trace', data_dict, 
                instrument_list = self.instrument_list)
     
            