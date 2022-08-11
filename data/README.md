## Data availability     

Due to the data capacity limit of, we partially uploads the data on this repository.  
If you want to attach the data, please contact to `segaukwa@gmail.com`.  

### North Korea  

The directories in this repoisitory contains:  

__NK__  
The Sentinel-2 images taken from 2016 to 2019, with 9.557m/pixel resoultion.  

__nk_annotation__  
The labeling result used to train trinary classifier urban/rural/uninhabited for pre-training the neural network.  
The result from 4 annotators on 1250 images(`gis/*.png`) are reported within soft-label manner (`labeling_result.csv`).   

__cluster_nk_11_11__  
The urban(11)/rural(11) clusters derived by Stage 1 of our model.  
23rd cluster, the uninhabited region, is not included in this directory because it comes from trinary classifier that determines urban/rural/uninhabited region.  