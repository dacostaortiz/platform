# -*- coding: utf-8 -*-
"""
@author: Diego

Collins model belongs to him, http://www2.unb.ca/gge/Pubs/TR203.pdf
"""

import numpy as np
from skimage import io
import matplotlib.pyplot as plt
import pandas as pd
from sympy import *
import pyproj
import utils
import pymap3d
import rinex_reader 

t1_names = ["Latitude","P","T","e", "beta", "lambda"]
t2_names = ["Latitude","delta_P","delta_T","delta_e", "delta_beta", "delta_lambda"]
global t1 = pd.DataFrame(np.array([[15, 1013.25, 299.65, 26.31, 6.30*10**-3, 2.77],
                                     [30, 1017.25, 294.15, 21.79, 6.05*10**-3, 3.15],
                                     [45, 1015.75, 283.15, 11.66, 5.58*10**-3, 2.57],
                                     [60, 1011.75, 272.15,  6.78, 5.39*10**-3, 1.81],
                                     [75, 1013.00, 263.65,  4.11, 4.53*10**-3, 1.55]]), 
                           columns=t1_names)
global t2 = pd.DataFrame(np.array([[15,  0.00,  0.00, 0.00, 0.00*10**-3, 0.00], 
                                      [30, -3.75,  7.00, 8.85, 0.25*10**-3, 0.33],
                                      [45, -2.25, 11.00, 7.24, 0.32*10**-3, 0.46],
                                      [60, -1.75, 15.00, 5.36, 0.81*10**-3, 0.74],
                                      [75, -0.50, 14.50, 3.39, 0.62*10**-3, 0.30]]), 
                            columns = t2_names)

def par_value(lat, day):
    if lat > 0:
        Dmin = 28
    else:
        Dmin = 211
    eps0 = [] #mean epsilon
    epsd = [] #delta epsilon (seasonal variation) 
    for i in range(5):
        eps0.append(np.interp(lat, t1.ix[:,0], t1.ix[:,i+1]))
        epsd.append(np.interp(lat, t2.ix[:,0], t2.ix[:,i+1])*(np.cos((2*np.pi*(day-Dmin))/365.25)))
    epsilon = np.array(eps0)-np.array(epsd)
    return epsilon

def obliquityFactor(E):
    # E   : Satellite Elevation
    M = 1.001/sqrt(0.002001+np.sin(np.deg2rad(E))**2)
    return M

def CollinsTropModel(E,H,lat,day,P=None,T=None,e=None,beta=None,lamb=None):
    # E   : Satellite Elevation
    # H   : Receiver's Height about the sea level 
    # lat : Receiver's Latitude
    # day : Day of the year
    # t1  : Table of averages for parameters P,T,e,beta y lambda
    # t2  : Table with seasonal variations for parameters
    
    ######constants#######
    k1 = 77.604  # K/mbar
    k2 = 382000  # K²/mbar
    Rd = 287.054 # Kg*K
    gm = 9.784   # m/s²
    g  = 9.80665 # m/s²
    ######################
    epsilon = [P,T,e,beta,lamb]
    if any(i is None for i in epsilon): # if any value is None, compute and replace.
        epsilon_table = par_value(lat,day,t1,t2)
        for idx, val in enumerate(epsilon):
            if epsilon[idx] is None:
                epsilon[idx] = epsilon_table[idx]
    P = epsilon[0]
    T = epsilon[1]
    e = epsilon[2]
    beta = epsilon[3]
    lamb = epsilon[4]
    Trz0d = ((10**-6)*k1*Rd*P)/gm
    Trz0w = ((10**-6)*k2*Rd*e)/(((lamb+1)*gm-beta*Rd)*T)
    Trzd = ((1-((beta*H)/T))**(g/(Rd*beta)))*Trz0d
    Trzw = ((1-((beta*H)/T))**((((lamb+1)*g)/(Rd*beta))-1))*Trz0d
    M = obliquityFactor(E)
    #print "epsilon", epsilon
    #print "oblicuity factor:", M
    #print "Dry trop",Trz0d ,"Wet trop", Trz0w
    #print "at receiver's height, dry trop", Trzd, "wet trop", Trzw
    Tr = (Trzd + Trzw)*M
    return Tr
    
########################################################################

def ls_by_epoch(data,rec_pos,fix=None):
    ls_errs    = []
    ls_err_pos = []
    ls_pos     = []
    for i in data.TIME.unique():
        dataepoch = data[data.TIME==i]
        array_epoch = []
        for index, group in dataepoch.groupby("PRN"):
            array_epoch.append(group.as_matrix()[0])
        c1, pos, clocks = [],[],[]
        for e in array_epoch:
            c1.append(e[1]) 
            pos.append(e[14][:,0])
            clocks.append(e[13])
        if len(c1)>=4:
            ls_computed_pos,_,_,_   = compute_least_squares_position(np.array(pos),np.array(clocks), np.array(c1))
            ls_pos.append(ls_computed_pos)
            err_pos = ls_computed_pos[:3] - rec_pos
            ls_err_pos.append(err_pos)
            if fix is not None:
                ls_computed_pos[:3]-=fix[i]
            ls_err   = np.linalg.norm(ls_computed_pos[:3] - rec_pos)
            ls_errs.append(ls_err)
    ls_errs = np.array(ls_errs)
    ls_err_pos = np.array(ls_err_pos)
    ls_pos = np.array(ls_pos)
    return ls_errs, ls_err_pos, ls_pos


def ls_trop_by_epoch(data,rec_pos, day, tropModel=None, met=None, fix=None):
    ls_errs    = []
    ls_err_pos = []
    ls_pos     = []
    rec_pos_g = ecef2geodetic(rec_pos[0], rec_pos[1], rec_pos[2])
    for i in data.TIME.unique():
        dataepoch = data[data.TIME==i]
        array_epoch = []
        for index, group in dataepoch.groupby("PRN"):
            array_epoch.append(group.as_matrix()[0])
        c1, pos, clocks, E = [],[],[],[]
        for eph in array_epoch:
            c1.append(eph[1]) 
            pos.append(eph[14][:,0])
            clocks.append(eph[13])
            E.append(eph[2])

        if tropModel is not None:
            P, T, e, beta, lamb = None,None,None,None,None
            if met is not None:
                m = met.iloc[i]
                P = m.pressure
                T = m.temperature + 273.15 #to kelvin
                e = m.humidity
            tropCorr = CollinsTropModel(E,rec_pos_g[2],rec_pos_g[0],day,t1,t2,P,T,e)
            c1 = c1 - tropCorr
        
        if len(c1)>=4:
            ls_computed_pos,_,_,_   = compute_least_squares_position(np.array(pos),np.array(clocks), np.array(c1))
            ls_pos.append(ls_computed_pos)
            err_pos = ls_computed_pos[:3] - rec_pos
            ls_err_pos.append(err_pos)
            if fix is not None:
                ls_computed_pos[:3]-=fix[i]
            print ls_computed_pos, rec_pos, rec_pos_g, ecef2geodetic(ls_computed_pos[0], ls_computed_pos[1], ls_computed_pos[2]) 
            ls_err   = np.linalg.norm(ls_computed_pos[:3] - rec_pos)
            ls_errs.append(ls_err)
    ls_errs = np.array(ls_errs)
    ls_err_pos = np.array(ls_err_pos)
    ls_pos = np.array(ls_pos)
    return ls_errs, ls_err_pos, ls_pos
