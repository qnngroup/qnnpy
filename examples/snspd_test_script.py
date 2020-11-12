# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 10:29:32 2020

@author: omedeiro


"""


''' Import functions '''
import sys
sys.path.append(r'Q:\qnnpy')
import qnnpy.functions.functions as qf
import qnnpy.functions.snspd as snspd
import qnnpy.functions.iv_sweep as iv


''' Specify path to configuration file.'''
config = r'S:\SC\Measurements\SPG264\SPG264_config.yml'


# %% Iv Sweep
a = snspd.IvSweep(config)
a.run_sweep()
a.plot()
a.isw_calc()
a.save()


# %% Pulse Trace Single

b = snspd.PulseTraceSingle(config)
b.trace_data();
b.plot()
b.save()

# %% Trigger Sweep 
c = snspd.TriggerSweep(config)
c.run_sweep()
c.plot()
c.save()


# %% Linearity Check
d = snspd.LinearityCheck(config)
d.run_sweep()
d.plot()
d.save()

# %% Photon counts
e = snspd.PhotonCounts(config)
e.light_counts()
e.dark_counts()
e.plot()
e.save()

# %% 

f = snspd.KineticInductancePhase(config)
f.run_sweep_current(plot=True, save=True)
