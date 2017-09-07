# -*- coding: utf-8 -*-
"""
@author: wanda
Modifications by Diego.

"""
import numpy as np
import pandas as pd
import datetime 
from os import  listdir, sep
import pyproj
from rinex_reader import rinexobs, rinexnav
    
##################################### SATELLITE POSITION ELEVATION AZIMUTH 
    
def getGpsTime(dt):
    """_getGpsTime returns gps time (seconds since midnight Sat/Sun) for a datetime
    """
    total = 0
    days = (dt.weekday()+ 1) % 7 # this makes Sunday = 0, Monday = 1, etc.
    total += days*3600*24
    total += dt.hour * 3600
    total += dt.minute * 60
    total += dt.second #sow
    sod = dt.hour*3600 + dt.minute*60 + dt.second
    return(total, sod)


def getElAz(satpos, obspos):
    '''Get elevation and azimuth of satellite.
    http://www.naic.edu/aisr/GPSTEC/drewstuff/MATLAB/elavazim.m
    '''
    #compute unit vector from observation station to satellite position
    r = np.linalg.norm(satpos-obspos)
    dx = (satpos - obspos)/r
    dx = dx[0]
    #compute the observation latitude and longitude
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    obslon, obslat, __ = pyproj.transform(ecef, lla, obspos[0], obspos[1],obspos[2], radians=True)
    #compute look-angles from observation station to satellite positi
    north = -1.*np.cos(obslon)*np.sin(obslat)*dx[0] - np.sin(obslon)*np.sin(obslat)*dx[1]+np.cos(obslat)*dx[2]
    east = -1.*np.sin(obslon)*dx[0]+np.cos(obslon)*dx[1]
    vertical = np.cos(obslon)*np.cos(obslat)*dx[0]+np.sin(obslon)*np.cos(obslat)*dx[1]+np.sin(obslat)*dx[2]
    #compute elevation
    elevation = (np.pi/2.-np.arccos(vertical))*(180./np.pi)     # degrees
    #compute azimuth; check for negative angles
    azimuth = (180./np.pi)*np.arctan2(east,north) # radians to degree
    return elevation, azimuth 


################################################################################################


def solveIter(Mk,ecc):
    """__solvIter returns an iterative solution for Ek
    Mk = Ek - e sin(Ek)
    """
    delta = 1
    zero = 1e-13
    E = Mk 
    #Eccentric anomaly !
    i = 0
    while delta>zero  :
        i+=1
        Ei = Mk + (ecc*np.sin(E))
        delta = np.abs(E-Ei)  
        E = Ei
    return E

        
def getSatXYZ(nav,sv,times):
    allSvInfo = nav[nav['sv']==sv] 
    timesarray = np.asarray(times,dtype='datetime64[ms]')
    navtimes = np.asarray(allSvInfo.index,dtype='datetime64[ms]')
    bestephind = np.array([np.argmin(abs(navtimes-t)) for t in timesarray])
    info = np.asarray(allSvInfo)[bestephind]
    info = pd.DataFrame(info,index=times,columns=allSvInfo.columns)
    info['sv'] = sv
    info['gpstime'] = np.array([getGpsTime(t)[0] for t in times])
    # constants
    GM = 3986005.0E8 # universal gravational constant
    OeDOT = 7.2921151467E-5
    Tgd = info['TGD'].values[0]
    #Basic Parameters
    t = (info['gpstime']-info['TimeEph']).values[0]
    mu = info['M0'].values[0]+t*(np.sqrt(GM/info['sqrtA'].values[0]**6)+info['DeltaN'].values[0])
    Ek = solveIter(mu,info['Eccentricity'].values[0])  
    Vk = np.arctan2(np.sqrt(1.0-info['Eccentricity'].values[0])*np.sin(Ek),np.cos(Ek)-info['Eccentricity'].values[0])
    PhiK = Vk + info['omega'].values[0]
    #Correct for orbital perturbations
    omega = info['omega'].values[0]+info['Cus'].values[0]*np.sin(2.0*PhiK) +info['Cuc'].values[0]*np.cos(2.0*PhiK)
    r = (info['sqrtA'].values[0]**2)*(1.0-info['Eccentricity'].values[0]*np.cos(Ek))+info['Crs'].values[0]*np.sin(2.0*PhiK)+info['Crc'].values[0]*np.cos(2.0*PhiK)
    i = info['Io'].values[0]+info['IDOT'].values[0]*t+info['CIS'].values[0]*np.sin(2.0*PhiK) +info['Cic'].values[0]*np.cos(2.0*PhiK)
    
    #Compute the right ascension
    Omega = info['OMEGA'].values[0]+(info['OMEGA DOT'].values[0]-OeDOT)*t-(OeDOT*info['TimeEph'].values[0])
    #Convert satellite position from orbital frame to ECEF frame
    cosOmega = np.cos(Omega)
    sinOmega = np.sin(Omega)
    cosomega = np.cos(omega)
    sinomega = np.sin(omega)
    cosi = np.cos(i)
    sini = np.sin(i)
    cosVk = np.cos(Vk)
    sinVk = np.sin(Vk)
    R11 = cosOmega*cosomega - sinOmega*sinomega*cosi
    R12 = -1.0*cosOmega*sinomega - sinOmega*cosomega*cosi
    R13 = np.sin(Omega)*np.sin(i)
    R21 = sinOmega*cosomega + cosOmega*sinomega*cosi
    R22 = -1.0*sinOmega*sinomega + cosOmega*cosomega*cosi
    R23 = -1.0*np.cos(Omega)*np.sin(i)
    R31 = sinomega*sini
    R32 = cosomega*sini
    R33 = np.cos(i)
    
    #R = np.array([[R11,R12,R13],[R21,R22,R23],[R31,R32,R33]])
    R = np.array([[R11,R12,0],[R21,R22,0],[R31,R32,0]])
    r = np.array([[r*cosVk],[r*sinVk],[0]])
    xyz = np.dot(R,r)
        
    return xyz, Tgd




