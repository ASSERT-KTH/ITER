#!/usr/bin/python
import sys, os, subprocess,fnmatch, shutil, csv,re, datetime
import time



if __name__ == '__main__':
    with open('meta.csv','r') as d4jcsv:
        lines = d4jcsv.readlines()
        for l in lines:
            output=''
            bugid = l.split('\t')[1]
            bugid=bugid.replace('_','')
            print(bugid)
            slbfpath=''
            if os.path.exists('../repair_iteration/'+bugid+'/FL-1/ochiai.ranking.csv'):
                slbfpath='../repair_iteration/'+bugid+'/FL-1/ochiai.ranking.csv'                
            elif os.path.exists('../repair_iteration/'+bugid+'/ochiai.ranking.csv'):
                slbfpath='../repair_iteration/'+bugid+'/ochiai.ranking.csv'
            if slbfpath not in '':  
                with open(slbfpath,'r') as fl:
                    flines = fl.readlines()
                    for f in flines[1:51]:
                        loc = f.split(':')[1]
                        loc=loc.split(';')[0]                    
                        src = f.split('#')[0]
                        src = src.replace('$','.')
                        output = output+ src+':'+loc+'\n'
            print(output)
            opath = './data/'+ bugid+'/input.txt'   
            os.system('rm '+opath)
            if slbfpath not in '':  
                with open(opath,'w') as inputtxt:
                    inputtxt.write(output)
            else:
                os.system('rm ./data/'+ bugid)
                
           
                    
                    
                    
                
                
                
                
                
                
                
                
                
                

