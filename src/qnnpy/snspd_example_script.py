# -*- coding: utf-8 -*-
"""
Created on Sun Aug 29 13:28:12 2021

@author: omedeiro

wide wire SPG600
"""

import sys

sys.path.append(r"Q:\qnnpy")
import qnnpy.functions.snspd as snspd

config = r"S:\SC\Measurements\SPG600\SPG600_config_300mK.yml"


# %% Iv Sweep
a = snspd.IvSweep(config)
a.run_sweep_fixed()
a.plot()
a.isw_calc()
a.save()


# %% Pulse Trace Single
b = snspd.PulseTraceSingle(config)
x, y = b.trace_data()
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
