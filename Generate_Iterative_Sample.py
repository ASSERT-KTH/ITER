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

def inRevertList(save_to_revert,patch_revert):
    flag=False

    if not os.path.exists(patch_revert):
        with open(patch_revert, 'w') as revertlist:
            revertlist.write(save_to_revert+'\n')
        return flag
        
    else:        
        with open(patch_revert, 'r') as revertlist:
            lines = revertlist.readlines()
            for line in lines:
                line=line.replace('\n','')
                if save_to_revert in line and line in save_to_revert:
                    flag = True
                    return flag
    if not flag:
        with open(patch_revert, 'a') as revertlist:
            revertlist.write(save_to_revert+'\n')
            
        return flag
    
    

def getBugInfo(bugid):
    bugid=str(bugid).replace(' ','')
    with open(TEST_PATH,'r') as testfile:
        lines = testfile.readlines()
        for l in lines:
            bid=l.split('\t')[0]
            bid=bid.replace(' ','')
            if bid in bugid and bugid in bid:
                patch = l.split('\t')[1]
                patch = patch.replace('[PATCH]','')
                bug_represent = l.split('\t')[2]
                file_path = l.split('\t')[3]
                
                if '[FE]' in bug_represent:
                    buggy = bug_represent.split('[FE]')[0]
                    buggy = buggy.split('[BUGGY]')[1]
                    bug_represent = ' [FE]' + bug_represent.split('[FE]')[1]
                elif '[CE]' in bug_represent:
                    buggy = bug_represent.split('[CE]')[0]
                    buggy = buggy.split('[BUGGY]')[1]
                    bug_represent = ' [CE]' + bug_represent.split('[CE]')[1]
                elif '[CONTEXT]' in bug_represent:
                    buggy = bug_represent.split('[CONTEXT]')[0]
                    buggy = buggy.split('[BUGGY]')[1]
                    bug_represent=' [CONTEXT] ' + bug_represent.split('[CONTEXT]')[1]
                                   
                
                return patch, buggy, bug_represent,file_path
                
def getNewId(result_filename):
    if not os.path.exists(result_filename):
        return 0
    with open(result_filename,'r') as results:
        lines = results.readlines()
        return len(lines)





        
def test( model, tokenizer, device, loader,model_index,index):
    
    return_sequences = 100
    model.eval()
    identicalset=[]
    
    with torch.no_grad():
        for _,data in enumerate(loader, 0):
            if _>-1:
                gc.collect()
                torch.cuda.empty_cache()
                y = data['target_ids'].to(device, dtype = torch.long)
                ids = data['source_ids'].to(device, dtype = torch.long)
                mask = data['source_mask'].to(device, dtype = torch.long)
                bugid = data['bugid'].to(device, dtype = torch.long)
                print("====bugid===",bugid.item())


                generated_ids = model.generate(
                input_ids = ids,
                attention_mask = mask, 
                max_length=64, 
                num_beams=return_sequences,
                repetition_penalty=3.0,
#                 length_penalty=0.5, 
                early_stopping = False,
                num_return_sequences=return_sequences,
                num_beam_groups = 1
                )


                preds = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in generated_ids]
                target = [tokenizer.decode(t, skip_special_tokens=True, clean_up_tokenization_spaces=True)for t in y]
                target = target[0]
                
                patch, buggy, bug_represent,file_path  = getBugInfo(bugid.item())

                
                   
                for i in range(0,return_sequences):
                    predition = preds[i]
                    predition_no_space=predition.replace(' ','')
                    patch_no_space = patch.replace(' ','')                    
                    buggy_no_space = buggy.replace(' ','')
                    
                    # not identical to patch
                    if predition_no_space in patch_no_space and patch_no_space in predition_no_space:
                        print('identical to patch')
                        with open('./D4J1_TEST_IDENTICAL_Iterative_'+index+'.csv', 'a') as csvfile:
                            filewriter = csv.writer(csvfile, delimiter='\t',escapechar=' ',quoting=csv.QUOTE_NONE)
                            position=(model_index-5)*return_sequences+i+1
                            filewriter.writerow([bugid.item(), position, patch, predition, bug_represent,file_path])
                    # not identical to buggy
                    elif predition_no_space in buggy_no_space and buggy_no_space in predition_no_space:
                        print('identical to original buggy')
                    else:
#                         repeatFlag = inRevertList(str(bugid.item())+'#'+predition_no_space,'revertlist.csv')
#                         print('repeatFlag: '+str(repeatFlag))
#                         if not repeatFlag:
                        new_bug_represent= '[BUG] [BUGGY] '+predition+' '+bug_represent
                        result_filename='./D4J1_TEST_Iterative'+index+'.csv'
                        newid = getNewId(result_filename)
                        with open(result_filename, 'a') as csvfile:
                            filewriter = csv.writer(csvfile, delimiter='\t',escapechar=' ',quoting=csv.QUOTE_NONE)
                            filewriter.writerow([str(newid), '[PATCH] '+patch, new_bug_represent, file_path, bugid.item()])
                        



            
                


def getGeneratorDataLoader(filepatch,tokenizer,batchsize):
    df = pd.read_csv(filepatch,encoding='latin-1',delimiter='\t')
    print(df.head(1))
    
    df = df[['bugid','patch','buggy']]

    params = {
        'batch_size': batchsize,
        'shuffle': True,
        'num_workers': 0
        }

    dataset=df.sample(frac=1.0, random_state = SEED).reset_index(drop=True)
    target_set = loader.GeneratorDataset(dataset, tokenizer, MAX_LEN, PATCH_LEN)
    target_loader = DataLoader(target_set, **params)
    return target_loader




def run_test(epoch,index):
      
    for i in range(5,11):
        gen = T5ForConditionalGeneration.from_pretrained('./model_IterativeRepair/IteRepair'+str(i),output_hidden_states=True)    
        gen_tokenizer = T5Tokenizer.from_pretrained('./model_IterativeRepair/IteRepair'+str(i),truncation=True)
        gen_tokenizer.add_tokens(['[PATCH]','[BUG]','{', '}','<','^','<=','>=','==','!=','<<','>>','[CE]','[FE]','[CONTEXT]','[BUGGY]','[CLASS]','[METHOD]','[RETURN_TYPE]','[VARIABLES]','[Delete]'])   
        gen = gen.to(device)       
        test_loader=getGeneratorDataLoader(TEST_PATH,gen_tokenizer,1)
        test(gen, gen_tokenizer, device, test_loader, i ,index)
          
        
if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    SEED=42
    LEARNING_RATE = 1e-4
    VALID_BATCH_SIZE = 1
    MAX_LEN = 384
    PATCH_LEN = 76 
    device = 'cuda' if cuda.is_available() else 'cpu'
    
    TEST_PATH='/home/D4J1_TEST_Iterative1.csv'
    run_test(0,'2')


