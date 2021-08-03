from tfx import v1 as tfx
import os
import shutil
from tfx.orchestration.metadata import Metadata
from tfx.types import standard_component_specs

from pipeline.config import pipe_config
from pipeline.schema_pipeline.pipeline import create_schema_pipeline
from pipeline.schema_pipeline.utils import get_latest_artifacts

tfx.orchestration.LocalDagRunner().run(
  create_schema_pipeline(
      pipeline_name=pipe_config.SCHEMA_PIPELINE_NAME,
      pipeline_root=pipe_config.SCHEMA_PIPELINE_ROOT,
      data_root=pipe_config.SCHEMA_DATA_ROOT,
      metadata_path=pipe_config.SCHEMA_METADATA_PATH))



metadata_connection_config = tfx.orchestration.metadata.sqlite_metadata_connection_config(
    pipe_config.SCHEMA_METADATA_PATH)

with Metadata(metadata_connection_config) as metadata_handler:
  # Find output artifacts from MLMD.
  stat_gen_output = get_latest_artifacts(metadata_handler, pipe_config.SCHEMA_PIPELINE_NAME,
                                         'StatisticsGen')
  stats_artifacts = stat_gen_output[standard_component_specs.STATISTICS_KEY]

  schema_gen_output = get_latest_artifacts(metadata_handler,
                                           pipe_config.SCHEMA_PIPELINE_NAME, 'SchemaGen')
  schema_artifacts = schema_gen_output[standard_component_specs.SCHEMA_KEY]


os.makedirs(pipe_config.SAVED_SCHEMA_PATH, exist_ok=True)
_generated_path = os.path.join(schema_artifacts[0].uri, pipe_config.SAVED_SCHEMA_NAME)

# Copy the 'schema.pbtxt' file from the artifact uri to a predefined path.
shutil.copy(_generated_path, pipe_config.SAVED_SCHEMA_PATH)