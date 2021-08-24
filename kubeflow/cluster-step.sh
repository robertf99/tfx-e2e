kind create cluster --name=tfx-kubeflow-cluster --config=kind-config.yaml
k apply -f pv-data.yaml
k3ai init
k3ai apply kubeflow-pipelines