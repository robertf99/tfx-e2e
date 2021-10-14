# used for tfx cli to generate robertf99/penguin-e2e image
# tfx pipeline create  --pipeline-path=runner_kubeflow.py --endpoint=http://localhost:8080 --build-image --engine=kubeflow  
FROM robertf99/tfx-tfdf

WORKDIR /pipeline
COPY ./ ./
ENV PYTHONPATH="/pipeline:${PYTHONPATH}"
ENV UNSUPPORTED_DO_NOT_PACKAGE_USER_MODULES="false"
