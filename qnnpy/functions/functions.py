# -*- coding: utf-8 -*-
"""
Created on Thu May  7 10:16:58 2020

@author: omedeiro
"""
from matplotlib import pyplot as plt
import yaml
import os
import logging
import datetime as dt
from datetime import datetime
import scipy.io
import re
import numpy as np
# import mariadb
import sys
from time import sleep

###############################################################################
# Plotting
###############################################################################


def plot(xdata, ydata, x_scale = 'linear', y_scale = 'linear',  
         title='', xlabel='', ylabel='',label = '', linestyle = 'o',
         path='', close=True, show=True ):
    
    
    """ 
        update to using **kwargs https://book.pythontips.com/en/latest/args_and_kwargs.html
        
        accepts arrays or lists of arrays. Scale is the same as plt.xscale(). 
        If path is specified the figure will be saved to that location. 
        Close and Show are true by default. 
        
    """

    if close:
        plt.close()


    if type(ydata) == list and type(xdata) != list:
        if label:
            for i in np.arange(0,len(ydata),1):
                plt.plot(xdata, ydata[i], linestyle ,label = label[i])
        else:
            for i in np.arange(0,len(ydata),1):
                plt.plot(xdata, ydata[i], linestyle)
                
                
    elif type(ydata) == list and type(xdata) == list:
        if label:
            for i in np.arange(0,len(ydata),1):
                plt.plot(xdata[i], ydata[i], linestyle ,label = label[i])
        else:
            for i in np.arange(0,len(ydata),1):
                plt.plot(xdata[i], ydata[i], linestyle)
    else:
        plt.plot(xdata, ydata, linestyle)
        
    plt.xscale(x_scale)
    plt.yscale(y_scale)


    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    if title:
        plt.title(title)
    if label:
        plt.legend()
    if not path=='':
        plt.savefig(path + '.png', bbox_inches='tight')
        print('File Saved:\n %s' % path)
    if show: #show should always be after save
        plt.show()
    return plt

    
def plot_new(x,y,**kwargs):
    plt.plot(x,y)
    for key, value in kwargs.items():
        plt.__dict__[key](value)
    
    return plt
###############################################################################
# Configuration
###############################################################################


def load_config(filename=None):
    
    
    """ Load config accepts the full name of a .yaml file. The sample name is 
        check for correct format (XXX123). 
        If verified, the file is loaded and the parameters are returned.  
    """
    #Check if there is a file 
    if filename is None:
        raise ValueError('Please enter filename')
        
    #Open file
    with open(filename) as f:
        parameters = yaml.load(f, Loader=yaml.FullLoader)
    
    sample_name=parameters['Save File']['sample name'] 
    check_sample_name(sample_name)
        
    # No longer accepting path location. FIXED PATH TO NETWORK
#    file_path=parameters['Save File']['filepath']
#    check_file_path(file_path)
    
    return parameters


def check_sample_name(sample_name):
    """ The sample name is required to match the XXX123 format. """
    result = re.match('^[A-Z]{3}[0-9]{3}$',sample_name)
    if not result:
        lablog_error('Invalid Sample Name. Name entered: "%s"' % sample_name)
        raise NameError('Invalid Sample Name. String must match XXX###')


def check_file_path(file_path):
    if not os.path.exists(file_path):
        try: 
            os.makedirs(file_path)
        except: 
            lablog_error('Invalid Path. Path entered: "%s"' % file_path)
            raise NameError('Invalid Path')
                

