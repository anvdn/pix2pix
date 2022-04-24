from barbar import Bar
import copy
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pickle
import re
from sklearn.metrics import f1_score
import time
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
import torch.nn.functional as F


images_path = os.path.join(os.getcwd(), 'images') 

# setting device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# setting data transformation dictionary for training, validation and testing
data_transforms = {
    'training': T.Compose([
        T.ToPILImage(),
        T.RandomHorizontalFlip(),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'validation': T.Compose([
        T.ToPILImage(),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'testing': T.Compose([
        T.ToPILImage(),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

def get_train_test_image_names(set ,images_path = images_path):
    """
    Description
    -------------
    List names of train and test videos
    Parameters
    -------------
    set            : name of the current data set used
    labels_path    : path to datasets 
    Returns
    -------------
    (train_names, val_names) , each of the tuple elements is a list of strings corresponding to images names
    """
    images_names = {}
    set_images_path = os.path.join(images_path, set) 
    
    for w in ['train','val']:
        set_images_path_w = os.path.join(set_images_path, w) 
        images_names[w] = os.listdir(set_images_path_w)
    # sort list of names
    images_names['train'].sort()
    images_names['val'].sort()

    return images_names


class ImageSet(Dataset):
    """The current data set."""

    def __init__(self,set , transform = None, 
                    val_mode = False ):
        """
        Description
        -------------
        Creates dataset class for the training set.
        Parameters
        -------------
        set                     : dataset name
        transform               : transforms to be applied to the frame (eg. data augmentation)
        test_mode               : boolean, if true there are no label in the annotation df and in the output of __getitem__
        Returns
        -------------
        Torch Dataset for the training set
        """
        self.set = set
        self.transform = transform
        self.val_mode = val_mode
        self.images_names = get_train_test_image_names(self.set)

    def __len__(self):
        if not self.val_mode:
            return len(self.images_names['train'])
        else:
            return len(self.images_names['val'])

    def __getitem__(self, index):
        if not self.val_mode:
            image_path = images_path + '/' + self.set + '/train/' + self.images_names['train'][index] 
            image = cv2.imread(image_path)
            w = image.shape[1]
            w = w // 2
            input_image = image[:, w:, :]
            real_image = image[:, :w, :]
        else: 
            image_path = images_path + '/' + self.set + '/val/' + self.images_names['val'][index] 
            image = cv2.imread(image_path)
            w = image.shape[1]
            w = w // 2
            input_image = image[:, w:, :]
            real_image = image[:, :w, :]
        if self.transform:
            input_image = self.transform(input_image)
            real_image = self.transform(real_image)
        return input_image, real_image
