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
import time
import astropy
import os


class Photometry_Pipeline:
    
    #Initilisation Function
    def __init__(self, 
                 Exposure_Time = None, 
                 Filter_Type = None,
                 Raw_Directory = None, 
                 Flat_Directory = None, 
                 Bias_Directory = None, 
                 Dark_Directory = None,
                 File_Path_Highest_Exp_Dark = None,
                 Highest_Exp_Time = None):
        
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
            
            self.Raw_Directory = Raw_Directory
            self.Flat_Directory = Flat_Directory
            self.Bias_Directory = Bias_Directory
            self.Dark_Directory = Dark_Directory
            
            self._initialise_file_dictionary(Flat_Directory, 'Flat')
            self._initialise_filter_type_dictionary(Flat_Directory, 'Flat')
            self._initialise_exp_time_dictionary(Dark_Directory, 'Dark')
            self._initialise_file_dictionary(Dark_Directory, 'Dark')
            self._initialise_file_dictionary(Raw_Directory, 'Raw')
            self._initialise_filter_type_dictionary(Raw_Directory, 'Raw')
            
            self.File_Path_Highest_Exp_Dark = File_Path_Highest_Exp_Dark
            self.Highest_Exp_Time = Highest_Exp_Time
            
            if self.Filter_Type == None:
                self.Specified_Filter = False
            else:
                self.Specified_Filter = True
            
            
            
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
                        
                elif acquisition_type == 'Raw':
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
    
    def Calculate_Bias_Combine(self):
        self.FUNC_NAME = '.Calculate_Bias_Combine()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            start_time = time.time()
            source_dir = Path(self.Bias_Directory)
            files = source_dir.glob('*.fits')
            files = list(files)
            big_array = []
            
            no_of_files = len(files)
            
            counter = 0
            bigger_array = []
            for file in files:
                data = self.open_fits(file)
                data = np.where(data>40000, np.nan, data)
                big_array.append(data)
                if counter%25 == 0 or counter == (no_of_files-1):
                    big_array = np.array(big_array)
                    master_array = np.zeros_like(big_array[0])
                    np.nanmedian(big_array, axis = 0, out = master_array)
                    big_array = []
                    bigger_array.append(master_array)
                counter += 1
            
            del(big_array)
            bigger_array = np.array(bigger_array)
            if len(bigger_array) == 1:
                finished_array = bigger_array[0]
            
            else:
                finished_array = np.nanmedian(bigger_array, axis = 0)
            
            del(bigger_array)
            del(master_array)
            hdu = fits.PrimaryHDU(data = finished_array)
            hdul = fits.HDUList([hdu])
            
            master_directory = Path(self.Bias_Directory + 'Master_Files/')
            
            if not master_directory.is_dir():
                os.mkdir(self.Bias_Directory + 'Master_Files/')
            print('I got here')
            hdul.writeto(self.Bias_Directory + 'Master_Files/' + 'Master_Bias.fits')
            print(f'Bias Master Array Complete! Time taken: {time.time() - start_time:.3f}s')
            return finished_array
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    #Function to create a master median file
    def Bias_Combine(self):
        self.FUNC_NAME = '.Bias_Combine()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            start_time = time.time()
            
            master_directory = Path(self.Bias_Directory  + 'Master_Files/')
            if master_directory.is_dir():
                master_array_file = Path(self.Bias_Directory + 'Master_Files/' + 'Master_Bias.fits')
                #Check if it exists, if it does return it
                if master_array_file.is_file():
                    print('A bias file already exists!')
                    with fits.open(self.Bias_Directory + 'Master_Files/' + 'Master_Bias.fits') as hdu:
                        data = hdu[0].data
                    print(f'Bias Master Array Complete! Time taken: {time.time() - start_time:.3f}s')
                    return data

                else:
                    print('No existing file found, creating Bias file')
                    return self.Calculate_Bias_Combine()
                
            #Otherwise make that file
            else:
                print('No existing file found, creating Bias file')
                return self.Calculate_Bias_Combine()
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
      
    #Function to create the Master Array file
    def Dark_Calculate_Master_Array(self):
        self.FUNC_NAME = '.Dark_Calculate_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            start_time = time.time()
            
            if hasattr(self, 'Bias_Master_Array') != True:
                self.Bias_Master_Array = self.Bias_Combine()
                
            if self.Exposure_Time == None:
                #Loop over exposure times
                for exp_time in self.Exposure_Time_Dictionary['Dark']:
                    big_array = []
                    
                    no_of_files = len(self.File_Dictionary['Dark'][exp_time])
                    
                    counter = 0
                    bigger_array = []
                    #Loop over the files
                    for file in self.File_Dictionary['Dark'][exp_time]:
                        data = self.open_fits(file)
                        data = np.where(data>40000, np.nan, data)
                        big_array.append(data)
                        if counter%25 == 0 or counter == (no_of_files-1):
                            big_array = np.array(big_array)
                            master_array = np.zeros_like(big_array[0])
                            for i in range(0,len(big_array)):
                                big_array[i] = np.subtract(big_array[i], np.array(self.Bias_Master_Array))
                            
                            np.nanmedian(big_array, axis = 0, out = master_array)
                            big_array = []
                            bigger_array.append(master_array)
                        counter += 1
                    del(big_array)
                    del(master_array)
                    
                    bigger_array = np.array(bigger_array)
                    if len(bigger_array) == 1:
                        finished_array = bigger_array[0]
                    
                    else:
                        finished_array = np.nanmedian(bigger_array, axis = 0)
                    
                    del(bigger_array)
                            
                    hdu = fits.PrimaryHDU(data = finished_array)
                    hdul = fits.HDUList([hdu])
                    
                    master_directory = Path(self.Dark_Directory + 'Master_Files/')
                    
                    if not master_directory.is_dir():
                        os.mkdir(self.Dark_Directory + 'Master_Files/')
                    
                    hdul.writeto(self.Dark_Directory + 'Master_Files/' + f'Master_Dark_{str(float(self.Exposure_Time)).replace(".","_")}.fits')
                    del(master_array)
                    print('IM BRICKED UP')
                    print(f'Master Dark for {exp_time} array complete! Time taken: {time.time() - start_time:.3f}s')
                    
                    return None
            else:
                big_array = []
                
                no_of_files = len(self.File_Dictionary['Dark'][self.Exposure_Time])
                
                counter = 0
                bigger_array = []
                #Loop over the files
                for file in self.File_Dictionary['Dark'][self.Exposure_Time]:
                    data = self.open_fits(file)
                    data = np.where(data>40000, np.nan, data)
                    big_array.append(data)
                    if counter%25 == 0 or counter == (no_of_files-1):
                        big_array = np.array(big_array)
                        master_array = np.zeros_like(big_array[0])
                        for i in range(0,len(big_array)):
                            big_array[i] = np.subtract(big_array[i], np.array(self.Bias_Master_Array))
            
                        np.nanmedian(big_array, axis = 0, out = master_array)
                        big_array = []
                        bigger_array.append(master_array)
                    counter += 1
                del(big_array)
                del(master_array)
                
                bigger_array = np.array(bigger_array)
                if len(bigger_array) == 1:
                    finished_array = bigger_array[0]
                
                else:
                    finished_array = np.nanmedian(bigger_array, axis = 0)
                
                del(bigger_array)
                        
                hdu = fits.PrimaryHDU(data = finished_array)
                hdul = fits.HDUList([hdu])
                
                master_directory = Path(self.Dark_Directory + 'Master_Files/')
                
                if not master_directory.is_dir():
                    os.mkdir(self.Dark_Directory + 'Master_Files/')
                
                hdul.writeto(self.Dark_Directory + 'Master_Files/' + f'Master_Dark_{str(float(self.Exposure_Time)).replace(".","_")}.fits')
                
                print(f'Master Dark for {self.Exposure_Time} array complete! Time taken: {time.time() - start_time:.3f}s')
                
                return finished_array
                
            
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Dark_Master_Array(self):
        self.FUNC_NAME = '.Dark_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try: 
            #This is pure calculation to use reduction specify a time exposure
            if self.Exposure_Time in self.Exposure_Time_Dictionary['Dark']:
                master_directory = Path(self.Dark_Directory + 'Master_Files/')
                if master_directory.is_dir():
                    master_array_file = Path(self.Dark_Directory + 'Master_Files/' + f'Master_Dark_{str(float(self.Exposure_Time)).replace(".","_")}.fits')
                    #Check if it exists, if it does return it
                    if master_array_file.is_file():
                        print(f'A file for a Dark with an exposure time of {self.Exposure_Time} exists!')
                        with fits.open(self.Dark_Directory + 'Master_Files/' + f'Master_Dark_{str(float(self.Exposure_Time)).replace(".","_")}.fits') as hdu:
                            data = hdu[0].data
                        return data
                    else:
                        print(f'No file for Dark with an exposure time of {self.Exposure_Time} exists, creating file!')
                        return self.Dark_Calculate_Master_Array()
                else:
                    print(f'No file for Dark with an exposure time of {self.Exposure_Time} exists, creating file!')
                    return self.Dark_Calculate_Master_Array()
            
            elif self.Exposure_Time == None:
                for exp_time in self.Exposure_Time_Dictionary['Dark']:
                    master_array_file = Path(self.Dark_Directory + f'Master_Dark_{str(exp_time).replace(".","_")}.txt')
                    #Check if it exists, if it does return it
                    if master_array_file.is_file():
                        print(f'A file for Dark for an exposure time of {exp_time} exists!')
                    else:
                        print(f'No file for Dark for an exposure time of {exp_time} exists, creating file!')
                        self.Calculate_Dark_Master_Array()
            else:
                self.ERR_STATEMENT += f'\nThere is no dark available in this directory with an exposure time of {self.Exposure_Time}'
                raise Exception
                
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Calculate_Flat_Master_Array(self):
        self.FUNC_NAME = '.Calculate_Flat_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            start_time = time.time()
            with fits.open(self.File_Path_Highest_Exp_Dark) as hdu:
                dark_data = hdu[0].data
            dark_data = dark_data/self.Highest_Exp_Time
            
            if hasattr(self, 'Bias_Master_Array') != True:
                self.Bias_Master_Array = self.Bias_Combine()
            
            if self.Filter_Type == None:
                for filt in self.Filter_Type_Dictionary['Flat']:
                    big_array = []
                    no_of_files = len(self.File_Dictionary['Flat'][filt])
                    
                    counter = 0
                    bigger_array = []
                    for file in self.File_Dictionary['Flat'][filt]:
                        with fits.open(file) as hdu:
                            data = hdu[0].data
                            exp_time = hdu[0].header['EXPTIME']
                        
                        data = np.where(data>40000, np.nan, data)
                        data = data/exp_time - self.Bias_Master_Array/exp_time - dark_data
                        big_array.append(data)
                        if counter%25 == 0 or counter == (no_of_files - 1):
                            big_array = np.array(big_array)
                            master_array = np.zeros_like(big_array[0])
                            np.nanmedian(big_array, axis = 0, out = master_array)
                            big_array = []
                            bigger_array.append(master_array)
                        counter += 1
                    del(big_array)
                    del(master_array)
                    
                    bigger_array = np.array(bigger_array)
                    if len(bigger_array) == 1:
                        finished_array = bigger_array[0]
                    
                    else:
                        finished_array = np.nanmedian(bigger_array, axis = 0)
                    
                    del(bigger_array)
                    finished_array = finished_array/np.nanmax(finished_array)
                    
                    hdu = fits.PrimaryHDU(data = finished_array)
                    hdul = fits.HDUList([hdu])
                    
                    master_directory = Path(self.Flat_Directory + 'Master_Files/')
                    
                    if not master_directory.is_dir():
                        os.mkdir(self.Flat_Directory + 'Master_Files/')
                    
                    hdul.writeto(self.Flat_Directory + 'Master_Files/' + f'Master_Flat_{filt}.fits')
                    
                    print(f'Master flat for filter {filt} array complete! Time taken: {time.time() - start_time:.3f}s')
                    return None
                
            else:
                big_array = []
                no_of_files = len(self.File_Dictionary['Flat'][self.Filter_Type])
                
                counter = 0
                bigger_array = []
                for file in self.File_Dictionary['Flat'][self.Filter_Type]:
                    with fits.open(file) as hdu:
                        data = hdu[0].data
                        exp_time = hdu[0].header['EXPTIME']
                    
                    data = np.where(data>40000, np.nan, data)
                    data = data/exp_time - self.Bias_Master_Array/exp_time - dark_data
                    big_array.append(data)
                    if counter%25 == 0 or counter == (no_of_files - 1):
                        big_array = np.array(big_array)
                        master_array = np.zeros_like(big_array[0])
                        np.nanmedian(big_array, axis = 0, out = master_array)
                        big_array = []
                        bigger_array.append(master_array)
                    counter += 1
                del(big_array)
                del(master_array)
                
                bigger_array = np.array(bigger_array)
                if len(bigger_array) == 1:
                    finished_array = bigger_array[0]
                
                else:
                    finished_array = np.nanmedian(bigger_array, axis = 0)
                
                del(bigger_array)
                
                finished_array = finished_array/np.nanmax(finished_array)
                
                hdu = fits.PrimaryHDU(data = finished_array)
                hdul = fits.HDUList([hdu])
                
                master_directory = Path(self.Flat_Directory + 'Master_Files/')
                
                if not master_directory.is_dir():
                    os.mkdir(self.Flat_Directory + 'Master_Files/')
                
                hdul.writeto(self.Flat_Directory + 'Master_Files/' + f'Master_Flat_{self.Filter_Type}.fits')
                
                print(f'Master flat for filter {self.Filter_Type} array complete! Time taken: {time.time() - start_time:.3f}s')
                return finished_array
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Flat_Master_Array(self):
        self.FUNC_NAME = '.Flat_Master_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            #This is pure calculation to use reduction specify a time exposure
            if self.Filter_Type in self.Filter_Type_Dictionary['Flat']:
                master_directory = Path(self.Flat_Directory + 'Master_Files/')
                if master_directory.is_dir():
                    master_array_file = Path(self.Flat_Directory + 'Master_Files/' + f'Master_Flat_{self.Filter_Type}.fits')
                    #Check if it exists, if it does return it
                    if master_array_file.is_file():
                        print(f'A file for a flat with a {self.Filter_Type} filter exists!')
                        with fits.open(self.Flat_Directory + 'Master_Files/' + f'Master_Flat_{self.Filter_Type}.fits') as hdu:
                            data = hdu[0].data
                        return data
                    
                    else:
                        print(f'No file for a flat with a {self.Filter_Type} filter exists, creating file!')
                        return self.Calculate_Flat_Master_Array()
                else:
                    print(f'No file for a flat with a {self.Filter_Type} filter exists, creating file!')
                    return self.Calculate_Flat_Master_Array()
            
            elif self.Filter_Type == None:
                for filt in self.File_Dictionary['Flat']:
                    master_array_file = Path(self.Flat_Directory + f'Master_Flat_{filt}.txt')
                    #Check if it exists, if it does return it
                    if master_array_file.is_file():
                        print(f'A file for a flat with a {filt} filter exists!')
        
                    else:
                        print(f'No file for a flat with a {filt} filter exists, creating file!')
                        self.Calculate_Flat_Master_Array()
            
            else:
                self.ERR_STATEMENT += f'\nThere is no flat available in this directory with a filter of {self.Filter_Type}'
                raise Exception
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
        
    def Calculate_Science_Array(self, 
                      Raw_File_Path = None):
        self.FUNC_NAME = '.Calculate_Science_Array()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            if Raw_File_Path == None:
                self.ERR_STATEMENT = self.ERR_STATEMENT + '\nPlease enter the file path of the raw file.'
                raise Exception 
                
            
            if self.Exposure_Time == None:
                self.Flat_Master_Array()
                self.Dark_Master_Array()
            
            else:
                print('Calculating/Importing Master Flat Array')
                Master_Flat_Array = self.Flat_Master_Array()
                '''
                with fits.open('flat_r.hcm') as hdu:
                    Master_Flat_Array = hdu[1].data
                    '''
                print('Importing Raw array')
                Raw_Array = self.open_fits(Raw_File_Path)
                print('Calculating/Importing Master Dark Array')
                Master_Dark_Array = self.Dark_Master_Array()
                print('Finished all imports')
                if hasattr(self, 'Bias_Master_Array') != True:
                    self.Bias_Master_Array = self.Bias_Combine()
                
                #norm = astropy.visualization.simple_norm(Raw_Array, percent = 90)
                #plt.imshow(Raw_Array, cmap = 'Greys_r', norm = norm)
                #plt.title('Raw Array')
                #plt.show()
            
                Science_Array = Raw_Array - self.Bias_Master_Array
                #norm = astropy.visualization.simple_norm(Science_Array, percent = 90)
                #plt.imshow(Science_Array, cmap = 'Greys_r', norm = norm)
                #plt.title('Science Array after Master Bias')
                #plt.show()
                
                Science_Array = Science_Array - Master_Dark_Array
                #norm = astropy.visualization.simple_norm(Science_Array, percent = 90)
                #plt.imshow(Science_Array, cmap = 'Greys_r', norm = norm)
                #plt.title('Science Array after Master Dark')
                #plt.show()
                
                Science_Array = np.where(Science_Array>40000, np.nan, Science_Array)
                Science_Array = np.divide(Science_Array,Master_Flat_Array)
                norm = astropy.visualization.simple_norm(Science_Array, percent = 90, )
                #plt.imshow(Science_Array, cmap = 'Greys_r', norm = norm)
                #plt.title('Science Array after Master Flat')
                #plt.show()
                
                return Science_Array
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Calculate_Reduce_Images(self, Object, filt):
        self.FUNC_NAME = '.Calculate_Reduce_Images()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        try:
            big_array = []
            self.Filter_Type = filt
            for file in self.File_Dictionary['Raw'][filt]:
                Single_image = self.Calculate_Science_Array(file)
                big_array.append(Single_image)
            big_array = np.array(big_array)
            master_array = np.zeros_like(big_array[0])
            np.nanmedian(big_array, axis = 0, out = master_array)
            del(big_array)
            
            norm = astropy.visualization.simple_norm(master_array, percent=90)
            plt.imshow(master_array, cmap = 'Greys_r', norm = norm)
            plt.title(f'Processed image of {Object} filter: {filt}')
            plt.show()
            
            hdu = fits.PrimaryHDU(data = master_array)
            hdul = fits.HDUList([hdu])
            
            processed_directory = Path(self.Raw_Directory + 'Processed_Files/')
            
            if not processed_directory.is_dir():
                os.mkdir(self.Raw_Directory + 'Processed_Files/')
            
            hdul.writeto(self.Raw_Directory + 'Processed_Files/' + f'{Object}_{filt}_{self.Exposure_Time}.fits', overwrite = True)
        
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
    
    def Reduce_Images(self, Object):
        self.FUNC_NAME = '.Reduce_Images()'
        self.ERR_STATEMENT = self.ERR_BASE + self.FUNC_NAME
        
        try:
            if hasattr(self, 'Bias_Master_Array') != True:
                self.Bias_Master_Array = self.Bias_Combine()
            if self.Specified_Filter == False:
                for filt in self.Filter_Type_Dictionary['Raw']:
                    self.Calculate_Reduce_Images(Object, filt)
                    
            else:
                self.Calculate_Reduce_Images(Object, self.Filter_Type)
        except Exception as e:
            print(self.ERR_STATEMENT)
            print(e)
        
    
