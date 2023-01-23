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
    with open(TEST_PATH) as testfile:
        lines = testfile.readlines()
        for l in lines:
            bid=l.split('\t')[0]
            bid=bid.replace(' ','')
            if bid in bugid and bugid in bid:
                original_bug_represent=l.split('\t')[1]
                bug_represent = l.split('\t')[1]
                if '[FE]' in bug_represent:
                    bug_represent= bug_represent.split('[FE]')[0]
                elif '[CE]' in bug_represent:
                    bug_represent= bug_represent.split('[CE]')[0]
                original_buggy = bug_represent.split('[BUGGY] ')[1]
                buggy_class=l.split('\t')[2]
                buggy_class=buggy_class.replace('\n','').replace('\t','').replace('\r','')
                suspiciousness=l.split('\t')[3]
                buggy_line=l.split('\t')[4]
                endbuggycode = l.split('\t')[5]
                failing_test_number=l.split('\t')[6]   
                action=l.split('\t')[7]
                previous_patch=l.split('\t')[8]
                return buggy_class,suspiciousness,buggy_line,endbuggycode,failing_test_number,original_buggy,original_bug_represent,action,previous_patch


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



def test_execute_info(project):   
    currentpath=os.path.dirname(os.path.realpath(__file__))
    failing_test_count=0
    diagnosis = ""
    failingtest=""
    if os.path.exists('./build/tests.txt'):
        os.system('rm -rf ./build/tests.txt')
    
    if os.path.exists('./build/gzoltar.ser'):
        os.system('rm -rf ./build/gzoltar.ser')
        
    if os.path.exists('./build/sfl'):
        os.system('rm -rf ./build/sfl')
    
#     if "Cli" in project or 'Math' in project:
    if "Cli" in project or 'Math' in project or 'Time' in project:
        if os.path.exists("./target/classes") and os.path.exists("./target/test-classes"):
            os.system("cp -rf ./target/classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build-tests/")    
    
    if "Lang" in project:
        if os.path.exists("./target") and os.path.exists("./target/tests"):
            os.system("cp -rf ./target/classes/*" + "  ./build/")
            os.system("cp -rf ./target/tests/*" + "  ./build/")
            os.system("cp -rf ./target/tests/*" + "  ./build-tests/")
        elif os.path.exists("./target") and os.path.exists("./target/test-classes"):
            os.system("mkdir build")
            os.system("mkdir build-tests")
            os.system("cp -rf ./target/classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build-tests/")

    
    with open("FL_execution.txt","r") as exec_script:
        
        exec_FL = exec_script.readlines()[0]
        exec_result = os.popen('timeout 120 '+ exec_FL).read()
        #if time out
        if 'DONE' not in exec_result:
            failing_test_count=1
            return failing_test_count, 'timeout'
            
        print(exec_result)
        if 'Run test methods in isolation' in str(exec_result):
            test_result = str(exec_result).split('Run test methods in isolation')[1]
            results = test_result.split('\n')
            for r in results:
                if 'Has it failed? true' in r:
                    failing_test_count+=1   
                    
    if failing_test_count>0:                
        with open('./build/sfl/txt/tests.csv','r') as testfails:
            lines = testfails.readlines()
            for l in lines:
                if "FAIL" in l:
                    if diagnosis in "":
                        failingtest=l.split(",")[0]
                        failingtest=failingtest.split("#")[1]
                        print(l)
                        diagnosis=l.split(",")[3]
                        if "at" in diagnosis:
                            diagnosis = diagnosis.split(" at")[0]
                            diagnosis=str(diagnosis)
                            if ":" in diagnosis:
                                diagnosis = diagnosis.split(":")[0]
                            if "." in diagnosis:
                                diagnosis = diagnosis.split(".")[-1]


        diagnosis = ' [FE] ' + diagnosis+' '+failingtest 
        diagnosis = diagnosis.replace("\r","").replace("\n","")

    
                    
    return failing_test_count, diagnosis
                
        
        

