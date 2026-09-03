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
import time


class Photometry_Pipeline:
    
    #Initilisation Function
    def __init__(self, save_file = False, Exposure_Time = None):
        #Error Handling
        self.MOD_NAME = 'Photometry_Pipeline'
        self.ERR_BASE = 'ERROR: ' + self.MOD_NAME
        self.FUNC_NAME = '.__init__()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            self.save_file = save_file
            self.Exposure_Time = Exposure_Time
            self.File_Dictionary = {}
            self.Exposure_Time_Dictionary = {}
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    #Initilise Exposure Time Dictionary to store all the available exposure times for each acquisition time
    def _initialise_exp_time_dictionary(self, Directory, acquisition_type):
        self.FUNC_NAME = '._initialise_exp_time_directory()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            self.Exposure_Time_Dictionary[acquisition_type] = []
            
            source_dir = Path(Directory)
            files = source_dir.glob('*.fits')
            for file in files:
                with fits.open(file) as hdu:
                    file_exp_time = hdu[0].header['EXPTIME']
                    
                if self.Exposure_Time == None:
                    if file_exp_time not in self.Exposure_Time_Dictionary[acquisition_type]:
                        self.Exposure_Time_Dictionary[acquisition_type].append(file_exp_time)
                else:
                    if file_exp_time not in self.Exposure_Time_Dictionary[acquisition_type] and self.Exposure_Time == file_exp_time:
                        self.Exposure_Time_Dictionary[acquisition_type].append(file_exp_time)
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    #Initilise File Dictionary to store all the files in terms of exposure time to reduce memory allocation
    def _initialise_file_dictionary(self, Directory, acquisition_type):
        self.FUNC_NAME = '._initialise_file_dictionary()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            self.File_Dictionary[acquisition_type] = {}
            source_dir = Path(Directory)
            files = source_dir.glob('*.fits')
            for file in files:
                with fits.open(file) as hdu:
                    file_exp_time = hdu[0].header['EXPTIME']
                        
                if file_exp_time in self.File_Dictionary[acquisition_type]:
                    self.File_Dictionary[acquisition_type][file_exp_time].append(file)
                else:
                    self.File_Dictionary[acquisition_type][file_exp_time] = [file]
                            
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
    def Bias_Combine(self, bias_directory):
        self.FUNC_NAME = '.Median_Combine()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            start_time = time.time()
            bias_file = Path(bias_directory + 'Master_Bias_File.txt')
            #Check if it exists, if it does return it
            if bias_file.is_file():
                print('Existing bias file found, reusing file!')
                print(f'Bias Master Array Complete! Time taken: {time.time() - start_time:.3f}s')
                return np.loadtxt(bias_directory + 'Master_Bias_File.txt')
            #Otherwise make that file
            else:
                print('No existing file found, creating Bias file')
                source_dir = Path(bias_directory)
                files = source_dir.iterdir()
                big_array = []
                
                for file in files:
                    data = self.open_fits(file)
                    data = np.where(data>40000, np.nan, data)
                    big_array.append(data)
                    
                big_array = np.array(big_array)
                master_array = np.zeros_like(big_array[0])
                np.nanmedian(big_array, axis = 0, out = master_array)
                del(big_array)
                
                np.savetxt(bias_directory + 'Master_Bias_File.txt', master_array)
                print(f'Bias Master Array Complete! Time taken: {time.time() - start_time:.3f}s')
                return master_array
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
      
    #Function to create the Master Array file
    def Calculate_Master_Array(self, Array_Directory = None, Bias_Directory = None, acquisition_type = None):
        self.FUNC_NAME = '.Calculate_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            if Array_Directory == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the directory of the files you want to master.'
                raise Exception 
            if Bias_Directory == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the directory of the bias files.'
                raise Exception
            if acquisition_type == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the acquisition type of the files you want to master.'
                raise Exception
            
            start_time = time.time()
            
            #Loop over exposure times
            for exp_time in self.Exposure_Time_Dictionary[acquisition_type]:
                big_array = []
                #Loop over the files
                for file in self.File_Dictionary[acquisition_type][exp_time]:
                    data = self.open_fits(file)
                    data = np.where(data>40000, np.nan, data)
                    big_array.append(data)
                    
                big_array = np.array(big_array)
                master_array = np.zeros_like(big_array[0])
    
                if hasattr(self, 'Bias_Master_Array') != True:
                    self.Bias_Master_Array = self.Bias_Combine(Bias_Directory)
                
                for i in range(0,len(big_array)):
                    big_array[i] = np.subtract(big_array[i], np.array(self.Bias_Master_Array))
                    
   
                np.nanmedian(big_array, axis = 0, out = master_array)
                del(big_array)
                if acquisition_type.lower() == 'flat':
                    master_array = master_array/np.max(master_array)
                
                np.savetxt(Array_Directory + f'Master_{acquisition_type}_{str(exp_time).replace(".","_")}.txt', master_array)
                del(master_array)
                print(f'Master {acquisition_type} for {exp_time} array complete! Time taken: {time.time() - start_time:.3f}s')
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Master_Array(self, Directory, Bias_Directory, acquisition_type):
        self.FUNC_NAME = '.Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try: 
            if self.Exposure_Time == None:
                #This is pure calculation to use reduction specify a time exposure
                self._initialise_file_dictionary(Directory, acquisition_type)
                for exp_time in self.Exposure_Time_Dictionary[acquisition_type]:
                    master_array_file = Path(Directory + f'Master_{acquisition_type}_{str(exp_time).replace(".","_")}.txt')
                    #Check if it exists, if it does return it
                    if master_array_file.is_file():
                        print(f'A file for {acquisition_type} for an exposure time of {exp_time} exists!')
                    else:
                        print(f'No file for {acquisition_type} for an exposure time of {exp_time} exists, creating file!')
                        self.Calculate_Master_Array(Directory, Bias_Directory, acquisition_type)
            else:
                p = 1
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
        
    def Science_Array(self, 
                      Raw_Directory = None, 
                      Dark_Directory = None, 
                      Bias_Directory = None, 
                      Flat_Directory = None):
        self.FUNC_NAME = '.Science_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            if Raw_Directory == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the directory of the raw files.'
                raise Exception 
            if Bias_Directory == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the directory of the bias files.'
                raise Exception
            if Dark_Directory == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the directory of the dark files.'
                raise Exception
            if Flat_Directory == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the directory of the bias files.'
                raise Exception
                
            #self._initialise_exp_time_dictionary(Raw_Directory, 'Raw')
            self._initialise_exp_time_dictionary(Dark_Directory, 'Dark')
            #self._initialise_exp_time_dictionary(Flat_Directory, 'Flat')
            
            if self.Exposure_Time == None:
                #self.Master_Array(Flat_Directory, Bias_Directory, 'Flat')
                #self.Master_Array(Raw_Directory, Bias_Directory, 'Raw')
                self.Master_Array(Dark_Directory, Bias_Directory, 'Dark')
            
            else:
                Master_Flat_Array = self.Master_Array(Flat_Directory, Bias_Directory, 'Flat')
                Master_Raw_Array = self.Master_Array(Raw_Directory, Bias_Directory, 'Raw')
                Master_Dark_Array = self.Master_Array(Dark_Directory, Bias_Directory, 'Dark')
            
                Science_Array = (Master_Raw_Array - Master_Dark_Array)/(Master_Flat_Array - Master_Dark_Array)
                return Science_Array
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
        
    
