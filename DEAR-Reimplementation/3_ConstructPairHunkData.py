#!/usr/bin/python
import sys, os, subprocess,fnmatch, shutil, csv,re, datetime
import time


def inLst(text,lists):
    flag=False
    for lst in lists:
        lst=lst.replace('\n','')
#         print(lst)
        if text in lst and lst in text:
            flag=True
            return flag
            
    return flag
            



if __name__ == '__main__':
    inferenceList=['Chart14','Chart16','Chart19','Cli34','Closure4','Closure4','Closure78','Closure79','Closure106','Closure109','Closure115','Closure131','Codec1','Lang7','Lang27','Lang34','Lang35','Lang41','Lang47','Lang60','Math1','Math4','Math22','Math24','Math35','Math43','Math46','Math62','Math65','Math71','Math77','Math79','Math88','Math90','Math93','Math98','Math99']

    with open('meta.csv','r') as d4jcsv:
        count=0
        lines = d4jcsv.readlines()      
        for l in lines:
            output=''
            bugid = l.split('\t')[1]
            bugid=bugid.replace('_','')
#             print(bugid)      
            
            #remove inference data from training
            if inLst(bugid,inferenceList):
                continue
           
            statementPath='./data/'+bugid+'/statements.txt'
            flPath='./data/'+bugid+'/input.txt'
            outPath='./data/'+bugid+'/out.txt'         
            stmtlines=''
            fllines=''
            outlines=''
            
            if not os.path.exists(statementPath):
                continue
                
            if not os.path.exists(flPath):
                continue
            
            if not os.path.exists(outPath):
                continue
                
                
            with open(statementPath,'r') as stmt:
                stmtlines = stmt.readlines()
            with open(flPath,'r') as fl:
                fllines = fl.readlines()
            with open(outPath,'r') as out:
                outlines = out.readlines()
            
            
            for i in range(0, len(fllines)):
                for k in range(i+1, len(fllines)):
                    f1 = fllines[i]
                    f1 = f1.replace('\n','').replace('\r','').replace('\t','')                             
                    f2 = fllines[k]
                    f2 = f2.replace('\n','').replace('\r','').replace('\t','')     

                    s1 = stmtlines[i]
                    s1 = s1.replace('\n','').replace('\r','').replace('\t','')                        
                    s2 = stmtlines[k]
                    s2 = s2.replace('\n','').replace('\r','').replace('\t','')     
                    
                    pair=f1+'-'+s1+'[CLS]'+f2+'-'+s2

                    label=''
                    if inLst(f1,outlines) and inLst(f2,outlines):
  
                        count=count+1
                        label='1' #Positive          
                        print(count)
                        print(bugid)
                        
                        for loop in range(1,100):
                            with open('TrainingPairs.csv','a') as paircsv:
                                paircsv.write(pair+'\t'+label+'\n')
                    else:
                        label='0' #Negative
                    
                    with open('TrainingPairs.csv','a') as paircsv:
                        paircsv.write(pair+'\t'+label+'\n')


                
                
                
                
            
                
                
                
                
            
           
                    
                    
                    
                
                
                
                
                
                
                
                
                
                

