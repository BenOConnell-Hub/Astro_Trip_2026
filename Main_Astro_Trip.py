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
<<<<<<< HEAD

PP = Photometry_Pipeline.Photometry_Pipeline()
data = PP.Master_Dark(None, 'Data/2026-08-31_OMICRON_F3p17_OPF_QHY600Ma_BIAS/')








=======
from astropy.io import fits
import astropy


#Dark_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_DARK/' #2026-09-01
Dark_Directory = 'Data/2026_09_03/2026-09-03_OMICRON_F3p17_OPF_QHY600Ma_DARK/'
#Bias_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_BIAS/' #2026-09-01
Bias_Directory = 'Data/2026_09_03/2026-09-03_OMICRON_F3p17_OPF_QHY600Ma_BIAS/'
Flat_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_FLAT/'
#Raw_Directory = 'Data/2026_08_31/2026-08-31_OMICRON_F3p17_OPF_QHY600Ma_M31/' #2026-08-31
Raw_Directory = 'Data/2026_09_02/2026-09-02_OMICRON_F3p17_OPF_QHY600Ma_M-16/'
Highest_Exp_Dark = "Data/2026_09_03/2026-09-03_OMICRON_F3p17_OPF_QHY600Ma_DARK/Master_Files/Master_Dark_60_0.fits"
Highest_Exp_Time = 60.0

PP = Photometry_Pipeline.Photometry_Pipeline(Exposure_Time=60, 
                                             Filter_Type='SDSSgp+',
                                             Raw_Directory = Raw_Directory,
                                             Flat_Directory = Flat_Directory,
                                             Bias_Directory = Bias_Directory,
                                             Dark_Directory = Dark_Directory,
                                             File_Path_Highest_Exp_Dark = Highest_Exp_Dark,
                                             Highest_Exp_Time = Highest_Exp_Time)
'''
Dark_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_DARK/'
Bias_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_BIAS/'
Flat_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_FLAT/'
Raw_File_Path = "Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_tres-2/tres-2_20260901T202356977_SC_SDSSgp+_0005s000_000000.fits"
'''
data = PP.Reduce_Images('M31')
#PP.Calculate_Flat_Master_Array(Flat_Directory, Bias_Directory)

'''
new_data = np.loadtxt(Flat_Directory + 'Master_Flat_SDSSrp+.txt')
plt.imshow(new_data, cmap='gray')
plt.colorbar()
plt.show()
'''
>>>>>>> master
