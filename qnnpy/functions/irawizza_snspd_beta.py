# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 15:18:06 2022

@author: QNN
"""
import qnnpy.functions.functions as qf
import time
from time import sleep
import numpy as np

#ctrl+f regex note to self: self\.(?!properties|inst|isw|R_srs|liveplotter|data|device_type|device_name|sample_name)

class TriggerSweep(qf.Measurement):
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
        self.data.store(v_bias = self.properties['trigger_sweep']['bias_voltage'])
        atten_level = self.properties['trigger_sweep']['attenuation_db']

        self.inst.source.set_output(False); sleep(.2)
        self.inst.source.set_output(True)
        self.inst.source.set_voltage(0)
        sleep(.2)
        self.inst.source.set_voltage(self.data.v_bias[0])
        sleep(1)
        # self.inst.counter.set_impedance(0) #50Ohm

        counting_time = self.properties['trigger_sweep']['counting_time']
        start = self.properties['trigger_sweep']['start']
        stop = self.properties['trigger_sweep']['stop']
        step = self.properties['trigger_sweep']['step']
        count_rate = []
        atten_list = [100, atten_level]
        atten_list_bool = [True, False]
        for i in range(2):
            print('\\\\\\\\ BEAM BLOCK: %s \\\\\\\\ ' % atten_list_bool[i])
            self.inst.attenuator.set_attenuation_db(atten_list[i])
            self.inst.attenuator.set_beam_block(atten_list_bool[i])
            trigger_v, count_rate = self.inst.counter.scan_trigger_voltage(voltage_range=[start, stop],
                                                                      counting_time=counting_time,
                                                                      num_pts=int(np.floor((stop-start)/step)))
            self.data.store(trigger_v = trigger_v)
            
            # IF LIVE PLOTTER ENABLED DO SOMETHING
            
            if i == 0:
                self.data.store(counts_trigger_dark = count_rate)
            else:
                self.data.store(counts_trigger_light = count_rate)
            sleep(1)
        self.inst.attenuator.set_beam_block(True)


    def plot(self, close=True):
        ydata = [np.asarray(self.data.counts_trigger_dark,dtype=np.float32), np.asarray(self.data.counts_trigger_light,dtype=np.float32)]
        label = ['Beam block: True', 'Beam block: False'] #maybe update this to be the attenuation level

        full_path = qf.get_path(self.properties, 'trigger_sweep')
        qf.plot(self.data.trigger_v, ydata,
                title=self.sample_name+" "+self.device_type+" "+self.device_name,
                xlabel='Trigger Voltage (V)',
                ylabel='Count Rate (Hz)',
                label=label,
                y_scale='log',
                path=full_path,
                close=close)

    def save(self):
        super.save('trigger_sweep')
        

class IvSweep(qf.Measurement):
    """ Class object for iv sweeps

    Configuration: iv_sweep:
    [start: initial bias current],
    [stop: final bias current],
    [steps: number of points],
    [sweep: number of itterations],
    [full_sweep: Include both positive and negative bias],
    [series_resistance: resistance at voltage source ie R_srs]
    
    """
    def run_sweep_with_voltages(self, Isource, sweep):
        self.v_set = np.tile(Isource, sweep) * self.R_srs

        self.inst.source.set_output(True)
        sleep(1)

        for n in self.v_set:
            self.inst.source.set_voltage(n)
            sleep(.1)  #CHANGE BACK TO 0.1

            vread = self.inst.meter.read_voltage() # Voltage

            iread = (n-vread)/self.R_srs#(set voltage - read voltage)

            print('V=%.4f V, I=%.2f uA, R =%.2f' %(vread, iread*1e6, vread/iread))
            self.data.store(v_source = n, v_device=vread, i_device=iread)
            if self.liveplotter:
                self.liveplotter.plot(vread, iread, linewidth=0)

        self.v_read = self.data.v_device
        self.i_read = self.data.i_device
    
    def run_sweep_fixed(self):
        """ Runs IV sweep with config paramters
        This constructs #steps between start and 75% of final current.
        Then, #steps between 75% and 100% of final current.
        
        np.linspace()
        """
        self.inst.source.reset()
        self.inst.meter.reset()

        self.inst.source.set_output(False)

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
        self.run_sweep_with_voltages(Isource, sweep)
        
        
    def run_sweep_dynamic(self):
        """ Runs IV sweep with config paramters
        This constructs [points_coarse] between start and [percent] of final current.
        Then, [points_fine] between [percent] and 100% of final current.

        uses np.linspace()
        """
        self.inst.source.reset()
        self.inst.meter.reset()

        self.inst.source.set_output(False)

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
        self.run_sweep_with_voltages(Isource, sweep)

    def run_sweep_spacing(self):
        """ Runs IV sweep with config paramters
        This constructs [points_coarse] between start and [percent] of final current.
        Then, [points_fine] between [percent] and 100% of final current.
        
        uses np.arange()
        """
        self.inst.source.reset()
        self.inst.meter.reset()

        self.inst.source.set_output(False)

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
            
        self.run_sweep_with_voltages(Isource, sweep)

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
            switches = np.asarray(np.where(abs(np.diff(self.data.i_read)/max(np.diff(self.data.i_read))) > 0.8),dtype=int).squeeze()
            isws = abs(np.asarray([self.data.i_read[i] for i in switches]))
            print(isws)
            self.isw = isws.mean()
            print('Isw_avg = %.4f µA :--: Isw_std = %.4f µA' % (self.isw*1e6, isws.std()*1e6))
        except:
            print('Could not calculate Isw. Isw set to 0')
            self.isw = 0
    
    def plot(self):
        full_path = qf.save(self.properties, 'iv_sweep')
        qf.plot(np.array(self.data.v_read), np.array(self.data.i_read)*1e6,
                title=self.sample_name+" "+self.device_type+" "+self.device_name,
                xlabel='Voltage (mV)',
                ylabel='Current (uA)',
                path=full_path,
                show=True,
                close=True)
    
    def save(self):
        self.data.store(temp=self.properties['Temperature']['initial temp'])
        super.save('iv_sweep')
        



class TriggerSweepScope(qf.Measurement):
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

        self.inst.source.set_output(False); sleep(.2)
        self.inst.source.set_output(True)
        self.inst.source.set_voltage(0)
        sleep(.2)
        self.inst.source.set_voltage(self.v_bias)
        sleep(1)
        self.inst.counter.write(':INP:IMP 1E6') #1 MOhm input impedance
        ct_volt = self.properties['trigger_sweep']['counter_trigger_voltage']
        self.inst.counter.set_trigger(trigger_voltage=ct_volt)

        counting_time = self.properties['trigger_sweep']['counting_time']
        start = self.properties['trigger_sweep']['start']
        stop = self.properties['trigger_sweep']['stop']
        step = self.properties['trigger_sweep']['step']
        trigger_v = np.arange(start, stop, step)

        atten_list = [100, atten_level]
        atten_list_bool = [True, False]
        for a in range(2):
            print('\\\\\\\\ BEAM BLOCK: %s \\\\\\\\ ' % atten_list_bool[a])
            self.inst.attenuator.set_attenuation_db(atten_list[a])
            self.inst.attenuator.set_beam_block(atten_list_bool[a])
            counts = []
            for i in trigger_v:
                self.inst.scope.set_trigger(source=self.inst.scope_channel, volt_level=i, slope='positive')
                tv, count_rate = self.inst.counter.scan_trigger_voltage(voltage_range=[ct_volt, ct_volt],
                                                                   counting_time=counting_time,
                                                                   num_pts=1)
                counts.append(count_rate)
                sleep(1)
                print('Scope Trigger: %0.3f' %(i))
                if a==0:
                    self.data.store(trigger_v = i, counts_trigger_dark = count_rate)
                else:
                    self.data.store(trigger_v = i, counts_trigger_light = count_rate)
                if self.liveplotter:
                    self.liveplotter.plot(i, count_rate, linewidth=0)
        self.inst.attenuator.set_beam_block(True)


    def plot(self, close=True):
        ydata = [np.asarray(self.data.counts_trigger_dark,dtype=np.float32), np.asarray(self.data.counts_trigger_light,dtype=np.float32)]
        label = ['Beam block: True', 'Beam block: False'] #maybe update this to be the attenuation level
    
        full_path = qf.get_path(self.properties, 'trigger_sweep')
        qf.plot(self.data.trigger_v, ydata,
                title=self.sample_name+" "+self.device_type+" "+self.device_name,
                xlabel='Trigger Voltage (V)',
                ylabel='Count Rate (Hz)',
                label=label,
                y_scale='log',
                path=full_path,
                close=close)


    def save(self):
        self.data.store(v_bias=self.v_bias)
        super.save('trigger_sweep')
        
        data_dict = {'trigger_v':self.trigger_v,
                     'counts_trigger_dark':self.counts_trigger_dark,
                     'counts_trigger_light':self.counts_trigger_light,
                     'v_bias':self.v_bias}
        self.full_path = qf.save(self.properties, 'trigger_sweep', data_dict, 
                                 instrument_list = self.instrument_list)
