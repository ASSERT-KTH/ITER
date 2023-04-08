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
    for i in range(1,106):
        PROJECT='Math'
        TEST_PATH='repair_iteration/'+PROJECT+str(i)+'/iteration_0'
        os.system('rm -rf '+TEST_PATH)
        os.system("python3 1_localize_fault.py "+PROJECT +" "+str(i))
        os.system("python3 2_bug_representation.py "+PROJECT +" "+str(i)+" 0.1 ")
        os.system("python3 3_repair.py "+PROJECT +" "+str(i))
