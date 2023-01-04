#!/usr/bin/python
import sys, os, subprocess,fnmatch, shutil, csv, re, datetime

if __name__ == '__main__':
    project=sys.argv[1]
    bug=sys.argv[2]
    rounds=sys.argv[3]
    
    #we configure the suspiciousness threshold value here
    suspiciousness_threshold = 0.0
    
    FL_file = "./"+project+bug+"/build/sfl/txt/ochiai.ranking.csv"
    if not os.path.exists(FL_file):
        print("This path does not exist: " + FL_file)
        sys.exit()
    else:
        print("OK " + FL_file)
        if not os.path.exists("./repair_iteration/"+project+bug+"/iteration_"+rounds):
            os.system("mkdir -p ./repair_iteration/"+project+bug+"/iteration_"+rounds)
        with open(FL_file,"r") as fl:
            lines = fl.readlines()
            for line in lines:
                if ";" in line and ":" in line and "#" in line:
                    suspiciousness =  line.split(";")[1]
                    suspiciousness=suspiciousness.replace("\n","").replace("\r","")
                    if float(suspiciousness) > suspiciousness_threshold:
                        buggy_class = line.split("#")[0]
                        buggy_class=buggy_class.replace(".","/").replace("$","/")
                        buggy_line = line.split(":")[1].split(";")[0]
                        print(buggy_class)
                        print(buggy_line)

                        
                        
                    
                    
        