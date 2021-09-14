
## Step 1. Pretrain
***

### 0) Download Optimizer

Download optimizer from https://github.com/lessw2020/Ranger-Deep-Learning-Optimizer
Rename directory into Ranger.

### 1) Annotate sample images

Choose 1,000 sample imagery from entire dataset. Human anotates 1,000 images among 3 categories : Urban, Rural, and Uninhabited. Make annotation result into single file and save this file and sample image (Refer to "lao_1_annotation" directory)


### 2) Pre-training

Pretrain model with default values of hyper-parameter defined in utils/parameters.py, pretrain_parser().


```
usage: 1_pretrain.py [-h] [--img IMG] [--name NAME]

pretrain parser

optional arguments:
  -h, --help            show this help message and exit
  --img IMG             name of the image directory
  --name NAME           model & annotated directory name

```

Example

```python3 1_pretrain.py --name lao_1 --img LAO```


## Step 2. Clustering
***

### 1) Train clustering model

Train clustering model and print silhouete score for each cluster number with default values of hyper-parameter defined in utils/parameters.py, siCluster_parser().


```
usage: 2_train_cluster.py [-h] [--lr LR] [--epochs EPOCHS] [--batch BATCH]
                          [--momentum MOMENTUM] [--seed SEED]
                          [--nmb_cluster NMB_CLUSTER] [--name NAME]
                          [--img IMG]

siCluster parser

optional arguments:
  -h, --help            show this help message and exit
  --lr LR               learning rate
  --epochs EPOCHS       number of total epochs to run
  --batch BATCH         mini-batch size
  --momentum MOMENTUM   momentum
  --seed SEED           random seed
  --nmb_cluster NMB_CLUSTER, --k NMB_CLUSTER
                        number of cluster for k-means
  --name NAME           model & annotated directory name
  --img IMG             name of the image directory
  
```


Example

```python3 2_train_cluster.py --name lao_1 --img LAO```

Example output
```
score of cluster 2 in city is 0.42540857195854187
score of cluster 2 in rural is 0.3261856436729431
score of cluster 3 in city is 0.39280208945274353
score of cluster 3 in rural is 0.28625282645225525
score of cluster 4 in city is 0.3649527132511139
score of cluster 4 in rural is 0.30611342191696167
score of cluster 5 in city is 0.3576197922229767
score of cluster 5 in rural is 0.3114365339279175
score of cluster 6 in city is 0.3412483036518097
score of cluster 6 in rural is 0.3132252097129822
score of cluster 7 in city is 0.33266395330429077
score of cluster 7 in rural is 0.29889968037605286
score of cluster 8 in city is 0.3302342891693115
score of cluster 8 in rural is 0.30160173773765564
score of cluster 9 in city is 0.32167160511016846
score of cluster 9 in rural is 0.30135852098464966
score of cluster 10 in city is 0.3545919954776764
score of cluster 10 in rural is 0.2908525764942169
score of cluster 11 in city is 0.338534951210022
score of cluster 11 in rural is 0.29690173268318176
score of cluster 12 in city is 0.33687207102775574
score of cluster 12 in rural is 0.29597207903862
score of cluster 13 in city is 0.34778445959091187
score of cluster 13 in rural is 0.29904696345329285
score of cluster 14 in city is 0.34466126561164856
score of cluster 14 in rural is 0.2922791540622711
score of cluster 15 in city is 0.3294903039932251
score of cluster 15 in rural is 0.29506686329841614
score of cluster 16 in city is 0.35617536306381226
score of cluster 16 in rural is 0.29051804542541504
score of cluster 17 in city is 0.31365838646888733
score of cluster 17 in rural is 0.2895110845565796
score of cluster 18 in city is 0.2882598340511322
score of cluster 18 in rural is 0.285915344953537
score of cluster 19 in city is 0.3144502341747284
score of cluster 19 in rural is 0.2863290011882782
score of cluster 20 in city is 0.30703505873680115
score of cluster 20 in rural is 0.290301650762558
```

### 2) Decide number of clusters

Human decide number of clusters referring to silhouette scores in previous step.

![Alt text](sil_example.png)
Choose cluster number which makes a peak (ex) 11 for city, 8 for rural)


### 3) Extract clusters

Extract clusters with default values of hyper-parameter defined in utils/parameters.py, extract_cluster_parser().

```
usage: 3_extract_cluster.py [-h] [--city_cnum CITY_CNUM]
                            [--rural_cnum RURAL_CNUM] [--name NAME]
                            [--img IMG]

extract_cluster parser

optional arguments:
  -h, --help            show this help message and exit
  --city_cnum CITY_CNUM
                        number of city clusters
  --rural_cnum RURAL_CNUM
                        number of rural clusters
  --name NAME           model & annotated directory name
  --img IMG             name of the image directory
```



Example

```python3 3_extract_cluster.py --name lao_1 --img LAO --city_cnum 8 --rural_cnum```

