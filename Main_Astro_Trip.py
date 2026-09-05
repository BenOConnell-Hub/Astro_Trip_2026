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

#Dark_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_DARK/' #2026-09-01
Dark_Directory = 'Data/2026_09_03/2026-09-03_OMICRON_F3p17_OPF_QHY600Ma_DARK/'
#Bias_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_BIAS/' #2026-09-01
Bias_Directory = 'Data/2026_09_03/2026-09-03_OMICRON_F3p17_OPF_QHY600Ma_BIAS/'
#Flat_Directory = 'Data/2026_09_01/2026-09-01_OMICRON_F3p17_OPF_QHY600Ma_FLAT/'
Flat_Directory = 'Data/2026_09_03/2026-09-03_OMICRON_F3p17_OPF_QHY600Ma_FLAT/'
Raw_Directory = 'Data/2026_09_03/2026-09-03_OMICRON_F3p17_OPF_QHY600Ma_ngc604/' #2026-08-31
#Raw_Directory = 'Data/2026_09_02/2026-09-02_OMICRON_F3p17_OPF_QHY600Ma_M-16/'
Highest_Exp_Dark = "Data/2026_09_03/2026-09-03_OMICRON_F3p17_OPF_QHY600Ma_DARK/Master_Files/Master_Dark_60_0.fits"
Highest_Exp_Time = 60.0


PP = Photometry_Pipeline.Photometry_Pipeline(Exposure_Time=5, 
                                             Filter_Type= None,
                                             Raw_Directory = Raw_Directory,
                                             Flat_Directory = Flat_Directory,
                                             Bias_Directory = Bias_Directory,
                                             Dark_Directory = Dark_Directory,
                                             File_Path_Highest_Exp_Dark = Highest_Exp_Dark,
                                             Highest_Exp_Time = Highest_Exp_Time)

PP.Create_Colour_Image('NGC604', 15.0, 10.0, 10.0, 83.5)
#data = PP.Reduce_Images('NGC604')