def executePatch(originFile,patch,startNo,endNo,action,project):  
    
    print('executePatch',action)
    
    if 'replace' in action:
        result, diagnosis, failing_test_count = replace_action(originFile,patch,startNo,endNo,project)
    
    elif 'add' in action:
        result, diagnosis, failing_test_count = add_action(originFile,patch,startNo,endNo,project)
    
        
    return result, diagnosis, failing_test_count,action
    

def replace_action(originFile,patch,startNo,endNo,project):   
    filename = originFile.split('/')[-1]
    project_bug = originFile.split('/')[1]   
    diagnosis=''    
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
          
    #project path
    os.chdir("./projects/"+project_bug)
    
    #compile
    exec_result = compilation_info() 
    diagnosis = exec_result
    failing_test_count='None'
    #execute tests
    if "OK" in exec_result: 
        failing_test_count, diagnosis = test_execute_info(project)
        if failing_test_count==0:
            exec_result = 'plausible'
        else:
            exec_result = 'compilable'   
    else:
        exec_result='non-compiled'
        

    #reset the original buggy file
    os.chdir("../../")
    os.system("mv ./projects/"+filename +"  "+originFile)


    return exec_result, diagnosis, failing_test_count



def add_action(originFile,patch,startNo,endNo,project):   
    filename = originFile.split('/')[-1]
    project_bug = originFile.split('/')[1]   
    diagnosis=''    
    #save the original
    os.system("cp "+originFile+" ./projects/ ")    
    
    #construct patched file
    newStr=''    
    #add
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
          
    #project path
    os.chdir("./projects/"+project_bug)
    
    #compile
    exec_result = compilation_info() 
    diagnosis = exec_result
    failing_test_count='None'
    #execute tests
    if "OK" in exec_result: 
        failing_test_count, diagnosis = test_execute_info(project)
        if failing_test_count==0:
            exec_result = 'plausible'
            print('plausible patch found:')
            print('patch:'+patch)

        else:
            exec_result = 'compilable'   
    else:
        exec_result='non-compiled'
        

    #reset the original buggy file
    os.chdir("../../")
    os.system("mv ./projects/"+filename +"  "+originFile)


    return exec_result, diagnosis, failing_test_count
    
   
    
    


