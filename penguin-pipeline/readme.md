Integrate TFX and TFDF in Docker Images using Penguin Dataset

Note:
TFDF only has a Linux version, no Mac support as of 27/07/2021
To run in Jupyterlab, need the following:

```
pipenv run jupyter labextension install tensorflow_model_analysis@0.33.0
```

## Local runner in docker
- Run the entire model inside docker image
- Run ad-hoc analysis in local system via jupyter-lab, choose ipykernel as python kernel

## Local Kubeflow Pipeline runner
- Enable Kubenetes in Docker, or create cluster using kind
- Init cluster config with k3ai: k3ai init
- Deploy kubeflow: k3ai apply kubeflow-pipelines (or k3ai apply -g kubeflow-pipelines-traefik for istio version)
- Port forward to localhost: kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
- Add hostpath (i.e., ./kubeflow/local) to Docker preferrence setting (resource/file sharing) to mount local path to cluster host node
- Create persistent volume and persistent volume claim in kubenetes cluster (namespace kubeflow) and attched node hostpath to volume
- Add a onprem.mount_pvc op to kubeflow_e2e_runner.py so that container would mount the pvc to its file system
- Compile and create pipeline to Kubeflow (Note: for tfx pipeline compile to succeed, the mount_pvc path shall have user write access, i.e, /tmp..)
- To reflect change of components (ie models, pipeline definition), update TFX_IMGAGE in config.py and rerun docker build container image (by default is robertf99/penguin-e2e) and push. Note currently schema, data and pipeline_output are mounted as hostPath.
- Trainer whl file needs to be put into pipeline root folder, or build into container image for kubeflow pipeline to access. Referencing .py file does not work
- For Model Evaluator to run in kubeflow (TFDF model only), there needs to be a custom module file with just `import tensorflow_decision_forest` as part of Evaluator config to allow for tensorflow op registration(https://github.com/tensorflow/decision-forests/issues/14). Same as Trainer module file, this custom module needs to be convert to whl or built into container image under pipeline root path. Currently due to TFDF has no Mac distribution, this step is currently done in docker image 

## Local Full Kubeflow Deployment (Notebook Server etc)
- Install kind: brew install kind
- Create a cluster with kind: kind create cluster (check cluster config by kind get kubeconfig)
- Install kfctl (Download, unzip and move to path)
- Create new empty folder for thge Kubeflow app and cd into it
- kfctl apply --file=${CONFIG} -V, where config=https://raw.githubusercontent.com/kubeflow/manifests/v1.2-branch/kfdef/kfctl_k8s_istio.v1.2.0.yaml. This should deploy all relevant serices to the cluster.
- kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80

## Issues
- kfp.Client() refuse connection when using cluster IP
- Kubeflow runs pipeline in docker images, for external input files, should use file URI, or some way of volume (try with full kubeflow deployment)