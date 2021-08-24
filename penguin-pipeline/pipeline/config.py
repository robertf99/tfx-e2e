from pydantic import BaseModel
import os


class PipelineConfig(BaseModel):

    SCHEMA_PIPELINE_NAME = "penguin-schema"
    SCHEMA_DATA_ROOT = os.path.join("../data", SCHEMA_PIPELINE_NAME)
    SCHEMA_PIPELINE_ROOT = os.path.join("pipeline_output", SCHEMA_PIPELINE_NAME)
    SCHEMA_METADATA_PATH = os.path.join("metadata", SCHEMA_PIPELINE_NAME, "metadata.db")
    SAVED_SCHEMA_NAME = "schema.pbtxt"
    SAVED_SCHEMA_PATH = os.path.join("schema", SCHEMA_PIPELINE_NAME, SAVED_SCHEMA_NAME)

    PIPELINE_NAME = "penguin-e2e"
    DATA_ROOT = os.path.join("../data", PIPELINE_NAME)
    PIPELINE_ROOT = os.path.join("pipeline_output", PIPELINE_NAME)
    METADATA_PATH = os.path.join("metadata", PIPELINE_NAME, "metadata.db")
    TRAINER_MODULE_PATH = os.path.join(
        "../models", "penguin_trainer_rf.py"  # running after cd ./penguin-pipeline
    )
    SERVING_MODEL_DIR = os.path.join("serving_model", PIPELINE_NAME)

    # Kubeflow configs
    # Persistent Volume
    PV_NAME = "tfx-pv"
    PVC_NAME = "tfx-pvc"
    PV_MOUNT_BASEPATH = "/tmp/tfx"

    # Image used
    TFX_IMAGE = "robertf99/tfx-tfdf"

    KUBE_DATA_ROOT = os.path.join(PV_MOUNT_BASEPATH, "data", PIPELINE_NAME)
    KUBE_TRAINER_MODULE_PATH = os.path.join(
        PV_MOUNT_BASEPATH, "models", "penguin_trainer_rf.py"
    )
    KUBE_PIPELINE_ROOT = os.path.join(
        PV_MOUNT_BASEPATH, "pipeline_output", PIPELINE_NAME
    )
    KUBE_SAVED_SCHEMA_PATH = os.path.join(
        PV_MOUNT_BASEPATH, "schema", SCHEMA_PIPELINE_NAME, SAVED_SCHEMA_NAME
    )
    KUBE_SERVING_MODEL_DIR = os.path.join(
        PV_MOUNT_BASEPATH, "serving_model", PIPELINE_NAME
    )


pipe_config = PipelineConfig()
