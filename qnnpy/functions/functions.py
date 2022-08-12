# -*- coding: utf-8 -*-
"""
Created on Thu May  7 10:16:58 2020

@author: omedeiro
"""
from matplotlib import pyplot as plt
import matplotlib.animation as animation
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
import time

import csv

from typing import List

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

# Requires IPython for interactive shell
class LivePlotter:
    """
        Automatically updating plotter
        Requires IPython to be enabled for interactive shell
        Simpily call plot(x, y) and the plot will add your points live
        Once you're done, you can save by calling save()
    """
    #data: dict[str, (list[float],list[float],list[float])]
    data: dict
    #__subplots: dict[str, plt.Subplot]
    def __init__(self, *, title: str ='', xlabel: str ='', ylabel: str='', legend: bool=False, legend_loc: str = 'best', max_len: int = -1):
        self.data={}
        if not plt.isinteractive():
            plt.ion()
        self.fig, self.ax = plt.subplots()
        #self.__subplots = {}
        #self.start_time: float = 0
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        self.show_legend: bool=legend
        self.legend_loc: str = legend_loc
        self.max_len = max_len
        self.def_col_idx = 0
        self.colors = ['r','g','b','c','m','y','k']
        # plt.xlim(0,1)
        # plt.ylim(0,1)
        plt.draw()
        
    def plot(self, x: float, y: float, label: str = '', *, linestyle='solid',color=None,marker='o',linewidth=3,markercolor=None):
        #if self.start_time == 0:
            #self.start_time = time.time()
        if markercolor==None:
            markercolor=color
        if self.data.get(label)==None:
            self.data[label]=([x],[y],self.colors[self.def_col_idx])
            self.def_col_idx+=1
            #self.data[label]=([x],[y],[time.time()-self.start_time])
        else:
            self.data[label][0].append(x)
            self.data[label][1].append(y)
            if color==None:
                color = self.data[label][2]
            if self.max_len>1 and len(self.data[label][0])>self.max_len:
                self.data[label][0].pop(0)
                self.data[label][1].pop(0)
            #self.data[label][2].append(time.time()-self.start_time)
        if len(self.ax.lines)>=len(self.data):
            self.ax.lines.pop(0) # beware memory leaks and other shenanagins 
        self.ax.plot(self.data[label][0],self.data[label][1],label=label,linestyle=linestyle,color=color,marker=marker,linewidth=linewidth,markerfacecolor=markercolor,markeredgecolor=markercolor)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        if self.show_legend: self.ax.legend(loc = self.legend_loc)
    
    def save(self, path:str=None, name:str=None, file_type:str = 'jpg'):
        if path!=None:
            if '.' in path:
                temp = path.rsplit(os.sep,1)
                path = temp[0]
                if name==None: name = temp[1]
            if not os.path.exists(path):
                os.makedirs(path)
            sys.path.append(path)
        if name==None:
            name: str = time.strftime(f"plot_%Y-%m-%d_%H-%M-%S.{file_type}", time.localtime())
        elif not '.' in name:
            name = f"{name}.{file_type}"
        self.fig.savefig(f"{path}{os.sep}{name}")
        



###############################################################################
# Configuration
###############################################################################


def load_config(filename=None):
    
    
    """ Load config accepts the full name of a .yaml file. The sample name is 
        check for correct format (XXX123). 
        If verified, the file is loaded and the parameters are returned.  
    """
    #Check if there is a file 
    parameters={}
    if filename is None:
        raise ValueError('Please enter filename')
        
    #Open file
    with open(filename) as f:
        parameters = yaml.load(f, Loader=yaml.FullLoader)
    
    if parameters.get('Save File'):
        if parameters.get('Save File').get('sample name'):
            sample_name=parameters['Save File']['sample name']
            check_sample_name(sample_name)
        elif parameters.get('Save File').get('sample name 1'):
            for i in range(5):
                if parameters['Save File'].get(f"sample name {i+1}") == None: break
                check_sample_name(parameters['Save File'][f"sample name {i+1}"])
    
        
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

