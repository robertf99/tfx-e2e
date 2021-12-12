## Tensorflow Decision Forest with TFX orchestrated in Kubeflow
Author: Robert Fu (robertf99@gmail.com)

Medium Summary: 
https://medium.com/@robertf99/mlops-with-tensorflow-extended-tfx-and-tensorflow-decision-forest-tf-df-part-1-bfa2f61580dc

## Folder Strucuture
### ./data: 
get initial data by
```
cd penguin-pipeline && python prepare_data.py
```
### ./penguin-pipeline: 
main pipeline folder, see readme.md inside

### ./models: 
ad hoc models
### ./schema: 
saved schema from initial run for subsequent validation

### ./kubeflow: 
kubeflow cluster configuration and mounted folders. See ./pentuin-pipeline/readme.md for more details
