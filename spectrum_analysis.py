# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 16:14:18 2016

@author: Oscar Tegmyr
oscar.tegmyr@gmail.com
"""
from numpy import ma, arange,exp,logical_or,abs
from scipy.signal import convolve, medfilt

def peak_finder(arr, smoothing=5, ddy_thresh=-300, dy0_thresh=5):
    array        = medfilt(arr, smoothing) 
    x            = arange(len(array))
    kernel       = [4, 0, -4]
    dY           = convolve(array, kernel, 'same') 
    ddy          = convolve(dY, kernel, 'same')
    falloff      = -15000*exp(-0.003*x) #This has to be worked on
    masked_array = ma.masked_where(logical_or(ddy>falloff+ddy_thresh, abs(dY) > dy0_thresh) , arr) 
    x_masked     = ma.array(x, mask=masked_array.mask)
    return ma.compressed(x_masked)
