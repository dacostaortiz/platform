# -*- coding: utf-8 -*-
"""
Read navigation and observation rinex files
@author: pyrinex (modified)
"""
try:
    from pathlib import Path
    Path().expanduser()
except (ImportError,AttributeError):
    from pathlib2 import Path

import numpy as np
from datetime import datetime
from pandas import DataFrame,Panel4D,read_hdf,Series
from io import BytesIO
from time import time
import re
from os.path import splitext,expanduser,getsize


##################### Navigation file ################################################


def rinexnavw(fn, ofn=None):
    """
    Reads RINEX 2.11 NAV files
    Michael Hirsch
    It may actually be faster to read the entire file via f.read() and then .split()
    and asarray().reshape() to the final result, but I did it frame by frame.
    http://gage14.upc.es/gLAB/HTML/GPS_Navigation_Rinex_v2.11.html
    """
    fn = Path(fn).expanduser()

    startcol = 3 #column where numerical data starts
    N = 7 #number of lines per record

    sv = []; epoch=[]; raws=''

    with fn.open('r') as f:
        """
        skip header, which has non-constant number of rows
        """
        while True:
            if 'END OF HEADER' in f.readline():
                break
        """
        now read data
        """
        for l in f:
            sv.append(int(l[:2]))
            # format I2
            year = int(l[3:5]) 
            if 80 <= year <=99:
                year += 1900
            elif year<80: #good till year 2180
                year += 2000
            epoch.append(datetime(year =year,
                                  month   =int(l[6:8]),
                                  day     =int(l[9:11]),
                                  hour    =int(l[12:14]),
                                  minute  =int(l[15:17]),
                                  second  =int(l[17:20]),  # python reads second and fraction in parts
                                  microsecond=int(l[21])*100000))
            """
            now get the data as one big long string per SV
            """
            raw = l[22:80]
            for _ in range(N):
                raw += f.readline()[startcol:80]
            # one line per SV
            #raws += raw + '\n'
            raws += raw + ' '
            

    raws = raws.replace('D','E')
    raws = re.sub(r'(\d-)', r' -', raws)
    raws = re.sub(r'\n', r' ', raws)
    
    lista = [float(i) for i in raws.split(' ') if len(i) != 0 ]
    sat_info = np.array(lista)
    sat_info = sat_info.reshape(len(lista)/29, 29)
    
    nav= DataFrame(data=np.concatenate((np.atleast_2d(sv).T,sat_info), axis=1),
                   index=epoch,
           columns=['sv','SVclockBias','SVclockDrift','SVclockDriftRate','IODE',
                'Crs','DeltaN','M0','Cuc','Eccentricity','Cus','sqrtA','TimeEph',
                'Cic','OMEGA','CIS','Io','Crc','omega','OMEGA DOT','IDOT',
                'CodesL2','GPSWeek','L2Pflag','SVacc','SVhealth','TGD','IODC',
                'TransTime','FitIntvl'])

   
    if ofn:
        #nav.to_hdf(ofn, 'table',append=True)
        nav.to_csv(ofn)
    return nav
######################################################################################

