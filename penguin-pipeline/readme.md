# Integrate TFX and TFDF in Docker Images using Penguin Dataset

## Note

TFDF only has a Linux version, no Mac support as of 27/07/2021

Use docker for local dev (Docckerfile_dev)

## Local runner in docker

- Make sure metadata and pipeline_output folder is empty
- Run the entire pipeline (including training TF-DF model) inside docker image

```
python ./penguin-pipeline/run_e2e_pipeline.py
```

- Run ad-hoc analysis in local system via jupyter-lab, choose ipykernel as python kernel

## Local Kubeflow Pipeline runner

### Run with pipeline_root as local drive
- Add hostpath (i.e., ./kubeflow/local) to Docker preferrence setting (resource/file sharing) to mount local path to cluster host node
- Enable Kubenetes in Docker, or create cluster using kind
- Deploy kubeflow using config inside ./kubeflow, and deploy kubeflow and configs
- Port forward to localhost: `kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80`
- Create persistent volume and persistent volume claim in kubenetes cluster (namespace kubeflow) and attched node hostpath to volume
- Add a onprem.mount_pvc op to `runner_kuberflow.py` so that container would mount the pvc to its file system
- Compile and create pipeline to Kubeflow (Note: for tfx pipeline compile to succeed, the mount_pvc path shall have user write access, i.e, /tmp..)
- To reflect change of components (ie models, pipeline definition), update TFX_IMGAGE in config.py and rerun docker build container image (by default is robertf99/penguin-e2e) and push. Note currently schema, data and pipeline_output are mounted as hostPath.

### Run with pipeline root as GCS and Kubeflow on prem
- Deploy Kubeflow pipeline and set up GCS secret within the cluster
- Use locally GCS-authenticated console to create pipeline directly with pipeline_root as GCS bucket via TFX CLI
- As of writing, the Evaluator will fail if TF-DF model is used, but normal Keras model works (check for `penguin_module_tft.py`)
- Possible workaround for TF-DF model:
    - When create pipeline use a local path as `pipeline_root`
    - For Model Evaluator to run in kubeflow (TFDF model only), there needs to be a custom module file with just `import tensorflow_decision_forest` as part of Evaluator config to allow for tensorflow op registration(https://github.com/tensorflow/decision-forests/issues/14). Same as Trainer module file, this custom module will be convert to whl and copied from system /tmp/tfx/... path to mounted system path ./kubeflow.
    - Evluator module file whl file needs to be put into pipeline root folder, or build into container image for kubeflow pipeline to access. Referencing .py file does not work
    - Pipeline root folder can be set to `gs://penguin-pipeline/pipeline-output/penguin-e2e` in Kubeflow UI. For this to work, ml-pipeline-ui service in kubeflow needs to be patched.


## Post-run Analysis

- use examine_outputs.ipynb to analyze model performance
- for pipelines is run through kubeflow, need to update ML-MD connection to MySQL pod (`kubectl port-forward -n kubeflow svc/mysql 3306:3306`) inside kubeflow

## Issues

- When running with Kubeflow Pipeline from local pipeline root in PV, Tensorboard instance will not run as static path is not supported, has to be a external URI
- Current deployment of Kubeflow(1.7.0) has metadata store version 6. However, when running adhoc analysis with TFX version 1.2, metadata store library is version 7. Best to downgrade the library version(install `ml-metadata= "==1.0.0"`) than to update the db version inside kubeflow deployment. Refer to `https://github.com/google/ml-metadata/blob/master/g3doc/get_started.md`