###############################################################################
# Saving
###############################################################################   
            
                            
def save(parameters, measurement, data_dict={}, instrument_list=None, db=False, meas_txt=None):
    """ Save follows the typical format of defining a data dictionary (data_dict) and saving as a .mat . 
        This function requires prameters from a loaded config file. The file is saved on the S:\ drive according to the configuration settings. 
        If the data_dict is not included this function returns the path created from the configuration file. 
        
    """
    if type(parameters) != dict:
        raise ValueError('save accepts dict from configured .yml file')
        

    file_path = 'S:\SC\Measurements'
    #Setup variables from parameters for file path
    user = parameters['User']['name']
    sample_name = parameters['Save File']['sample name'] #this field should describe the material SPX111 or GaN_ID#20
    device_name = parameters['Save File']['device name'] #this field should describe which device is being tested
    device_type = parameters['Save File']['device type'] #this field should describe device type ntron, snspd, coupler, memory
    
    if parameters['Save File'].get('port'):
        device_type_ext = device_type + "_" + parameters['Save File']['port']
        port = parameters['Save File']['port']
    else:
        device_type_ext = device_type
        port = 1
        
    time_str = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            
    ''' Shorten parameter list to only include current measurement and the instruments used'''
    if instrument_list:
        new_parameters = {}
        new_parameters['User'] = parameters['User']
        new_parameters['Save File'] = parameters['Save File']
        new_parameters[measurement] = parameters[measurement]
        for i in range(len(instrument_list)):
            new_parameters[instrument_list[i]] = parameters[instrument_list[i]]
        parameters = new_parameters
        
    ''' Create folder and save .mat file. '''
    while os.path.exists(file_path):
        if meas_txt:
            measurement_alt = measurement+meas_txt
        else:
            measurement_alt = measurement
                
        file_name = sample_name +"_"+measurement_alt+"_"+ device_type_ext +"_"+ device_name +"_"+time_str 
        file_path = os.path.join(file_path, sample_name, device_type, device_name, measurement)
        os.makedirs(file_path, exist_ok=True)
        full_path = os.path.join(file_path, file_name)
        if data_dict:
            scipy.io.savemat(full_path + '.mat', mdict=data_dict)
            output_log(parameters, full_path)
            print('File Saved:\n %s' % full_path)
            try:
                insert_measurement_event(user, measurement, sample_name, device_type, device_name, port)
            except:
                print('Logging to qnndb failed.')
                
            
        break

    
    return full_path




###########################################################################
#Loggging
###########################################################################

def insert_measurement_event(user, meas_type, sample_name, device_type, device_id, port=1):
    '''
    
    '''
    try:
        conn = mariadb.connect(host= "18.25.16.44", 
                                    user= "omedeiro", 
                                    port= 3307, 
                                    password= 'vQ7-om(PKh', 
                                    database= 'qnndb' )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    
    
    # Get Cursor
    cur = conn.cursor()
    
    sql = "INSERT INTO `measurement_events` (`user`, `meas_type`, `sample_name`, `device_type`, `device_id`, `port`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (user, meas_type, sample_name, device_type, device_id, port)
    cur.execute(sql)
    conn.commit()
    return cur
    
def lablog_error(message):
    """
    The lablog method logs errors to 'S:\SC\ErrorLogging'
    """
    # formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    # log = logging.getLogger('lablog')
    # if not log.handlers:
    #     handler = logging.FileHandler('S:\SC\Logging\qnn-lablog.log')        
    #     handler.setFormatter(formatter)    
        
    #     log.setLevel(logging.ERROR)        
    #     log.addHandler(handler)
    #     log.propagate = False
        
    # log.error(message)
    
    timestamp = str(datetime.now())+" "
    path = r'S:\SC\ErrorLogging\lablog_error.txt'
    file = open(path,'a')
    
    file.write(timestamp + message + " \n")
    file.close()


def lablog_measurement(parameters, measurement=None):
    """
    The lablog_measurement method logs the measurement history within the lab. 
    
    """
    if type(parameters) != dict:
        raise ValueError('log_measurement accepts dictionary from configured .yml file')
    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    lab_measurement_log = logging.getLogger('lab_measurement_log')
    if not lab_measurement_log.handlers:
        handler = logging.FileHandler('S:\SC\MeasurementLogging\qnn-lablog-measurement.log')        
        handler.setFormatter(formatter)     
        
        lab_measurement_log.setLevel(logging.INFO)        
        lab_measurement_log.addHandler(handler)
        lab_measurement_log.propagate = False
        
    if measurement:
        parameters['Save File']['measurement'] = measurement
    lab_measurement_log.info(parameters)

    
