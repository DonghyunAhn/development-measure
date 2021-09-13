import glob
import torch
import numpy as np
from skimage import io, transform
from torchvision import transforms
import torchvision.transforms.functional as F 
from torch.utils.data import Dataset
from PIL import Image
import random

class ClusterDataset(Dataset):
    def __init__(self, cluster_list, dir_name, transform=None):
        self.file_list = []
        self.transform = transform      
        for cluster_num in cluster_list:
            self.file_list.extend(glob.glob('./data/{}/{}/*.png'.format(dir_name, cluster_num)))

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        image = io.imread(self.file_list[idx]) / 255.0
        if self.transform:
            image = self.transform(np.stack([image])).squeeze()
        return image

    
class RandomRotate(object):
    def __call__(self, images):
        rotated = np.stack([self.random_rotate(x) for x in images])
        return rotated
    
    def random_rotate(self, image):
        rand_num = np.random.randint(0, 4)
        if rand_num == 0:
            return np.rot90(image, k=1, axes=(0, 1))
        elif rand_num == 1:
            return np.rot90(image, k=2, axes=(0, 1))
        elif rand_num == 2:
            return np.rot90(image, k=3, axes=(0, 1))   
        else:
            return image
    
    
class Normalize(object):
    def __init__(self, mean, std, inplace=False):
        self.mean = mean
        self.std = std
        self.inplace = inplace

    def __call__(self, images):
        normalized = np.stack([F.normalize(x, self.mean, self.std, self.inplace) for x in images]) 
        return normalized
 

    
class Grayscale(object):
    def __init__(self, prob = 1):
        self.prob = prob

    def __call__(self, images):     
        random_num = np.random.randint(100, size=1)[0]
        if random_num <= self.prob * 100:
            gray_images = (images[:, 0, :, :] + images[:, 1, :, :] + images[:, 2, :, :]) / 3
            gray_scaled = gray_images.unsqueeze(1).repeat(1, 3, 1, 1)
            return gray_scaled
        else:
            return images
        

    

class ToTensor(object):
    def __call__(self, images):
        images = images.transpose((0, 3, 1, 2))
        return torch.from_numpy(images).float()

class AverageMeter(object):
    def __init__(self):
        self.reset()
                   
    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0 

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count