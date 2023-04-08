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


def trace_multi_location(patch_path):
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
                diagnostic=p1.split('\t')[13]
                patch_trace = bline+' '+action+'  buggy code at line '+lineNo + ' Diagnostic: '+diagnostic+' \n - '+ buggy +'\n +  '+ patch +' \n'+patch_trace
                
                bline=p2.split('\t')[4]

                lineNo=p2.split('\t')[6]
                susp=p2.split('\t')[5]
                action=p2.split('\t')[9]
                buggy=p2.split('\t')[11]
                patch=p2.split('\t')[10]
                patch_trace = bline+' '+action+'  buggy code at line '+lineNo + 'Diagnostic: '+diagnostic+' \n - '+ buggy +'\n + '+ patch +' \n'+patch_trace

                with open('./patches.csv', 'a') as result:
                    result.write(str(patch_trace)+'\n'+'-'*50+'\n')
  
    
    
    
def getPrevious(patch_path,line,patch_trace):
    print('getPrevious patch_path:'+patch_path)
    print('getPrevious line :'+line)
    print('getPrevious patch_trace :'+patch_trace)
    


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
                diagnostic=l.split('\t')[11]

                                                
                if 'iteration_0' in previousPath:
                    info = previousPath.split('/iteration_')[0]
                    info = info.split('repair_iteration/')[1]
                    info = info.replace('/', ' -  FL is ranked in the ')
                    patch_trace=patch_trace.replace('  ',' ')

                    with open('./patches.csv', 'a') as result:
                        result.write(info +'\n' +str(patch_trace)+'\n')
                else:
                    getPrevious(previousPath,line,patch_trace)
                    
                


        


                
        
        




            
def trace_plausible(PATCH_PATH,count):
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
                            
                            last_iteration=patch_path.split('iteration_')[1]
                            last_iteration=last_iteration.replace('/plausible.csv','')
                            last_iteration=last_iteration.replace('/patches.csv','')
                            diagnostic=l.split('\t')[11]

                            if 'iteration_0'  not in patch_path:  
                                patch_trace = ' '
                                
                                patch_trace = 'iteration_'+last_iteration+ ' '+action+' buggy code at line '+lineNo + ' Diagnostic: '+diagnostic+  ' \n - '+ buggy +'\n + '+ patch +' \n '+'-'*100 
                                patch_path=patch_path.replace('plausible.csv','patches.csv')
                            
                                getPrevious(patch_path,l,patch_trace)
                                
                                
                            else:
                                patch_trace = 'iteration_'+last_iteration+ ' '+action+'  buggy code at line '+lineNo  +' \n - '+ buggy +'\n + '+ patch +' \n '+'-'*50 
                                patch_trace.replace('  ',' ')
                                info = patch_path.split('/iteration_')[0]
                                info = info.split('repair_iteration/')[1]
                                info = info.replace('/', ' -  FL is ranked in the ')
                                count = count+1
                                print(count)
                                with open('./patches.csv', 'a') as result:
                                    result.write(patch_path+'\n')
                                                 
                       
        else:
            trace_plausible(PATCH_PATH+'/'+f, count)
                
                

if __name__ == '__main__':
    if os.path.exists('patches.csv'):
        os.system('rm patches.csv')
    PATCH_PATH='repair_iteration'
    PATCH=''
    trace_plausible(PATCH_PATH,0)


