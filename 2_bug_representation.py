#!/usr/bin/python
import sys, os, subprocess,fnmatch, shutil, csv, re, datetime

def getDiagnosis(project,bug):
    failingtest = ''
    faildiag = ''
    project_info="defects4j info -p "+ project +" -b " +bug
    result = os.popen(project_info).read()
    if 'Root cause in triggering tests:' in str(result):
        result=str(result).split('Root cause in triggering tests:')[1]
    if 'List of modified sources' in str(result):
        result=str(result).split('List of modified sources')[0]
    
    print(result)
    resultLines = str(result).split('\\')
    
    for l in resultLines:
        if '-' in l and '::' in l and failingtest  in '':
            failingtest = l.split('::')[1]
            if '-->' in failingtest:
                failingtest = failingtest.split('-->')[0]
            failingtest=failingtest.strip()
            print('failingtest******'+failingtest)

            break
    for l in resultLines:
        if '-->' in l and faildiag in '':
            faildiag = l.split('-->')[1]
            if '-' in faildiag:
                faildiag = faildiag.split('-')[0]
            if ':' in faildiag:
                faildiag = faildiag.split(':')[0]
            if '.' in faildiag:
                faildiag = faildiag.split('.')[-1]
                break
    
    diagnosis = ' [FE] ' + faildiag +' '+failingtest 
    diagnosis = diagnosis.replace("\r","").replace("\n","")
    return diagnosis


def getDiagnosis_fromFL(test_path):
    fail_count=0
    diagnosis=""
    with open(test_path) as testfails:
        lines = testfails.readlines()
        for l in lines:
            if "FAIL" in l:
                fail_count+=1
                if diagnosis in "":
                    diagnosis=l.split(",")[-1]
                    if "at" in diagnosis:
                        diagnosis = diagnosis.split(" at")[0]
                        if ":" in diagnosis:
                            diagnosis = diagnosis.split(":")[0]
                        if "." in diagnosis:
                            diagnosis = diagnosis.split(".")[-1]
                            print(diagnosis)

    diagnosis = ' [FE] ' + diagnosis
    diagnosis = diagnosis.replace("\r","").replace("\n","")
    return fail_count,diagnosis


    
def getContext(buggy_class,buggy_line,start_no,end_no):
    
    buggycode = ""
    contextcode = ""
    endbuggyline= 0
    if int(buggy_line) - int(start_no)>10:
        start_no=int(buggy_line)-10
    if int(end_no) - int(buggy_line)>10:
        end_no=int(buggy_line)+10
        
    
    with open(buggy_class,'r') as buggyFile:
        lines = buggyFile.readlines()
        for i in range(0,len(lines)):
            if i > int(start_no)-2 and i < int(end_no):
                l = lines[i]
                l = l.strip()
                #remove comments
                if  l.startswith('/') or l.startswith('*'):
                    l = ' '
                l = l.replace('  ','').replace('\r','').replace('\n','')
                if i == int(buggy_line)-1:
                    if buggycode in "":
                        buggycode=l
                        buggycode=buggycode.strip()
                        buggycode=buggycode.replace("  "," ")
                        if not buggycode.endswith(";") and not buggycode.endswith("{") and not buggycode.endswith("}") :
                            buggycode+=lines[i+1]
                            endbuggyline=1
                            if not buggycode.endswith(";") and not buggycode.endswith("{") and not buggycode.endswith("}") :
                                buggycode+=lines[i+2]
                                endbuggyline=2
                        
                    l='[BUGGY] '+buggycode + ' [BUGGY] '

                
                contextcode+=l+' '
    
    return buggycode,contextcode,endbuggyline


if __name__ == '__main__':
    project=sys.argv[1]
    bug=sys.argv[2]
    suspiciousness_threshold=sys.argv[3]
    suspiciousness_threshold=float(suspiciousness_threshold)
    rounds=sys.argv[4]

    
    FL_file = "./projects/"+project+bug+"/build/sfl/txt/ochiai.ranking.csv"
    TEST_file = "./projects/"+project+bug+"/build/sfl/txt/tests.csv"
    if not os.path.exists(FL_file):
        print("This path does not exist: " + FL_file)
        sys.exit()
    else:
        bug_representation_path="./repair_iteration/"+project+bug+"/iteration_"+rounds
        if not os.path.exists(bug_representation_path):
            os.system("mkdir -p "+bug_representation_path)
        os.system("cp "+FL_file + " "+bug_representation_path)
        os.system("cp "+TEST_file + " "+bug_representation_path)

#         diagnosis = getDiagnosis(project,bug)
        failing_test_number, diagnosis = getDiagnosis_fromFL(TEST_file)
        print(failing_test_number)
        with open(bug_representation_path+'/bugs.csv', 'w') as csvfile:
            csvfile.write('bugid\tbuggy\tbuggy_class\tsuspiciousness\tbuggy_line\tendbuggycode\tfailing_test_number\tpatch\n')
        
        with open(FL_file,"r") as fl:
            lines = fl.readlines()
            count=0
            for line in lines:
                if ";" in line and ":" in line and "#" in line:
                    count=count+1
                    suspiciousness =  line.split(";")[1]
                    suspiciousness=suspiciousness.replace("\n","").replace("\r","")
                    if float(suspiciousness) > suspiciousness_threshold:
                        buggy_class = line.split("#")[0]
                        buggy_class=buggy_class.replace(".","/").replace("$","/")
                        buggy_line = line.split(":")[1].split(";")[0]
                        buggy_class=buggy_class+".java"                  
                        if os.path.exists("projects/"+project+bug+"/source/"+buggy_class):
                            buggy_class = "projects/"+project+bug+"/source/"+buggy_class
                            
                        
                        utils_path = "./utils/context.jar "
                        results = os.popen("java -jar "+utils_path +buggy_class +" test-"+buggy_line).read()
                        results = str(results)
                        if "[CLASS]" in results and "startline:" in results:
                            results = results.split("[CLASS]")[1]
                            meta = " [CLASS] " + results.split("startline:")[0]
                            start_no =  results.split("startline:")[1].split("endline:")[0]
                            end_no =  results.split("endline:")[1].replace("\n","").replace("\r","")
                            
                            buggycode,contextcode,endbuggycode = getContext(buggy_class,buggy_line,start_no,end_no)
                            endbuggycode=int(buggy_line)+int(endbuggycode)
                            buggycode = buggycode.replace("  "," ")
                            buggycode = buggycode.replace("  "," ")
                            sample='[BUG] [BUGGY] ' + buggycode + diagnosis+ ' [CONTEXT] ' + contextcode + meta 
                            sample = sample.replace('\r','').replace('\n','').replace('\t','').replace('  ',' ')
                            sample = str(count)+'\t'+sample +'\t'+buggy_class+'\t'+suspiciousness+'\t'+buggy_line+'\t'+str(endbuggycode)+'\t'+str(failing_test_number)+'\t'
                            
                            print(sample)                            
                            
                            with open(bug_representation_path+'/bugs.csv','a') as bugrep:
                                bugrep.write(sample+'\n')
                            
                        

                        
                        
                    
                    
        