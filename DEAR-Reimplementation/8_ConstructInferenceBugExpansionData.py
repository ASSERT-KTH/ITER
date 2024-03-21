from transformers import pipeline
import os


def getContext(buggy_class,buggy_line,start_no,end_no):
    
    buggycode = ""
    contextcode_replace = ""
    contextcode_add=""
    endbuggyline= 0        
    if not os.path.exists(buggy_class):
        return ''
        
    with open(buggy_class,'r') as buggyFile:
        lines = buggyFile.readlines()
        for i in range(0,len(lines)):
            if i > int(start_no)-2 and i < int(end_no)+5:
                l = lines[i]
                l = l.strip()
                #remove comments
                if  l.startswith('/') or l.startswith('*'):
                    l = ' '
                l = l.replace('  ','').replace('\r','').replace('\n','')
                l_add = l
                if i == int(buggy_line)-1:
                    if buggycode in "":
                        buggycode=l
                        buggycode=buggycode.strip()
                        buggycode=buggycode.replace("  "," ")
                        

    
    return buggycode


def getExpansionStatement(srcfile,loc):
    buggy_class=srcfile.replace('.','/')
    buggy_class=buggy_class+'.java'
    if os.path.exists("../projects/"+bugid+"/source/"+buggy_class):
        print("../projects/"+bugid+"/source/"+buggy_class)
        buggy_class = "../projects/"+bugid+"/source/"+buggy_class
    elif os.path.exists("../projects/"+bugid+"/src/java/"+buggy_class):
        print("../projects/"+bugid+"/src/java/"+buggy_class)
        buggy_class = "../projects/"+bugid+"/src/java/"+buggy_class
    elif os.path.exists("../projects/"+bugid+"/src/main/java/"+buggy_class):
        print("../projects/"+bugid+"/src/main/java/"+buggy_class)
        buggy_class = "../projects/"+bugid+"/src/main/java/"+buggy_class
    elif os.path.exists("../projects/"+bugid+"/gson/src/main/java/"+buggy_class):
        print("../projects/"+bugid+"/gson/src/main/java/"+buggy_class)
        buggy_class = "../projects/"+bugid+"/gson/src/main/java/"+buggy_class
    elif os.path.exists("../projects/"+bugid+"/src/"+buggy_class):
        print("../projects/"+bugid+"/src/"+buggy_class)
        buggy_class = "../projects/"+bugid+"/src/"+buggy_class   

    stmt =  getContext(buggy_class,loc,loc-1,loc+1)
    stmt =  stmt.replace('  ',' ')
    return stmt
    


if __name__ == '__main__':
    inferenceList=['Chart-14','Chart-16','Chart-19','Cli-34','Closure-4','Closure-78','Closure-79','Closure-106','Closure-109','Closure-115','Closure-131','Codec-1','Lang-7','Lang-27','Lang-34','Lang-35','Lang-41','Lang-47','Lang-60','Math-1','Math-4','Math-22','Math-24','Math-35','Math-43','Math-46','Math-62','Math-65','Math-71','Math-77','Math-79','Math-88','Math-90','Math-93','Math-98','Math-99']

    for bugid in inferenceList:
        bug=bugid.replace('-','')
        InferencePair = './data/'+bug+'/PositivePrediction.csv'
        
        if not os.path.exists(InferencePair):
            continue
            
        
        project=bugid.split('-')[0]
        bid=bugid.split('-')[1]

        os.system('defects4j checkout -p '+project+' -v '+bid+'b -w ../projects/'+bugid)

        with open(InferencePair,'r') as infer:
            inferLines = infer.readlines()
            for line in inferLines:
                s1 = line.split('[CLS]')[0]
                s2 = line.split('[CLS]')[1]
                srcfile1=s1.split(':')[0]
                loc1=s1.split(':')[1]
                loc1=loc1.split('-')[0]
                print('srcfile1:'+srcfile1)
                print('loc1:'+loc1)
                loc1=int(loc1)              
                srcfile2=s2.split(':')[0]
                loc2=s2.split(':')[1]
                loc2=loc2.split('-')[0]
                loc2=int(loc2)
                
                for expansionLine in range (loc1-5,loc1+6):
                    expStmt = getExpansionStatement(srcfile1,expansionLine)
                    expansionPath = './data/'+bug+'/expansion.csv'
                    if expStmt not in '':
                        with open(expansionPath,'a') as expCSV:
                            expCSV.write(srcfile1+':'+str(expansionLine)+'-'+expStmt+'\n')
                        
                for expansionLine in range (loc2-5,loc2+6):
                    expStmt = getExpansionStatement(srcfile2,expansionLine)
                    expansionPath = './data/'+bug+'/expansion.csv'
                    if expStmt not in '':
                        with open(expansionPath,'a') as expCSV:
                            expCSV.write(srcfile2+':'+str(expansionLine)+'-'+expStmt+'\n')
                    
                    

                
                