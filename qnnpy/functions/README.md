# QNNPY\FUNCTIONS

A collection of scripts containing device specific measurement functions. `functions.py` contains the base-level functions used by most other device specific scripts. Using a device specific script, such as `snspd.py`, to measure another device will likely cause more headaches then saved lines of code. The best advice I could give is to either: 1) write a completely new script for your device and use the `functions.py` for saving and plotting. or 2) copy a function that is close to what you want from `snspd.py` to your own script and edit it there. Otherwise, using the `snspd.py` script for another device will not allow the necessary flexibility when testing, things will be plotted in an incorrect way, saving dictionaries will be incorrect, etc.

## Organization 
I have not figured out the best way to orgainize everything. Currently all of the SNSPD measurements are in `snspd.py` but there are other files like `iv_sweep.py` or `tc_measurement.py` that are not exactly device specific. 

## functions.py

#### plot

#### saving

#### logging

## snspd.py
File containing the Snspd class and measurement subclasses.

### Snspd Quick Start Guide

If you want to measure a snspd using this script the easiest thing to do is to copy the [snspd_test_script.py](https://github.mit.edu/qnn/qnnpy/blob/master/examples/snspd_test_script.py) and [snspd_example_ICE (config)](https://github.mit.edu/qnn/qnnpy/blob/master/config/snspd_example_ICE.yml) to your own directory (either a personal location or to the corresponding NAS S:\ drive location).
Once copied, update the configuration path, and the configuration data. Then each measurement can be run from the snspd_test_script.py. Your configuration file should only include the instruments you have on, otherwise the script will try and connect to the instruments. You can delete an instrument from the configuration or comment it out.


In spyder I find the below setup to be the most comfortable. A second panel can be created by right clicking the script tap and selecting split vertically (or, Crtl+{). 

![spyder-ice](/examples/spyder_split_window.PNG)

### Snspd Class Documentation 

##### init
Compatable Instruments:
- Counter
	- Agilent53131a
- Attenuator
	- JDSHA9
- Scope
	- LeCroy620Zi
- Meter
	- Keithley2700
	- Keithley2400
	- Keithley2001
- Source
	- SIM928
- AWG
	- Agilent33250a
- VNA
	- KeysightN5224a
- Temperature
	- Cryocon350
	- Cryocon34
	- ICE 
	- DEWAR

Note: code for instrument setup has been moved to functions.Instruments, and instruments are now accessed through inst.scope, inst.source, etc.

##### average_counts
This method belongs to the Snspd class and returns the average count rate for a given number of iterations. This function accepts the counting time, iterations, and trigger voltage. 
For every iteration the device is biased, the counts are recorded, the voltage is measured, the results are printed, and the bias is turned off. After the specified number of iterations the average count is returned. If SNSPD voltage is greater than 5mV the counts will be printed with `# wire switched` but the value will still be included within the average. 

##### tc_measurement
Very primitive Tc measurement for the ICE Oxford. Accepts bias voltage and path. 

The path must include filename.txt. Bias the device at some value much lower than Ic. This code will bias device, measure voltage, and turn off voltage, every two seconds. The ICE will measure temp every 10 seconds. Slower sweep is better. Keyboard Interrupt to end. File will be saved at path. 
#### TriggerSweep

#### TriggerSweepScope

#### IvSweep

#### PhotonCounts

#### LinearityCheck

#### PulseTraceSingle

#### PulseTraceCurrentSweep

#### KineticInductancePhase

## functions.py
### Plotting
#### LivePlotter
Live-updating plotter. Requires IPython to be enabled for interactive shell. Simpily call plot(x, y) and the plot will add your points live. Once you're done, you can save to a png or jpg by calling save() 
```
Instantiation of the class can also takes optional arguments:
title: str - title of the plot
xlabel: str - label for the x axis
ylabel: str - label for the y axis
legend: bool - whether to show the legend or not
legend_loc: str - location for the legend, default is "best", also can be "upper right", "lower left" etc
max_len: int - maximum allowed length of each line in this plot, default is infinite. if the number of lines in one label exceeds this number, the oldest data points get cut off. if you're running a measurement for a very long time, it's best to set this to a number to prevent overusing memory
```
plot() also optionally takes in a label: str argument to diffrentiate multiple lines and data points, along with most arguments used in the default matplotlib plot() method

save() can take a name, file path, and file type. if no name is provided, a random name based on the current time will be used instead

Basic usage example:

```
p = LivePlotter()
for x in range(5):
    y = x+2
    p.plot(x, y)
```

### Configuration
### Saving
#### data_saver(parameters, measurement)
```
the data_saver class is used to save data from both LivePlotter and Data classes into a pre-defined organized file structure based on the run configuration defined in the external yaml file. required arguments for the data_saver function are parameters, which is where the yaml file must be passed, and measurement, which is a string defining what measurement is being done (ie: iv_sweep)
measurement data and information will be organized into {meas_path}/{sample_name}/{device_type}/{device_name}/{measurement}, where:
meas_path - root folder, by default S:\SC\Measurements
sample_name - the 'sample name' key under 'Save File' in the yaml file
device_type - the 'device type' key under 'Save File' in the yaml file
device name - the 'device name' key under 'Save File' in the yaml file
measurement - whatever is passed into the 'measurement' argument when the function is being called

other important arguments to include in the function are:
data - the instance of the data class to be saved
inst - the instance of the instruments class to be saved
plot - instance of the LivePlotter class to be saved
```
optionally, if instead of 'sample name', the 'Save File' key in the yaml file defines a 'sample name 1' and 'sample name 2', and the data or plot arguments is a list instead of a single instance of the class, then data_saver() will recursively call itself for every sample name included in the yaml file (in this example, 2), and element in the data or plot list. 

### Logging

#### database_connection(**kwargs) -> mariadb.connection
returns a connection to a database. if kwargs is not provided, then simpily returns a connection to qnndb using Owen's username and password

#### log_data_to_database(table_name: str, connection = None, **kwargs)
logs data provided in kwargs to a database table

if connection is not provided or None, then simpily uses qnndb with Owen's username and password

Example:
```
log_data_to_database("measurement_events", connection=None, user='IR', port=1)
```
This will add a row to the 'measurement_events' table with the 'user' column as 'IR' and 'port' column as 1

#### update_table(table_name: str, set_col: str, conditional: str = 'NULL', connection = None)
allows you to run sql commands in the format `'UPDATE' table_name SET 'set_col' WHERE 'conditional'` easily from the terminal


### Measurement
### Code Testing
#### mock_builder(class_to_mock) -> object
Primitive class-mocking function which creates a mock instance of a class, replicating any function definitions within the class but replacing the functionality of the original functions with a simple print: <function> was called in <class name>

This function isn't related to the measurement-taking and saving in the rest of qnnpy, and is only for code-testing, for example creating mock instances of instruments to test code without actually being connected to the instrument. 

### Instrument Setup
#### Instruments(properties: dict)
This class sets up and stores all compatible instruments:
- Counter
	- Agilent53131a
- Attenuator
	- JDSHA9
- Scope
	- LeCroy620Zi
- Meter
	- Keithley2700
	- Keithley2400
	- Keithley2001
- Source
	- SIM928
- AWG
	- Agilent33250a
- VNA
	- KeysightN5224a
- Temperature
	- Cryocon350
	- Cryocon34
	- ICE 
	- DEWAR

To use the class, store load_config(yaml_configuration_file) into a variable then pass the variable into Instruments, and store the result (ie: instruments = Instruments(load_config(config_file))   ). Instruments can now be accessed with instruments.scope, instruments.awg, instruments.VNA, etc. 

If you want to use multiple of the same type of instrument, for example two source, modify your yaml file to include a Source1 and Source2. When instantiating the Instruments class, these two source will be accessible with instruments.source1, instruments.source2. instruments.source will automatically be set to instruments.source1 as well. 
	
If you do not postfix the instrument type in the yaml file with a number, then Instruments will assume you only intend on using one of that type of instrument and will only load one of that type of instrument (different types of instruments will still load). For example, having a Source and Source1 in a yaml file will only load Source, ignoring Source1 or any other Source. If you intend on using multiple instruments, don't start with any number other than 1 as well. 

If an instrument fails to connect, then attempting to get that instrument will result in an attribute error. For example, if source fails to connect, then attempting to call instruments.source will yield "AttributeError: 'Instruments' object has no attribute 'source'"
	
### Data storage
#### Data
The data class is used to store and save any collected data

Optionally can be used to automatically save data on a specific interval, for long-term data collection. To set up automatic data saving, set the "autosave" argument when instantiating the Data class to True, for example: d = Data(autosave = True). Note that autosaving only works for csv files. Make sure to still call save() after all measurements have finished to save any final measurements which were taken in between the save_increment. Calling save() by default will save to whatever file location was generated when the data class was created, see data.save() documentation below. 

Optionally, can also be set up to automatically log to a database. This requires that the table to log to already exists, and that each inputted data key has a corresponding column in the database table. 
```	
Other arguments can also be specified:
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
connection : mariadb.connection, optional
    If you want to auto-log data to a database, then you can set a connection here.
    Just remember to run connection.close() after you're done!
table_name : str, optional
    database table name
logtime: bool, optional
    logs the time in the data dict as 'time' in addition to other variables whenever store() is called
```

date.store() - stores data into an internal dictionary in the data class. also makes calls to save() and empty() if autosave is enabled
	
data.empty() - empties out any data but preserves the key names. for example if you ran d.store(voltage=1, temperature=10), then ran d.empty(), the keys voltage and temperature would still exist, but the values 1 and 10 would be emptied out. 
	
data.save() - saves the current contents of the data class. if autosave is being used, then it's likely that some of the contents of the data class have already been transferred into the file, so it's not guarenteed that this will save all data. 
	
Basic usage example:
```
d = Data()
for i in range(5):
     V = take_voltage()
     T = take_temperature()
     d.store(voltage=V, temperature=T)
d.save()
d.empty() # clear data

if you want to access data in a data class, you can optionally use one of the following:
voltages: list = d.get('voltage')
voltages: list = d.voltage # beware that this will crash if 'voltage' was never passed in d.store()
```

Date + database example:
```
import qnnpy.functions.functions as qf

d = qf.Data(table_name = 'measurements', connection=qf.database_connection()) # see database_connection() for more info on this function
for i in range(5):
    V = take_voltage()
    T = take_temperature()
    d.store(voltage=V, temperature=T) # this requires the database table you're committing to to have columns named 'voltage' and 'temperature'

d.connection.close() # make sure to close the connection after you're done! the Data class does not automatically close the connection. 
```	
	
	
# irawizza functions.py update - Usage Example:
```
import qnnpy.functions.functions as qf
+any other necessary imports

config = r'YAML\CONFIG\FILE\LOCATION'
properties = qf.load_config(config)
instruments = qf.Instruments(properties)
+any instrument-specific setup, ie instruments.source.setup_read_volt()
	
d=qf.Data()
p=qf.LivePlotter()
	
for i in range(100):
    V, I = instruments.source.read_voltage_and_current()
    d.store(voltage=V, current=I)
    p.plot(V, I)

qf.data_saver(properties, 'iv_sweep', meas_path=r'C:\Users\QNN\Documents\Measurements', data=d, plot=p, inst=instruments)
```

this makes writing your own measurement scripts very easy, but if you still want pre-existing measurement scripts in snspd.py or ntron.py, then those should still work the same. 

## Multiple samples example:
Example yaml file, note how sample name 1 and sample name 2 are specified
```
User:
  name: TST

Save File:
  sample name 1: SPG755
  sample name 2: SPG765
  device type: wire
  device name: TST

Source:
  name: 'Keithley2400'
  port: "GPIB0::14"

Temperature:
  name: 'Cryocon34'
  port: 'GPIB0::12'
  channel: 'C'
```
create seperate Data and LivePlotter classes for each sample:
```
import qnnpy.functions.functions as qf

sample_1_data = qf.Data()
sample_2_data = qf.Data()
sample_1_plot = qf.LivePlotter()
sample_2_plot = qf.LivePlotter()
```
now when you save, make sure you select the right yaml file, and include both data classes as an list, and both liveplotters as a list:
```
import qnnpy.functions.functions as qf

config = r'Q:\qnnpy-beta\yml_configs\example_config.yaml'
properties = qf.load_config(config)

qf.data_saver(properties, "test", r"C:\Users\QNN\Documents\Measurements", data = [sample_1_data, sample_2_data], inst = inst, plot = [sample_1_plot, sample_2_plot])
```
also note that both the "data" and "plot" arguments in data_saver() are optional
