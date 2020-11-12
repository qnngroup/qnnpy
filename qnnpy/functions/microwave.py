# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 16:40:17 2020

@author: omedeiro
"""
import qnnpy.functions.functions as qf
import time
from time import sleep
import numpy as np

class Microwave:
    """ Class for microwave measurements. This class handels the instrument
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
                    self.source.reset()
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
                    self.awg.reset()
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
                    self.VNA.get_start()
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

 
            
class FrequencyResponseCurrentSweep(Microwave):
    
    def run_sweep_current(self, Ic_break=None, save=None, plot=None):
        self.VNA.write('CALC:FORM SMITh')
        start = self.properties['frequency_response_current_sweep']['start']
        stop = self.properties['frequency_response_current_sweep']['stop']
        steps = self.properties['frequency_response_current_sweep']['steps']

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
                if(voltage>0.01):
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
        full_path = qf.save(self.properties, 'frequency_response_current_sweep')
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
        qf.save(self.properties, 'frequency_response_current_sweep', data_dict, 
                instrument_list = self.instrument_list)
   
    