# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 15:45:36 2016

@author: oscaralmen
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress
import matplotlib.pyplot as plt
def fit_the_peak(en, array):
    pslope, pintercept = linreg(en, array)
    pmu = np.average(en, weights=array)

    pstd = 0.7
    pa = np.max(array)
    params = [pa, pmu, pstd, pslope, pintercept]
    coeff, var_matrix = curve_fit(gauss_lin, en, array, p0=params)
    print coeff
#    print var_matrix
    x = np.linspace(en[0], en[-1],num=500)
    
    plt.plot(x, gauss_lin(x, *coeff))    
    plt.plot(x, x*coeff[3]+coeff[4])
   
   
   
   
   
    
def linreg(en,array):
    x = np.append(en[:3],en[-3:])
    y = np.append(array[:3],array[-3:])
    values = linregress(x,y)
    return values[0], values[1] 


    
    
#    coeff, var_matrix = curve_fit(gauss, en, array, p0=p0)
    
    
    
    

def gauss_lin(x, *p):
    A, mu, sigma, slope, intercept = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2)) +x*slope + intercept

# p0 is the initial guess for the fitting coefficients (A, mu and sigma above)
#p0 = [1., 0., 1.]
#
#
#
#
#
#
#
#
#
## Get the fitted curve
#hist_fit = gauss(bin_centres, *coeff)
#
#plt.plot(bin_centres, hist, label='Test data')
#plt.plot(bin_centres, hist_fit, label='Fitted data')
#
## Finally, lets get the fitting parameters, i.e. the mean and standard deviation:
#print 'Fitted mean = ', coeff[1]
#print 'Fitted standard deviation = ', coeff[2]
#
#plt.show()
