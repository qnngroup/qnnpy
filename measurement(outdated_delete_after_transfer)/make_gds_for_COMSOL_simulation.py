#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 22:38:08 2019

@author: dizhu
"""
#%%
import numpy as np
from phidl import Device, Layer, quickplot, make_device, Port
import phidl.geometry as pg
import phidl.routing as pr
import scipy.io
from datetime import *
import gdspy
#import phidl.dzgeometry as dzpg
#%%


fname = '2018-12-01_taper_study_1000MHz_gap=3um_w=300nm.gds'
D = pg.import_gds(fname)

BOX = pg.bbox([(D.xmin-100, D.ymin+3),(D.xmax+100, D.ymax-3)])


NBN = pg.boolean(BOX,D, 'a-b', layer = 1)
BOX.flatten(single_layer = 0)


M = Device()
M.add_ref(BOX)
M.add_ref(NBN)

M.flatten()

fname = str(datetime.now()).split(' ')[0]+'_1G_taper_simulation'
print(fname)
M.write_gds(filename=fname+'.gds', unit=1e-6, precision=1e-9)



