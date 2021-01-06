# QNNPY

## About
QNNPY is an python-based instrument control toolbox for the Quantum Nanostructure and Nanofabrication Group (QNN) at MIT. The primary goal of this package is to simplify and standardize the measurement of superconducting nanowire single photon detectors (SNSPDs) and other superconducting nanoelectronics. This package is split into two main sections: functions, and instruments. 

This reposotory does not contain commands that will perform your measurements for you. Its purpose is to organize, standardize, and improve the existing programming infrastructure. 

### Instruments
Within `qnnpy\instruments` you will find a collection of scripts containing functions that send SCPI commands to each instrument. Please use the following format/capitalization when creating a new instrument script. 

```
agilent_53131a.py #lower_case 


class Agilent53131a: #captalize each word
	def read(self): #lower_case
		...
	
	def run_sweep(self): #lower_case
		...
```

Changing measurement setups is complicated by the different protocols used by each manufacturer. There are two things to strive for that might alleviate this issue. First, is to try and standarize each definition name. If every multimeter has a command `read_voltage` there would be no additional changes to our script beyond changing the instrument name. This of course does not work if the instruments have dissimilar abilities. For example we might bias a device with a voltage source or a current source where commands like `set_current` would not apply to both. (Second) In this case it makes sense to code in a conditional statement based on the instrument selection. This is cumbersome but generally is uncommon and will only have to be performed once. See the temperature selection in `qnnpy\function\snspd.py` for example.


### Functions
Within functions there are multiple device classes and one class for all base-level functions. 

These base-functions contain standard processes like saving, plotting, or logging. This allows us to standardize the parts of these functions that should never be changed and are applicable to every measurement in the lab (like filepaths or file formats). 

#### Base functions
Base functions contain standard processes like saving, plotting, or logging. This allows us to standardize the parts of these functions that should never be changed and are applicable to every measurement in the lab (like filepaths or file formats). 

For example, qf.plot is basically a stripped down version of matplotlib.pyplot.plot with plot.savefig built in. 
```
import qnnpy.functions.functions as qf
import numpy as np
file_path = r'S:\correct_file_path'

x_data = np.arange(-10,10,.5)
y_data = np.tanh(x_data)

qf.plot(x_data,y_data,linestyle='r-', path=file_path)
```

A device class contains all of the relevant measurements for that device. For example, a snspd class might contain a count-vs-bias measurement or a IV measurement but you would not expect to find S11phase-vs-temperature. For devices with a large number of potential measurements it makes sense to define each measurement as a subclass. Within each subclass will be the method that runs the measurement/sweep and methods that save and plot the data. The save and plot methods within the subclass will build on the base-functions, adding things like axis labels, titles, additional save parameters; any detail specifict to that subclass. 
	
#### An Example of a Device class
```
import qnnpy.functions.functions as qf  #base-functions
class Snspd: #Class
	def __init__(self, configuration_file):
		...
		
	
class TriggerSweep(Snspd): #Subclass
	def run_sweep(self):
		...
		
	def save(self):
		data_dict = {'trigger_v':self.trigger_v, 'count_rate':self.counts, 'v_bias':self.v_bias}
		qf.save(self.properties, 'trigger_sweep', data_dict)
		
	def plot(self):
		qf.plot(self.trigger_v,self.counts,
                
        title=self.sample_name+" "+self.device_type+" "+self.device_name,
        xlabel = 'Trigger Voltage (V)',
        ylabel = 'Counts (cps)',
        path = self.full_path,
        close=True)
```

#### How to use the Device class
```
config = r'Q:\somepath\configuration.yml'

c = snspd.TriggerSweep(config)
data = c.run_sweep() #return data if you want
c.plot()
c.save()
```

#### How to create a configuration file
Configuration files should be formatted into four sections: User, Device, Measurements, and Instruments. Below is a quick example showing the four sections. These four sections do not explicitly relate to their own dictionary; each measurement and instrument should have their own dictionary, hence the ellipsis. 

Here is an example .yml configuration file with four dictionaries. 
```
User: 
  name:
  
Save File: #maybe rename this
  sample name: SPG000
  device type: snspd 
  device name: A0
  
some_measurement: #maybe change to same string as subclass
  parameter1:
  parameter2:
  
... 

some_instrument:
  name:
  port:
  
...
```



## Requirements
PyYAML 5.1 and later

## Notes
~~There have been some issues with permissions from the NAS. Ideally the lab computers will have RO access to the network repository.~~ This appears to have been resolved after NAS reboot. 

`help(module)` for documentation. ex: `help(snspd)`


## Network
Each computer in the lab is connected to the qnn-nas by maping a network drive to the desired folder. 

- `\\18.25.29.148\qnn-repo` is mapped to Q: for Qnn (or R: if Q: is taken)
- `\\18.25.29.148\Data` is mapped to S: for Synology


## Short Term TO-DO (write problem + solution)
- Remove reset on PulseTrace module. Still need to capture settings. 
- ~~Output log is too long and hard to find information. Change output to just the section specific to the measurement and the instruments.~~
- Logging was broken, consider just using open(), open().write, close() for everything. 
- Convert all SNSPD bias to either current or voltage (see linearity check and trigger sweep)
- Save all logging as either *.dat or *.txt and build analysis functions. This should help with memory usage. 
- Add positive and negative Isw averaging over multiple sweeps to Isw_calc. Might be good to save Isw as a separate .mat file, or just write to DB.
- Add yaml device parameter option. save parameters to data_dict
- ~~Move logs to network location~~
- ~~Add documentation to qnnpy.functions~~  
- ~~Add temperature controllers. still problems with ICE~~ ICE controller already has 1 listener (ICE gui) over serial... so we cannot interface. Currently a script checks if the logging feature within the gui is active and pulls the most recent temperature reading. If logging is off it will notify at begining of measurement and will not save old temp. 
- Temp vs bias. temp vs counts.  (difficult for ice)
- qf.plot should be reformatted to better handel arrays/lists  
- yaml NAMESPACE  
- device type NAMESPACE  
- consider moving subclasses out of snspd class. make them stand alone.  
- ~~all classes/methods should follow CapWord/lower_case convention.~~ 
- use NAS opposed to google drive stream to store IoT data  
- ~~consider saving only the configuration for that measurement. eg just the iv_sweep section gets saved when a iv sweep is run.~~ 
- `pip install lakeshore`  a lakeshore package for all models, we should look into this more  
- ~create documentation for adding new instruments or codes.~
- ICE temperature can only be read every 10seconds from log. Need to find a way around this. 


## Long Term TO-DO
- Link AJA Sample database with NAS location  
- Link PHIDL gds layouts with NAS location. (still not sure how to do this, see qnngds)
- ~~qnnmat (collect all scripts libraries from marco/brenden)~~ new repo qnn\qnnmat
- create IoT section for cryogenic integration  
