from ml_metadata.proto import metadata_store_pb2

# Non-public APIs, just for showcase.
from tfx.orchestration.portable.mlmd import execution_lib

# TODO(b/171447278): Move these functions into the TFX library.


def get_latest_artifacts(metadata, pipeline_name, component_id):
    """Output artifacts of the latest run of the component."""
    context = metadata.store.get_context_by_type_and_name(
        "node", f"{pipeline_name}.{component_id}"
    )
    executions = metadata.store.get_executions_by_context(context.id)
    latest_execution = max(executions, key=lambda e: e.last_update_time_since_epoch)
    return execution_lib.get_artifacts_dict(
        metadata, latest_execution.id, metadata_store_pb2.Event.OUTPUT
    )