def Extract_Data3(nfile, ofile):
    """Reads observation data and returns a dataframe which can be processed
    """
    wf1, wf2 = 0.190293672798, 0.244210213425
    newdf = pd.DataFrame()
    #get ephemerides data
    eph = rinexnav(nfile)
    #get receiver observation data
    odata, oheader = rinexobs(ofile)
    rec_pos = oheader['APPROX POSITION XYZ'] #[x,y,z] ECEF
    x, y, z = rec_pos[0], rec_pos[1], rec_pos[2]
    IPPx, IPPy, IPPz = x, y, z #
    #get geoocentric latitude, longitude
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    rec_lon, rec_lat, __ = pyproj.transform(ecef, lla, x, y,z, radians=False)
    #get ephemerides data
    eph = rinexnav(nfile)
    eph = eph[eph.SVhealth == 0] #only healthy ephemerides
    
    for epoch in odata.labels:
        #only satellites with all observables
        odata_epoch = odata[epoch,:,:,["data","lli"]] #labels,sats, epochs, data(2 ibs y lli)
        obs_types = odata_epoch.major_axis
        if 'C1' and 'L1' in obs_types:
            labels = ['C1','L1'] #only these 
            odata_epoch = odata_epoch[:,labels,:]
            #sats with all observables
            sats = odata_epoch[:,:,"data"].dropna(axis=1).columns.values
            for sat in sats:
                try:
                    # Find satellite position at observation time!
                    sat_pos, Tgd =  getSatXYZ(eph,sat,[epoch]) #ECEF convert epoch to pydate 
                    elev, az = getElAz(sat_pos.T, rec_pos)

                    C1 = odata_epoch[sat,labels,"data"].C1
                    L1 = odata_epoch[sat,labels,"data"].L1
                    LLI_1 = odata_epoch[sat,labels,"lli"].L1
                    
                    clock_bias = eph[eph.sv==sat].SVclockBias.iloc[0]
                    
                    if C1 == 0.0:
                        C1 = np.nan
                        
                    if L1 == 0.0:
                        L1 = np.nan
                    else:
                        L1 *= wf1

                    sow,sod = getGpsTime(epoch)
                    temp = pd.DataFrame([{'PRN':sat,'TIME':sod,'C1':C1,'L1':L1,'Tgd':Tgd,'IPPx':IPPx,'IPPy':IPPy,'IPPz':IPPz,'LLI_1':LLI_1,'Elevation':elev, 'Azimuth':az,'Lat':rec_lat,'Lon':rec_lon, 'sat_pos':sat_pos, 'clock_bias':clock_bias}])
                    frames = [newdf, temp]
                    newdf = pd.concat(frames)
                except:
                    print "cant read ephem"
                    pass
    return newdf

