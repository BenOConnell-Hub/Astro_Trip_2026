# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 18:52:46 2026

@author: benoc

The main astro trip file for running all the pipelines
"""

import Photometry_Pipeline 
import datetime
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

PP = Photometry_Pipeline.Photometry_Pipeline(save_file=True, Exposure_Time=None)
Dark_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_DARK/'
Bias_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_BIAS/'
data = PP.Science_Array('None', Dark_Directory, Bias_Directory, 'None')


'''
new_data = np.loadtxt(Dark_Directory + 'Master_Dark_0_5.txt')
print(np.max(new_data))
plt.imshow(new_data, cmap='Wistia', vmin = np.min(new_data), vmax = np.max(new_data))
plt.colorbar()
plt.show()
'''







