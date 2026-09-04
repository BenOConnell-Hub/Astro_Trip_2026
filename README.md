This README is an explanation of how to use the Photometry_Pipeline.py.

To use this to create processed image files all you need to do is the following:
PP = Photometry_Pipeline.Photometry_Pipeline(Exposure_Time=10, 
                                             Filter_Type=None,
                                             Raw_Directory = Raw_Directory,
                                             Flat_Directory = Flat_Directory,
                                             Bias_Directory = Bias_Directory,
                                             Dark_Directory = Dark_Directory.
                                             File_Path_Highest_Exp_Dark = File_Path_Highest_Exp_Dark,
                                             Highest_Exp_Time = Highest_Exp_Time)
PP.Reduce_Images(Observed_Object)

The exposure time is the exposure time of the raws, make sure the dark directory contains a dark with the same exposure time.
It does not need to be a master dark, the code will make the master dark. 

Only change the filter type from None if you want to process a specific filter only, otherwise the code will process every 
raw file regardless of filter, if the corresponding flats exist. Again, the flats do not need to be master flats, just be a 
directory with the flats of the filters you want to process. The code will create the master flats.

The Raw_Directory is the directory which contains the images you want to process.
The Flat_Direectory is the directory which contains the Flats.
The Bias_Direectory is the directory which contains the Bias.
The Dark_Direectory is the directory which contains the Darks.

File_Path_Highest_Exp_Dark is the file path to the master dark with the largest exposure time which is needed to calculate the
master flats.
Highest_Exp_Time is the exposure time of the master dark you specified above.

The code will output the master files for each acquisition type in their respective directories under the folder Master_Files.
The process images files are in the raw directory under the folder Processed_Files.

All files are .fits files. 

Observed_Object only changes the name of the saved .fits processed files.



