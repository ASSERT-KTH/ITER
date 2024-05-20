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
import sys, subprocess,fnmatch, shutil, csv,re, datetime,time


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
    
    
    
def getNewBugId(patch_path):
    with open(patch_path,'r') as patchfile:
        lines = patchfile.readlines()
        return len(lines)
    

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
                    old_diagnostic = bug_represent.split('[FE]')[1]
                    if '[CONTEXT]' in old_diagnostic:
                        old_diagnostic='[FE] ' + old_diagnostic.split('[CONTEXT]')[0]

                    bug_represent= bug_represent.split('[FE]')[0]

                elif '[CE]' in bug_represent:
                    old_diagnostic = bug_represent.split('[CE]')[1]
                    if '[CONTEXT]' in old_diagnostic:
                        old_diagnostic='[CE] ' + old_diagnostic.split('[CONTEXT]')[0]
                    bug_represent= bug_represent.split('[CE]')[0]
                    
                original_buggy = bug_represent.split('[BUGGY] ')[1]
                if '[CE]' in original_buggy:
                    original_buggy=original_buggy.split('[CE]')[0]
                elif '[FE]' in original_buggy:
                    original_buggy=original_buggy.split('[FE]')[0]
                    
                buggy_class=l.split('\t')[2]
                buggy_class=buggy_class.replace('\n','').replace('\t','').replace('\r','')
                suspiciousness=l.split('\t')[3]
                buggy_line=l.split('\t')[4]
                endbuggycode = l.split('\t')[5]
                failing_test_number=l.split('\t')[6]   
                action=l.split('\t')[7]
                previous_patch=l.split('\t')[8]
                return buggy_class,suspiciousness,buggy_line,endbuggycode,failing_test_number,original_buggy,original_bug_represent,action,previous_patch,old_diagnostic


def compilation_info():
    #compile
    cmd = "timeout 180 defects4j compile"
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
    if "Cli" in project or 'Math' in project or 'Compress' in project or 'Gson' in project or 'Csv' in project or 'JacksonCore' in project  or 'JacksonDatabind' in project  or 'Jsoup' in project or 'JxPath' in project:
        if os.path.exists("./target/classes") and os.path.exists("./target/test-classes"):
            os.system("cp -rf ./target/classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build-tests/")    
    if "Codec" in project : 
        if os.path.exists("./target"):
            os.system("mkdir build")
            os.system("mkdir build-tests")
            os.system("cp -rf ./target/classes/*" + "  ./build/")
            os.system("cp -rf ./target/tests/*" + "  ./build/")
            os.system("cp -rf ./target/tests/*" + "  ./build-tests/")     
    if 'Time' in project:
        if os.path.exists("./target"):
            os.system("mkdir build")
            os.system("mkdir build-tests")
            os.system("cp -rf ./target/classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build-tests/")
        elif os.path.exists("./build"):
            os.system("mkdir build-tests")
            os.system("cp -rf ./build/classes/*" + "  ./build/")
            if os.path.exists("./build/tests"):
                os.system("cp -rf ./build/tests/*" + "  ./build/")
                os.system("cp -rf ./build/tests/*" + "  ./build-tests/")
    
    if "Closure" in project:
        if os.path.exists("./build/classes"):
            os.system("mkdir build-tests")
            os.system("cp -rf ./build/classes/*" + "  ./build/")
            os.system("cp -rf ./build/test/*" + "  ./build/")
            os.system("cp -rf ./build/test/*" + "  ./build-tests/")
    
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
        exec_result = os.popen('timeout 720 '+ exec_FL).read()
        #if time out
        if 'DONE' not in exec_result:
            failing_test_count=10
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


        diagnosis = ' [FE] ' + diagnosis+' '
        diagnosis = diagnosis.replace("\r","").replace("\n","")

    
                    
    return failing_test_count, diagnosis
                
        
        

def executePatch(originFile,patch,startNo,endNo,action,project,origin_failing_test):  
    
    print('executePatch',action)
    
    if 'replace' in action:
        result, diagnosis, failing_test_count = replace_action(originFile,patch,startNo,endNo,project,origin_failing_test)
    
    elif 'add' in action:
        result, diagnosis, failing_test_count = add_action(originFile,patch,startNo,endNo,project,origin_failing_test)
    
        
    return result, diagnosis, failing_test_count,action
    

