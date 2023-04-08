
# ITER: Iterative Neural Repair for Multi-Location Patches (paper under review)


## Folder Structure
 ```bash
 ├── repair_iteration: in this folder, you will find all repair iterations of considered bugs
 │────────The folder is structured as ** repair_iteration/BugID/RankedFL/Iterations **
 │ 
 ├── gzoltar: in this folder, you will find the FL dependency used in ITER
 │
 ├── 1_localize_fault.py: script to obtain ranked list of bug under repair
 │
 ├── 2_execute_perturbation.py: script to prepare bug representation of the ranked FL
 │
 ├── 3_repair.py: script to iterative repair
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

