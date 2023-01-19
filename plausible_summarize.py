import numpy as np
import pandas as pd
import torch,sys
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler
import warnings
from torch import cuda
from transformers import T5Tokenizer, T5ForConditionalGeneration
import loader
import torch.autograd as autograd
import csv
import os, gc
import sys, subprocess,fnmatch, shutil, csv,re, datetime


def travFolder(PATCH_PATH):
    listdirs = os.listdir(PATCH_PATH)
    for f in listdirs:
        pattern = 'patches.csv'
        if os.path.isfile(os.path.join(PATCH_PATH, f)):
            if fnmatch.fnmatch(f, pattern):
                patch_path = os.path.join(PATCH_PATH, f)
                with open(patch_path, 'r') as p_file:
                    lines = p_file.readlines()
                    for l in lines:
                        if 'plausible' in l:
                            with open('./results.csv', 'a') as result:
                                result.write(patch_path+'\t'+l)                   
                       
        else:
            travFolder(PATCH_PATH+'/'+f)
                
                

if __name__ == '__main__':
    PATCH_PATH='repair_iteration'
    travFolder(PATCH_PATH)