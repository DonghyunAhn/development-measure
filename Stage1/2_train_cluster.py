import sys
sys.path.append("..")
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim
import torch.utils.data
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import torchvision.models as models
import numpy as np
from utils.siCluster_utils import *
from utils.parameters import *
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def main(args):
    # fix random seeds
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    np.random.seed(args.seed)
    path = '../checkpoint/'+args.name+'_resnet18_200.ckpt'
    model = models.resnet18(pretrained=False)
    model = nn.DataParallel(model)
    model.module.fc = nn.Linear(512, args.nmb_cluster)
    cudnn.benchmark = True
    #model.load_state_dict(torch.load(path)['state_dict'], strict = False)
    model.load_state_dict(torch.load(path), strict = False)
    model.module.fc = nn.Sequential()
    model.cuda()
    cudnn.benchmark = True
    
    cluster_transform =transforms.Compose([
                      transforms.Resize(256),
                      transforms.CenterCrop(224),
                      transforms.RandomGrayscale(p=0.5),
                      transforms.ToTensor(),
                      transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    
    train_transform1 =transforms.Compose([
                      transforms.Resize(256),
                      transforms.CenterCrop(224),
                      transforms.RandomHorizontalFlip(),
                      transforms.RandomVerticalFlip(),
                      transforms.RandomGrayscale(p=0.5),
                      transforms.ToTensor(),
                      transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    
    
    criterion = nn.CrossEntropyLoss().cuda()
    criterion2 = AUGLoss().cuda()

    city = pd.read_csv('../meta_data/meta_city_'+args.name+'.csv')
    rural = pd.read_csv('../meta_data/meta_rural_'+args.name+'.csv')
    inhabited = pd.concat([city,rural],axis=0)
    inhabited.to_csv('../meta_data/meta_inhabited_'+args.name+'.csv',index=False)

    urban_num = len(city)
    rural_num = len(rural)


    clusterset = GPSDataset('../meta_data/meta_inhabited_'+args.name+'.csv', '../data/'+args.img, cluster_transform)
    trainset = GPSDataset('../meta_data/meta_inhabited_'+args.name+'.csv', '../data/'+args.img, train_transform1)

    clusterloader = torch.utils.data.DataLoader(clusterset, batch_size=args.batch, shuffle=False, num_workers=1)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=args.batch, shuffle=True, num_workers=1, drop_last = True)
    optimizer = torch.optim.Adam(model.parameters(), args.lr) 
    #deepcluster = Kmeans(args.nmb_cluster, args.mode)
    features = compute_features(clusterloader, model, len(clusterset), args.batch)
    print("loaded")
    
    for epoch in range(0, args.epochs):
        print("Epoch : %d"% (epoch))
        features = compute_features(clusterloader, model, len(clusterset), args.batch)

        kmeans = KMeans(n_clusters=50).fit(features)
        #clustering_loss, p_label = deepcluster.cluster(features)an

        p_label = kmeans.labels_
        p_label = p_label.tolist()
        p_label = torch.tensor(p_label).cuda()
        model.train()
        fc = nn.Linear(512, args.nmb_cluster)
        fc.weight.data.normal_(0, 0.01)
        fc.bias.data.zero_()
        fc.cuda()
        
        for batch_idx, (inputs, indexes) in enumerate(trainloader):
            inputs, indexes = inputs.cuda(),indexes.cuda()           
            labels = p_label[indexes].cuda()
            outputs = model(inputs)
            outputs2 = fc(outputs)
            loss = criterion(outputs2, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            if batch_idx % 20 == 0:
                torch.save(model.state_dict(), '../checkpoint/ckpt_vanilla_cluster_'+args.name+'_50_pretrained.t7')
                print("[BATCH_IDX : ", batch_idx, "LOSS : ",loss.item(),"]" )
    torch.save(model.state_dict(), '../checkpoint/ckpt_vanilla_cluster_'+args.name+'_50_pretrained.t7')
    



    for i in range(2,21):
     #   features = compute_features(clusterloader, convnet, len(clusterset), 128) 
        print(len(features))

      #  features = compute_features(clusterloader, convnet, len(clusterset), 128) 
        kmeans = KMeans(n_clusters=i).fit(features[:urban_num])
        p_label = kmeans.labels_
        score = silhouette_score(features[:urban_num], p_label, metric="euclidean")
        #score = kmeans.inertia_
        print("score of cluster {} in city is {}".format(i, score))
        kmeans = KMeans(n_clusters=i).fit(features[urban_num:])
        p_label = kmeans.labels_
        score = silhouette_score(features[urban_num:], p_label, metric="euclidean")
        #score = kmeans.inertia_
        print("score of cluster {} in rural is {}".format(i, score))




    
if __name__ == "__main__":
    args = siCluster_parser()
    main(args)    
    