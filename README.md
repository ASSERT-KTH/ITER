
# ITER: Iterative Neural Repair for Multi-Location Patches (paper under review)


## Folder Structure
 ```bash
 ├── repair_iteration: in this folder, you will find all repair iterations of considered bugs
 │────────The folder is structured as ** repair_iteration/BugID/RankedFL/Iterations **
 │ 
 ├── gzoltar: in this folder, you will find the FL dependency used in ITER
 │
 ├── Generate_Iterative_Sample.py: script to generate iterative training samples.
 │
 ├── 1_localize_fault.py: script to obtain ranked list of bug under repair
 │
 ├── 2_bug_representation.py: script to prepare bug representation of the ranked FL
 │
 ├── 3_repair.py: script to iterative repair
 │
 ├── 4_trace_patches.py:  script to trace plausible patches over iterations
 │
 ├──utils/context.jar: tool to obtain the context of bug under repair, used by 2_execute_perturbation.py
 │
 ├── run_gzoltar_fl.sh: script to execute gzoltar, used by 1_localize_fault.py
 │
 ├── patches.csv: the file to compare with the state-of-the-art
 
```




## Prerequisites
* JDK 1.8
* Pytorch==1.7.1
* transformers>=4.10.0
* pip install transformers
* pip install sentencepiece
* setup Defect4J export PATH = $PATH:your/path/defects4j/framework/bin
* configure Gzoltar:
--formula "ochiai"  --metric "entropy" --granularity "line" --inclPublicMethods --inclStaticConstructors  --inclDeprecatedMethods 


## Checkout the buggy program and produce a ranked list for the bug. 
```
python3 1_localize_fault.py projectID bugID init
e.g., python3 1_localize_fault.py Chart 1 init
```
**The result will be found under projects/Chart1/build/sfl/txt/ochiai.ranking.csv**


## Transform the FL to input representation
The suspicious_threshold by default configures to 0.1 and we consider at most top-50 ranked suspicious statements.
```
python3 2_bug_representation.py projectID bugID suspicious_threshold init
e.g., python3 2_bug_representation.py Chart 1 0.1 init
```
**The result will be found under repair_iteration/Chart1/bugs.csv**


## Iterative Program Repair
```
python3 3_repair.py projectID bugID 
e.g., python3 3_repair.py Chart 1 
```
**The result will be found under repair_iteration/Chart1/1,...,n, where n is the ranked position of suspucious statements**


## Trace patches
```
python3 4_trace_patches.py 
```
**The result will be found in patches.csv**