#save as save but uses data instruments and liveplotter class
def data_saver(parameters: dict, measurement: str, meas_path: str = r'S:\SC\Measurements', data = None, inst = None, plot = None, file_name_append: str = ""):
    """

    Parameters
    ----------
    parameters : dict
        parameters from loaded yaml config file.
    measurement : str
        name of the measurement: ie, iv_sweep.
    meas_path : str, optional
        root folder location for measurements to be saved to. The default is r'S:\SC\Measurements'.
    data : Data or List[Data], optional
        data class to save. The default is None.
        if a list is provided, then iteratively saves each element seperately. If multiple samples are defined in parameters, each iterative save will use the next sample
    inst : Instruments, optional
        instruments that were used. The default is None.
    plot : LivePlotter or List[LivePlotter], optional
        optionally save the live plotter which was used. The default is None.
        if a list is provided, does the same thing as data if data is a list
    Raises
    ------
    ValueError
        if there is an error in parameters.

    Returns
    -------
    full_path : str or list[str]
        full path of where data was saved.
        if multiple samples are used, an array of paths for each sample save location is given back

    """
    # for saving multiple samples
    if parameters.get('Save File') and parameters.get('Save File').get('sample name') == None:
        res: list = []
        for i in range(4): #maximum of 4 samples can be saved at a time
            if parameters['Save File'].get(f"sample name {i+1}") == None: break
            d = data[i%len(data)] if type(data) == list else data
            p = plot[i%len(plot)] if type(plot) == list else plot
            parameters['Save File'] = {} if parameters.get('Save File')==None else parameters['Save File']
            parameters['Save File']['sample name']=parameters['Save File'][f"sample name {i+1}"] if parameters['Save File'].get(f'sample name {i+1}') else parameters.get('Save File').get('sample name') if parameters.get('Save File').get('sample name') else ""
            res.append(data_saver(parameters, measurement, meas_path, data=d, inst=inst, plot=p, file_name_append=str(i)))
        return res
    if type(data) == list or type(plot)==list:
        res: list = []
        for i in range(max(len(data), len(plot))):
            d = data[i%len(data)] if type(data) == list else data
            p = plot[i%len(plot)] if type(plot) == list else plot
            res.append(data_saver(parameters,measurement, meas_path, data=d, inst=inst, plot=p, file_name_append = str(i)))
        return res
    #ensure parameters is dict
    if type(parameters) != dict:
        try:
            parameters = load_config(parameters)
        except:
            raise ValueError('save accepts dict from configured .yml file, try using load_config(parameters) first!')
    file_path = meas_path
    #Setup variables from parameters for file path
    user = parameters['User']['name'] if parameters.get('User') and parameters.get('User').get('name') else ""
    if parameters.get('Save File'):
        sample_name = parameters['Save File']['sample name'] if parameters.get('Save File').get('sample name') else "" #this field should describe the material SPX111 or GaN_ID#20
        device_name = parameters['Save File']['device name'] if parameters.get('Save File').get('device name') else "" #this field should describe which device is being tested
        device_type = parameters['Save File']['device type'] if parameters.get('Save File').get('device type') else "" #this field should describe device type ntron, snspd, coupler, memory
    else:
        sample_name, device_name, device_type = "", "", ""
    if parameters['Save File'].get('port'):
        device_type_ext = device_type + "_" + f"port{parameters['Save File']['port']}"
        port = parameters['Save File']['port']
    else:
        device_type_ext = device_type
        port = 1
    # Shorten parameter list to only include current measurement and the instruments used
    if inst and len(inst.instrument_list)>0:
        new_parameters = {'User': parameters.get('User'), 'Save File': parameters.get('Save File'), 'Measurement': parameters.get(measurement)}
        new_parameters = {key: parameters[key] for key in inst.instrument_list}
        # for i in range(len(inst.instrument_list)):
        #     new_parameters[inst.instrument_list[i]] = parameters[inst.instrument_list[i]]
        parameters = new_parameters
    # Create folder and save .mat file
    full_path=file_path
    if os.path.exists(file_path):
        # if meas_txt:
        #     measurement_alt = measurement+meas_txt
        # else:
        #     measurement_alt = measurement
        # makes file path
        time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        file_name = sample_name +"_"+measurement+"_"+ device_type_ext +"_"+ device_name +"_"+time_str+ (f"_({file_name_append})" if file_name_append != "" else "")
        file_path = os.path.join(file_path, sample_name, device_type, device_name, measurement)
        os.makedirs(file_path, exist_ok=True)
        full_path = os.path.join(file_path, file_name)
        if data:
            # scipy.io.savemat(full_path + '.mat', mdict=data.data)
            data.save(path=f"{full_path}.mat")
            output_log(parameters, full_path)
            print('File Saved:\n %s' % full_path)
            # saving to database
            try:
                insert_measurement_event(user, measurement, sample_name, device_type, device_name, port)
            except:
                print('Logging to qnndb failed.')
        if plot:
            plot.save(path=f"{full_path}.png")
    else:
        print("\033[1;31;49mmeas_path does not exist, forcing a save elsewhere: \033[1;37;49m")
        data.save(printloc=True)
        plot.save(name="forced_plot_save")
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
        #       Code testing
