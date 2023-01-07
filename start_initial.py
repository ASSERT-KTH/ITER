#!/usr/bin/python
import sys, os, subprocess,fnmatch, shutil, csv, re, datetime


if __name__ == '__main__':
    project=sys.argv[1]
    bug=sys.argv[2]
    
    #checkout the project
    checkout_project="defects4j checkout -p " + project +" -v "+ bug+"b  -w ./projects/"+project+bug
    os.system(checkout_project)
    
    #get project information
    project_info="defects4j info -p "+ project +" -b " +bug
    infos = os.popen(project_info).read()
    infos=str(infos)
    tests = infos.split("List of modified sources:")[0]
    tests = tests.split("Root cause in triggering tests:")[1]
    sources = infos.split("List of modified sources:")[1]
    
    #infomation of failing tests
    fail_tests = ""
    tests=tests.split(" - ")
    for t in tests:
        if "::" in t:
            t = t.split("::")[0]
            t = t.replace("\n","").replace("\r","")
            fail_tests+=t   
    print("*********fail_tests:*******"+fail_tests)
    
    
    source_files = ""
    sources=sources.split(" - ")
    for s in sources:
        s =s.split("--")[0]
        s = s.replace("\n","").replace("\r","")
        source_files+=s   
    print("*********source_files:*******"+source_files)
    
    #copy run.sh to the target project
    os.system("cp run_gzoltar_fl.sh ./projects/"+project+bug)
       
    #compile target project
    os.chdir("./projects/"+project+bug)
    os.system("defects4j compile")
    
    #execute the Gzoltar FL
    os.system("./run_gzoltar_fl.sh --instrumentation online --failtests "+fail_tests+" --sourcefiles "+source_files)
    
    
