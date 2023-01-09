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



# bugid	buggy	buggy_class	suspiciousness	buggy_line	endbuggycode	failing_test_number	patch

def getBugInfo(bugid):
    bugid=str(bugid).replace(' ','')
    buggy_class=''
    suspiciousness=''
    buggy_line=''
    endbuggycode=''
    failing_test_number=''
    with open(TEST_PATH) as testfile:
        lines = testfile.readlines()
        for l in lines:
            bid=l.split('\t')[0]
            bid=bid.replace(' ','')
            if bid in bugid and bugid in bid:
                buggy_class=l.split('\t')[2]
                buggy_class=buggy_class.replace('\n','').replace('\t','').replace('\r','')
                suspiciousness=l.split('\t')[3]
                buggy_line=l.split('\t')[4]
                endbuggycode = l.split('\t')[5]
                failing_test_number=l.split('\t')[6]                
    
    return buggy_class,suspiciousness,buggy_line,endbuggycode,failing_test_number


def compilation_info():
    #compile
    cmd = "timeout 90 defects4j compile"
    exectresult='[timeout]'
    symbolVaraible=''
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
     
    if 'Running ant (compile)' in str(result):
        result = str(result).split("Running ant (compile)")[1]
        result=result.split('\n')
        for i in range(0,len(result)):
            if 'error: ' in result[i]:
                firstError=result[i].split('error: ')[1]
                exectresult=firstError.split('[javac]')[0]
                if '\\' in exectresult:
                    exectresult=exectresult.split('\\')[0]
                print('=======First Error========='+firstError)
                # 'cannot  find  symbol      
                if 'symbol' in firstError and 'cannot' in firstError and 'find' in firstError:       
                    if '[javac]' in firstError:
                        lines = firstError.split('[javac]')
                        for l in lines:
                            if 'symbol:'in l and 'variable' in l:
                                symbolVaraible=l.split('variable')[1]
                                if '\\' in symbolVaraible:
                                    symbolVaraible=symbolVaraible.split('\\')[0]
                                break



                exectresult='[CE] '+exectresult+symbolVaraible
                break
            elif 'OK' in result[i]:               
                exectresult='OK'
                compile_error_flag=False
                
    return exectresult



def executePatch(originFile,patch,startNo,endNo,failing_test_number):   
    filename = originFile.split('/')[-1]
    project_bug = originFile.split('/')[1]
    
    print(patch)
    
    #save the original
    os.system("cp "+originFile+" ./projects/ ")    
    
    #construct patched file
    newStr=''
    endNo=int(endNo)   
    with open(originFile,'r') as of:
        lines=of.readlines()
        for i in range(0,len(lines)):
            l=lines[i]
            if i+1 < int(startNo):
                newStr+=l 
            if i+1 == int(startNo):
                newStr+=patch+'\n'
            if i+1 >= endNo:
                newStr+=l
    
    with open(originFile,'w') as newfile:
        newfile.write(newStr)
    
      
       
    #project path
    os.chdir("./projects/"+project_bug)
    
    #compile
    exec_result = compilation_info() 
    print(exec_result)

    #execute tests
    if "OK" in exec_result: 
        exec_FL=""
        with open("FL_execution.txt","r") as exec_script:
            exec_FL = exec_script.readlines()[0]
        print(exec_FL)      
        exec_result = os.popen(exec_FL).read()       
        print(exec_result)
        
        
    #reset the original buggy file
    os.chdir("../../")
    os.system("mv ./projects/"+filename +"  "+originFile)


    return exec_result
    
   
    
    


def test( model, tokenizer, device, loader):    
    return_sequences = 1
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
                print("bugid:",bugid.item())

                generated_ids = model.generate(
                input_ids = ids,
                attention_mask = mask, 
                max_length=64, 
                num_beams=return_sequences,
                repetition_penalty=3.0,
                early_stopping = False,
                num_return_sequences=return_sequences,
                num_beam_groups = 1
                )

                preds = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in generated_ids]
                target = [tokenizer.decode(t, skip_special_tokens=True, clean_up_tokenization_spaces=True)for t in y]
                target = target[0]
                
                buggy_class,suspiciousness,buggy_line,endbuggycode,failing_test_number  = getBugInfo(bugid.item())
                patch_path=TEST_PATH.replace("bugs.csv","patches.csv")
                with open(patch_path, 'a') as csvfile:
                    filewriter = csv.writer(csvfile, delimiter='\t',escapechar=' ',quoting=csv.QUOTE_NONE)                 
                    for i in range(0,return_sequences):
                        new_bugid = int(bugid.item()-1)*(return_sequences)+i+1
                        execution_result = executePatch(buggy_class,preds[i],buggy_line,endbuggycode,failing_test_number)
                        filewriter.writerow([str(new_bugid),project+bug,buggy_class,suspiciousness,buggy_line,endbuggycode,failing_test_number,preds[i]])


def getGeneratorDataLoader(filepath,tokenizer,batchsize):
    df = pd.read_csv(filepath,encoding='latin-1',delimiter='\t')
    print(df.head(1))
    
    df = df[['bugid','buggy','patch']]

    params = {
        'batch_size': batchsize,
        'shuffle': True,
        'num_workers': 0
        }

    dataset=df.sample(frac=1.0, random_state = SEED).reset_index(drop=True)
    target_set = loader.GeneratorDataset(dataset, tokenizer, MAX_LEN, PATCH_LEN)
    target_loader = DataLoader(target_set, **params)
    return target_loader

        
def run_test():    
    gen = T5ForConditionalGeneration.from_pretrained('./model/IteRepair',output_hidden_states=True)       
    gen_tokenizer = T5Tokenizer.from_pretrained('./model/IteRepair',truncation=True)
    gen_tokenizer.add_tokens(['[PATCH]','[BUG]','{', '}','<','^','<=','>=','==','!=','<<','>>','[CE]','[FE]','[CONTEXT]','[BUGGY]','[CLASS]','[METHOD]','[RETURN_TYPE]','[VARIABLES]','[Delete]'])   
    gen = gen.to(device)       
    test_loader=getGeneratorDataLoader(TEST_PATH,gen_tokenizer,1)
    test(gen, gen_tokenizer, device, test_loader)




if __name__ == '__main__':
#     for i in range(26,27):
#         os.system("./1_localize_fault.py Chart "+str(i))
#         os.system("./2_bug_representation.py Chart "+str(i)+" 0.1  0 ")
        
    project=sys.argv[1]
    bug=sys.argv[2]
    rounds=sys.argv[3]  
    warnings.filterwarnings('ignore')
    SEED=42
    LEARNING_RATE = 1e-4
    VALID_BATCH_SIZE = 1
    MAX_LEN = 384
    PATCH_LEN = 76 
    device = 'cuda' if cuda.is_available() else 'cpu'

    TEST_PATH='repair_iteration/'+project+bug+'/iteration_'+rounds+'/bugs.csv'
    print(TEST_PATH)
    
    run_test()
    
    
    
    
    
    
    
 