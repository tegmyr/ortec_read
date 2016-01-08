# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 21:54:00 2016

@author: Oscar Tegmyr
oscar.tegmyr@gmail.com

For more infor

==== Binary header structure ===
0  2 Must be 1
2  2 MCA number or Detector number
4  2 Segment number (set to 1 in UMCBI)
6  2 ASCII seconds of start time
8  4 Real Time (increments of 20 ms) (4-byte integer)
12 4 Live Time (increments of 20 ms) (4-byte integer)
16 8 Start date as ASCII DDMMMYY* or binary zeros, if not known. The *
     character should be ignored if it is not a "1". If it is a "1", it 
     indicates the data is after the year 2000.
24 4 Start time as ASCII HHMM or binary zeros, if not known (see Byte 6 above)
28 2 Channel offset of data
30 2 Number of channels (length of data)
"""
import struct
import sys
import spectrum_analysis as sa
#import os.path
import numpy as np 
import matplotlib.pyplot as plt

class gamma_data:
    def __init__(self,filename='A1_0_5cm.Chn', mca_bins=4096):
        
        try:
            self.infile         = open(filename, "rb")
            self.read_chn_binary(mca_bins)
        except ValueError:
            print('Unable to load file ' + filename)

     
    def read_chn_binary(self,mca_bins):       # We start by reading the 32 byte header
        self.version            = struct.unpack('h', self.infile.read(2))[0]
        self.mca_detector_id    = struct.unpack('h', self.infile.read(2))[0]
        self.segment_number     = struct.unpack('h', self.infile.read(2))[0]
        self.start_time_ss      = self.infile.read(2)
        self.real_time          = struct.unpack('I', self.infile.read(4))[0]
        self.live_time          = struct.unpack('I', self.infile.read(4))[0]
        self.start_date         = self.infile.read(8) #Ascii type date in 
                                #DDMMMYY* where * == 1 means 21th century
        self.start_time_hhmm    = self.infile.read(4)
        self.chan_offset        = struct.unpack('h', self.infile.read(2))[0]
        self.no_channels        = struct.unpack('h', self.infile.read(2))[0]    
        self.hist_array         = np.zeros(mca_bins) #Init hist_array 
        
        #Read the binary data
        for index in range(len(self.hist_array)):
            self.hist_array[index]= struct.unpack('I', self.infile.read(4))[0]
        self.infile.close()


if __name__ == '__main__':   
    if len(sys.argv) >1:
        filename = sys.argv[1]
    else: 
        filename = raw_input('Filename of binary, (including .bin): ')
    gamma_object = gamma_data(filename)
   
    x = range(len(gamma_object.hist_array))
    sa.peak_finder(gamma_object.hist_array)
#    plt.step(x, gamma_object.hist_array)
#    plt.show()
 