def test( model, tokenizer, device, loader, index,project):    
    return_sequences = 5
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
                generated_ids = model.generate(
                input_ids = ids,
                attention_mask = mask, 
                max_length=128, 
                num_beams=return_sequences,
                repetition_penalty=3.0,
                early_stopping = False,
                num_return_sequences=return_sequences,
                num_beam_groups = 1
                )

                preds = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in generated_ids]
                target = [tokenizer.decode(t, skip_special_tokens=True, clean_up_tokenization_spaces=True)for t in y]
                target = target[0]
                
                buggy_class,suspiciousness,buggy_line,endbuggycode,original_failing_test_number,original_buggy,old_BR,action,previous_patch = getBugInfo(bugid.item())
                
                patch_path=TEST_PATH.replace("bugs.csv","patches.csv")
                patch_minimization=TEST_PATH.replace("bugs.csv","patch_discard.csv")
                patch_revert=TEST_PATH.replace("bugs.csv","revert.csv")
                patch_plausible=TEST_PATH.replace("bugs.csv","plausible.csv")


                if not os.path.exists(patch_path):
                    with open(patch_path, 'w') as csvfile:
                        csvfile.write('bugid\tbuggy\tbuggy_class\tsuspiciousness\tbuggy_line\tendbuggycode\toriginal_failing_test_number\taction\tpatch\toriginal_buggy\texecution_result\tdiagnosis\tprevious_bug_id\tnew_failing_test_number\tthis_action')
                                                                                      
                for i in range(0,return_sequences):
                    #avoid the prediction is same with buggy
                    original_buggy_no_space=original_buggy.replace(" ","")
                    prediction_no_space = preds[i].replace(" ","")
                    prediction=preds[i]                                                       

                    #perform the deletion action
                    if i==return_sequences-1 and 'replace' in action:
                        prediction=" "
                    if 'add' in action:
                        prediction=previous_patch+'  '+prediction
                    
                    prediction=prediction.replace('\n','')    
                    
                    print('buggy line NB: '+buggy_line)
                    print('- '+original_buggy)
                    print('+ '+prediction)
                    
                    if i==0:
                        #create a regression list with original buggy 
                        save_original_buggy=buggy_class+buggy_line+original_buggy
                        save_original_buggy=save_original_buggy.replace(' ','')                    
                    
                    #patch minimization
                    # Rule 1: discard the patch is same with buggy code
                    inRevertList(save_original_buggy,patch_revert)
                    #create a regression list with prediction                             
                    save_to_revert=buggy_class+buggy_line+prediction
                    save_to_revert=save_to_revert.replace(' ','')
                    #patch minimization
                    # Rule: patch revert to previous patch or buggy code 
                   
                    existFlag = inRevertList(save_to_revert,patch_revert)
                    if existFlag:
                        print('in revertion list, will not be executed')
                        print('='*50)                        

                    elif not existFlag:
                        execution_result,diagnosis,new_failing_test_number,action = executePatch(buggy_class,prediction,buggy_line,endbuggycode,action,project)                        

                        #patch minimization
                        # Rule 2: discard the patch with compilation error                                   
                        print(execution_result, diagnosis)
                        print('='*50)
                        print(' '*50)

                        if '[CE]' in diagnosis:
                            if 'not a statement' in diagnosis:
                                break
                            if 'incompatible' in diagnosis:
                                break
                            if 'illegal' in diagnosis:
                                break
                            with open(patch_minimization, 'a') as patch_minimization_file:
                                patch_minimization_file.write('compilation error,'+buggy_line+','+action+','+diagnosis+','+original_buggy+','+prediction+'\n')
                            break
                                


                         #patch minimization
                        # Rule 4: discard the patch with increase failing test number                      
                        print('new_failing_test_number:',new_failing_test_number)
                        print('original_failing_test_number:',original_failing_test_number)

                        if 'compilable' in execution_result and 'None' not in str(new_failing_test_number) and int(original_failing_test_number)<int(new_failing_test_number):
                            with open(patch_minimization, 'a') as patch_minimization_file:
                                patch_minimization_file.write('increase failing tests,'+buggy_line+','+action+','+diagnosis+','+original_buggy+','+prediction+'\n')


                        else:
                            new_bugid = int(_)*int(return_sequences)*int(index)*2+i+1 

                            #new bug representation based on new prediction
                            BR_context=old_BR.split('[CONTEXT]')[1]
                            context_parts = BR_context.split('[BUGGY]') 
                            if len(context_parts)>2:
                                new_BR_replace = '[BUG] [BUGGY] '+prediction+' '+diagnosis+' [CONTEXT] '+context_parts[0]+' [BUGGY] '+ prediction + ' [BUGGY] '+context_parts[2]
                                new_BR_add = '[BUG] [BUGGY] '+diagnosis+' [CONTEXT] '+context_parts[0]+' [BUGGY] '+ prediction + ' [BUGGY] '+context_parts[2]

                                new_BR_replace=new_BR_replace.replace('  ',' ')
                                new_BR_add=new_BR_add.replace('  ',' ')

                                if 'plausible' in execution_result:
                                    with open(patch_plausible, 'a') as csvfile:
                                        filewriter = csv.writer(csvfile, delimiter='\t',escapechar=' ',quoting=csv.QUOTE_NONE)
                                        filewriter.writerow([str(new_bugid),old_BR,buggy_class,suspiciousness,buggy_line,endbuggycode,original_failing_test_number,action,prediction,original_buggy,execution_result,diagnosis,str(bugid.item()),new_failing_test_number]) 
                                else:  
                                    print('write to patches.csv:'+save_to_revert)
                                    with open(patch_path, 'a') as csvfile:
                                        filewriter = csv.writer(csvfile, delimiter='\t',escapechar=' ',quoting=csv.QUOTE_NONE)
                                        if 'compilable' in execution_result:
                                            filewriter.writerow([str(new_bugid),new_BR_add,buggy_class,suspiciousness,buggy_line,endbuggycode,original_failing_test_number,'add',prediction,original_buggy,execution_result,diagnosis,str(bugid.item()),new_failing_test_number,action]) 
                                            filewriter.writerow([str(new_bugid+1),new_BR_replace,buggy_class,suspiciousness,buggy_line,endbuggycode,original_failing_test_number,'replace',prediction,original_buggy,execution_result,diagnosis,str(bugid.item()),new_failing_test_number,action]) 
                                        else:
                                            filewriter.writerow([str(new_bugid),new_BR_replace,buggy_class,suspiciousness,buggy_line,endbuggycode,original_failing_test_number,'replace',prediction,original_buggy,execution_result,diagnosis,str(bugid.item()),new_failing_test_number,action]) 