def output_log(parameters, path):
    """
    The output_log method logs the configuration file used for each measurement
    to the file location where that measurement is saved. 
    
    """
    # formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # output_log = logging.getLogger('output_log')
    # formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    # handler = logging.FileHandler(path+'.txt')        
    # handler.setFormatter(formatter)
    
    # output_log.setLevel(logging.INFO)
    # output_log.addHandler(handler)

    # output_log.info(parameters)

    file = open(path+'.txt', "w")
    file.write("\n".join("{}\t\t{}".format(k, v) for k, v in parameters.items()))
    file.close()

###########################################################################
#Measurement
###########################################################################



def ice_get_temp(select=None):
    """Access ICE log to return lakeshore 336 temperature. 
    
    If the optional input 'select' is specified (as an int between 0-4)
    the dictionary index is returned. Else all of the 
    values are returned as a dictionary.
    
    data_dict = {'date1':date1,
                   'temp1':temp1,
                   'temp2':temp2,
                   'temp3':temp3,
                   'temp4':temp4}
    
    """
    now = datetime.now()
    while not os.path.exists(r'S:\SC\InstrumentLogging\Cryogenics\Ice\ice-log\Results\%s' % str(now)[:10]):
        sleep(1)
        
    f=r'S:\SC\InstrumentLogging\Cryogenics\Ice\ice-log\Results\%s\%s' % (str(now)[:10], str(now)[:10])+".log"
    
    with open(f) as f: # Get txt from log file and split the last (most recent) entry        
        last = f.readlines()[-1].split(',')
        
        then = datetime.strptime(last[0]+" "+last[1], '%m/%d/%Y %I:%M:%S %p')
        
        if now-then>dt.timedelta(minutes=1):
            temp1 = ''
            print('TEMPERATURE: ICE Logging is off')
        else:
            date1 = last[3]
            temp1 = float(last[4]) # A
            temp2 = float(last[5]) 
            temp3 = float(last[6])
            temp4 = float(last[7])
    
    data_dict = {'date1':date1,
                   'temp1':temp1,
                   'temp2':temp2,
                   'temp3':temp3,
                   'temp4':temp4}
    data_list = [date1,temp1,temp2,temp3,temp4]
    if select:
        select_temp = data_list[select]
        return select_temp
    else:
        return data_dict

#######################################################################
        #       General function for setting up instruments
