from tfx import v1 as tfx
import tensorflow_model_analysis as tfma


def create_schema_pipeline(
    pipeline_name: str,
    pipeline_root: str,
    data_root: str,
    metadata_path: str,
    schema_path: str,
    trainer_module_file: str,
    serving_model_dir: str,
) -> tfx.dsl.Pipeline:
    """Creates a three component penguin pipeline with TFX."""
    # Split data
    example_gen = tfx.components.CsvExampleGen(input_base=data_root)

    # Generate current data statistics
    statistics_gen = tfx.components.StatisticsGen(
        examples=example_gen.outputs["examples"]
    )

    # Import saved schema
    schema_importer = tfx.dsl.Importer(
        source_uri=schema_path, artifact_type=tfx.types.standard_artifacts.Schema
    ).with_id("schema_importer")

    # Validate Schema
    example_validator = tfx.components.ExampleValidator(
        statistics=statistics_gen.outputs["statistics"],
        schema=schema_importer.outputs["result"],
    )

    # Trainer
    trainer = tfx.components.Trainer(
        module_file=trainer_module_file,
        examples=example_gen.outputs["examples"],
        schema=schema_importer.outputs["result"],  # Pass the imported schema.
        train_args=tfx.proto.TrainArgs(),
        eval_args=tfx.proto.EvalArgs(),
    )

    # Evaluation
    eval_config = tfma.EvalConfig(
        model_specs=[
            # This assumes a serving model with signature 'serving_default'. If
            # using estimator based EvalSavedModel, add signature_name: 'eval' and
            # remove the label_key.
            tfma.ModelSpec(label_key="species")
        ],
        metrics_specs=[
            tfma.MetricsSpec(
                metrics=[
                    tfma.MetricConfig(class_name="ExampleCount"),
                    tfma.MetricConfig(
                        class_name="SparseCategoricalAccuracy",
                        threshold=tfma.MetricThreshold(
                            value_threshold=tfma.GenericValueThreshold(
                                lower_bound={"value": 0.9}
                            ),
                            # Change threshold will be ignored if there is no
                            # baseline model resolved from MLMD (first run).
                            change_threshold=tfma.GenericChangeThreshold(
                                direction=tfma.MetricDirection.HIGHER_IS_BETTER,
                                absolute={"value": -1e-10},
                            ),
                        ),
                    ),
                ]
            )
        ],
        slicing_specs=[
            # An empty slice spec means the overall slice, i.e. the whole dataset.
            tfma.SlicingSpec(),
            # Data can be sliced along a feature column. In this case, data is
            # sliced along feature column trip_start_hour.
            tfma.SlicingSpec(feature_keys=["sex"]),
        ],
    )

    model_resolver = tfx.dsl.Resolver(
        strategy_class=tfx.dsl.experimental.LatestBlessedModelStrategy,
        model=tfx.dsl.Channel(type=tfx.types.standard_artifacts.Model),
        model_blessing=tfx.dsl.Channel(type=tfx.types.standard_artifacts.ModelBlessing),
    ).with_id("latest_blessed_model_resolver")

    evaluator = tfx.components.Evaluator(
        examples=example_gen.outputs["examples"],
        model=trainer.outputs["model"],
        baseline_model=model_resolver.outputs["model"],
        eval_config=eval_config,
    )

    # Pusher
    pusher = tfx.components.Pusher(
        model=trainer.outputs["model"],
        model_blessing=evaluator.outputs["blessing"],
        push_destination=tfx.proto.PushDestination(
            filesystem=tfx.proto.PushDestination.Filesystem(
                base_directory=serving_model_dir
            )
        ),
    )

    components = [
        example_gen,
        statistics_gen,
        schema_importer,
        example_validator,
        trainer,
        evaluator,
        pusher,
    ]

    return tfx.dsl.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        metadata_connection_config=tfx.orchestration.metadata.sqlite_metadata_connection_config(
            metadata_path
        ),
        components=components,
    )