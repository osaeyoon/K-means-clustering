from warnings import filterwarnings

filterwarnings(action='ignore',category=DeprecationWarning,message='`np.bool` is a deprecated alias')

from netCDF4 import Dataset
import numpy as np

EA = [70,160,10,70] 
region = EA

######################
dataset='ERA5' # choose NCEP / ERA5
f1 = './data/%s.Z500_ano_1958to2020_JJA.nc'%(dataset)

f = Dataset(f1,'r')

lons = f.variables['lon'][:]
lats = f.variables['lat'][:]
lons_idx = (lons >= region[0]) & (lons <= region[1])
lats_idx = (lats >= region[2]) & (lats <= region[3])

GPH = f.variables['GPH'][:,lats_idx][...,lons_idx]

f.close()
print(GPH.shape)

lons_anl = lons[lons_idx]; lats_anl = lats[lats_idx]

coslat = np.cos(np.deg2rad(lats_anl))

Wij = np.ones((len(lats_anl),len(lons_anl)))
for i in range(0,len(lats_anl)):
    Wij[i,:] = coslat[i]
print(Wij.shape) ## Wij (lat,lon)

#######################

AWPCs = []
for t1 in range(0,len(GPH)):
    AWPC_tmp = []
    for t2 in range(0,len(GPH)): ## t1: X, t2: Y, len(GPH)=5796
        a1 = np.sum(Wij*GPH[t1]*GPH[t2])
        b1 = np.sum(Wij*GPH[t1]**2)
        b2 = np.sum(Wij*GPH[t2]**2)
        AWPC = a1 / (np.sqrt(b1) * np.sqrt(b2))
        AWPC_tmp.append(AWPC)
    AWPCs.append(AWPC_tmp)
AWPCs = np.array(AWPCs)
print(AWPCs.shape) #(5796,5796)

########################
ddir='./data/'
f = Dataset(ddir+'AWPC_%s.1958to2020.JJA.nc'%(dataset),'w',format='NETCDF4')
N = f.createDimension('N',len(GPH))

AWPC = f.createVariable('AWPC',AWPCs.dtype,('N','N'))

AWPC[:] = AWPCs

f.close()