#######################################################################
class Instruments:
    def __init__(self, properties):
        self.instrument_list: list[str] = []
        self.__instrument_dict: dict[str,object] = {}
        
        #instantiates variables, prevents crashes if an instrument which is not specified in the config is attempted to be used
        self.attenuator: object = None
        self.counter: object = None
        self.scope: object = None
        self.scope1: object = None # note: supposedly used for multiple of the same instrument
        self.meter: object = None
        self.source: object = None
        self.awg: object = None
        self.VNA: object = None
        self.temp: object = None
        
        # Attenuator
        if properties.get('Attenuator'):
            self.instrument_list.append('Attenuator')
    
            if properties['Attenuator']['name'] == 'JDSHA9':
                from qnnpy.instruments.jds_ha9 import JDSHA9
                try:
                    self.attenuator = JDSHA9(properties['Attenuator']['port'])
                    self.attenuator.set_beam_block(True)
                    print('ATTENUATOR: connected')
                except:
                    print('ATTENUATOR: failed to connect')
            else:
                raise NameError('Invalid Attenuator. Attenuator name is not configured')
        
        # Counter
        if properties.get('Counter'):
            self.instrument_list.append('Counter')
            if properties['Counter']['name']:
                if properties['Counter']['name'] == 'Agilent53131a':
                    from qnnpy.instruments.agilent_53131a import Agilent53131a
                    try:
                        self.counter = Agilent53131a(properties['Counter']['port'])
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
                    raise NameError('Invalid counter. Counter name is not '\
                                    'configured')
        
        # Scope
        if properties.get('Scope'):
            self.instrument_list.append('Scope')
    
            if properties['Scope']['name'] == 'LeCroy620Zi':
                from qnnpy.instruments.lecroy_620zi import LeCroy620Zi
                try:
                    self.scope = LeCroy620Zi("TCPIP::%s::INSTR" % properties['Scope']['port'])
                    # self.scope_channel = properties['Scope']['channel']
                    print('SCOPE: connected')
                except:
                    print('SCOPE: failed to connect')
            else:
                raise NameError('Invalid Scope. Scope name is not configured')
    
            if properties.get('Scope1'):
                if properties['Scope1']['name'] == 'LeCroy620Zi':
                    from qnnpy.instruments.lecroy_620zi import LeCroy620Zi
                    try:
                        self.scope1 = LeCroy620Zi("TCPIP::%s::INSTR" % properties['Scope1']['port'])
                        # self.scope_channel = properties['Scope']['channel']
                        print('SCOPE: connected')
                    except:
                        print('SCOPE: failed to connect')
                else:
                    raise NameError('Invalid Scope. Scope name is not configured')
                
        # Meter
        if properties.get('Meter'):
            self.instrument_list.append('Meter')
    
            if properties['Meter']['name'] == 'Keithley2700':
                from qnnpy.instruments.keithley_2700 import Keithley2700
                try:
                    self.meter = Keithley2700(properties['Meter']['port'])
                    self.meter.reset()
                    print('METER: connected')
                except:
                    print('METER: failed to connect')
    
            elif properties['Meter']['name'] == 'Keithley2400':
                # this is a source meter
                from qnnpy.instruments.keithley_2400 import Keithley2400
                try:
                    self.meter = Keithley2400(properties['Meter']['port'])
                    self.meter.reset()
                    print('METER: connected')
                except:
                    print('METER: failed to connect')
    
            elif properties['Meter']['name'] == 'Keithley2001':
                from qnnpy.instruments.keithley_2001 import Keithley2001
                try:
                    self.meter = Keithley2001(properties['Meter']['port'])
                    self.meter.reset()
                    print('METER: connected')
                except:
                    print('METER: failed to connect')
            else:
                raise NameError('Invalid Meter. Meter name: "%s" is not configured' % properties['Meter']['name'])
            
    
        # Source
        if properties.get('Source'):
            self.instrument_list.append('Source')
    
            if properties['Source']['name'] == 'SIM928':
                from qnnpy.instruments.srs_sim928 import SIM928
                try:
                    self.source = SIM928(properties['Source']['port'], properties['Source']['port_alt'])
                    self.source.reset()
                    
                    try:
                        properties.get('Source')['port_alt2']
                        self.source2 = SIM928(properties['Source']['port'], properties['Source']['port_alt2'])
                    except:
                        print('No second SRS specified')
                    
                    print('SOURCE: connected')
                except:
                    print('SOURCE: failed to connect')
            elif properties['Source']['name'] == 'YokogawaGS200':
               from qnnpy.instruments.yokogawa_gs200 import YokogawaGS200
               try:
                   self.source = YokogawaGS200(properties['Source']['port'])
                   # self.source.reset()
                   self.source.set_output(False)
                   self.source.set_voltage_range(5)
                   print('SOURCE: connected')
               except:
                   print('SOURCE: failed to connect')
            elif properties['Source']['name'] == 'Keithley2400':
                from qnnpy.instruments.keithley_2400 import Keithley2400
                try:
                    self.source = Keithley2400(properties['Source']['port'])
                    self.source.reset()
                    print('SOURCE: connected')
                except:
                    print('SOURCE: failed to connect')
            else:
                raise NameError('Invalid Source. Source name: "%s" is not configured' % properties['Source']['name'])
            
    
        # AWG
        if properties.get('AWG'):
            self.instrument_list.append('AWG')
    
            if properties['AWG']['name'] == 'Agilent33250a':
                from qnnpy.instruments.agilent_33250a import Agilent33250a
                try:
                    self.awg = Agilent33250a(properties['AWG']['port'])
                    self.awg.beep()
                    print('AWG: connected')
                except:
                    print('AWG: failed to connect')
            else:
                raise NameError('Invalid AWG. AWG name: "%s" is not configured' % properties['AWG']['name'])
            
        
        # VNA
        if properties.get('VNA'):
            self.instrument_list.append('VNA')
    
            if properties['VNA']['name'] == 'KeysightN5224a':
                from qnnpy.instruments.keysight_n5224a import KeysightN5224a
                try:
                    self.VNA = KeysightN5224a(properties['VNA']['port'])
                    # self.VNA.reset()
                    print('VNA: connected')
                except:
                    print('VNA: failed to connect')
            else:
                raise NameError('Invalid VNA. VNA name: "%s" is not configured' % properties['VNA']['name'])
        
        # Temperature Controller
        if properties.get('Temperature'):
            self.instrument_list.append('Temperature')
    
            if properties['Temperature']['name'] == 'Cryocon350':
                from qnnpy.instruments.cryocon350 import Cryocon350
                try:
                    self.temp = Cryocon350(properties['Temperature']['port'])
                    self.temp.channel = properties['Temperature']['channel']
                    properties['Temperature']['initial temp'] = self.temp.read_temp(self.temp.channel)
                    print('TEMPERATURE: connected | '+str(properties['Temperature']['initial temp']))
                except:
                    print('TEMPERATURE: failed to connect')
    
            elif properties['Temperature']['name'] == 'Cryocon34':
                from qnnpy.instruments.cryocon34 import Cryocon34
                try:
                    self.temp = Cryocon34(properties['Temperature']['port'])
                    self.temp.channel = properties['Temperature']['channel']
                    properties['Temperature']['initial temp'] = self.temp.read_temp(self.temp.channel)
                    print('TEMPERATURE: connected | '+str(properties['Temperature']['initial temp']))
                except:
                    print('TEMPERATURE: failed to connect')
    
            elif properties['Temperature']['name'] == 'ICE':
                try:
                    properties['Temperature']['initial temp'] = ice_get_temp(select=1)
                    print('TEMPERATURE: connected' + ice_get_temp(select=1))
                except:
                    print('TEMPERATURE: failed to connect')
                    
            elif properties['Temperature']['name'] == 'DEWAR':
                try:
                    properties['Temperature']['initial temp'] = 4.2
                    print('TEMPERATURE: ~connected~ 4.2K')
                except:
                    print('TEMPERATURE: failed to connect')
    
            else:
                raise NameError('Invalid Temperature Controller. TEMP name: "%s" is not configured' % properties['Temperature']['name'])
        else:
            properties['Temperature'] = {'initial temp': 'None'}
            
        #just in case you want to access instruments using a string rather than the variable itself
        self.__instrument_dict['ATTENUATOR'] = self.attenuator
        self.__instrument_dict["COUNTER"] = self.counter
        self.__instrument_dict["SCOPE"] = self.scope
        self.__instrument_dict["SCOPE1"] = self.scope1 
        self.__instrument_dict["METER"] = self.meter
        self.__instrument_dict["SOURCE"] = self.source
        self.__instrument_dict["AWG"] = self.awg
        self.__instrument_dict["VNA"] = self.VNA
        self.__instrument_dict["TEMPERATURE"] = self.temp
        self.__instrument_dict["TEMP"] = self.temp
        
    def get_instrument(self, instrument_type: str) -> object:
        return self.__instrument_dict.get(instrument_type)
        
