# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 17:42:10 2020

@author: omedeiro
"""
import qnnpy.functions.functions as qf
import time
from time import sleep
import numpy as np



class nTron:
    """ Class for nTron measurement. This class handels the instrument
    configuration, measurement, plotting, logging, and saving.
    """
    def __init__(self, configuration_file):
        
        #######################################################################
        #       Load .yaml configuraiton file
        #######################################################################

        # qf is a package of base functions that can be used in any class.
        self.properties = qf.load_config(configuration_file)
    
        self.sample_name = self.properties['Save File']['sample name']
        self.device_name = self.properties['Save File']['device name']
        self.device_type = self.properties['Save File']['device type']
        

        self.isw = 0
        self.instrument_list = []
        
        self.R_srs = self.properties['iv_sweep']['series_resistance']
        self.R_srs_g = self.properties['iv_sweep']['series_resistance_g']

        # Scope
        if self.properties.get('Scope'):
            self.instrument_list.append('Scope')

            if self.properties['Scope']['name'] == 'LeCroy620Zi':
                from qnnpy.instruments.lecroy_620zi import LeCroy620Zi
                try:
                    self.scope = LeCroy620Zi("TCPIP::%s::INSTR" % self.properties['Scope']['port'])
                    # self.scope_channel = self.properties['Scope']['channel']
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
                    
                    try:
                        self.properties.get('Source')['port_alt2']
                        self.source2 = SIM928(self.properties['Source']['port'], self.properties['Source']['port_alt2'])
                    except:
                        print('No second SRS specified')
                    
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
            
            
    def voltage2current(self, V, attenuation, R=50):
        V = V*10**(attenuation/20)
        I = V/R
        return I
    
    def current2voltage(self, I, attenuation, R=50):
        V = I*R
        V = V/10**(attenuation/20)
        return V

        

class IvSweep(nTron):
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
        if self.properties['Save File'].get('port'):
            qf.plot(np.array(self.v_read), np.array(self.i_read)*1e6,
                title=self.sample_name+" "+self.device_type+" "+self.device_name+" "+self.properties['Save File']['port'],
                xlabel='Voltage (mV)',
                ylabel='Current (uA)',
                path=full_path,
                show=True,
                close=True)
        else:
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



class DoubleSweep(nTron):
    """ Class object for iv sweeps

    Configuration: iv_sweep:
    [start: initial bias current],
    [stop: final bias current],
    [steps: number of points],
    [sweep: number of itterations],
    [full_sweep: Include both positive and negative bias],
    [series_resistance: resistance at voltage source ie R_srs]
    
    """
    def run_sweep(self):
        """ Runs IV sweep with config paramters
        This constructs #steps between start and 75% of final current.
        Then, #steps between 75% and 100% of final current.
        

        """
        self.source.reset()
        self.meter.reset()

        self.source.set_output(False)
        self.source2.set_output(False)

        start = self.properties['double_sweep']['start']
        stop = self.properties['double_sweep']['stop']
        steps = self.properties['double_sweep']['steps']
        sweep = self.properties['double_sweep']['sweep']
        Ig_start = self.properties['double_sweep']['Ig_start']
        Ig_stop = self.properties['double_sweep']['Ig_stop']
        Ig_steps = self.properties['double_sweep']['Ig_steps']
        
        
        # To select full (positive and negative) trace or half trace
        full_sweep = self.properties['double_sweep']['full_sweep']
        Isource1 = np.linspace(start, stop, steps) #Coarse
        #Isource2 = np.linspace(stop*0.75, stop, steps) #Fine

        Isource_Ig = np.linspace(Ig_start, Ig_stop, Ig_steps)

        if full_sweep == True:
            Isource = np.concatenate([Isource1, Isource1[::-1]])
            Isource = np.concatenate([Isource, -Isource])
        else:
            Isource = Isource1
        self.v_set = np.tile(Isource, sweep) * self.R_srs
        self.v_set_g = np.tile(Isource_Ig, sweep) * self.R_srs_g

        self.source.set_output(True)
        self.source2.set_output(True)
        sleep(1)
        self.v_list = []
        self.i_list = []

        self.ig_list = []
        for m in self.v_set_g:
            voltage = []
            current = []
            self.source2.set_voltage(m)
            sleep(0.1)
            for n in self.v_set:
                self.source.set_voltage(n)
                sleep(0.1)
    
                vread = self.meter.read_voltage() # Voltage
    
                iread = (n-vread)/self.R_srs#(set voltage - read voltage)
    
                print('Vd=%.4f V, Id=%.2f uA, Ig=%.2f uA, R =%.2f' %(vread, iread*1e6, m*1e6/self.R_srs_g, vread/iread))
                voltage.append(vread)
                current.append(iread)
    
            
            self.v_list.append(np.asarray(voltage, dtype=np.float32))
            self.i_list.append(np.asarray(current, dtype=np.float32))
            self.ig_list.append(m/self.R_srs)
            
            
            
        
        
        
    def plot(self):
        full_path = qf.save(self.properties, 'double_sweep')
        qf.plot(self.v_list, self.i_list,
                title=self.sample_name+" "+self.device_type+" "+self.device_name,
                xlabel='Voltage (V)',
                ylabel='Current (A)',
                label = self.ig_list,
                path=full_path,
                show=True,
                close=True)

    def save(self):

        #Set up data dictionary

        data_dict = {'V_source': self.v_set,
                 'V_device': self.v_list,
                 'I_device': self.i_list,
                 'I_gate': self.ig_list,
                 'R_srs': self.R_srs,
                 'temp': self.properties['Temperature']['initial temp']}


        self.full_path = qf.save(self.properties, 'double_sweep', data_dict, 
                                 instrument_list = self.instrument_list)


class DoubleSweepScope(nTron):
    """ use awg and scope to aquire Ic distributions.  
        Awg settings and scope settings are not currently programmed.
    
    """
    def run_sweep(self):
        'runs the sweep'
        
        self.source.reset()
        self.source.set_output(False)
        self.R_srs = self.properties['double_sweep_scope']['series_resistance_srs']
        start = self.properties['double_sweep_scope']['start']
        stop = self.properties['double_sweep_scope']['stop']
        steps = self.properties['double_sweep_scope']['steps']
        sweep = self.properties['double_sweep_scope']['sweep']
        
        trace_signal = self.properties['double_sweep_scope']['trace_signal']
        trace_trigger = self.properties['double_sweep_scope']['trace_trigger']
        trace_hist = self.properties['double_sweep_scope']['trace_hist']

        Isource = np.linspace(start, stop, steps) 

        self.v_set = np.tile(Isource, sweep) * self.R_srs
        
        
        
        
        for i in self.v_set:
            self.source.set_voltage(i)
            self.source.set_output(True)
            print('Voltage:%0.2f ' % i)
            sleep(0.1)
            
            self.scope.set_trigger_mode(trigger_mode = 'Stop')
            self.scope.math_histogram_clear_sweeps()
            
            self.data_dict = self.scope.save_traces_multiple_sequence(
                channels = [trace_signal, trace_trigger], 
                num_traces = 1, 
                NumSegments = 1000)
            hist = self.scope.get_wf_data(trace_hist)
            self.data_dict['hist'] = hist
            self.data_dict['i_bias'] = i/self.R_srs
            
            self.full_path = qf.save(self.properties, 'double_sweep_scope', self.data_dict, 
                                     instrument_list = self.instrument_list)
            self.scope.save_screenshot(file_name=self.full_path+'.png', white_background=False)
            
        self.scope.set_segments(2)
        

        


    
class PulseTraceCurrentSweep(nTron):
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
                x, y = self.source.get_single_trace(channel='C2')
                snspd_traces_x.append(x);  snspd_traces_y.append(y)
                x, y = self.source.get_single_trace(channel='C3')
                pd_traces_x.append(x);  pd_traces_y.append(y)

            snspd_traces_x_list.append(snspd_traces_x)
            snspd_traces_y_list.append(snspd_traces_y)
            pd_traces_x_list.append(pd_traces_x)
            pd_traces_y_list.append(pd_traces_y)
            
            
    def save(self):
        """ write"""