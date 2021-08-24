from tfx import v1 as tfx
from pipeline.config import pipe_config
from pipeline.e2e_pipeline.pipeline import create_pipeline
from kfp import onprem


def run():
    """Define a pipeline to be executed using Kubeflow V2 runner."""

    tfx_image = pipe_config.TFX_IMAGE
    metadata_config = (
        tfx.orchestration.experimental.get_default_kubeflow_metadata_config()
    )
    metadata_config.grpc_config.grpc_service_host.value = (
        "metadata-grpc-service.kubeflow"
    )
    metadata_config.grpc_config.grpc_service_port.value = "8080"

    runner_config = tfx.orchestration.experimental.KubeflowDagRunnerConfig(
        kubeflow_metadata_config=metadata_config,
        tfx_image=tfx_image,
        pipeline_operator_funcs=(
            [
                onprem.mount_pvc(
                    pipe_config.PV_NAME,
                    pipe_config.PVC_NAME,
                    pipe_config.PV_MOUNT_BASEPATH,
                )
            ]
        ),
    )

    pod_labels = {
        "add-pod-env": "true",
        tfx.orchestration.experimental.LABEL_KFP_SDK_ENV: "tfx-template",
    }

    dsl_pipeline = create_pipeline(
        pipeline_name=pipe_config.PIPELINE_NAME,
        pipeline_root=pipe_config.KUBE_PIPELINE_ROOT,
        data_root=pipe_config.KUBE_DATA_ROOT,
        schema_path=pipe_config.KUBE_SAVED_SCHEMA_PATH,
        trainer_module_file=pipe_config.KUBE_TRAINER_MODULE_PATH,
        serving_model_dir=pipe_config.KUBE_SERVING_MODEL_DIR,
    )
    runner = tfx.orchestration.experimental.KubeflowDagRunner(
        config=runner_config, pod_labels_to_attach=pod_labels
    )

    runner.run(pipeline=dsl_pipeline)


if __name__ == "__main__":
    run()