def replace_action(originFile,patch,startNo,endNo,project,origin_failing_test):   
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
        

        
   #check if failing test number reduce
    if 'compilable' in exec_result and str(failing_test_count).isnumeric() and int(origin_failing_test)>int(failing_test_count):
        #keep this partial fix
        os.chdir("../../")
    else:
        #reset the original buggy file
        os.chdir("../../")
        os.system("mv ./projects/"+filename +"  "+originFile)                       

    return exec_result, diagnosis, failing_test_count



def add_action(originFile,patch,startNo,endNo,project,origin_failing_test):   
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
        
    #check if failing test number reduce
    if 'compilable' in exec_result and str(failing_test_count).isnumeric() and int(origin_failing_test)>int(failing_test_count):
        #keep this partial fix
        os.chdir("../../")
    else:
        #reset the original buggy file
        os.chdir("../../")
        os.system("mv ./projects/"+filename +"  "+originFile)


    return exec_result, diagnosis, failing_test_count
    
   
    
    


def test( model, tokenizer, device, loader, index,project, FL, fl_iteration):    
    return_sequences = 10
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
                
                buggy_class,suspiciousness,buggy_line,endbuggycode,original_failing_test_number,original_buggy,old_BR,action,previous_patch,old_diagnostic = getBugInfo(bugid.item())
                
                patch_path=TEST_PATH.replace("bugs.csv","patches.csv")
                patch_revert=TEST_PATH.replace("bugs.csv","revert.csv")
                patch_plausible=TEST_PATH.replace("bugs.csv","plausible.csv")

                if not os.path.exists(patch_path):
                    with open(patch_path, 'w') as csvfile:
                        csvfile.write('bugid\tbuggy\tbuggy_class\tsuspiciousness\tbuggy_line\tendbuggycode\toriginal_failing_test_number\taction\tpatch\toriginal_buggy\texecution_result\tdiagnosis\tprevious_bug_id\tnew_failing_test_number\tthis_action\n')
                                                                                      
                for i in range(0,return_sequences):
                    continue_repair=True
                    #avoid the prediction is same with buggy
                    original_buggy_no_space=original_buggy.replace(" ","")
                    prediction_no_space = preds[i].replace(" ","")
                    prediction=preds[i] 
                    
                    prediction=prediction.replace('< =','<=')
                    prediction=prediction.replace('> =','>=')
                    prediction=prediction.replace('= =','==')
                    prediction=prediction.replace('! =','!=')


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
                        execution_result,diagnosis,new_failing_test_number,action = executePatch(buggy_class,prediction,buggy_line,endbuggycode,action,project,original_failing_test_number)                        

                        #patch minimization
                        print(execution_result, diagnosis)
                        print('='*50)
                        print(' '*50)

                                
                        # patch minimization
                        # Rule 4: discard the patch with increase failing test number                      
                        print('new_failing_test_number:',new_failing_test_number)
                        print('original_failing_test_number:',original_failing_test_number)

                        ## save the partial fix that reduce the original failing tests
                        ## reexcute FL
                        if 'compilable' in execution_result and 'None' not in str(new_failing_test_number) and int(original_failing_test_number)>int(new_failing_test_number) and str(new_failing_test_number).isnumeric():
                            project_bug = buggy_class.split('/')[1] 
                            print('partial fix is found!')
                            print(project+','+buggy_class+','+buggy_line+','+action+','+diagnosis+','+original_buggy+','+prediction+','+str(original_failing_test_number)+','+str(new_failing_test_number))
                            with open(Partial_Fix, 'a') as patch_partial_file:
                                patch_partial_file.write(project_bug+'\t'+'FL-'+fl+'\t'+buggy_class+'\t'+buggy_line+'\t'+suspiciousness+'\t'+action+'\t'+diagnosis+'\t'+original_buggy+'\t'+prediction+'\t'+str(original_failing_test_number)+'\t'+str(new_failing_test_number)+'\n')
                                
                              
                            print(project_bug)
                            if 'Math' in project_bug:
                                proj='Math'
                                project_bug = project_bug.replace('Math','')
                            elif 'Closure' in project_bug:
                                proj='Closure'
                                project_bug = project_bug.replace('Closure','')
                            elif 'Lang' in project_bug:
                                proj='Lang'
                                project_bug = project_bug.replace('Lang','')                           
                            elif 'Chart' in project_bug:
                                proj='Chart'
                                project_bug = project_bug.replace('Chart','')
                            elif 'Time' in project_bug:
                                proj='Time'
                                project_bug = project_bug.replace('Time','')
                            elif 'Cli' in project_bug:
                                proj='Cli'
                                project_bug = project_bug.replace('Cli','')
                            elif 'Codec' in project_bug:
                                proj='Codec'
                                project_bug = project_bug.replace('Codec','')
                            elif 'Compress' in project_bug:
                                proj='Compress'
                                project_bug = project_bug.replace('Compress','')

                            cmd='nohup python3 ITER_FL.py ' + proj+'  '+project_bug  + ' '+str(new_failing_test_number) +'  & '
                            os.system(cmd)
                            sys.exit(0)



                        if True:
                            new_bugid = getNewBugId(patch_path)
                            print('new_bugid:'+str(new_bugid))
                            print('execution_result:'+execution_result)

                            #new bug representation based on new prediction
                            BR_context=old_BR.split('[CONTEXT]')[1]
                            context_parts = BR_context.split('[BUGGY]') 
                            if len(context_parts)>2:
                                old_diagnostic='[FE]  '+old_diagnostic.split('[FE]')[-1]
                                new_BR_replace = '[BUG] [BUGGY] '+prediction+' '+diagnosis+' '+old_diagnostic+' [CONTEXT] '+context_parts[0]+' [BUGGY] '+ prediction + ' [BUGGY] '+context_parts[2]
                                new_BR_add = '[BUG] [BUGGY] '+diagnosis+' '+old_diagnostic+' [CONTEXT] '+context_parts[0]+' [BUGGY] '+ prediction + ' [BUGGY] '+context_parts[2]

                                new_BR_replace=new_BR_replace.replace('  ',' ')
                                new_BR_add=new_BR_add.replace('  ',' ')

                                if 'plausible' in execution_result:
                                    with open(patch_plausible, 'a') as csvfile:
                                        filewriter = csv.writer(csvfile, delimiter='\t',escapechar=' ',quoting=csv.QUOTE_NONE)
                                        filewriter.writerow([str(new_bugid),old_BR,buggy_class,suspiciousness,buggy_line,endbuggycode,original_failing_test_number,action,prediction,original_buggy,execution_result,diagnosis,str(bugid.item()),new_failing_test_number]) 
                                        
                                             
                                    #record plausible patches in FL, iteration and rounds                  
                                    print('a plausible patch is found!')
                                    end = time.time() - start
                                    print("--- %s seconds ---" % end)
                                    if not os.path.exists(PLAUSIBLE):
                                        os.system('touch '+PLAUSIBLE) 
                                        with open(PLAUSIBLE,'w') as plausible:
                                            plausible.write('FL_Ranking,Iteration,Time\n')
                                    with open(PLAUSIBLE,'a') as plausible:
                                        info=fl_iteration+','+FL+','+str(rounds)+','+str(end)+'\n'
                                        plausible.write(info)
                                       
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

        
def run_test(project, FL,fl_iteration):
    for m in [2]:
        gen = T5ForConditionalGeneration.from_pretrained('./model_ItRepair/IteRepair'+str(m),output_hidden_states=True)       
        gen_tokenizer = T5Tokenizer.from_pretrained('./model_ItRepair/IteRepair'+str(m),truncation=True)
        gen_tokenizer.add_tokens(['[PATCH]','[BUG]','{', '}','<','^','<=','>=','==','!=','<<','>>','[CE]','[FE]','[CONTEXT]','[BUGGY]','[CLASS]','[METHOD]','[RETURN_TYPE]','[VARIABLES]','[Delete]'])   
        gen = gen.to(device)       
        test_loader=getGeneratorDataLoader(TEST_PATH,gen_tokenizer,1)
        index=1
        test(gen, gen_tokenizer, device, test_loader, index,project,FL,fl_iteration)




