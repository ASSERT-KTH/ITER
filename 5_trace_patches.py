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


def trace_ensemble(patch_path):
    with open(patch_path,'r') as ensemble_file:
        lines = ensemble_file.readlines()
        for line in lines:
            if 'Failing tests: 0' in line:
                p1 = line.split('###')[1]
                p2 = line.split('###')[2]
                print(p1)
                patch_trace=''
                bline=p1.split('\t')[4]
                lineNo=p1.split('\t')[6]
                susp=p1.split('\t')[5]
                action=p1.split('\t')[9]
                buggy=p1.split('\t')[11]
                patch=p1.split('\t')[10]
                patch_trace = bline+' '+action+' '+lineNo + ' suspicious value: '+susp+' \n - '+ buggy +'\n +  '+ patch +' \n'+patch_trace
                
                bline=p2.split('\t')[4]

                lineNo=p2.split('\t')[6]
                susp=p2.split('\t')[5]
                action=p2.split('\t')[9]
                buggy=p2.split('\t')[11]
                patch=p2.split('\t')[10]
                patch_trace = bline+' '+action+' '+lineNo + ' suspicious value: '+susp+' \n - '+ buggy +'\n + '+ patch +' \n'+patch_trace

                with open('./patches.csv', 'a') as result:
                    result.write(str(patch_trace)+'\n'+'-'*50+'\n')
  
    
    
    
def getPrevious(patch_path,line,patch_trace):
    previoud_pid = line.split('\t')[12]
    rounds=patch_path.split('iteration_')[1]
    rounds=rounds.split('/')[0]
    rest = patch_path.split('iteration_'+rounds)[1]
    previousPath=patch_path.split('iteration_')[0]+'iteration_'+str(int(rounds)-1)+rest
    
    with open(previousPath, 'r') as result:
        lines=result.readlines()
        for i in range(1,len(lines)):
            l = lines[i]
            pid =  l.split('\t')[0]
            if pid in previoud_pid and previoud_pid in pid:
                line=l
                lineNo=l.split('\t')[4]
                susp=l.split('\t')[3]
                action=l.split('\t')[7]
                buggy=l.split('\t')[9]
                patch=l.split('\t')[8]
                patch_trace = 'iteration_'+str(int(rounds)-1) + ' '+action+' '+lineNo + ' suspicious value: '+susp+' \n - '+ buggy +'\n + '+ patch +' \n'+patch_trace

    
    if 'iteration_0' not in previousPath:
        getPrevious(previousPath,line,patch_trace)
        
    else:
        return patch_trace
        


                
        
        




            
def trace_plausible(PATCH_PATH):
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
                            susp=l.split('\t')[3]
                            lineNo=l.split('\t')[4]
                            action=l.split('\t')[7]
                            patch=l.split('\t')[8]
                            buggy=l.split('\t')[9]
                            if 'iteration_0' not in patch_path:                               
                                patch_trace = ' '
                                patch_trace = action+' '+lineNo + ' suspicious value: '+susp+  ' \n - '+ buggy +'\n + '+ patch +' \n '+'-'*50 
                                patch_path=patch_path.replace('plausible.csv','patches.csv')
                                patch_trace = patch_path +'\n'+ str(getPrevious(patch_path,l,patch_trace))
                                patch_trace=patch_trace.replace('  ',' ')
                                print(patch_trace)
                            else:
                                patch_trace = patch_path + ' '+action+' '+lineNo + ' suspicious value: '+susp +' \n - '+ buggy +'\n + '+ patch +' \n '+'-'*50 
                                print(patch_trace)
                            
                            with open('./patches.csv', 'a') as result:
                                result.write(str(patch_trace)+'\n')
                                                 
                       
        else:
            trace_plausible(PATCH_PATH+'/'+f)
                
                

if __name__ == '__main__':
    if os.path.exists('patches.csv'):
        os.system('rm patches.csv')
    PATCH_PATH='repair_iteration'
    trace_ensemble('ensemble.csv')
    trace_plausible(PATCH_PATH)


