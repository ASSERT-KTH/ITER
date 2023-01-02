
### start_initial.py 
With this script, we get the initial status of the bug.
You can find all the fault localization files are generated under folder the build folder the buggy project.
```
start_initial.py Project Bug
For example: start_initial.py Chart 1
The FL related files are generated under Chart1/build/sfl/txt. The ranking list is generated in ochiai.ranking.csv.
```

### run_gzoltar_fl.sh 
This script localize fauty lines with Gzoltar tool. This script is called by **start_initial.py**. Specifically, we use the following parameters. 
```
Gzoltar Version: 1.7.3
--formula "ochiai"  --metric "entropy" --granularity "line" --inclPublicMethods --inclStaticConstructors  --inclDeprecatedMethods 
```