def rinexnav(fn,writeh5=None):
    """
    Michael Hirsch
    It may actually be faster to read the entire file via f.read() and then .split()
    and asarray().reshape() to the final result, but I did it frame by frame.
    http://gage14.upc.es/gLAB/HTML/GPS_Navigation_Rinex_v2.11.html
    """
    stem,ext = splitext(expanduser(fn))
    startcol = 3 #column where numerical data starts
    nfloat=19 #number of text elements per float data number
    nline=7 #number of lines per record

    with open(expanduser(fn),'r') as f:
        #find end of header, which has non-constant length
        while True:
            if 'END OF HEADER' in f.readline(): break
        #handle frame by frame
        sv = []; epoch=[]; raws=''
        while True:
            headln = f.readline()
            if not headln: break
            #handle the header
            sv.append(headln[:2])
            year = int(headln[2:5])
            if 80<= year <=99:
                year+=1900
            elif year<80: #good till year 2180
                year+=2000
            #print len(headln)
            epoch.append(datetime(year =year,
                                  month   =int(headln[5:8]),
                                  day     =int(headln[8:11]),
                                  hour    =int(headln[11:14]),
                                  minute  =int(headln[14:17]),
                                  second  =int(headln[17:20]),
                                  microsecond=int(headln[21])*100000))
            """
            now get the data.
            Use rstrip() to chomp newlines consistently on Windows and Python 2.7/3.4
            Specifically [:-1] doesn't work consistently as .rstrip() does here.
            """
            raw = (headln[22:].rstrip() +
                   ''.join(f.readline()[startcol:].rstrip() for _ in range(nline-1))
                   +f.readline()[startcol:40].rstrip())

            raws += raw + '\n'

    raws = raws.replace('D','E')

    strio = BytesIO(raws.encode())
    darr = np.genfromtxt(strio,delimiter=nfloat)

    nav= DataFrame(darr, epoch,
               ['SVclockBias','SVclockDrift','SVclockDriftRate','IODE',
                'Crs','DeltaN','M0','Cuc','Eccentricity','Cus','sqrtA','TimeEph',
                'Cic','OMEGA','CIS','Io','Crc','omega','OMEGA DOT','IDOT',
                'CodesL2','GPSWeek','L2Pflag','SVacc','SVhealth','TGD','IODC',
                'TransTime','FitIntvl'])
    nav['sv'] = Series(np.asarray(sv,int), index=nav.index)

    if writeh5:
        h5fn = stem + '.h5'
        print('saving NAV data to {}'.format(h5fn))
        nav.to_hdf(h5fn,key='NAV',mode='a',complevel=6,append=False)

    return nav

##################### Observation file ################################################
def rinexobs(fn, ofn=None):
    """
    Program overviw:
    1) scan the whole file for the header and other information using scan(lines)
    2) each epoch is read and the information is put in a 4D Panel
    3)  rinexobs can also be sped up with if an h5 file is provided,
        also rinexobs can save the rinex file as an h5. The header will
        be returned only if specified.

    rinexobs() returns the data in a 4D Panel, [Parameter,Sat #,time,data/loss of lock/signal strength]
    """
    #open file, get header info, possibly speed up reading data with a premade h5 file
    fn = Path(fn).expanduser()
    with fn.open('r') as f:
        #tic = time()
        lines = f.read().splitlines(True)
        header,version,headlines,headlength,obstimes,sats,svset = scan(lines)
        
        if fn.suffix=='.h5':
            data = read_hdf(fn, key='data')
        else:
            data = processBlocks(lines,header,obstimes,svset,headlines,headlength,sats)

    
    #write an h5 file if specified
    if ofn:
        ofn = Path(ofn).expanduser()
        #print('saving OBS data to',str(ofn))
        """if ofn.is_file():
            wmode='a'
        else:
            wmode='w'
            # https://github.com/pandas-dev/pandas/issues/5444"""
        #data.to_hdf(ofn, key='OBS', mode=wmode, complevel=6,format='table')

    return data,header



