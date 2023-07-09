#!/usr/bin/python
import sys, os, subprocess,fnmatch, shutil, csv,re, datetime
import time



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

if __name__ == '__main__':
    with open('meta.csv','r') as d4jcsv:
        lines = d4jcsv.readlines()
        for l in lines[652:]:
            output=''
            bugid = l.split('\t')[1]
            project=bugid.split('_')[0]
            bid = bugid.split('_')[1]
            bugid=bugid.replace('_','')
            print(bugid)
            try:
                os.system('defects4j checkout -p '+project+' -v '+bid+'b -w ../projects/'+bugid)
                slbfpath=''
                if os.path.exists('../repair_iteration/'+bugid+'/FL-1/ochiai.ranking.csv'):
                    slbfpath='../repair_iteration/'+bugid+'/FL-1/ochiai.ranking.csv'                
                elif os.path.exists('../repair_iteration/'+bugid+'/ochiai.ranking.csv'):
                    slbfpath='../repair_iteration/'+bugid+'/ochiai.ranking.csv'
                if slbfpath not in '':  
                    with open(slbfpath,"r") as fl:
                        buggycode=''
                        lines = fl.readlines()
                        endrange=51
                        if len(lines)<51:
                            endrange=len(lines)                        
                        for i in range(1,endrange):
                            line = lines[i]
                            if ";" in line and ":" in line and "#" in line:
                                suspiciousness = line.split(";")[1]
                                suspiciousness=suspiciousness.replace("\n","").replace("\r","")
                                buggy_class = line.split("#")[0]
                                buggy_class=buggy_class.replace(".","/").replace("$","/")
                                buggy_line = line.split(":")[1].split(";")[0]
                                buggy_class=buggy_class+".java" 
                                print(buggy_class)
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
                                buggycode = getContext(buggy_class,buggy_line,buggy_line,buggy_line)
                                buggycode = buggycode.replace("  "," ")
                                buggycode = buggycode.replace("  "," ")                             
                                opath = './data/'+ bugid+'/statements.txt'   
                                with open(opath,'a') as inputtxt:
                                    inputtxt.write(buggycode+'\n')
            except:
                print('error')

        
                
           
                    
                    
                    
                
                
                
                
                
                
                
                
                
                