#######################################################################



def mock_builder(class_to_mock) -> object:
    """
    Cool class mocking method
    Takes in a class (ie: mock_builder(float)), returns a new instance 
    of that class (ie: Mockfloat), with mock versions of the original's 
    methods that print out when the method is called

    Parameters
    ----------
    class_to_mock : CLASS
        Class that you want to make a mock version of, such as for testing

    Returns
    -------
    Object
        Mock instance of the inputted class.

    """
    method_list: List[str] = [func for func in dir(class_to_mock) if callable(getattr(class_to_mock, func))]
    gen_code: str = f"class Mock{class_to_mock.__name__}:"
    for m in method_list:
        if not(m.startswith('__') and not m=='__init__'):
            gen_code += f"\n\tdef {m}(*placeholder):\n\t\tprint('\033[1;33;49mMocking: \033[1;36;49mcalled \033[1;35;49m{m}()\033[1;36;49m in \033[0;35;49mMock{class_to_mock.__name__}\033[1;37;49m')\n\t\treturn None"
    exec(gen_code)
    return eval(f"Mock{class_to_mock.__name__}")

#######################################################################
        #       Instrument Setup
#######################################################################
class Instruments:
    """
    Instruments general setup now supports using multiple of the same instrument. 
    Currently duplicate instruments are created by naming the instrument in the 
    yaml file as Source1, Source2... and are accessed using instruments(or whatever 
    you named your Instruments variable).source1, instuments.source2... If you don't 
    postfix your yaml instrument type with a number, it's assumed that only one
    of that instrument is used, and that instrument is accessed normally using 
    inst.source (without number).

    """
    attenuator = None
    counter = None
    scope = None
    meter = None
    source = None
    awg = None
    VNA = None
    temp = None
    def __init__(self, properties: dict):
        self.instrument_list: List[str] = []
        
        # Attenuator
        if properties.get('Attenuator'):
            self.attenuator_setup(properties)
        elif properties.get('Attenuator1'):
            for i in range(1,100): #if you're using 100 or more attenuators then maybe don't use 100 attenuators? idk man
                if properties.get(f'Attenuator{i}'):
                    self.attenuator_setup(properties,i)
                else: 
                    break
        
        # Counter
        if properties.get('Counter'):
            self.counter_setup(properties)
        elif properties.get('Counter1'):
            for i in range(1,100): 
                if properties.get(f'Counter{i}'):
                    self.counter_setup(properties,i)
                else: 
                    break
        
        # Scope
        if properties.get('Scope'):
            self.scope_setup(properties)
        elif properties.get('Scope1'):
            for i in range(1,100): 
                if properties.get(f'Scope{i}'):
                    self.scope_setup(properties,i)
                else: 
                    break
                
        # Meter
        if properties.get('Meter'):
            self.meter_setup(properties)
        elif properties.get('Meter1'):
            for i in range(1,100): 
                if properties.get(f'Meter{i}'):
                    self.meter_setup(properties,i)
                else: 
                    break
    
        # Source
        if properties.get('Source'):
            self.source_setup(properties)
        elif properties.get('Source1'):
            for i in range(1,100): 
                if properties.get(f'Source{i}'):
                    self.source_setup(properties,i)
                else: 
                    break
    
        # AWG
        if properties.get('AWG'):
            self.AWG_setup(properties)
        elif properties.get('AWG1'):
            for i in range(1,100): 
                if properties.get(f'AWG{i}'):
                    self.AWG_setup(properties,i)
                else: 
                    break
            
        # VNA
        if properties.get('VNA'):
            self.VNA_setup(properties)
        elif properties.get('VNA1'):
            for i in range(1,100): 
                if properties.get(f'VNA{i}'):
                    self.VNA_setup(properties,i)
                else: 
                    break
        
        # Temperature Controller
        if properties.get('Temperature'):
            self.temp_setup(properties)
        elif properties.get('Temperature1'):
            for i in range(1,100): 
                if properties.get(f'Temperature{i}'):
                    self.temp_setup(properties,i)
                else: 
                    break
        else:
            properties['Temperature'] = {'initial temp': 'None'}
            
    
    def attenuator_setup(self,properties:dict, instrument_num: int = 0):
        appender: str = str(instrument_num)
        if instrument_num==0: appender=''
        self.instrument_list.append('Attenuator'+appender)

        if properties[f'Attenuator{appender}']['name'] == 'JDSHA9':
            from qnnpy.instruments.jds_ha9 import JDSHA9
            try:
                exec(f"self.attenuator{appender} = JDSHA9(properties['Attenuator{appender}']['port'])")
                exec(f"self.attenuator{appender}.set_beam_block(True)")
                print(f'ATTENUATOR{appender}: connected')
            except:
                print(f'ATTENUATOR{appender}: failed to connect')
        else:
            raise NameError('Invalid Attenuator. Attenuator name is not configured')
        if instrument_num==1 and hasattr(self,"attenuator1"):
            self.attenuator=self.attenuator1
    
    
    def counter_setup(self,properties:dict, instrument_num: int = 0):
        appender: str = str(instrument_num)
        if instrument_num==0: appender=''
        self.instrument_list.append('Counter'+appender)
        if properties[f'Counter{appender}']['name'] == 'Agilent53131a':
            from qnnpy.instruments.agilent_53131a import Agilent53131a
            try:
                exec(f"self.counter{appender} = Agilent53131a(properties['Counter{appender}']['port'])")
                #without the reset command this section will evaluate connected
                #even though the GPIB could be wrong
                #similary story for the other insturments
                exec(f"self.counter{appender}.reset()")
                exec(f"self.counter{appender}.basic_setup()")
                # self.counter.write(':EVEN:HYST:REL 100')
                print(f'COUNTER{appender}: connected')
            except:
                print(f'COUNTER{appender}: failed to connect')
        else:
            raise NameError('Invalid counter. Counter name is not '\
                            'configured')
        if instrument_num==1 and hasattr(self,"counter1"):
            self.counter=self.counter1
    
    def scope_setup(self,properties:dict, instrument_num: int = 0):
        appender: str = str(instrument_num)
        if instrument_num==0: appender=''
        self.instrument_list.append('Scope'+appender)

        if properties[f'Scope{appender}']['name'] == 'LeCroy620Zi':
            from qnnpy.instruments.lecroy_620zi import LeCroy620Zi
            try:
                exec(f"self.scope{appender} = LeCroy620Zi('TCPIP::%s::INSTR' % properties['Scope{appender}']['port'])")
                # self.scope_channel = properties[f'Scope{appender}']['channel']
                print(f'SCOPE{appender}: connected')
            except:
                print(f'SCOPE{appender}: failed to connect')
        else:
            raise NameError('Invalid Scope. Scope name is not configured')
        if instrument_num==1 and hasattr(self,"scope1"):
            self.scope=self.scope1
    
    
    def meter_setup(self,properties:dict,instrument_num:int = 0):
        appender: str = str(instrument_num)
        if instrument_num==0: appender=''
        self.instrument_list.append('Meter'+appender)

        if properties[f'Meter{appender}']['name'] == 'Keithley2700':
            from qnnpy.instruments.keithley_2700 import Keithley2700
            try:
                exec(f"self.meter{appender} = Keithley2700(properties['Meter{appender}']['port'])")
                exec(f"self.meter{appender}.reset()")
                print(f'METER{appender}: connected')
            except:
                print(f'METER{appender}: failed to connect')
                # exec(f"self.meter{appender} = mock_builder(Keithley2700)")

        elif properties[f'Meter{appender}']['name'] == 'Keithley2400':
            # this is a source meter
            from qnnpy.instruments.keithley_2400 import Keithley2400
            try:
                exec(f"self.meter{appender} = Keithley2400(properties['Meter{appender}']['port'])")
                exec(f"self.meter{appender}.reset()")
                print(f'METER{appender}: connected')
            except:
                print(f'METER{appender}: failed to connect')
                # exec(f"self.meter{appender} = mock_builder(YokogawaGS200)")

        elif properties[f'Meter{appender}']['name'] == 'Keithley2001':
            from qnnpy.instruments.keithley_2001 import Keithley2001
            try:
                exec(f"self.meter{appender} = Keithley2001(properties['Meter{appender}']['port'])")
                exec(f"self.meter{appender}.reset()")
                print(f'METER{appender}: connected')
            except:
                print(f'METER{appender}: failed to connect')
                # exec(f"self.meter{appender} = mock_builder(Keithley2001)")
        else:
            raise NameError('Invalid Meter. Meter name: "%s" is not configured' % properties[f'Meter{appender}']['name'])
        if instrument_num==1 and hasattr(self,"meter1"):
            self.meter=self.meter1
    
    def source_setup(self,properties:dict,instrument_num:int = 0):
        appender: str = str(instrument_num)
        if instrument_num==0: appender=''
        self.instrument_list.append('Source'+appender)

        if properties[f'Source{appender}']['name'] == 'SIM928':
            from qnnpy.instruments.srs_sim928 import SIM928
            try:
                exec(f"self.source{appender} = SIM928(properties['Source{appender}']['port'], properties['Source{appender}']['port_alt'])")
                exec(f"self.source{appender}.reset()")
                exec(f"self.source{appender}.set_output(False)")
                print(f'SOURCE{appender}: connected')
            except:
                print(f'SOURCE{appender}: failed to connect')
                # exec(f"self.source{appender} = mock_builder(SIM928)")
        elif properties[f'Source{appender}']['name'] == 'YokogawaGS200':
           from qnnpy.instruments.yokogawa_gs200 import YokogawaGS200
           try:
               exec(f"self.source{appender} = YokogawaGS200(properties['Source{appender}']['port'])")
               # self.source.reset()
               exec(f"self.source{appender}.set_output(False)")
               exec("self.source{appender}.set_voltage_range(5)")
               print(f'SOURCE{appender}: connected')
           except:
               print(f'SOURCE{appender}: failed to connect')
               # exec(f"self.source{appender} = mock_builder(YokogawaGS200)")
        elif properties[f'Source{appender}']['name'] == 'Keithley2400':
            from qnnpy.instruments.keithley_2400 import Keithley2400
            try:
                exec(f"self.source{appender} = Keithley2400(properties['Source{appender}']['port'])")
                exec(f"self.source{appender}.reset()")
                print(f'SOURCE{appender}: connected')
            except:
                print(f'SOURCE{appender}: failed to connect')
                # exec(f"self.source{appender} = mock_builder(Keithley2400)")
        else:
            raise NameError('Invalid Source. Source name: "%s" is not configured' % properties[f'Source{appender}']['name'])
        if instrument_num==1 and hasattr(self,"source1"):
            self.source=self.source1
    
    def AWG_setup(self,properties: dict, instrument_num: int = 0):
        appender: str = str(instrument_num)
        if instrument_num==0: appender=''
        self.instrument_list.append('AWG'+appender)

        if properties['AWG'+appender]['name'] == 'Agilent33250a':
            from qnnpy.instruments.agilent_33250a import Agilent33250a
            try:
                exec(f"self.awg{appender} = Agilent33250a(properties['AWG{appender}']['port'])")
                exec(f"self.awg{appender}.beep()")
                print(f'AWG{appender}: connected')
            except:
                print(f'AWG{appender}: failed to connect')
        else:
            raise NameError('Invalid AWG. AWG name: "%s" is not configured' % properties['AWG'+appender]['name'])
        if instrument_num==1 and hasattr(self,"awg1"):
            self.awg=self.awg1
    
    # VNA
    def VNA_setup(self, properties: dict, instrument_num: int = 0):
        appender:str=str(instrument_num)
        if instrument_num==0: appender=''
        self.instrument_list.append("VNA"+appender)

        if properties["VNA"+appender]['name'] == 'KeysightN5224a':
            from qnnpy.instruments.keysight_n5224a import KeysightN5224a
            try:
                exec(f"VNA{appender} = KeysightN5224a(properties['VNA{appender}']['port'])")
                # self.VNA.reset()
                print(f'VNA{appender}: connected')
            except:
                print(f'VNA{appender}: failed to connect')
        else:
            raise NameError('Invalid VNA. VNA name: "%s" is not configured' % properties['VNA'+appender]['name'])
        if instrument_num==1 and hasattr(self,"VNA1"):
            self.VNA=self.VNA1
    
    #Temperature Controller
    def temp_setup(self, properties: dict, instrument_num:int=0):
        appender:str=str(instrument_num)
        if instrument_num==0: appender=''
        self.instrument_list.append("Temperature"+appender)

        if properties["Temperature"]['name'] == 'Cryocon350':
            from qnnpy.instruments.cryocon350 import Cryocon350
            try:
                exec(f"self.temp{appender} = Cryocon350(properties['Temperature{appender}']['port'])")
                exec(f"self.temp{appender}.channel = properties['Temperature{appender}']['channel']")
                exec(f"properties['Temperature{appender}']['initial temp'] = self.temp{appender}.read_temp(self.temp{appender}.channel)")
                print("TEMPERATURE"+appender+': connected | '+str(properties['Temperature'+appender]['initial temp']))
            except:
                properties['Temperature'+appender]['initial temp'] = 0
                print("TEMPERATURE"+appender+': failed to connect')
                # exec(f"self.temp{appender} = mock_builder(Cryocon350)")

        elif properties['Temperature'+appender]['name'] == 'Cryocon34':
            from qnnpy.instruments.cryocon34 import Cryocon34
            try:
                exec(f"self.temp{appender} = Cryocon34(properties['Temperature{appender}']['port'])")
                exec(f"self.temp{appender}.channel = properties['Temperature{appender}']['channel']")
                exec(f"properties['Temperature{appender}']['initial temp'] = self.temp{appender}.read_temp(self.temp{appender}.channel)")
                print("TEMPERATURE"+appender+': connected | '+str(properties['Temperature'+appender]['initial temp']))
            except: 
                properties['Temperature'+appender]['initial temp'] = 0
                print("TEMPERATURE"+appender+': failed to connect')
                # exec(f"self.temp{appender} = mock_builder(Cryocon34)")

        elif properties['Temperature'+appender]['name'] == 'ICE':
            try:
                properties['Temperature'+appender]['initial temp'] = ice_get_temp(select=1)
                print("TEMPERATURE"+appender+': connected' + ice_get_temp(select=1))
            except:
                properties['Temperature'+appender]['initial temp'] = 0
                print("TEMPERATURE"+appender+': failed to connect')
                
        elif properties['Temperature'+appender]['name'] == 'DEWAR':
            try:
                properties['Temperature'+appender]['initial temp'] = 4.2
                print("TEMPERATURE"+appender+': ~connected~ 4.2K')
            except:
                properties['Temperature'+appender]['initial temp'] = 0
                print("TEMPERATURE"+appender+': failed to connect')
        else:
            raise NameError('Invalid Temperature Controller. TEMP name: "%s" is not configured' % properties['Temperature'+appender]['name'])
        if instrument_num==1 and hasattr(self,"temp1"):
            self.VNA=self.VNA1
            
            

