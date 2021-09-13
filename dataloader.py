import os
import glob
import torch
import numpy as np
import pandas as pd
from skimage import io, transform
from torchvision import transforms
import torchvision.transforms.functional as F 
from torch.utils.data import Dataset
from PIL import Image
    
        
class ProxyDataset(Dataset):
    def __init__(self, metadata, root_dir, transform=None):
        self.metadata = pd.read_csv(metadata)
        self.root_dir = root_dir
        self.transform = transform
        
    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        assert(idx < len(self))     
        image_name, urban, rural,  nature = self.metadata.iloc[idx, :].values

        image_name = str(int(image_name)) + '.png'
        image_path = "{}/{}".format(self.root_dir, image_name)
        image = Image.open(image_path)
        
        y = [urban, rural, nature]
        #y = [0, 0, 0]
        #y[answer] = 1
        sample = {'image': image, 'y': torch.Tensor(y)}      
        if self.transform:
            sample['image'] = self.transform(image)
        return sample   

    
class UnlabeledDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.file_list = glob.glob('./{}/*/*.png'.format(root_dir))
        self.transform = transform

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        images = Image.open(self.file_list[idx])
        if self.transform:
            images = self.transform(images)
        return images

class UnlabeledDataset_year(Dataset):
    def __init__(self, metadata, root_dir,transform=None):
        self.metadata = pd.read_csv(metadata).values
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.metadata)*5

    def __getitem__(self, idx):
        year = idx % 5 
        root_dir = self.root_dir + str(year+2015)
        img_name = os.path.join(root_dir, self.metadata[year*len(self.metadata)+ idx//5][0])
        image =  Image.open(img_name)
        if self.transform:
            img = self.transform(image)
                
        return img, idx   
    
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
        
    
class ToTensor(object):
    def __call__(self, images):
        images = images.transpose((0, 3, 1, 2))
        return torch.from_numpy(images).float()
    