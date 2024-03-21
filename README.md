# K-means-clustering

### 1. AWPC 구하기 [001_AWPC.py]

클러스터링할 모든 데이터에 대한 Area-Weighted Pattern Correlation을 구합니다.

```
12  dataset='NCEP' or 'ERA'
```

원하는 데이터셋을 선택해서 돌리면, output으로 **AWPC_*dataset*.1958to2020.JJA.nc**가 저장이 됩니다. 

예를 들어, 1958년부터 2020년까지의 JJA daily GPH data에 대한 AWPC를 구하려고 한다면, 
데이터의 총 길이는 92 * 63 = 5796 개가 되고, 자신을 포함한 두 데이터 간의 pattern correlation 값이 저장이 됩니다.
**AWPC_*dataset*.1958to2020.JJA.nc**의 shape은 (5796,5796)이고, (0,4)에 해당하는 값은 1번째 데이터와 5번째 데이터 간의 pattern correlation 값을 의미합니다. 

********

### 2. 적절한 클러스터 수, threshold 값 정하기 [002_1_AWPC_cr.sh]

K-means clustering을 하기 위해서는 클러스터의 수(M)와 클러스터링을 위한 기준값(AWPC_cr)을 정해야 합니다. 

본 연구에서는 NCEP에서는 M=10, AWPC_cr=0.5로 정하고, ERA5에서는 M=11, AWPC_cr=0.55로 정했습니다. 

그 이유는 간단하게 설명하면, 본 연구에서는 클러스터링을 완료했을 때 총 평균 AWPC 값이 0.55를 처음으로 넘게 되는 클러스터 수를 정하는데 NCEP은 M=10일 때, ERA5는 M=11일 때 처음으로 0.55 이상의 평균 AWPC가 계산되었습니다. 

그리고 AWPC-cr는 0.55 이상을 넘는 클러스터 수에서 가장 큰 최소 AWPC 값을 가지는 AWPC_cr로 정하게 됩니다. 

* 이 때 말하는 AWPC는 각각의 데이터와 그 데이터가 속한 클러스터의 centroid와의 AWPC 값을 의미합니다.
* centroid는 한 클러스터 내에 속하는 모든 데이터들의 평균을 의미합니다.
* 
**002_1_AWPC_cr.sh**를 돌리면 AWPC_cr가 0.3에서 0.7까지 0.05 간격으로 정해져서 **002_clustering.py**를 돌리게 됩니다.  

```
21  #AWPC_cr = 0.5 # 주석 처리
22  AWPC_cr = float(os.environ['awpc_cr']) ### input
23  AWPC_cr = AWPC_cr / 100
24  M = 10
```
위 코드는 002_clustering.py에서 002_1_AWPC_cr.sh가 전달하는 awpc_cr 값을 받는 코드입니다. 
24line 에서 원하는 클러스터 개수를 지정한 다음 shellscript를 돌리게 되면, 각각 M과 AWPC_cr에 맞게 클러스터링이 진행되고, 그 때의 평균 AWPC 값과 최소 AWPC 값이 화면에 프린트됩니다. 

* 주의: 이 shell script는 적절한 클러스터 개수와 AWPC_cr 값을 정하기 위해 돌리는 용도이기 때문에, 002_clustering.py에서 맨 아래에 있는 ncfile을 작성하는 코드를 주석 처리한 후 돌려야 합니다.
* 적절한 클러스터 개수와 AWPC_cr 값이 정해졌다면, 002_clustering.py 에서 정해진 값을 부여한 후, 마지막 코드를 풀어서 돌리면 됩니다.
* 만약 reproduce 목적이라면, 이 과정을 생락하고 바로 3번으로 가는 것을 추천합니다. 

********

### 3. 002_clustering.py

적절한 클러스터 수(M)와 기준값(AWPC_cr)이 정해졌다면 아래와 같이 002_clustering.py에 AWPC_cr, M 값을 지정합니다.

```
21  AWPC_cr = 0.5 
22  #AWPC_cr = float(os.environ['awpc_cr']) ### input # 주석 처리
23  #AWPC_cr = AWPC_cr / 100                          # 주석 처리
24  M = 10
```

아래 ncfile을 작성하는 코드 또한 주석 처리를 풀어냅니다.

```
f = Dataset(OUTPUT,'w',format='NETCDF4')
new_cen = f.createDimension('Centroid',len(M_centroid))
new_n = f.createDimension('Sample',len(SLP))

cenidx = f.createVariable('Cluster_index', last_cen_idx.dtype, ('Sample'))
new_awpc = f.createVariable('Cluster_avg_AWPC', centroid_AWPC.dtype, ('Centroid'))

cenidx[:] = last_cen_idx
new_awpc[:] = centroid_AWPC

f.close()
```

002_clustering.py 코드를 돌리면 output으로 클러스터링을 완료한 정보가 담긴 **OUTPUT(AWPC_idx_*dataset*.Z500_1958to2020_M*M*_JJA.nc)** 파일이 만들어집니다. 

OUTPUT 파일에는 각 데이터가 몇번 클러스터에 속해있는지에 대한 정보가 담겨있습니다. 

********

### 4. 003_composite.py

클러스터링한 각 클러스터의 centroid를 그림으로 나타냅니다.

각 클러스터에 속하는 데이터의 수와 클러스터의 평균 AWPC의 정보를 함꼐 나타냅니다.

********

### 5. 004_timeseries.py

클러스터별 연간 발생 빈도를 plot으로 나타냅니다.
