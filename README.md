
# ITER: Iterative Neural Repair for Multi-Location Patches

ITER is a neural program repair system with an original training and inference loop enabling  advanced multi-location patches. See [the paper](http://arxiv.org/pdf/2304.12015).

```bibtex
@inproceedings{2304.12015,
 title = {ITER: Iterative Neural Repair for Multi-Location Patches},
 booktitle = {Proceedings of International Conference on Software Engineering},
 year = {2024},
 author = {He Ye and Martin Monperrus},
 url = {http://arxiv.org/pdf/2304.12015},
}
```


## Repo Structure
 ```bash
 ├── repair_iteration: in this folder, you will find all repair iterations of considered bugs
 │────────The folder is structured as ** repair_iteration/BugID/FL_Iteration/Ranked_Suspicious_Statement/Iterations **
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
 ├── 4_trace_patches.py:  script to trace plausible patches over iterations, this script generates patches.csv
 │
 ├── ITER_FL.py: script to be called by 3_repair.py to re-execute FL.
 │
 ├── utils/context.jar: tool to obtain the context of bug under repair, called by 2_bug_representation.py
 │
 ├── run_gzoltar_fl.sh: script to execute gzoltar, used by 1_localize_fault.py
 │
 ├── patches.csv: all plausible patches.
 
```

In addition, the models are put on Zenodo, see <https://zenodo.org/records/14993858> (2.3GB).



## Prerequisites
* JDK 1.8
* Pytorch==1.7.1
* transformers>=4.10.0
* pip install transformers
* pip install sentencepiece
* setup Defect4J export PATH = $PATH:your/path/defects4j/framework/bin
* configure Gzoltar:
--formula "ochiai"  --metric "entropy" --granularity "line" --inclPublicMethods --inclStaticConstructors  --inclDeprecatedMethods 


## How to read *repair_iteration* folder
* repair_iteration/BugID/FL_Iteration/Ranked_Suspicious_Statement/Iterations  (single test failure bug does not has FL iteration folder)

```
Example: 
>> repair_iteration/Math46/FL-2/1
indicates the second iteration (FL-2) of fault localization with 1st ranked suspicious statement (1).
each suspicious statement has its iteration_0/iteration_1/iteration_2.
each iteration has its bugs.csv, patches.csv and revert.csv(to avoid the duplicated patches).
```

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