#######################################################################
        #       Temporary Data Storage and Cache-ing
#######################################################################

class Data:
    """
    The data class is used to store and save any collected data
    If no default file save location is provided, one will automatically be generated

    NOTE that autosaving does not work with .mat files due to how the binary
    data in a .mat file is stored. the only way to append to a mat file is
    to read the whole file into a python dictionary, modify, then re-write
    the entire thing, which defeats the purpose of "autosaving" to minimize
    memory usage. 

    Parameters
    ----------
    autosave : bool, optional
        When enabled, periodically empties out Data and auto-saves it to the file location provided. The default is False.
        Note: If using autosave, remember to still call save() at the end to store any data in the current save_increment that hasn't been transferred yet!
    save_increment : int, optional
        How often to autosave whenever store() is called. The default is every 128th time store() is called.
    path : str, optional
        file path to save to. automatically sets up folders if full path doesn't exist. The default is None.
    name : str, optional
        file name to save to. if a name is already provided in path, it is overridden by this. The default is None.
    file_type : str, optional
        file type to save to. The default is 'csv'.
    preserve_pos_order : bool, optional
        if store(v1=1,v2=2) then store(v2=3, v3=4) is called, by default v1
        and v4 will be compressed into the first line, while v2 will appear
        on lines 1 and 2. Enabling preserve_pos_order will create empty
        columns to fix this ordering. The default is False.

    Returns
    -------
    None.

    """
    #data: dict[str,list[object]]
    date:dict
    numcalls: int #number of times store is called, reset to 0 when empty() is called
    #save_increment = how often to save csv when calling store, every time (1), every other time (2)
    def __init__(self, *, autosave: bool = False, save_increment: int = 128, path:str=None, name:str=None, file_type:str = 'csv', preserve_pos_order: bool=False):
        self.data={}
        self.numcalls = 0
        self.preserve_pos = preserve_pos_order
        if path!=None:
            if '.' in path:
                temp = path.rsplit(os.sep,1)
                path = temp[0]
                if name==None: name = temp[1]
            if not os.path.exists(path):
                os.makedirs(path)
        if name==None:
            name: str = time.strftime(f"data_%Y-%m-%d_%H-%M-%S.{file_type}", time.localtime())
        elif not '.' in name:
            name = f"{name}.{file_type}"
        if path==None: self.save_loc=name
        else: self.save_loc=f"{path}{os.sep}{name}"
        # print(self.save_loc)
        self.autosave = autosave
        if autosave:
            #self.close_csv()
            self.save_increment = save_increment
            self.save_increment_counter = 0
    
    def store(self,**kwargs):
        for key in kwargs:
            if self.data.get(key) != None:
                self.data[key].append(kwargs[key])
            else:
                if self.preserve_pos and self.numcalls>0:
                    self.data[key]=['']*self.numcalls
                    self.data[key].append(kwargs[key])
                else:
                    self.data[key]=[kwargs[key]]
                exec(f"self.{key}=self.data['{key}']")
        if self.preserve_pos and len(kwargs)<len(self.data):
            for key in self.data:
                if kwargs.get(key) == None:
                    self.data[key].append('')
        if self.autosave:
            self.save_increment_counter+=1
            if self.save_increment_counter>=self.save_increment:
                self.save(path=self.save_loc)
                self.empty()
                self.save_increment_counter=0
        self.numcalls += 1
    
    def get(self, key: str) -> List[object]:
        return self.data[key]
    
    def last(self, key: str) -> object:
        return self.get(key)[-1]
    
    def close_csv(self):
        if hasattr(self, 'live_csv'):
            self.live_csv.close()
            
    def empty(self):
        """
        empties out the values stored in the data dict, but retains any
        dictionary keys

        Returns
        -------
        None.

        """
        for key in self.data:
            self.data.get(key).clear()
        self.numcalls = 0
    
    def save(self, path:str=None, name:str=None, file_type:str = 'csv', override: bool = False, printloc: bool = False):
        """
        saves the current contents of the data class to a file. 
        if a default save location is provided in initialization, arguments 
        provided here will override defaults, UNLESS no arguments are provided,
        (excluding override argument), in which case defaults will still be used
        
        note that if autosaving is enabled, then the data will periodically
        get cleared to save memory, which means not all data collected will be
        included in newer files created by save(), only the autosave file will
        include all data. 
        
        also note: saving once to a .mat file works just fine, but attempting to
        append to a .mat file DOES NOT WORK. This also means that autosave does
        not work with .mat files. 
        
        Parameters
        ----------
        path : str, optional
            file path to use. automatically sets up folders if full path doesn't exist. The default is None.
        name : str, optional
            file name to use. if a name is already provided in path, it is overridden by this. The default is None.
        file_type : str, optional
            file type. The default is 'csv'.
        override : bool, optional
            if to override previous file if it already exists. The default is False.
        Returns
        -------
        None
        """       
        if path == None and name == None and file_type=='csv':
            path = self.save_loc
        if path!=None and not os.sep in path:
            name=path
            path=None
        if path!=None:
            if '.' in path:
                temp = path.rsplit(os.sep,1)
                path = temp[0]
                if name==None: name = temp[1]
            if not os.path.exists(path):
                os.makedirs(path)
            # sys.path.append(path)
        if name==None:
            name: str = time.strftime(f"data_%Y-%m-%d_%H-%M-%S.{file_type}", time.localtime())
        elif not '.' in name:
            name = f"{name}.{file_type}"
        if path == None: path = ''
        try:
            mode: str = 'w'
            if os.path.exists(f"{path}{os.sep}{name}") and not override: mode = 'a'
            if mode == 'a' and name.rsplit('.',1)[1]=='mat': mode='ab'
            # print(mode + " " + str(os.path.exists(f"{path}{os.sep}{name}")) + " " + f"{path}{os.sep}{name}")
            with open(f"{path}{os.sep}{name}", mode) as f:
                if name.rsplit('.',1)[1]=='mat':
                    # print(self.data)
                    if mode=='ab': scipy.io.savemat(f, mdict=self.data)
                    else: scipy.io.savemat(f"{path}{os.sep}{name}", mdict=self.data)
                    return
                writer = csv.writer(f)
                if mode=='w': writer.writerow(self.data.keys())
                writer.writerows(zip(*self.data.values()))
            if printloc: print(f"{path}{os.sep}{name}")
        except IOError as e:
            # even if initial save attempt fails, will try to force store data in a temporary file at the script location
            print(f"\033[1;31;49mI/O error: {e}, attempting to force data save... \033[1;37;49m")
            try:
                with open("forced_data_save.csv", 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.data.keys())
                    writer.writerows(zip(*self.data.values()))
                print("data saved at *this user*\\forced_data_save.csv")
            except Exception as e:
                print("Backup failed somehow, if you're seeing this things are really messed up: {e}")
                
        


