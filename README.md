# K-means-clustering

### 1. AWPC 구하기 [001_AWPC.py]

클러스터링할 모든 데이터에 대한 Area-Weighted Pattern Correlation을 구한다.

```
12  dataset='NCEP' or 'ERA'
```

원하는 데이터셋을 선택해서 돌리면, output으로 **AWPC_*dataset*.1958to2020.JJA.nc**가 저장이 된다. 

예를 들어, 1958년부터 2020년까지의 JJA daily GPH data에 대한 AWPC를 구하려고 한다면, 
데이터의 총 길이는 92 * 63 = 5796 개가 되고, 자신을 포함한 두 데이터 간의 pattern correlation 값이 저장이 된다.
**AWPC_*dataset*.1958to2020.JJA.nc**의 shape은 (5796,5796)이고, (0,4)에 해당하는 값은 1번째 데이터와 5번째 데이터 간의 pattern correlation 값을 의미한다. 

********

### 2. 적절한 클러스터 수, threshold 값 정하기 [002_1_AWPC_cr.sh]



********

### 3. 002_clustering

********
### 4. 003_conformal.py


6. 
