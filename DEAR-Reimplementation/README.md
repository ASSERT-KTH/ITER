## This is Reimplementation of DEAR FL

## Scripts 
 ```bash
 ├── 1_GetSBFL.py: This script takes input as the SBFL ranked list and output them as input.txt
 │
 ├── 2_ConstructStatement.py: For each suspicious location idnetified in input.txt, this script extracts the actual code statement for it (covert the FL to  
 │                            code). This script outputs statements.txt.
 │                            
 ├── 3_ConstructPairHunkData.py: This script pairwise two statements from statements.txt to construct TrainingPairs.csv 
 │
 ├── 4_TrainBertHunkPairDetection.py: This script trains the BERT model with TrainingPairs.csv.
 │
 ├── 5_InferenceHunkDetection.py: This script uses the trained BERT model to infer the buggy locations from test dataset.
 │
 ├── 6_ConstructTrainingBugExpansionData.py:  This script constructs the training bug prediction data and label according to the ground truth labels in 
 │                                            out.txt.  This script outputs TrainingBugExpansion.csv.
 │
 ├── 7_TrainBERTBugExpansion.py: This script trains the BERT model with TrainingBugExpansion.csv.


 
```
