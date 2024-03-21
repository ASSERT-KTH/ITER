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

    

if __name__ == '__main__':
    
    PROJECT=sys.argv[1]
    BUG=sys.argv[2]
    new_failing_test=sys.argv[3]
    os.system('python3 1_localize_fault.py '+PROJECT +' '+BUG+' False ')
    os.system('python3 2_bug_representation.py '+PROJECT +' '+BUG+' 0.1 ' +new_failing_test)
    os.system('CUDA_VISIBLE_DEVICES=1 nohup python3 3_repair.py '+PROJECT +' '+BUG+' & ')
    
    
    