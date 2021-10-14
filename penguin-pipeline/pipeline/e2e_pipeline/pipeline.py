from typing import Optional
from tfx import v1 as tfx
import tensorflow_model_analysis as tfma
from ml_metadata.proto import metadata_store_pb2


def create_pipeline(
    pipeline_name: str,
    pipeline_root: str,
    data_root: str,
    schema_path: str,
    serving_model_dir: str,
    trainer_module_path: str,
    evaluation_module_path: str = None,
    metadata_connection_config: Optional[metadata_store_pb2.ConnectionConfig] = None,
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
        module_file=trainer_module_path,
        examples=example_gen.outputs["examples"],
        schema=schema_importer.outputs["result"],  # Pass the imported schema.
        train_args=tfx.proto.TrainArgs(num_steps=300),
        eval_args=tfx.proto.EvalArgs(num_steps=50),
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
                    tfma.MetricConfig(class_name="AUC"),
                    tfma.MetricConfig(class_name="AUCPrecisionRecall"),
                    tfma.MetricConfig(class_name="Precision"),
                    tfma.MetricConfig(class_name="Recall"),
                    tfma.MetricConfig(class_name="MeanPrediction"),
                    tfma.MetricConfig(class_name="CalibrationPlot"),
                    tfma.MetricConfig(class_name="ConfusionMatrixPlot"),
                    tfma.MetricConfig(
                        class_name="SparseCategoricalAccuracy",
                        threshold=tfma.MetricThreshold(
                            value_threshold=tfma.GenericValueThreshold(
                                lower_bound={"value": 0.5}
                            ),
                            # Change threshold will be ignored if there is no
                            # baseline model resolved from MLMD (first run).
                            change_threshold=tfma.GenericChangeThreshold(
                                direction=tfma.MetricDirection.HIGHER_IS_BETTER,
                                absolute={"value": 1e-10},
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
            # tfma.SlicingSpec(feature_keys=["sex"]),
            # tfma.SlicingSpec(feature_keys=["island"]),
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
        module_file=evaluation_module_path
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
        model_resolver,
        evaluator,
        pusher,
    ]

    return tfx.dsl.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        metadata_connection_config=metadata_connection_config,
        components=components,
    )
