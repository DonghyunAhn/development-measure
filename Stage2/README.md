# Stage 2: Handling human-in-the-loop solution  

## Make Partial Order Graph (POG) with clusters

Compare each cluster and sort the clusters according to the degree of economic development as follows :

22 < 11=19 < 12=13=18=21 < 15=17=20 < 14=16 < 5=8=10 < 0=7=9 < 1=2=3=4=6

Then, rearrange it according to following rule and save it as text file.

Example (graph_config/nk.txt)

```
0<1
5<0
14<5
15<14
12<15
11<12
22<11
1=2=3=4=6
0=7=9
5=8=10
14=16
15=17=20
12=13=18=21
11=19
```

## Ensemble POG annotation  
<TODO>  ensemble code implementation & hyperparameters  

## Test robustness of human POGs
<TODO>  kendall-tau
