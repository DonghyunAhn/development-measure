# Stage 2: Handling human-in-the-loop solution  

## Collect Partial Order Graph (POG) from humman annotator  

From stage 1, the model splits the satellite imageries into the clusters.  

For instance, we obtain 11 urban clusters (0 ~ 10) and 11 rural clusters (11 ~ 21) on North Korea.  

Then we ask human annotators to compare each cluster and sort the clusters according to the degree of economic development as follows :  

3=4=6 > 1=2=7 > 0 > 5=8=9 > 10 > 14=16=20 > 15=18 > 11=13 > 12=17=19 > 21  

The uninhabited cluster (22), which is not asked to the annotators, automatically placed at the lowest one.  

In this research, we call this human labels as the **'Partial order graph(POG)'**.  

Ten human participants of varying backgrounds (i.e., satellite imagery experts, North Korean defectors, and economists) were recruited to build POGs.  

The annotation results are listed in `./POG_annotation` directory.  

## Test robustness of human POGs
<TODO>  kendall-tau

## Ensemble POG annotation  
<TODO>  ensemble code implementation & hyperparameters  

## Input for Stage 3  

Rearrange POG according to following rule and save it as text file.

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