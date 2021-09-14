import sys
sys.path.append("..")
import os
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.utils.data
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import torchvision.models as models
from utils.siCluster_utils import *
from utils.parameters import *
import glob
import shutil
import copy
import csv
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans


urban_cluster_num = 8
rural_cluster_num = 9
bare_cluster_num = 6
def extract_inhabited_cluster(args):
    convnet = models.resnet18(pretrained=True)
    convnet = torch.nn.DataParallel(convnet)    
    print("loaded")
    ckpt = torch.load('../checkpoint/ckpt_vanilla_cluster_'+args.name+'_50_pretrained.t7')
    convnet.load_state_dict(ckpt, strict = False)
    convnet.module.fc = nn.Sequential()
    convnet.cuda()
    cluster_transform =transforms.Compose([
                      transforms.Resize(256),
                      transforms.CenterCrop(224),
                      transforms.RandomGrayscale(p=1.0),
                      transforms.ToTensor(),
                      transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])    

    city = pd.read_csv('../meta_data/meta_city_'+args.name+'.csv')

    urban_num = len(city)

    clusterset = GPSDataset('../meta_data/meta_inhabited_'+args.name+'.csv', '../data/'+args.img, cluster_transform)
    clusterloader = torch.utils.data.DataLoader(clusterset, batch_size=128, shuffle=False, num_workers=1)
    features = compute_features(clusterloader, convnet, len(clusterset), 128) 

    kmeans = KMeans(n_clusters=args.city_cnum).fit(features[:urban_num])
    p_label1 = kmeans.labels_
    kmeans = KMeans(n_clusters=args.rural_cnum).fit(features[urban_num:])
    p_label2= kmeans.labels_


    labels1 = p_label1.tolist()
    labels2 = p_label2.tolist()
    f = open('../meta_data/meta_inhabited_'+args.name+'.csv', 'r', encoding='utf-8')
    images = []
    rdr = csv.reader(f)
    for line in rdr:
        images.append(line[0])
    f.close()
    images.pop(0)    
    rural_cluster = []
    print(len(images))
    for i in range(0, urban_num):
        rural_cluster.append([images[i], labels1[i]])
    for j in range(urban_num, len(images)):
        rural_cluster.append([images[j], labels2[j-urban_num]+args.city_cnum])

    return rural_cluster



def extract_nature_cluster(args):
    f = open('../meta_data/meta_nature_'+args.name+'.csv', 'r', encoding='utf-8')
    images = []
    rdr = csv.reader(f)
    for line in rdr:
        images.append(line[0])
    f.close()
    images.pop(0)    
    nature_cluster = []
    cnum = args.city_cnum + args.rural_cnum 
    for i in range(0, len(images)):
        nature_cluster.append([images[i], cnum])
        
    return nature_cluster



def main(args):
    # make cluster directory
    print("main")
    inhabited_cluster = extract_inhabited_cluster(args)
    nature_cluster = extract_nature_cluster(args)
    total_cluster = inhabited_cluster + nature_cluster 
    
    cluster_dir = '../data/cluster_'+args.name+'_'+str(args.city_cnum)+'_'+str(args.rural_cnum)+'/'
    if not os.path.exists(cluster_dir):
        os.makedirs(cluster_dir)
        for i in range(0, args.city_cnum + args.rural_cnum  + 1):
            os.makedirs(cluster_dir + str(i))

    
    for img_info in total_cluster:
        cur_dir = '../data/'+args.img+'/' + img_info[0]
    
        new_dir = cluster_dir + str(img_info[1])
        new_file = cluster_dir + str(img_info[1])+'/'+img_info[0].split('/')[1]

        shutil.copy(cur_dir, new_dir)
       # os.rename(cluster_dir + str(img_info[1])+'/'+img_info[0][-14:], new_file)
'''
    file_list = glob.glob("./{}/*/*.png".format(args.cluster_dir))
    grid_dir = cluster_dir + args.grid
    f = open(grid_dir, 'w', encoding='utf-8')
    wr = csv.writer(f)
    wr.writerow(['y_x', 'cluster_id'])
    
    for file in file_list:
        file_split = file.split("/")
        folder_name = file_split[2]
        file_name = file_split[-1].split(".")[0]
        wr.writerow([file_name, folder_name])
    f.close()
    
'''
if __name__ == "__main__":
    args = extract_cluster_parser()
    main(args)    
    