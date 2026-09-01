# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 18:23:34 2026

@author: benoc

My attempt at a photometry pipeline
"""
from astropy.io import fits
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import numpy as np
from datetime import datetime 


class Photometry_Pipeline:
    
    def __init__(self, save_file):
        self.MOD_NAME = 'Photometry_Pipeline'
        self.ERR_BASE = 'ERROR: ' + self.MOD_NAME
        self.FUNC_NAME = '.__init__()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            self.save_file = save_file
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    #Test opening a fits file
    def open_fits(self, file_path):
        self.FUNC_NAME = '.open_fits()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try: 
            #Closing fits automatically when out of with statement
            with fits.open(file_path) as hdu:
                data = hdu[0].data
            return data
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    #Function to create a master median file
    def Median_Combine(self, file_directory):
        self.FUNC_NAME = '.Median_Combine()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            source_dir = Path(file_directory)
            files = source_dir.iterdir()
            big_array = []
            for file in files:
                big_array.append(self.open_fits(file))
            big_array = np.array(big_array)
            master_array = np.zeros_like(big_array[0])
            np.median(big_array, axis = 0, out = master_array)
            
            if self.save_file == True:
                np.savetxt(f'Median_Combine_Output_{datetime.today().isoformat().replace(":","")}.txt', master_array)
            return master_array
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
      
    #Function to create the Master_Dark file
    def Master_Dark(self, Dark_Directory, Bias_Directory):
        self.FUNC_NAME = '.Master_Dark()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            
            source_dir = Path(Dark_Directory)
            files = source_dir.iterdir()
            big_array = []
            for file in files:
                big_array.append(self.open_fits(file))
            big_array = np.array(big_array)
            master_array = np.zeros_like(big_array[0])

            if hasattr(self, 'Bias_Master_Array') != True:
                self.Bias_Master_Array = self.Median_Combine(Bias_Directory)
            
            for i in range(0, len(big_array)):
                big_array[i] = big_array[i] - self.Bias_Master_Array
            np.median(big_array, axis = 0, out = master_array)
            if self.save_file == True:
                np.savetxt(f'Master_Dark_Output_{datetime.today().isoformat().replace(":","")}.txt', master_array)
            return master_array
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
        
    
