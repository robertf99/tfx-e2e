from tfx import v1 as tfx


def create_schema_pipeline(
    pipeline_name: str, pipeline_root: str, data_root: str, metadata_path: str
) -> tfx.dsl.Pipeline:
    """Creates a three component penguin pipeline with TFX."""
    # Brings data into the pipeline.
    example_gen = tfx.components.CsvExampleGen(input_base=data_root)

    # Computes statistics over data for visualization and schema generation.
    statistics_gen = tfx.components.StatisticsGen(
        examples=example_gen.outputs["examples"]
    )

    # Generates schema based on the generated statistics.
    schema_gen = tfx.components.SchemaGen(
        statistics=statistics_gen.outputs["statistics"], infer_feature_shape=True
    )

    components = [example_gen, statistics_gen, schema_gen]

    return tfx.dsl.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        metadata_connection_config=tfx.orchestration.metadata.sqlite_metadata_connection_config(
            metadata_path
        ),
        components=components,
    )