def getGeneratorDataLoader(filepath,tokenizer,batchsize):
    df = pd.read_csv(filepath,encoding='latin-1',delimiter='\t')    
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

        
def run_test(project):
    for m in [5,8,10]:
        gen = T5ForConditionalGeneration.from_pretrained('./ItRepair/model_ItRepair/ItRepair'+str(m),output_hidden_states=True)       
        gen_tokenizer = T5Tokenizer.from_pretrained('./ItRepair/model_ItRepair/ItRepair'+str(m),truncation=True)
        gen_tokenizer.add_tokens(['[PATCH]','[BUG]','{', '}','<','^','<=','>=','==','!=','<<','>>','[CE]','[FE]','[CONTEXT]','[BUGGY]','[CLASS]','[METHOD]','[RETURN_TYPE]','[VARIABLES]','[Delete]'])   
        gen = gen.to(device)       
        test_loader=getGeneratorDataLoader(TEST_PATH,gen_tokenizer,1)
        if m == 5:
            index=1
        elif m == 8:
            index=2
        elif m == 10:
            index=3
        test(gen, gen_tokenizer, device, test_loader, index,project)




if __name__ == '__main__':
        
    project=sys.argv[1]
    bug=sys.argv[2]
    warnings.filterwarnings('ignore')
    SEED=42
    LEARNING_RATE = 1e-4
    VALID_BATCH_SIZE = 1
    MAX_LEN = 512
    PATCH_LEN = 128 
    device = 'cuda' if cuda.is_available() else 'cpu'

    for rounds in range(0,5):
        print('Iteration '+str(rounds)+'  '+project+bug)
        TEST_PATH='repair_iteration/'+project+bug+'/iteration_'+str(rounds)+'/bugs.csv'
        run_test(project)       
        PATCH_PATH='repair_iteration/'+project+bug+'/iteration_'+str(rounds)+'/patches.csv'
        REVERT_PATH='repair_iteration/'+project+bug+'/iteration_'+str(rounds)+'/revert.csv'
        NEXT_REVERT_PATH='repair_iteration/'+project+bug+'/iteration_'+str(rounds+1)+'/revert.csv'


        NEXT_ROUND_PATH='repair_iteration/'+project+bug+'/iteration_'+str(rounds+1)        
        if os.path.exists(PATCH_PATH):
            os.system('rm -rf '+NEXT_ROUND_PATH)
            os.system('mkdir -p '+NEXT_ROUND_PATH)
            os.system('cp '+PATCH_PATH+'  '+NEXT_ROUND_PATH+'/bugs.csv')
            os.system('cp '+REVERT_PATH+'  '+NEXT_ROUND_PATH)
        
        
    
    
    
    
    
    
    
 