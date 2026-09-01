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

PP = Photometry_Pipeline.Photometry_Pipeline()
data = PP.Master_Dark(None, 'Data/2026-08-31_OMICRON_F3p17_OPF_QHY600Ma_BIAS/')








