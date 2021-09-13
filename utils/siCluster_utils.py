import time
import os
import faiss
import numpy as np
import torch
import torch.utils.data as data
import torchvision.transforms as transforms
from torch.utils.data import Dataset
import torch.nn as nn
import pandas as pd
from PIL import Image


class GPSDataset(Dataset):
    def __init__(self, metadata, root_dir,transform1=None, transform2=None):
        self.metadata = pd.read_csv(metadata).values
        self.root_dir = root_dir
        self.transform1 = transform1
        self.transform2 = transform2

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, str(self.metadata[idx][0]))
        
        image =  Image.open(img_name)
        if self.transform1:
            img1 = self.transform1(image)
        if self.transform2:
            img2 = self.transform2(image)
            return img1, img2, idx
                
        return img1, idx

class GPSDataset_year(Dataset):
    def __init__(self, metadata, root_dir,transform1=None):
        self.metadata = pd.read_csv(metadata).values
        self.root_dir = root_dir
        self.transform1 = transform1

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.metadata[idx][0][8:])
        
        image =  Image.open(img_name)
        if self.transform1:
            img1 = self.transform1(image)
                
        return img1, idx

class GPSDataset_test(Dataset):
    def __init__(self, metadata, root_dir,transform1=None, transform2=None):
        self.metadata = pd.read_csv(metadata).values
        self.root_dir = root_dir
        self.transform1 = transform1
        self.transform2 = transform2

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.metadata[idx][0][8:])
        
        image =  Image.open(img_name)
        if self.transform1:
            img1 = self.transform1(image)
        if self.transform2:
            img2 = self.transform2(image)
            return img1, img2, idx
                
        return img1, idx

class AUGLoss(nn.Module):
    def __init__(self):
        super(AUGLoss, self).__init__()

    def forward(self, x1, x2):
        b = (x1 - x2)
        b = b*b
        b = b.sum(1)
        b = torch.sqrt(b)
        return b.sum()

# Below codes are from Deep Clustering for Unsupervised Learning of Visual Features github code        
def preprocess_features(npdata, pca=128):
    _, ndim = npdata.shape
    npdata =  npdata.astype('float32')

    # Apply PCA-whitening with Faiss
    mat = faiss.PCAMatrix (ndim, pca, eigen_power=-0.5)
    mat.train(npdata)
    assert mat.is_trained
    npdata = mat.apply_py(npdata)

    # L2 normalization
    row_sums = np.linalg.norm(npdata, axis=1)
    npdata = npdata / row_sums[:, np.newaxis]

    return npdata

def cluster_assign(images_lists, dataset):
    assert images_lists is not None
    pseudolabels = []
    image_indexes = []
    for cluster, images in enumerate(images_lists):
        image_indexes.extend(images)
        pseudolabels.extend([cluster] * len(images))

    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    t = transforms.Compose([transforms.RandomResizedCrop(224),
                            transforms.RandomHorizontalFlip(),
                            transforms.ToTensor(),
                            normalize])

    return ReassignedDataset(image_indexes, pseudolabels, dataset, t)


def run_kmeans(x, nmb_clusters):
    n_data, d = x.shape

    # faiss implementation of k-means
    clus = faiss.Clustering(d, nmb_clusters)

    # Change faiss seed at each k-means so that the randomly picked
    # initialization centroids do not correspond to the same feature ids
    # from an epoch to another.
    clus.seed = np.random.randint(1234)

    clus.niter = 20
    clus.max_points_per_centroid = 10000000
    res = faiss.StandardGpuResources()
    flat_config = faiss.GpuIndexFlatConfig()
    flat_config.useFloat16 = False
    flat_config.device = 0
    index = faiss.GpuIndexFlatL2(res, d, flat_config)

    # perform the training
    clus.train(x, index)
    _, I = index.search(x, 1)
    losses = faiss.vector_to_array(clus.obj)
    #print('k-means loss evolution: {0}'.format(losses))

    return [int(n[0]) for n in I], losses[-1]


def compute_features(dataloader, model, N, batch_size):
    model.eval()
    # discard the label information in the dataloader
    for i, (inputs, _) in enumerate(dataloader):
        inputs = inputs.cuda()
        aux = model(inputs).data.cpu().numpy()
        aux = aux.reshape(-1, 512)
        if i == 0:
            features = np.zeros((N, aux.shape[1]), dtype='float32')

        aux = aux.astype('float32')
        if i < len(dataloader) - 1:
            features[i * batch_size: (i + 1) * batch_size] = aux
        else:
            features[i * batch_size:] = aux

    return features  


class Kmeans(object):
    def __init__(self, k, mode):
        self.k = k
        self.mode = mode

    def cluster(self, data):
        end = time.time()

        # PCA-reducing, whitening and L2-normalization
        if self.mode == 'city':
            xb = preprocess_features(data, pca = 100)
        if self.mode == 'rural':
            xb = preprocess_features(data, pca = 256)    
        

        # cluster the data
        I, loss = run_kmeans(xb, self.k)
        self.images_lists = [[] for i in range(self.k)]
        label = []
        for i in range(len(data)):
            label.append(I[i])
            self.images_lists[I[i]].append(i)
        label = torch.tensor(label).cuda()
        #print('k-means time: {0:.0f} s'.format(time.time() - end))

        return loss, label

    



