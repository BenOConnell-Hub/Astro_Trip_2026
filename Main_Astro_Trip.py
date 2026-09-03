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
import astropy

PP = Photometry_Pipeline.Photometry_Pipeline(Exposure_Time=5.0, Filter_Type= 'SDSSgp+')
Dark_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_DARK/'
Bias_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_BIAS/'
Flat_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_FLAT/'
Raw_File_Path = "Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_tres-2/tres-2_20260901T202356977_SC_SDSSgp+_0005s000_000000.fits"
data = PP.Science_Array(Raw_File_Path, Dark_Directory, Bias_Directory, Flat_Directory)
#PP.Calculate_Flat_Master_Array(Flat_Directory, Bias_Directory)

'''
new_data = np.loadtxt(Flat_Directory + 'Master_Flat_SDSSrp+.txt')
plt.imshow(new_data, cmap='gray')
plt.colorbar()
plt.show()
'''