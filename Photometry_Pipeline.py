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
from astropy.visualization import SimpleNorm
import astropy


class Photometry_Pipeline:
    
    #Initilisation Function
    def __init__(self, Exposure_Time = None, Filter_Type = None):
        #Error Handling
        self.MOD_NAME = 'Photometry_Pipeline'
        self.ERR_BASE = 'ERROR: ' + self.MOD_NAME
        self.FUNC_NAME = '.__init__()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            self.Exposure_Time = Exposure_Time
            self.Filter_Type = Filter_Type
            self.File_Dictionary = {}
            self.Exposure_Time_Dictionary = {}
            self.Filter_Type_Dictionary = {}
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    #Initilise Filter Times for Flats
    def _initialise_filter_type_dictionary(self, Directory, acquisition_type):
        self.FUNC_NAME = '._initiliase_filter_time_dictionary()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            self.Filter_Type_Dictionary[acquisition_type] = []
            source_dir = Path(Directory)
            files = source_dir.glob('*.fits')
            for file in files:
                with fits.open(file) as hdu:
                    filt = hdu[0].header['INSTFILT']
                if filt not in self.Filter_Type_Dictionary[acquisition_type]:
                    self.Filter_Type_Dictionary[acquisition_type].append(filt)
        
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
            if acquisition_type not in self.File_Dictionary:
                self.File_Dictionary[acquisition_type] = {}
            source_dir = Path(Directory)
            files = source_dir.glob('*.fits')
            for file in files:
                with fits.open(file) as hdu:
                    file_exp_time = hdu[0].header['EXPTIME']
                    filt = hdu[0].header['INSTFILT']
                if acquisition_type == 'Dark':
                    if file_exp_time in self.File_Dictionary[acquisition_type]:
                        self.File_Dictionary[acquisition_type][file_exp_time].append(file)
                    else:
                        self.File_Dictionary[acquisition_type][file_exp_time] = [file]
                
                elif acquisition_type == 'Flat':
                    if filt in self.File_Dictionary[acquisition_type]:
                        self.File_Dictionary[acquisition_type][filt].append(file)
                    else:
                        self.File_Dictionary[acquisition_type][filt] = [file]
                
                else:
                    self.ERR_STATEMENT += '\nInvalid acquisition type entered!'
                    raise Exception
                            
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
        self.FUNC_NAME = '.Bias_Combine()'
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
    def Dark_Calculate_Master_Array(self, Array_Directory = None, Bias_Directory = None):
        self.FUNC_NAME = '.Dark_Calculate_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            if Array_Directory == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the directory of the files you want to master.'
                raise Exception 
            if Bias_Directory == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the directory of the bias files.'
                raise Exception
            
            start_time = time.time()
            
            if hasattr(self, 'Bias_Master_Array') != True:
                self.Bias_Master_Array = self.Bias_Combine(Bias_Directory)
                
            if self.Exposure_Time == None:
                #Loop over exposure times
                for exp_time in self.Exposure_Time_Dictionary['Dark']:
                    big_array = []
                    #Loop over the files
                    for file in self.File_Dictionary['Dark'][exp_time]:
                        data = self.open_fits(file)
                        data = np.where(data>40000, np.nan, data)
                        big_array.append(data)
                        
                    big_array = np.array(big_array)
                    master_array = np.zeros_like(big_array[0])
                    
                    for i in range(0,len(big_array)):
                        big_array[i] = np.subtract(big_array[i], np.array(self.Bias_Master_Array))
                        
       
                    np.nanmedian(big_array, axis = 0, out = master_array)
                    del(big_array)
                    
                    np.savetxt(Array_Directory + f'Master_Dark_{str(exp_time).replace(".","_")}.txt', master_array)
                    del(master_array)
                    print(f'Master Dark for {exp_time} array complete! Time taken: {time.time() - start_time:.3f}s')
                    
                    return None
            else:
                big_array = []
                #Loop over the files
                for file in self.File_Dictionary['Dark'][self.Exposure_Time]:
                    data = self.open_fits(file)
                    data = np.where(data>40000, np.nan, data)
                    big_array.append(data)
                    
                big_array = np.array(big_array)
                master_array = np.zeros_like(big_array[0])
                
                for i in range(0,len(big_array)):
                    big_array[i] = np.subtract(big_array[i], np.array(self.Bias_Master_Array))
                    
   
                np.nanmedian(big_array, axis = 0, out = master_array)
                del(big_array)
                
                np.savetxt(Array_Directory + f'Master_Dark_{str(self.Exposure_Time).replace(".","_")}.txt', master_array)
                print(f'Master Dark for {self.Exposure_Time} array complete! Time taken: {time.time() - start_time:.3f}s')
                
                return master_array
                
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Dark_Master_Array(self, Directory, Bias_Directory):
        self.FUNC_NAME = '.Dark_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try: 
            #This is pure calculation to use reduction specify a time exposure
            self._initialise_exp_time_dictionary(Directory, 'Dark')
            self._initialise_file_dictionary(Directory, 'Dark')
            
            if self.Exposure_Time in self.Exposure_Time_Dictionary['Dark']:
                master_array_file = Path(Directory + f'Master_Dark_{str(self.Exposure_Time).replace(".","_")}.txt')
                #Check if it exists, if it does return it
                if master_array_file.is_file():
                    print(f'A file for Dark for an exposure time of {self.Exposure_Time} exists!')
                    return np.loadtxt(Directory + f'Master_Dark_{str(self.Exposure_Time).replace(".","_")}.txt')
                else:
                    print(f'No file for Dark for an exposure time of {self.Exposure_Time} exists, creating file!')
                    return self.Calculate_Dark_Master_Array(Directory, Bias_Directory)
            
            elif self.Exposure_Time == None:
                for exp_time in self.Exposure_Time_Dictionary['Dark']:
                    master_array_file = Path(Directory + f'Master_Dark_{str(exp_time).replace(".","_")}.txt')
                    #Check if it exists, if it does return it
                    if master_array_file.is_file():
                        print(f'A file for Dark for an exposure time of {exp_time} exists!')
                    else:
                        print(f'No file for Dark for an exposure time of {exp_time} exists, creating file!')
                        self.Calculate_Dark_Master_Array(Directory, Bias_Directory)
            else:
                self.ERR_STATEMENT += '\nThere is no dark available in this directory with an exposure time of {self.Exposure_Time}'
                raise Exception
                
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Calculate_Flat_Master_Array(self, Flat_Directory, Dark_Directory, Bias_Directory):
        self.FUNC_NAME = '.Calculate_Flat_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            start_time = time.time()
            dark_data = np.loadtxt(Dark_Directory + 'Master_Dark_15_0.txt')
            dark_data = dark_data/15
            
            if hasattr(self, 'Bias_Master_Array') != True:
                self.Bias_Master_Array = self.Bias_Combine(Bias_Directory)
            
            for filt in self.Filter_Type_Dictionary['Flat']:
                big_array = []
                for file in self.File_Dictionary['Flat'][filt]:
                    with fits.open(file) as hdu:
                        data = hdu[0].data
                        exp_time = hdu[0].header['EXPTIME']
                    
                    data = np.where(data>40000, np.nan, data)
                    data = data/exp_time - self.Bias_Master_Array/exp_time - dark_data
                    big_array.append(data)
                
                big_array = np.array(big_array)
                master_array = np.zeros_like(big_array[0])
                np.nanmedian(big_array, axis = 0, out = master_array)
                del(big_array)
                
                master_array = master_array/np.nanmax(master_array)
                
                np.savetxt(Flat_Directory + f'Master_Flat_{filt}.txt', master_array)
                print(f'Master flat for filter {filt} array complete! Time taken: {time.time() - start_time:.3f}s')
                return master_array
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Flat_Master_Array(self,Flat_Directory, Dark_Directory, Bias_Directory):
        self.FUNC_NAME = '.Flat_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            #This is pure calculation to use reduction specify a time exposure
            self._initialise_file_dictionary(Flat_Directory, 'Flat')
            self._initialise_filter_type_dictionary(Flat_Directory, 'Flat')
            
            if self.Filter_Type in self.Filter_Type_Dictionary['Flat']:
                master_array_file = Path(Flat_Directory + f'Master_Flat_{self.Filter_Type}.txt')
                #Check if it exists, if it does return it
                if master_array_file.is_file():
                    print(f'A file for a flat with a {self.Filter_Type} filter exists!')
                    return np.loadtxt(Flat_Directory + f'Master_Flat_{self.Filter_Type}.txt')
                else:
                    print(f'No file for a flat with a {self.Filter_Type} filter exists, creating file!')
                    return self.Calculate_Flat_Master_Array(Flat_Directory, Dark_Directory, Bias_Directory)
            
            elif self.Filter_Type == None:
                for filt in self.File_Dictionary['Flat']:
                    master_array_file = Path(Flat_Directory + f'Master_Flat_{filt}.txt')
                    #Check if it exists, if it does return it
                    if master_array_file.is_file():
                        print(f'A file for a flat with a {filt} filter exists!')
        
                    else:
                        print(f'No file for a flat with a {filt} filter exists, creating file!')
                        self.Calculate_Flat_Master_Array(Flat_Directory, Dark_Directory, Bias_Directory)
            
            else:
                self.ERR_STATEMENT += '\nThere is no flat available in this directory with a filter of {self.Filter_Type}'
                raise Exception
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
        
    def Science_Array(self, 
                      Raw_File_Path = None, 
                      Dark_Directory = None, 
                      Bias_Directory = None, 
                      Flat_Directory = None):
        self.FUNC_NAME = '.Science_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            if Raw_File_Path == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the file path of the raw file.'
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
                
            
            if self.Exposure_Time == None:
                self.Flat_Master_Array(Flat_Directory, Dark_Directory, Bias_Directory)
                self.Dark_Master_Array(Dark_Directory, Bias_Directory)
            
            else:
                print('Calculating/Importing Master Flat Array')
                Master_Flat_Array = self.Flat_Master_Array(Flat_Directory, Dark_Directory, Bias_Directory)
                '''
                with fits.open('flat_r.hcm') as hdu:
                    Master_Flat_Array = hdu[1].data
                    '''
                print('Importing Raw array')
                Raw_Array = self.open_fits(Raw_File_Path)
                print('Calculating/Importing Master Dark Array')
                Master_Dark_Array = self.Dark_Master_Array(Dark_Directory, Bias_Directory)
                print('Finished all imports')
                if hasattr(self, 'Bias_Master_Array') != True:
                    self.Bias_Master_Array = self.Bias_Combine(Bias_Directory)
                
                norm = astropy.visualization.simple_norm(Raw_Array, percent = 90)
                plt.imshow(Raw_Array, cmap = 'Greys_r', norm = norm)
                plt.title('Raw Array')
                plt.show()
            
                Science_Array = Raw_Array - self.Bias_Master_Array
                norm = astropy.visualization.simple_norm(Science_Array, percent = 90)
                plt.imshow(Science_Array, cmap = 'Greys_r', norm = norm)
                plt.title('Science Array after Master Bias')
                plt.show()
                
                Science_Array = Science_Array - Master_Dark_Array
                norm = astropy.visualization.simple_norm(Science_Array, percent = 90)
                plt.imshow(Science_Array, cmap = 'Greys_r', norm = norm)
                plt.title('Science Array after Master Dark')
                plt.show()
                
                Science_Array = np.where(Science_Array>40000, np.nan, Science_Array)
                Science_Array = np.divide(Science_Array,Master_Flat_Array)
                norm = astropy.visualization.simple_norm(Science_Array, percent = 90)
                plt.imshow(Science_Array, cmap = 'Greys_r', norm = norm)
                plt.title('Science Array after Master Flat')
                plt.show()
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
        
    
