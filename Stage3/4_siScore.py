import sys
sys.path.append("..")
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
import torch.backends.cudnn as cudnn
import pandas as pd
from torch.utils.data import DataLoader
from utils.graph import *
from utils.siScore_utils import *
from utils.parameters import *
import os
from itertools import permutations
import copy
from Ranger.ranger import Ranger 

class TestDataset(Dataset):
    def __init__(self, transform=None):
        self.file_list = glob.glob('../data/'+args.img+'/*/*.png')
        self.transform = transform        

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        path = self.file_list[idx]
        #con = path.split("/")[-3][:3]
        direc = path.split("/")[-2]
        #name = path[-19:-9]
        name = path.split("/")[-1].split(".png")[0]
        name = direc + '*' + name
        #image =  Image.open(path)
        image = io.imread(path) / 255.0


        if self.transform:
            #image =  self.transform(image)
            image = self.transform(np.stack([image])).squeeze()

        return image, name

def make_data_loader(cluster_list, batch_sz):
    cluster_dataset = ClusterDataset(cluster_list, dir_name = args.dir_name, transform = transforms.Compose([
                                       RandomRotate(),
                                       ToTensor(),
                                       Grayscale(prob = 1.0),
                                       Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                                    ]))
    cluster_loader = torch.utils.data.DataLoader(cluster_dataset, batch_size=batch_sz, shuffle=True, num_workers=4, drop_last=True)
    return cluster_loader
    
    
def generate_loader_dict(total_list, unified_cluster_list, batch_sz):
    loader_dict = {}
    for cluster_id in total_list:
        cluster_loader = make_data_loader([cluster_id], batch_sz)
        loader_dict[cluster_id] = cluster_loader        
    
    for cluster_tuple in unified_cluster_list:
        cluster_loader = make_data_loader(cluster_tuple, batch_sz)
        for cluster_num in cluster_tuple:
            loader_dict[cluster_num] = cluster_loader
    return loader_dict


def deactivate_batchnorm(model):
    for m in model.modules():
        if isinstance(m, nn.BatchNorm2d):
            m.reset_parameters()
            m.eval()
            with torch.no_grad():
                m.weight.fill_(1.0)
                m.bias.zero_()
                

def train(args, epoch, model, optimizer, scheduler, loader_list, cluster_path_list, device):
    model.train()
    # Deactivate the batch normalization before training
    deactivate_batchnorm(model.module)
    train_loss = AverageMeter()
    linear_loss = AverageMeter()
    reg_loss = AverageMeter()
    
    # For each cluster route
    path_idx = 0
    avg_loss = 0
    count = 0
    
    steps = 38
  
    for cluster_path in cluster_path_list:

        path_idx += 1
        dataloaders = []
        for cluster_id in cluster_path:
            dataloaders.append(loader_list[cluster_id])
        #print(dataloaders)
        #print(scheduler.get_lr())
        scheduler.step()
        for batch_idx, data in enumerate(zip(*dataloaders)):
            
            #print("in")
            lam = np.random.beta(1.0, 1.0)
            cluster_num = len(data)
            data_zip = torch.cat(data, 0).to(device)
            
            scores = model(data_zip).squeeze()
            scores = torch.clamp(scores, min=0, max=1)
            
            idx_A = torch.randperm(data_zip.shape[0])
            idx_B = torch.randperm(data_zip.shape[0])
            img_A1 = copy.deepcopy(data_zip[idx_A, :, :])
            img_B1 = copy.deepcopy(data_zip[idx_B, :, :])
            img_A1[:, :int(lam*256),:] = 0
            img_B1[:, int(lam*256):,:] = 0
            img_M1 = img_A1 + img_B1

            # Generating Score
            score_A = scores[idx_A]
            score_B = scores[idx_B]
            score_M1 = model(img_M1).squeeze()
            score_M1 = torch.clamp(score_M1, min=0, max=1)
            loss_linear = torch.abs(score_M1 - (lam*score_A + (1-lam)*score_B)).sum() / score_M1.shape[0]
            score_list = torch.split(scores, args.batch_sz, dim = 0)
            linear_loss.update(loss_linear.item(), args.batch_sz)
            # Differentiable Ranking with sigmoid function
            rank_matrix = torch.zeros((args.batch_sz, cluster_num, cluster_num)).to(device)
            for itertuple in list(permutations(range(cluster_num), 2)):
                score1 = score_list[itertuple[0]]
                score2 = score_list[itertuple[1]]
                diff = args.lamb * (score2 - score1)
                results = torch.sigmoid(diff)
                rank_matrix[:, itertuple[0], itertuple[1]] = results
                rank_matrix[:, itertuple[1], itertuple[0]] = 1 - results

            rank_predicts = rank_matrix.sum(1)
            temp = torch.Tensor(range(cluster_num))
            target_rank = temp.unsqueeze(0).repeat(args.batch_sz, 1).to(device)

            # Equivalent to spearman rank correlation loss
            #print(rank_predicts[0])
            #print(target_rank[0])
            loss_train = ((rank_predicts - target_rank)**2).mean()
            loss = loss_train + loss_linear*args.alpha
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss.update(loss_train.item(), args.batch_sz)
            
            avg_loss += loss.item()
            count += 1

            # Print status
            if batch_idx % 10 == 0:
                print('Epoch: [{epoch}][{path_idx}][{elps_iters}] '
                      'Train loss: {train_loss.val:.4f} ({train_loss.avg:.4f}) '
                      'Linear loss: {linear_loss.val:.4f} ({linear_loss.avg:.4f})'.format(
                          epoch=epoch, path_idx=path_idx, elps_iters=batch_idx, train_loss=train_loss, linear_loss=linear_loss, reg_loss=reg_loss))
                
    return avg_loss / count
   

