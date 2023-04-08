#!/usr/bin/python
import sys, os, subprocess,fnmatch, shutil, csv, re, datetime


if __name__ == '__main__':
    project=sys.argv[1]
    bug=sys.argv[2]
    
    if os.path.exists("./projects/"+project+bug):
        os.system("rm -rf ./projects/"+project+bug)
    
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
            if t not in fail_tests:
                fail_tests+=t+"#*:" 
    fail_tests = fail_tests[:len(fail_tests)-1]
    
    
    source_files = ""
    sources=sources.split(" - ")
    for s in sources:
        s =s.split("--")[0]
        s = s.replace("\n","").replace("\r","")
        if s not in source_files:
            source_files+=s+":" 
    source_files = source_files[:len(source_files)-1]
    
    #copy run.sh to the target project
    if "Closure" in project:
        os.system("cp run_gzoltar_fl_Closure-after.sh ./projects/"+project+bug)
        os.system('mv  ./projects/'+project+bug+'/run_gzoltar_fl_Closure.sh  ./projects/'+project+bug+'/run_gzoltar_fl.sh')
    else:
        os.system("cp run_gzoltar_fl.sh ./projects/"+project+bug)
    
    
    #compile target project
    os.chdir("./projects/"+project+bug)
    os.system("defects4j compile")
    
    
    currentpath=os.path.dirname(os.path.realpath(__file__))
    print("currentpath:"+currentpath)
    #create build folder
    if "Cli" in project or 'Math' in project or 'Compress' in project or 'Gson' in project or 'Csv' in project  or 'JacksonCore' in project  or 'JacksonDatabind' in project or 'Jsoup' in project:
        if os.path.exists("./target"):
            os.system("mkdir build")
            os.system("mkdir build-tests")
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
#             os.system("cp -rf ./build/lib/*" + "  ./lib/")
#             os.system("cp -rf ./lib/classes/*" + "  ./lib/")
    
    if "Lang" in project:
        if os.path.exists("./target") and os.path.exists("./target/tests"):
            os.system("mkdir build")
            os.system("mkdir build-tests")
            os.system("cp -rf ./target/classes/*" + "  ./build/")
            os.system("cp -rf ./target/tests/*" + "  ./build/")
            os.system("cp -rf ./target/tests/*" + "  ./build-tests/")
        elif os.path.exists("./target") and os.path.exists("./target/test-classes"):
            os.system("mkdir build")
            os.system("mkdir build-tests")
            os.system("cp -rf ./target/classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build/")
            os.system("cp -rf ./target/test-classes/*" + "  ./build-tests/")

            
    
    #execute the Gzoltar FL
    

    fl_result = os.popen("./run_gzoltar_fl.sh --instrumentation online --failtests "+fail_tests+" --sourcefiles "+source_files).read()       
    print(fl_result)

    with open("./FL_execution.txt","w") as fl_file:
        fl_file.write("./run_gzoltar_fl.sh --instrumentation online --failtests "+fail_tests+" --sourcefiles "+source_files)
    with open("./FL_result.txt","w") as fl_result_file:
        fl_result_file.write(fl_result)
        
    
    
