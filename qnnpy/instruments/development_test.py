# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 12:21:00 2019

@author: dizhu
"""

# %%
import sys

import matplotlib.pyplot as plt
import pyvisa

sys.path.append(r"C:\Users\dizhu\Desktop\GitHub\qnn-lab-instr-python")

from qnnpy.instruments.yokogawa_aq6370 import AQ6370

rm = pyvisa.ResourceManager()
rm.list_resources()


osa = AQ6370("GPIB0::7::INSTR")

# %%


osa.quick_setup()

wl, power = osa.single_sweep()
plt.plot(wl * 1e9, power)


# %%

# repeat_sweep(osa)

# %%

# %%

idn(osa)
