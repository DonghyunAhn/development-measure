import os
import csv
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torch.nn.functional as Func
import torchvision.models as models
from torch.autograd import Variable
from torch.utils.data import DataLoader
import argparse
import sys
sys.path.append("..")
from Ranger.ranger import Ranger 

import numpy as np
from dataloader import *
from math import log
from utils.parameters import *

class GPSNDataset(Dataset):
    def __init__(self, metadata, root_dir,transform1=None):
        self.metadata = pd.read_csv(metadata).values
        self.root_dir = root_dir
        self.transform = transform1

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.metadata[idx][0])
        image =  Image.open(img_name)
        
        if self.transform:
            try:
                image = self.transform(image)
            except OSError:
                print(img_name)
                
        return image, idx , self.metadata[idx][0]
def main(args):
    global CONSISTENCY
    global RAMPUP
    global global_step
    global EMA_DECAY
    LEARNING_RATE = 1e-4
    EPOCHS = 200
    BATCH_SIZE = 64
    EVALUATION_EPOCHS = 10
    CHECKPOINT_EPOCHS = 10
    CONSISTENCY = 12.5
    RAMPUP = 20
    global_step = 0
    EMA_DECAY = 0.999




    origin = 'data/'+args.img+'/'


    f = open('./meta_data/'+args.img+'_metadata.csv', 'w', encoding='utf-8', newline='')
    wr = csv.writer(f)
    wr.writerow(['img_name'])

    dirs = os.listdir(origin)
    for d in dirs:
        imgs = os.listdir(origin+d)
        for img in imgs:
            wr.writerow([d+'/'+img])


    f.close()   
    #parser = argparse.ArgumentParser(description='READ extract embedding parser')
    #parser.add_argument('--arch', '-a', metavar='ARCH', default=args.name+'_resnet18')   
    #args = parser.parse_args()
    #print(args.arch)
    #ARCH = args.arch

    train_labeled = ProxyDataset(metadata = "./data/"+args.name+"_annotation/labelling_result.csv", 
                                 root_dir = "./data/"+args.name+"_annotation/gis",
                                 transform=transforms.Compose([
                                     transforms.RandomGrayscale(p=1.0),
                                     transforms.RandomApply([transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)], p=0.8),
                                     transforms.RandomVerticalFlip(p=0.5),
                                      transforms.RandomHorizontalFlip(p=0.5),
                                      transforms.ToTensor(),
                                      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                                 ]))
    
    train_unlabeled = UnlabeledDataset(root_dir = "./data/"+args.img,
                                       transform=transforms.Compose([
                                          transforms.RandomGrayscale(p=1.0),
                                          transforms.RandomApply([transforms.ColorJitter(0.4, 0.4, 0.4, 0.1)], p=0.8),
                                          transforms.RandomVerticalFlip(p=0.5),
                                          transforms.RandomHorizontalFlip(p=0.5),
                                          transforms.ToTensor(),
                                          transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                                       ]))

    train_labeled_loader = torch.utils.data.DataLoader(train_labeled, batch_size=BATCH_SIZE, shuffle=True, num_workers=4, drop_last = True)
    train_unlabeled_loader = torch.utils.data.DataLoader(train_unlabeled, batch_size=BATCH_SIZE, shuffle=True, num_workers=4, drop_last = True)
     
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = models.resnet18(pretrained = True)
    model.fc = nn.Sequential(nn.Linear(512, 3), nn.Softmax())
    ema_model = models.resnet18(pretrained = False)   
    ema_model.fc = nn.Sequential(nn.Linear(512, 3), nn.Softmax())  
    if torch.cuda.device_count() > 1:
        model = nn.DataParallel(model)
        ema_model = nn.DataParallel(ema_model)
        
    model.to(device)
    ema_model.to(device)
    #optimizer = torch.optim.Adam(model.parameters(), lr = LEARNING_RATE)
    optimizer = Ranger(model.parameters(), lr=LEARNING_RATE, weight_decay=0)
    best_loss = float('inf')
    for epoch in range(EPOCHS):
        train(train_labeled_loader, train_unlabeled_loader, model, ema_model, optimizer, epoch, BATCH_SIZE)
        if (epoch + 1) % EVALUATION_EPOCHS == 0:
            save_checkpoint({'state_dict': model.state_dict()}, "./checkpoint", model, epoch + 1, args.name+'_resnet18')
            
    

    #cudnn.benchmark = True
    
    test_transform =transforms.Compose([
                      transforms.Resize(256),
                      transforms.CenterCrop(224),
                      transforms.RandomGrayscale(p=1.0),
                      transforms.ToTensor(),
                      transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    
    testset = GPSNDataset('./meta_data/'+args.img+'_metadata.csv', './data/'+args.img, test_transform)
    testloader = torch.utils.data.DataLoader(testset, batch_size=256, shuffle=False, num_workers=4)
    
    
        
    model.eval()
    label = []
    for batch_idx, (inputs, _, name) in enumerate(testloader):
        #print(name)
        #print(inputs)
        logits = torch.argmax(model(inputs), dim = 1)
        label.extend(logits.tolist())
        
        
    print("Eval Finish")
    
    f = open('./meta_data/'+args.img+'_metadata.csv', 'r', encoding='utf-8')
    images = []
    
    rdr = csv.reader(f)
    for line in rdr:
        images.append(line[0])
    f.close()
    print(images)
    images.pop(0)
    f1 = open('./meta_data/meta_city_'+args.name+'.csv', 'w', encoding='utf-8')
    f2 = open('./meta_data/meta_rural_'+args.name+'.csv', 'w', encoding='utf-8')
    f3 = open('./meta_data/meta_nature_'+args.name+'.csv', 'w', encoding='utf-8')
    wr1 = csv.writer(f1)
    wr1.writerow(['img_name','label'])
    wr2 = csv.writer(f2)
    wr2.writerow(['img_name','label'])
    wr3 = csv.writer(f3)
    wr3.writerow(['img_name','label'])

    for i in range(0, len(images)):
        if label[i] == 0:
            wr1.writerow([images[i], label[i]])
        elif label[i] == 1:
            wr2.writerow([images[i], label[i]])
        elif label[i] == 2:
            wr3.writerow([images[i], label[i]])
        if i % 10000 == 0:
            print(i)
            
    f1.close()
    f2.close()
    f3.close()



def softmax_mse_loss(input_logits, target_logits):
    num_classes = input_logits.size()[1]
    return Func.mse_loss(input_logits, target_logits, reduction='sum') / num_classes            
   
    
def sigmoid_rampup(current, rampup_length):
    if rampup_length == 0:
        return 1.0
    else:
        current = np.clip(current, 0.0, rampup_length)
        phase = 1.0 - current / rampup_length
        return float(np.exp(-5.0 * phase * phase))
     
        
def update_ema_variables(model, ema_model, alpha, global_step):
    alpha = min(1 - 1 / (global_step + 1), alpha)
    for ema_param, param in zip(ema_model.parameters(), model.parameters()):
        ema_param.data.mul_(alpha).add_(1 - alpha, param.data)            
                
def train(train_labeled_loader, train_unlabeled_loader, model, ema_model, optimizer, epoch, batch_size):
    global global_step
    model.train()
    ema_model.eval()
    total_loss = 0
    total_supervised_loss = 0
    total_unsupervised_loss = 0
    count = 0
    consistency_criterion = softmax_mse_loss    
    
    unlabeled_iter = iter(train_unlabeled_loader)
    for i_batch, sample_batched in enumerate(train_labeled_loader):   
        ema_input = next(unlabeled_iter)
        ema_input_var = torch.autograd.Variable(ema_input).cuda() 
        input_image = torch.autograd.Variable(sample_batched['image'].cuda())
        total_input = torch.cat((input_image, ema_input_var), dim = 0)
 
        t = torch.autograd.Variable(sample_batched['y'].cuda())
        y_total = model(total_input)
        y = y_total[:batch_size]
        y_ema = y_total[batch_size:]
        
        supervised_loss = torch.mean(torch.sum(- t * torch.log(y), 1))
       
        ema_model_out = ema_model(ema_input_var)
        ema_logit = ema_model_out
        ema_logit = Variable(ema_logit.detach().data, requires_grad=False)
        consistency_weight = get_current_consistency_weight(epoch)
        consistency_loss = consistency_weight * consistency_criterion(y_ema, ema_logit) / (batch_size * 5)        

        loss = supervised_loss + consistency_loss
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        total_supervised_loss += supervised_loss.item()
        total_unsupervised_loss += consistency_loss.item()
        count += 1
        global_step += 1
        update_ema_variables(model, ema_model, EMA_DECAY, global_step)        
        
    total_loss /= count
    total_supervised_loss /= count
    total_unsupervised_loss /= count
    print(consistency_weight)
    print('[Epoch: %d]\tsuploss: %.5f\tunsuploss: %.5f\tloss: %.5f' % (epoch + 1, total_supervised_loss, total_unsupervised_loss, total_loss))     
       

def get_current_consistency_weight(epoch):
    return CONSISTENCY * sigmoid_rampup(epoch, RAMPUP)    
    
def save_checkpoint(state, dirpath, model, epoch, arch_name):
    filename = '{}_{}.ckpt'.format(arch_name, epoch)
    checkpoint_path = os.path.join(dirpath, filename)
    torch.save(state, checkpoint_path)
           

if __name__ == '__main__':
    args = pretrain_parser()
    main(args)
