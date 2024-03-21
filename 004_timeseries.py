import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

dataset='NCEP' ## NCEP or ERA5
M = 10

f = xr.open_dataset('./data/AWPC_idx_%s.Z500_1958to2020_M%d_JJA.nc'%(dataset,M))

CI = f['Cluster_index'].values
CAWPC = f['Cluster_avg_AWPC'].values

year = np.arange(1958,2021)
time_series = np.zeros((len(CAWPC),len(year)))
for i in range(len(CI)):
    year_idx = i//92
    cluster_idx = CI[i]
    time_series[cluster_idx,year_idx] += 1

### trend calculation
sig = 95
sig_lev = (100 - sig)*0.01

slope = []; pval = []; intercept = []
for i in range(len(time_series)):
    sl,inte,r,p,std_er = stats.linregress(year, time_series[i])
    slope.append(sl)
    pval.append(p)
    intercept.append(inte)

print(slope)

#==========================================================
# Figure
#==========================================================
## figsize = (14,6.5) --> 11
fig = plt.figure(figsize=(14,6.5))

xmajor_ticks = np.arange(1950,2021,10)
xminor_ticks = np.arange(1950,2020,2)
ymajor_ticks = np.arange(0,61,10)
yminor_ticks = np.arange(0,60,2)

for i in range(len(time_series)):
    ax = plt.subplot(3,4,i+1)
    ax.plot(year, time_series[i], markersize=5, color='k',linewidth=2)

    if pval[i] <= sig_lev:
        ax.plot(year, slope[i]*year+intercept[i], '--', linewidth=1.5, color='red')

    ax.set_xticks(xmajor_ticks)
    ax.set_xticks(xminor_ticks, minor=True)
    ax.set_yticks(ymajor_ticks)
    ax.set_yticks(yminor_ticks, minor=True)
    ax.set_xlabel('Year')
    ax.set_ylabel('Occurrence number')
    ax.set_xlim(1957,2021)
    ax.set_ylim(-2,60)
    ax.grid(which='major', alpha=0.5, linestyle='--')
    ax.tick_params(axis='both',which='major',labelsize=10,width=1.0,length=6,right=True,top=False)
    ax.tick_params(axis='both',which='minor',width=1.0,length=3,right=True,top=False)
    ax.set_title('Cluster%d'%(i+1),loc='left',fontsize=12)

plt.tight_layout()
#plt.show()
plt.savefig('./figure/Time_series.NCEP.png')
