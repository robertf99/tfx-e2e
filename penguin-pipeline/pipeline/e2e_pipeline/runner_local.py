from tfx import v1 as tfx
from config import pipe_config
from pipeline import create_pipeline

tfx.orchestration.LocalDagRunner().run(
    create_pipeline(
        pipeline_name=pipe_config.PIPELINE_NAME,
        pipeline_root=pipe_config.PIPELINE_ROOT,
        data_root=pipe_config.DATA_ROOT,
        metadata_connection_config=tfx.orchestration.metadata.sqlite_metadata_connection_config(
            pipe_config.METADATA_PATH
        ),
        schema_path=pipe_config.SAVED_SCHEMA_PATH,
        trainer_module_file=pipe_config.TRAINER_MODULE_PATH,
        evaluator_module_file=pipe_config.EVAL_MODULE_PATH,
        serving_model_dir=pipe_config.SERVING_MODEL_DIR,
    ),
)
