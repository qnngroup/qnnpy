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