# this will scan the document for the header info and for the line on
# which each block starts
def scan(L):
    header={}
    # Capture header info
    for i,l in enumerate(L):
        #print i, l
        if "END OF HEADER" in l:
            i+=1 # skip to data
            break
        if l[60:80].strip() not in header: #Header label
            header[l[60:80].strip()] = l[:60]  # don't strip for fixed-width parsers
            # string with info
        else:
            header[l[60:80].strip()] += " "+l[:60]
            #concatenate to the existing string
    verRinex = float(header['RINEX VERSION / TYPE'][:9])  # %9.2f
    # list with x,y,z cartesian
    header['APPROX POSITION XYZ'] = [float(j) for j in header['APPROX POSITION XYZ'].split()]
    #observation types
    header['# / TYPES OF OBSERV'] = header['# / TYPES OF OBSERV'].split()
    #turn into int number of observations 
    header['# / TYPES OF OBSERV'][0] = int(header['# / TYPES OF OBSERV'][0])
    #header['INTERVAL'] = float(header['INTERVAL'][:10])

    headlines=[]
    headlength = []
    obstimes=[]
    sats=[]
    svset=set() 
    
    while i < len(L):
        if len(L[i].split()) >  header['# / TYPES OF OBSERV'][0]: #then its headerline 
            if int(L[i][28]) in (0,1,5,6): # CHECK EPOCH FLAG  STATUS
                headlines.append(i)
                year, month, day, hour = L[i][1:3], L[i][4:6], L[i][7:9], L[i][10:12]
                minute, second = L[i][13:15], L[i][16:26]
                obstimes.append(_obstime([year,  month,
                                      day,  hour,
                                      minute,second]))
                #ONLY GPS SATELLITES
                numsvs = int(L[i][29:32])  # Number of visible satellites %i3
                headlength.append(1 + (numsvs-1)//12)  # number of lines in header, depends on how many svs on view
                if numsvs > 12:
                    sv=[]
                    for s in range(numsvs):
                        if s>0 and s%12 == 0:
                            i += 1  #every 12th sat  will add new headline row ex >12 2 rows
                        if L[i][33+(s%12)*3-1] == 'G':
                            sv.append(int(L[i][33+(s%12)*3:35+(s%12)*3])) 
                    sats.append(sv)
                    i += numsvs+1
                    
                else:
                    sats.append([int(L[i][33+s*3:35+s*3]) for s in range(numsvs) if L[i][33+s*3-1]=='G']) #lista de satelites (numeros prn)
                    i += numsvs + 1
            
            else:
                flag=int(L[i][28])
                if(flag!=4):
                    print(flag)
                skip=int(L[i][30:32])
                i+=skip+1
    
    for sv in sats:
        svset = svset.union(set(sv))
        
    return header,verRinex,headlines,headlength,obstimes,sats,svset

def _obstime(fol):
    year = int(fol[0])
    if 80 <= year <=99:
        year+=1900
    elif year<80: #because we might pass in four-digit year
        year+=2000
    return datetime(year=year, month=int(fol[1]), day= int(fol[2]),
                    hour= int(fol[3]), minute=int(fol[4]),
                    second=int(float(fol[5])),
                    microsecond=int(float(fol[5]) % 1 * 100000)
                    )


def processBlocks(lines,header,obstimes,svset,headlines,headlength,sats):
    obstypes = header['# / TYPES OF OBSERV'][1:]
    blocks = Panel4D(labels = obstimes,
                     items=list(svset),
                     major_axis=obstypes,
                     minor_axis=['data','lli','ssi'])

    for i in range(len(headlines)):
        linesinblock = len(sats[i])*int(np.ceil((header['# / TYPES OF OBSERV'][0]*1.)/5)) #nsats x observations
        # / 5 there is space for 5 observables per line
        block = ''.join(lines[headlines[i]+headlength[i]:headlines[i]+linesinblock+headlength[i]])
        bdf = _block2df(block,obstypes,sats[i],len(sats[i])) 
        blocks.loc[obstimes[i],sats[i]] = bdf   # matrices # satelites
    return blocks


def _block2df(block,obstypes,svnames,svnum): #de gps, funciona bien!
    """
    input: block of text corresponding to one time increment INTERVAL of RINEX file
    output: 2-D array of float64 data from block. Future: consider whether best to use Numpy, Pandas, or Xray.
    """
    nobs = len(obstypes)
    stride=3

    strio = BytesIO(block.encode())
    barr = np.genfromtxt(strio, delimiter=(14,1,1)*5).reshape((svnum,-1), order='C')

    data = barr[:,0:nobs*stride:stride]
    lli  = barr[:,1:nobs*stride:stride]
    ssi  = barr[:,2:nobs*stride:stride]

    data = np.vstack(([data.T],[lli.T],[ssi.T])).T

    return data
