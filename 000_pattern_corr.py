import numpy as np
import 


A_pattern
B_pattern

coslat = np.cos(np.deg2rad(lats_anl))

Wij = np.ones((len(lats_anl),len(lons_anl)))
for i in range(0,len(lats_anl)):
    Wij[i,:] = coslat[i]

a1 = np.sum(Wij*A_pattern*B_pattern)
b1 = np.sum(Wij*A_pattern**2)
b2 = np.sum(Wij*B_pattern**2)
AWPC = a1 / (np.sqrt(b1) * np.sqrt(b2))

print(AWPC)
