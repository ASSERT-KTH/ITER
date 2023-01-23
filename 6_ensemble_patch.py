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





def apply_add(line):
    originFile=line.split('\t')[4]
    startNo=line.split('\t')[6]
    endNo=line.split('\t')[7]
    patch=line.split('\t')[10]
    #save the original
    os.system("cp "+originFile+" ./projects/ ")    
    
    #construct patched file
    newStr=''    
    #replace
    with open(originFile,'r') as old_file:
        lines=old_file.readlines()
        for i in range(0,len(lines)):
            l=lines[i]
            if i+1 < int(startNo):
                newStr+=l 
            if i+1 == int(startNo):
                newStr+=patch+'\n'+l
            if i+1 > int(startNo):
                newStr+=l
    
    with open(originFile,'w') as newfile:
        newfile.write(newStr)
        

def apply_replace(line):
    originFile=line.split('\t')[4]
    startNo=line.split('\t')[6]
    endNo=line.split('\t')[7]
    patch=line.split('\t')[10]
    #save the original
    os.system("cp "+originFile+" ./projects/ ")    
    
    #construct patched file
    newStr=''    
    #replace
    with open(originFile,'r') as old_file:
        lines=old_file.readlines()
        for i in range(0,len(lines)):
            l=lines[i]
            if i+1 < int(startNo):
                newStr+=l 
            if i+1 == int(startNo):
                newStr+=patch+'\n'
            if i+1 > int(endNo):
                newStr+=l
    
    with open(originFile,'w') as newfile:
        newfile.write(newStr)
        

def apply_patch(line):
    buggy=line.split('\t')[11]
    buggy=buggy.replace(' ','')
    if buggy in '':
        apply_add(line)
    else:
        apply_replace(line)
    

def revert_buggy_class(line):
    originFile=line.split('\t')[4]
    filename = originFile.split('/')[-1]
    os.system("mv ./projects/"+filename +"  "+originFile)


    

def execute(line,n_line):
    bid = line.split('\t')[0]
    project=''
    bug=''
    
    if 'Math' in bid:
        project='Math'
        bug=bid.split('Math')[1]
    elif 'Chart' in bid:
        project='Chart'
        bug=bid.split('Chart')[1]    
    
    elif 'Cli' in bid:
        project='Cli'
        bug=bid.split('Chart')[1]
        
    #checkout the project
    checkout_project="defects4j checkout -p " + project +" -v "+ bug+"b  -w ./projects/"+project+bug
    os.system(checkout_project)
       
    apply_patch(line)
    apply_patch(n_line)
    
    #project path
    os.chdir("./projects/"+bid)
    os.system("defects4j compile")
    test_result = os.popen("defects4j test").read()
    print(test_result)
    os.chdir("../../")
    
    revert_buggy_class(line)
    revert_buggy_class(n_line)

    os.system("rm -rf ./projects/"+bid)
    
    
    with open('./ensemble.csv', 'a') as result:
        r = test_result+'###'+line+'###'+n_line
        r = r.replace('\n','')
        result.write(r+'\n')    


            
def ensemble(PATCH_PATH):
    with open(PATCH_PATH,'r') as result_file:
        lines = result_file.readlines()
        for i in range(0, len(lines)):            
            line=lines[i]
            if 'Chart18' in line:
                bid=line.split('\t')[0]
                buggy_class=line.split('\t')[4]
                for k in range(i+1, len(lines)):
                    n_line=lines[k]
                    n_bid=n_line.split('\t')[0]
                    n_buggy_class=n_line.split('\t')[4]
                    if bid in n_bid and n_bid in bid and n_buggy_class not in buggy_class:
                        execute(line,n_line)
                    

    
                       
       
                
                

if __name__ == '__main__':
    PATCH_PATH='result_failing_test.csv'
    ensemble(PATCH_PATH)
