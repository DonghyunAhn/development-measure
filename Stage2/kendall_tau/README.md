## Kendall-tau correlation  

Runnable code for measuring kendall-tau correlation across all annotators (Table S1).  
Input : POG textfile path, POG annotato info path  
Output : kendall-tau corr. accorss all annotators. Results are saved in results/tau_pog.csv 

```
txt2kendall2.py {POG textfile} {POG annotator info textfile}
```
In our repository, we saved the both textfile in the directory POG_annotation.   

```
python3 txt2kendall2.py ../POG_annotation/POG_collection.txt ../POG_annotation/POG_annotators.txt
```
You can check the result on *results/tau_pog.csv*   