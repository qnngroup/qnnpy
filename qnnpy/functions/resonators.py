import qnnpy.functions.functions as qf
import numpy as np

# note: instrument libraries are imported within the class as needed from config file

class Resonators():
    '''
    class for measuring superconducting resonators
    '''
    def __init__(self, config_file):
        # Load config file
        self.properties = qf.load_config(config_file)

        self.sample_name = self.properties['Save File']['sample name']
        self.device_name = self.properties['Save File']['device name']
        self.device_type = self.properties['Save File']['device type']

        self.instrument_list = []

        # Set up instruments
        if self.properties.get('PNA'):
            self.instrument_list.append('PNA')

            if self.properties['PNA']['name'] == 'KeysightN5224a':
                from qnnpy.instruments.keysight_n5224a import KeysightN5224a
                try:
                    self.pna = KeysightN5224a(self.properties['PNA']['port'])
                    self.pna.set_power(0)
                    print('PNA: connected')
                except:
                    print('PNA: failed to connect')
            else:
                qf.lablog('Invalid PNA. PNA name: "%s" is not'\
                    'configured' % self.properties['PNA']['name'])
                raise NameError('Invalide PNA. PNA name is not configured')

    def configure_pna(self, start_freq, stop_freq, num_points, power=0, if_bandwidth=100):
        self.pna.reset(measurement='S21', if_bandwidth = 20, start_freq = 200E6,
            stop_freq = 20E9, power = -40)
        
        self.pna.set_start(start_freq)
        self.pna.set_stop(stop_freq)
        self.pna.set_points(num_points)
        self.pna.set_if_bw(if_bandwidth)
        self.pna.set_power(power)

    def S21_measurement(self, start_freq, stop_freq, num_points, power=0, if_bandwidth=100):
        '''
        measure the S21 data on a superconducting resonator using a VNA
        start_freq, stop_freq = start/end points of frequency sweep (Hz)
        num_points = number of points in frequenyc sweep
        if_bandwidth = if_bandwidth (Hz)
        power = output power of VNA (dBm)

        class stores the measured source attenuation, the frequency points
        swept over, and resulting S21 values
        '''
        self.configure_pna(start_freq, stop_freq, num_points, power, if_bandwidth)

        self.f, self.S21 = self.pna.single_sweep()
        self.att = self.pna.get_source_attenuation()

    def phase_measurement(self, start_freq, stop_freq, num_points, power=0, if_bandwidth=100):
        self.configure_pna(start_freq, stop_freq, num_points, power, if_bandwidth)

        self.f, self.phase = self.pna.single_sweep_phase()
        self.att = self.pna.get_source_attenuation()

    def power_characterization(self, start_freq, stop_freq, num_points, powers, if_bandwidth=100):
        for power in powers:
            self.run_S21_measurement(start_freq, stop_freq, num_points, power, if_bandwidth)
            self.save()
            self.plot()

    def S21_to_dBm(self):
        return 20*np.log10(np.abs(self.S21))

    def plot(self, close=True):
        full_path = qf.save(self.properties, 'S21_meas')
        qf.plot(self.f, self.S21_to_dBm(),
                title=self.sample_name+' '+self.device_type+' '+self.device_name+' '+self.get_power()+'dB',
                xlabel='Frequency (Hz)',
                ylabel='S21 (dBm)',
                path=full_path,
                close=close)
    
    def save(self):
        data_dict = {'S21':self.S21_to_dBm(), 'pna_power':self.get_power(), 
                'f':self.f, 'pna_att':self.att}
        self.full_path = qf.save(self.properties, 'S21_meas', data_dict,
                    instrument_list = self.instrument_list)