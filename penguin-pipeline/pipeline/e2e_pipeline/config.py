from pydantic import BaseModel, validator
import os

# from pydantic import validator


class PipelineConfig(BaseModel):

    PIPELINE_NAME = "penguin-e2e"
    SAVED_SCHEMA_NAME = "schema.pbtxt"
    SAVED_SCHEMA_PATH = os.path.join("../schema/penguin-schema", SAVED_SCHEMA_NAME)
    DATA_ROOT = os.path.join("../../../data", PIPELINE_NAME)
    PIPELINE_ROOT = os.path.join("../pipeline_output", PIPELINE_NAME)
    METADATA_PATH = os.path.join("../metadata", PIPELINE_NAME, "metadata.db")
    MODULE_PATH = "penguin_trainer_keras.py"  # penguin_module_tft
    EVAL_MODULE_PATH = "custom_evaluator.py"
    SERVING_MODEL_DIR = os.path.join("../serving_model", PIPELINE_NAME)

    # Kubeflow configs
    # Persistent Volume
    PV_NAME = "tfx-pv"
    PVC_NAME = "tfx-pvc"
    PV_MOUNT_BASEPATH = "/tmp/tfx"
    GCS_ROOT = "gs://penguin-pipeline"

    # Image used
    TFX_IMAGE = "robertf99/penguin-e2e"

    KUBE_DATA_ROOT = os.path.join(GCS_ROOT, "data", PIPELINE_NAME)
    KUBE_PIPELINE_ROOT = os.path.join(GCS_ROOT, "pipeline_output", PIPELINE_NAME)
    KUBE_SAVED_SCHEMA_PATH = os.path.join(
        GCS_ROOT, "schema/penguin-schema", SAVED_SCHEMA_NAME
    )
    KUBE_SERVING_MODEL_DIR = os.path.join(GCS_ROOT, "serving_model", PIPELINE_NAME)
    KUBE_TRAINER_MODULE_PATH = "penguin_module_tft.py" # penguin_module_tft
    # KUBE_EVAL_MODULE_PATH = "custom_evaluator.py"


pipe_config = PipelineConfig()
