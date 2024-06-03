# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 14:53:32 2020

@author: medeiroso

"""

# import qnnpy.
# %%
from qnnpy.functions.iv_sweep import iv_sweep

x = iv_sweep()
x.load_config(filename=r"C:\Users\ICE\Documents\GitHub\qnnpy\config\example.yml")
x.run_sweep()
x.save()
x.plot()

# file_path='C:\Users\medeiroso\Desktop\SPG100_standard_snspd_D12_2020-04-17 16-03-07\SPG100\standard_snspd\D12\IV sweep'
