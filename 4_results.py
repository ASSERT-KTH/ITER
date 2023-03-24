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


def travFolder_failing_tests(PATCH_PATH):
    listdirs = os.listdir(PATCH_PATH)
    for f in listdirs:
        pattern = 'patches.csv'
        if os.path.isfile(os.path.join(PATCH_PATH, f)):
            if fnmatch.fnmatch(f, pattern) :
                patch_path = os.path.join(PATCH_PATH, f)
                with open(patch_path, 'r') as p_file:                 
                    lines = p_file.readlines()
                    if len(lines) > 1:
                        for i in range(1,len(lines)):
                            l=lines[i]
                            bid=l.split('\t')[0]
                            if bid.isdigit():
                                new_failing_test_nb=l.split('\t')[13]
                                original_failing_test_nb=l.split('\t')[6]
                                print('new_failing_test_nb',new_failing_test_nb)
                                print('original_failing_test_nb',original_failing_test_nb)
                                new_failing_test_nb = new_failing_test_nb.replace(' ','')
                                if new_failing_test_nb.isnumeric() and 'None' not in  new_failing_test_nb and 'timeout' not in l:
                                    if new_failing_test_nb not in '' and int(new_failing_test_nb) < int(original_failing_test_nb) and 'Closure79' in patch_path :
                                        with open('./result_failing_test_closure79.csv', 'a') as result:
                                            patch_path=patch_path.replace('repair_iteration/','').replace('/patches.csv','').replace('/','\t')
                                            result.write(patch_path+'\t'+l)                   
                       
        else:
            travFolder_failing_tests(PATCH_PATH+'/'+f)

            
def travFolder_plausible(PATCH_PATH):
    listdirs = os.listdir(PATCH_PATH)
    for f in listdirs:
        pattern = 'plausible.csv'
        if os.path.isfile(os.path.join(PATCH_PATH, f)):
            if fnmatch.fnmatch(f, pattern):
                patch_path = os.path.join(PATCH_PATH, f)
                with open(patch_path, 'r') as p_file:
                    lines = p_file.readlines()
                    for l in lines:
                        if 'plausible' in l:
                            with open('./result_plausible.csv', 'a') as result:
                                print(patch_path)
                                patch_path=patch_path.replace('repair_iteration/','').replace('plausible.csv','').replace('/','\t')
                                # 1st folder
                                # 2nd FL
                                # 3rd iteration
                                print(patch_path)
                                result.write(patch_path+'\t'+l)                   
                       
        else:
            travFolder_plausible(PATCH_PATH+'/'+f)
                
                

if __name__ == '__main__':
    PATCH_PATH='repair_iteration'
    if os.path.exists('result_failing_test.csv'):
        os.system('rm result_failing_test.csv')
    travFolder_failing_tests(PATCH_PATH)