def main(args):
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    np.random.seed(args.seed)

    # Input example
    cluster_number = args.cluster_num
    #os.environ["CUDA_VISIBLE_DEVICES"]='1,2,3'

    # Graph generation mode
    graph_config = '../graph_config/'+args.graph_config  

    
    # Dataloader definition   
    start, end, partial_order, cluster_unify = graph_process(graph_config)  
    print(partial_order, end)
    loader_list = generate_loader_dict(range(cluster_number), cluster_unify, args.batch_sz)
    cluster_graph = generate_graph(partial_order, cluster_number)
    cluster_path_list = cluster_graph.printPaths(start, end)
    print("Cluster_path: ", cluster_path_list)
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("loader list", cluster_unify)
    model = models.resnet18(pretrained=False)
    model.fc = nn.Sequential()

    if torch.cuda.device_count() > 1:
        model = nn.DataParallel(model) 
        cudnn.benchmark = True

      
    model.module.fc = nn.Sequential(nn.Linear(512, 3))    
    model.load_state_dict(torch.load('../checkpoint/'+args.name+'_resnet18_200.ckpt')['state_dict'], strict = True)
    model.module.fc = nn.Sequential(nn.Linear(512, 1))
    #model.load_state_dict(torch.load(args.pretrained_path)['model'], strict = True)
    #print("loaded {loss}".format( loss=torch.load(args.pretrained_path)['loss']))
    model.to(device)
    
    optimizer = Ranger(model.parameters(), lr=args.lr, weight_decay=0)
    
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, 200)    
    #optimizer = torch.optim.Adam(model.parameters(), lr = args.lr)
    print("Pretrained net load finished")
    
    best_loss = float('inf')
    if args.load == False:    
        for epoch in range(args.epochs):          
            loss = train(args, epoch, model, optimizer, scheduler,loader_list, cluster_path_list, device)

            if epoch % 10 == 0 and epoch != 0:                
                if best_loss > loss:
                    print("state saving...")
                    state = {
                        'model': model.state_dict(),
                        'loss': loss
                    }
                    if not os.path.isdir('checkpoint'):
                        os.mkdir('checkpoint')
                    torch.save(state, '../checkpoint/{}'.format(args.name))
                    best_loss = loss
                    print("best loss: %.4f\n" % (best_loss))

    model.eval()    
    test_dataset = TestDataset(transform = transforms.Compose([
                                          #transforms.ToTensor(),  
                                          #transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

                                          ToTensor(),  Grayscale(),
                                          Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                                       ]))
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=200, shuffle=False, num_workers=4)
    print(len(test_dataset))    
    df2 = pd.DataFrame(columns = ['direc','y_x', 'score'])
    #df2 = pd.DataFrame(columns = [ 'name', 'score'])
    cnt = 0

    with torch.no_grad():
        for batch_idx, (data, name) in enumerate(test_loader):
            print(batch_idx)
            data = data.to(device)
            scores = model(data).squeeze()
            count = 0
            scores = torch.clamp(scores, min=0, max=1)
            #print("here")nohupn py
            for each_name in name:
                #print(each_name[:10], each_name[11:])
                #con = each_name.split('*')[0][:3]
                
                dist = each_name.split('*')[0]
                na  = each_name.split('*')[1]
                df2.loc[cnt] = [dist, na, scores[count].cpu().data.numpy()]
                cnt += 1  
                count += 1  
            df2.to_csv(args.name+'_'+args.img+'_scores.csv')
    df2.to_csv(args.name+'_'+args.img+'_scores.csv')

if __name__ == "__main__":
    args = siScore_parser()
    main(args)

