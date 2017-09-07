import numpy as np
import pandas as pd
from numba import autojit
from numpy.linalg import norm
import pyproj

ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')

def lla2ecef(lat,lon,alt, isradians=True):
    return pyproj.transform(lla, ecef, lon, lat, alt, radians=isradians)

def ecef2lla(X,Y,Z, isradians=True):
    lon, lat, alt = pyproj.transform(ecef, lla, X,Y,Z, radians=isradians)
    return lat, lon, alt

@autojit
def compute_distances(rc, svs):
    # return np.array( [np.sqrt((rc[0]-sv[0])**2 + (rc[1]-sv[1])**2) for sv in svs] )
    return np.linalg.norm(rc-svs, axis=1)


@autojit
def predict_pseudoranges(x, prns_pos, prns_clockbias):
    c = 299792458
    rhos    = compute_distances(x[:3], prns_pos)
    pranges = rhos + x[3]-c*prns_clockbias
    return rhos, pranges

@autojit
def apply_earth_rotation_to_svs_position(svs, prs):
    c = 299792458
    we = 7.2921159e-5
    rpos = np.zeros(svs.shape)
    pos = np.array(svs)
    for i in range(len(pos)):
        dt = prs[i]/c
        theta = we*dt
        R = np.array([[np.cos(theta), np.sin(theta),0.],[-np.sin(theta), np.cos(theta),0.],[0.,0.,1.]])
        rpos[i] = R.dot(pos[i])
    svs = np.array(rpos)
    return svs

def compute_least_squares_position(svs, svs_clocks, prs, max_iters=200, apply_earth_rotation=True):

    if apply_earth_rotation:
        svs = apply_earth_rotation_to_svs_position(svs, prs)
    
    if len(svs)==0 or len(prs)==0:
        return np.array([0.,0.,0.,0.]),None, None, None

    ri = np.array([0.,0.,0.,0.])

    #for i in range(max_iters):
    delta,i = 1,0
    while (norm(delta)>1e-8 and i<max_iters):
        rhos, pranges = predict_pseudoranges(ri, svs, svs_clocks)
        b = prs - pranges
        A = np.hstack(((ri[:3]-svs)/rhos[:,None],np.ones((len(b), 1))))
        delta =  np.linalg.pinv(A.T.dot(A)).dot(A.T).dot(b)
        ri += delta
        i+=1
    return ri, A, b, delta

def compute_least_squares_position_ignore_clock(svs, prs, max_iters=200, apply_earth_rotation=True):
    if apply_earth_rotation:
        svs = apply_earth_rotation_to_svs_position(svs, prs)

    if len(svs)==0 or len(prs)==0:
        return np.array([0,0,0])

    ri = np.array([0,0,0]).astype(float)
    for i in range(max_iters):
        oldri = ri.copy()
        p_computed = compute_distances(ri, svs)
        b = prs - p_computed
        A = (ri-svs)/p_computed[:,None]
        delta =  np.linalg.pinv(A.T.dot(A)).dot(A.T).dot(b)
        ri += delta
        if np.linalg.norm(delta)<1e-8:
            break
    return ri,A,b,delta



# translated from  matlab code
def Delta_Rho_Compute(Rhoc, SV_Pos, Rcv_Pos, b):
    m,n = SV_Pos.shape
    Delta_Rho = np.zeros(m)
    for i in range(m):
        Rho0 = np.linalg.norm(SV_Pos[i]-Rcv_Pos)+b
        Delta_Rho[i] = Rhoc[i] - Rho0
    return Delta_Rho

def G_Compute(SV_Pos, Rcv_Pos):
    m,n = SV_Pos.shape
    dX = SV_Pos - Rcv_Pos
    Nor = np.sqrt(np.sum(dX**2,axis=1)).reshape(-1,1)
    Unit_Mtrix = dX/Nor
    G = np.hstack( (-Unit_Mtrix, np.ones((len(Unit_Mtrix),1))))
    return G

def Rcv_Pos_Compute(SV_Pos, SV_Rho):
    Num_Of_SV=len(SV_Pos)
    if Num_Of_SV<4:
        return np.array([0,0,0]), 0
    Rcv_Pos, Rcv_b =np.array([0,0,0]), 0
    B1=1
    END_LOOP=100
    count=0
    while (END_LOOP > B1):
        G = G_Compute(SV_Pos, Rcv_Pos);
        Delta_Rho = Delta_Rho_Compute(SV_Rho, SV_Pos, Rcv_Pos, Rcv_b);
        Delta_X = np.linalg.pinv(G.T.dot(G)).dot(G.T).dot(Delta_Rho)
        Rcv_Pos = (Rcv_Pos.T + Delta_X[:3]).T
        Rcv_b = Rcv_b + Delta_X[3];
        END_LOOP = (Delta_X[0]**2 + Delta_X[1]**2 + Delta_X[2]**2)**.5;
        count = count+1;
        if count>10:
            END_LOOP=B1/2;
    return Rcv_Pos, Rcv_b  

def get_dop(o, sigma=5):
    x,A,b,d = compute_least_squares_position(o.prns_pos, o.prns_clockbias, o.P1)
    return get_dop_raw(x,A,b,d,sigma)

def get_dop_raw(x,A,b,d,sigma=5):
    Cs = sigma*np.eye(len(o.P1))
    Cx = sigma**2 * np.linalg.pinv(A.T.dot(A))
    lat, lon, alt = ecef2lla(x[0], x[1], x[2])
    G = np.array([[-np.sin(lat)*np.cos(lon), -np.sin(lat)*np.sin(lon), np.cos(lat)],
                  [-np.sin(lon),             -np.cos(lon),             0 ],
                  [np.cos(lat)*np.cos(lon),  np.cos(lat)*np.sin(lon), np.sin(lat)]])
    Cl = G.dot(Cx[:3,:3]).dot(G.T)
    VDOP = Cl[2,2]
    HDOP = np.sqrt(Cl[0,0]**2+Cl[1,1]**2)
    return VDOP, HDOP

