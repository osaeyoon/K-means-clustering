from warnings import filterwarnings

filterwarnings(action='ignore',category=DeprecationWarning,message='`np.bool` is a deprecated alias')

from netCDF4 import Dataset
import numpy as np
import collections 
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import LOA_share as loa
import os 

s_idx = 59 + (1958-1951)*90
e_idx = s_idx + (2019-1958)*90

dataset='NCEP' ## 'NCEP' or 'ERA'
f1 = './data/AWPC_%s.1958to2020.JJA.nc'%(dataset)
f2 = './data/%s.Z500_ano_1958to2020_JJA.nc'%(dataset)
#================================================

AWPC_cr = 0.5
#AWPC_cr = float(os.environ['awpc_cr']) ### input
#AWPC_cr = AWPC_cr / 100
M = 10


START = 1958
END = 2020
#start_idx = (START - 1958)*92
#end_idx = start_idx + 2760

EA = [70,160,10,70]
region = EA

OUTPUT = './data/AWPC_idx_%s.Z500_1958to2020_M%d_JJA.nc'%(dataset,M)

########## AWPC based K-mean clustering Functions

def cal_AWPC(Wij,T1array,T2array): ## Wij, T1, T2 array are 2-D
    a1 = np.sum(Wij*T1array*T2array)
    b1 = np.sum(Wij*T1array**2)
    b2 = np.sum(Wij*T2array**2)
    AWPC = a1 / (np.sqrt(b1) * np.sqrt(b2))
    return AWPC

def cal_initial_LN_idx(AWPC,AWPC_cr):
    LN,LNI = 0,0
    for i in range(0,len(AWPC)): ## N Samples
        a = np.where(AWPC[i]>=AWPC_cr)
        if len(a[0]) > LN:
            LN = len(a[0])
            LNI = i
    LN_idx = np.where(AWPC[LNI]>=AWPC_cr)[0]
    return LN_idx

def find_initial_M_centroid(M,AWPC,AWPC_cr,LN_idx,Tarray):
    M_centroid,centroid_tmp = [],[]
    for i in range(0,len(Tarray)):
        if i in LN_idx:
            centroid_tmp.append(Tarray[i])
    centroid_tmp = np.array(centroid_tmp)
    
    M_centroid.append(np.mean(centroid_tmp,axis=0)) ## First initial centroid

    for i in range(1,M):
        AWPC_removed1 = np.delete(AWPC,LN_idx,axis=0)
        AWPC_removed2 = np.delete(AWPC_removed1,LN_idx,axis=1)
        Tarray_removed = np.delete(Tarray,LN_idx,axis=0)

        LN_idx2 = cal_initial_LN_idx(AWPC_removed2,AWPC_cr)

        centroid_tmp = []
        for j in range(0,len(Tarray_removed)):
            if j in LN_idx2:
                centroid_tmp.append(Tarray_removed[j])
        centroid_tmp = np.array(centroid_tmp)

        M_centroid.append(np.mean(centroid_tmp,axis=0))

        AWPC = AWPC_removed2
        LN_idx = LN_idx2
        Tarray = Tarray_removed

    return M_centroid

def find_within_AWPC(Wij,Tarray,M_centroid):
    cen_idx,LPCs = [],[]
    for t in range(0,len(Tarray)):
        centroid_tmp = []
        for i in range(0,len(M_centroid)):
            AWPC = cal_AWPC(Wij,Tarray[t],M_centroid[i])
            centroid_tmp.append(AWPC)
        cen_idx.append(np.argmax(centroid_tmp))
        LPCs.append(np.max(centroid_tmp))
    LPCs = np.array(LPCs); cen_idx = np.array(cen_idx)
    
    Within_AWPC_tmp = []
    for t in range(0,len(M_centroid)):
        mask = (cen_idx==t)
        new_LPCs = np.ma.masked_where(mask==False,LPCs)
        Within_AWPC_tmp.append(np.ma.mean(new_LPCs))
    Within_AWPC_tmp = np.array(Within_AWPC_tmp)

    Within_AWPC = np.mean(Within_AWPC_tmp)
    Minimum_AWPC = np.min(Within_AWPC_tmp)
    return cen_idx, Within_AWPC, Minimum_AWPC, Within_AWPC_tmp

def new_centroid(M,Tarray,cen_idx):
    NEW_M_centroid = []
    for i in range(0,M):
        idx = (cen_idx==i)
        new_Tarray = Tarray[idx]
        NEW_M_centroid.append(np.mean(new_Tarray,axis=0))
    NEW_M_centroid = np.array(NEW_M_centroid)
    return NEW_M_centroid

#########################

f = Dataset(f1,'r')

AWPC = f.variables['AWPC'][:]
f.close()

f = Dataset(f2,'r')

lons = f.variables['lon'][:]
lats = f.variables['lat'][:]
lons_idx = (lons >= region[0]) & (lons <= region[1])
lats_idx = (lats >= region[2]) & (lats <= region[3])

SLP = f.variables['GPH'][:,lats_idx][...,lons_idx]

f.close()

lons_anl = lons[lons_idx]; lats_anl = lats[lats_idx]

coslat = np.cos(np.deg2rad(lats_anl))

Wij = np.ones((len(lats_anl),len(lons_anl)))
for i in range(0,len(lats_anl)):
    Wij[i,:] = coslat[i]

#########################

LN_idx = cal_initial_LN_idx(AWPC,AWPC_cr)
M_centroid = find_initial_M_centroid(M,AWPC,AWPC_cr,LN_idx,SLP)

######################### First Within-Group AWPC & Centroid index

cen_idx, Within_AWPC, Min_AWPC, centroid_AWPC = find_within_AWPC(Wij,SLP,M_centroid)

######################### iterate until Within-Group AWPC diff. < 10^-6

last_cen_idx = []
while(1):
    new_M_centroid = new_centroid(M,SLP,cen_idx)
    cen_idx, new_within_AWPC, new_min_AWPC, centroid_AWPC = find_within_AWPC(Wij,SLP,new_M_centroid)

    AWPC_diff = new_within_AWPC - Within_AWPC
    #print('Within-Group AWPC Diff: ', AWPC_diff)
    if abs(AWPC_diff) < pow(10,-6):
        last_cen_idx = cen_idx
        break
    else:
        Within_AWPC = new_within_AWPC

print ('M: %d, AWPC_cr: %1.2f'%(M,AWPC_cr))
print ('Average Sample AWPC: %1.6f'%(new_within_AWPC))
print ('Minimum Sample AWPC: %1.6f'%(new_min_AWPC))
#print ('Final Centroid Index: ', last_cen_idx)
#print (collections.Counter(last_cen_idx))
#print ('Centroid Average AWPC: ', centroid_AWPC)

#########################

f = Dataset(OUTPUT,'w',format='NETCDF4')
new_cen = f.createDimension('Centroid',len(M_centroid))
new_n = f.createDimension('Sample',len(SLP))

cenidx = f.createVariable('Cluster_index', last_cen_idx.dtype, ('Sample'))
new_awpc = f.createVariable('Cluster_avg_AWPC', centroid_AWPC.dtype, ('Centroid'))

cenidx[:] = last_cen_idx
new_awpc[:] = centroid_AWPC

f.close()


#########################