if __name__ == '__main__':
        
    project=sys.argv[1]
    bug=sys.argv[2]
    warnings.filterwarnings('ignore')
    SEED=42
    LEARNING_RATE = 1e-4
    VALID_BATCH_SIZE = 1
    MAX_LEN = 512
    PATCH_LEN = 76 
    device = 'cuda' if cuda.is_available() else 'cpu'
    PLAUSIBLE_FLAG=False   
    PARTIAL_FIX_FLAG=False   

    start = time.time()

    BUGS_PATH='repair_iteration/'+project+bug+'/bugs.csv'
    PLAUSIBLE='repair_iteration/'+project+bug+'/plausible.csv'
    Partial_Fix='repair_iteration/'+project+bug+'/partial.csv'


    if os.path.exists(BUGS_PATH):
        with open(BUGS_PATH,'r') as bug_path:
            all_buggy = bug_path.readlines()
            
            #fault localization iteration
            #suspicious statement iteration
            if os.path.exists('repair_iteration/'+project+bug+'/'+'FL-4'):
                fl='5'
            elif os.path.exists('repair_iteration/'+project+bug+'/'+'FL-3'):
                fl='4'
            elif os.path.exists('repair_iteration/'+project+bug+'/'+'FL-2'):
                fl='3'
            elif os.path.exists('repair_iteration/'+project+bug+'/'+'FL-1'):
                fl='2'
            else:
                fl='1'
                
                
            print('FL:'+str(fl))
            for i in range(0,len(all_buggy)-1,2):   
                print(str(i))
                bug_str=all_buggy[0]+all_buggy[i]

                root='repair_iteration/'+project+bug+'/'+'FL-'+fl+'/'+str(int(i/2)+1)
                TEST_PATH = root +'/iteration_0/bugs.csv'
                os.system('mkdir -p '+ root+'/iteration_0/' )
                os.system('touch '+  TEST_PATH)
                os.system('cp  repair_iteration/'+project+bug+'/bugs.csv  repair_iteration/'+project+bug+'/'+'FL-'+fl)
                os.system('cp  repair_iteration/'+project+bug+'/tests.csv  repair_iteration/'+project+bug+'/'+'FL-'+fl)
                os.system('cp  repair_iteration/'+project+bug+'/ochiai.ranking.csv' +'  repair_iteration/'+project+bug+'/'+'FL-'+fl)

                with open(TEST_PATH,'w') as target_bug:
                    target_bug.write(bug_str)

                #repair attemp iteration
                for rounds in range(0,3):
                    print('Iteration '+str(rounds)+'  '+project+bug +' FL: '+str(int(i/2)+1))
                    TEST_PATH = root +'/iteration_'+str(rounds)+'/bugs.csv'

                    run_test(project,str(int(i/2)+1),fl)
                    PATCH_PATH=root+'/iteration_'+str(rounds)+'/patches.csv' 
                    REVERT_PATH=root+'/iteration_'+str(rounds)+'/revert.csv'
                    NEXT_REVERT_PATH=root+'/iteration_'+str(rounds+1)+'/revert.csv'
                    NEXT_ROUND_PATH=root+'/iteration_'+str(rounds+1)  


                    # parse the patches generated in previous iteration as the bugs to be repaired in next iterat
                    with open(PATCH_PATH,'r') as next_bugs:
                        lines = next_bugs.readlines()
                        if len(lines)==1:
                            print('break iteration for '+ project+bug + ' with FL '+str(int(i/2)+1) + ' in round '+ str(rounds))
                            break
                        else:
                            os.system('rm -rf '+NEXT_ROUND_PATH)
                            os.system('mkdir -p '+NEXT_ROUND_PATH)
                            os.system('cp '+PATCH_PATH+'  '+NEXT_ROUND_PATH+'/bugs.csv')
                            os.system('cp '+REVERT_PATH+'  '+NEXT_ROUND_PATH)
        