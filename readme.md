## Tensorflow Decision Forest with TFX orchestrated in Airflow
Author: Robert Fu (robertf99@gmail.com)

Dataset: Panguin dataset

## Folder Strucuture
### ./data: 
get initial data by
```
cd penguin-pipeline && python prepare_data.py
```

### ./models: 
trainer module file
### ./penguim-pipeline: 
pipeline definition
### ./schema: 
saved schema from initial run for subsequent validation

## To Do
* TF Transform as preprocess_fn