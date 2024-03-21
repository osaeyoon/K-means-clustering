from netCDF4 import Dataset
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy import stats, signal
import LOA_share as loa
import collections
from warnings import filterwarnings

filterwarnings(action='ignore',category=DeprecationWarning,message='`np.bool` is a deprecated alias')

import cartopy.crs                    as ccrs
import cartopy.mpl.ticker             as ctk
import matplotlib.path                as mpath
import matplotlib.ticker              as mticker
import cartopy.feature                as cfeature

M = 10
sig = 95
EA = [70,160,10,70]
region = EA

lon1, lon2, lat1, lat2 = [70, 160, 9.9, 70.1]

dataset='NCEP' ## NCEP or ERA5
f1 = './data/%s.Z500_ano_1958to2020_JJA.nc'%(dataset)
f2 = './data/AWPC_idx_%s.Z500_1958to2020_M%d_JJA.nc'%(dataset,M)
#================================================

f = Dataset(f1,'r')

lons = f.variables['lon'][:]
lats = f.variables['lat'][:]
lons_idx = (lons >= region[0]) & (lons <= region[1])
lats_idx = (lats >= region[2]) & (lats <= region[3])

times = f.variables['time'][:]
dt_time = [dt.date(1800,1,1) + dt.timedelta(hours=t) for t in times]
print(dt_time[0])

GPH = f.variables['GPH'][:,lats_idx][...,lons_idx]
f.close()

lons_anl = lons[lons_idx]; lats_anl = lats[lats_idx]

#############################

f = Dataset(f2,'r')

CI = f.variables['Cluster_index'][:]
CAWPC = f.variables['Cluster_avg_AWPC'][:]
f.close()

cluster_num = collections.Counter(CI)

#==========================================================
### boundary to draw projection of Lambert conformal ###
rect = mpath.Path([[lon1, lat1], [lon2, lat1],
    [lon2, lat2], [lon1, lat2], [lon1, lat1]]).interpolated(50)

name='LambertConformal'
proj=ccrs.LambertConformal(central_longitude=(lon1+lon2)*0.5,
    central_latitude=(lat1+lat2)*0.5, standard_parallels=(60,75))
#==========================================================
sig = 95
sig_level = (100 - sig) * 0.01
xskip=2; yskip=2

centroids=[]
for cen_idx in range(0,len(CAWPC)):
    gph_M = []
    for t in range(0,len(GPH)):
        if CI[t] == cen_idx:
            gph_M.append(GPH[t])
    gph_M = np.array(gph_M)
    gph_M_mean = np.mean(gph_M,axis=0)
    
    stat, p = stats.ttest_ind(gph_M,GPH,axis=0)
    sig_map = (p <= sig_level)
    
    gph_M_mean = np.ma.masked_where(sig_map==False,gph_M_mean)
    centroids.append(gph_M_mean)    

centroids = np.ma.array(centroids)

fig = plt.figure(figsize=(25,15))

for cen_idx in range(len(CAWPC)):
    ax=plt.subplot(3,4,cen_idx+1,projection=proj)
    proj_to_data = ccrs.PlateCarree()._as_mpl_transform(ax) - ax.transData
    rect_in_target = proj_to_data.transform_path(rect)
    ax.set_boundary(rect_in_target)
    ax.set_xlim(rect_in_target.vertices[:,0].min(), rect_in_target.vertices[:,0].max())
    ax.set_ylim(rect_in_target.vertices[:,1].min(), rect_in_target.vertices[:,1].max())
    #
    lon2d, lat2d = np.meshgrid(lons_anl,lats_anl)
    #
    image = ax.contourf(lons_anl,lats_anl,centroids[cen_idx],np.arange(-100,100.1,20),transform=ccrs.PlateCarree(), cmap=plt.cm.RdBu_r, extend='both') ## Spectral_r
    '''
    gl = ax.gridlines(draw_labels=False, xlocs=range(60,161,10), ylocs=range(15,76,15), linestyle='dashed')
    gl.top_labels=False
    gl.right_labels=False
    gl.bottom_labels=False
    gl.ylabel_style = {'rotation':'horizontal'}
    '''
    ### draw gridlines again to set lables on the bottom ### 
    gl = ax.gridlines(draw_labels=True, x_inline=False, y_inline=False,
        xlocs=range(70,161,15),ylocs=range(10,70,15),linestyle='dashed')
    gl.top_labels, gl.bottom_labels, gl.left_labels, gl.right_labels = [False,True,True,True]
    gl.xformatter=ctk.LongitudeFormatter(zero_direction_label=True)
    gl.yformatter=ctk.LatitudeFormatter()
    gl.xlabel_style = {'size':15}
    gl.ylabel_style = {'size':15}
    #cs = plt.scatter(lon2d[::yskip,::xskip],lat2d[::yskip,::xskip],sig_map[::yskip,::xskip],c='k',transform=ccrs.PlateCarree())
    #
    cbar = plt.colorbar(image, orientation='horizontal', ticks=np.arange(-100,100.1,20), shrink=0.8, pad=0.1, drawedges=False, aspect=30)
    ax.set_title('('+chr(97+cen_idx)+') Cluster%d (%d/%d)'%(cen_idx+1, cluster_num[cen_idx], len((CI))),loc='left',fontsize=20,position=[-0.1,1.1])
    ax.set_title('%1.2f'%(CAWPC[cen_idx]),loc='right',fontsize=20,position=[1,1.1])
    #
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, zorder=10)

#plt.show()
plt.savefig('./figure/Centroids.%s.png'%(dataset))
