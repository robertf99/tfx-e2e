# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# This file runs each step of pipeline seperately as a debug tool

# %%
from tfx import v1 as tfx
from pipeline.config import pipe_config

# import tensorflow_decision_forests as tfdf


# %%
from tfx.orchestration.experimental.interactive import visualizations


def visualize_artifacts(artifacts):
    """Visualizes artifacts using standard visualization modules."""
    for artifact in artifacts:
        visualization = visualizations.get_registry().get_visualization(
            artifact.type_name
        )
        if visualization:
            visualization.display(artifact)


from tfx.orchestration.experimental.interactive import standard_visualizations

standard_visualizations.register_standard_visualizations()

# %% [markdown]
# # Connect to Pipeline output

# %%
# from ml_metadata import metadata_store
# connection_config = metadata_store_pb2.ConnectionConfig()
# connection_config.sqlite.filename_uri = pipe_config.METADATA_PATH
# store = metadata_store.MetadataStore(connection_config,enable_upgrade_migration = True)
metadata_connection_config = (
    tfx.orchestration.metadata.sqlite_metadata_connection_config(
        pipe_config.METADATA_PATH
    )
)


# %%
# get lattest trainer artifacts
from pipeline.schema_pipeline.utils import get_latest_artifacts
from tfx.orchestration.metadata import Metadata
from tfx.types import standard_component_specs

with Metadata(metadata_connection_config) as metadata_handler:
    stat_gen_output = get_latest_artifacts(
        metadata_handler, pipe_config.PIPELINE_NAME, "StatisticsGen"
    )
    stats_artifacts = stat_gen_output[standard_component_specs.STATISTICS_KEY]

    ev_output = get_latest_artifacts(
        metadata_handler, pipe_config.PIPELINE_NAME, "ExampleValidator"
    )
    anomalies_artifacts = ev_output[standard_component_specs.ANOMALIES_KEY]

    trainer_outputs = get_latest_artifacts(
        metadata_handler, pipe_config.PIPELINE_NAME, "Trainer"
    )
    example_gen_outputs = get_latest_artifacts(
        metadata_handler, pipe_config.PIPELINE_NAME, "CsvExampleGen"
    )
    evaluator_outputs = get_latest_artifacts(
        metadata_handler, pipe_config.PIPELINE_NAME, "Evaluator"
    )
    eval_artifact = evaluator_outputs[standard_component_specs.EVALUATION_KEY][0]


# %%
evaluator_outputs

# %% [markdown]
# ## Stats Gen

# %%
visualize_artifacts(stats_artifacts)

# %% [markdown]
# ## Example Validator

# %%

visualize_artifacts(anomalies_artifacts)

# %% [markdown]
# ## Trainer

# %%
model_run_artifact_dir = trainer_outputs["model_run"][0].uri


# %%
# %load_ext tensorboard
# get_ipython().run_line_magic("tensorboard", "--logdir {model_run_artifact_dir}")

# %% [markdown]
# ## Evaluator

# %%
import tensorflow_model_analysis as tfma


# %%
# !jupyter nbextension enable --py widgetsnbextension
# !jupyter nbextension enable --py tensorflow_model_analysis
# !jupyter labextension install tensorflow_model_analysis@0.33.0


# %%
# get_ipython().system("jupyter nbextension list")
# get_ipython().system("jupyter labextension list  # for JupyterLab")


# %%
eval_result = tfma.load_eval_result(eval_artifact.uri, model_name="candidate")


# %%
tfma.view.render_slicing_metrics(eval_result, slicing_column="sex")


# %%
tfma.addons.fairness.view.widget_view.render_fairness_indicator(eval_result)


# %%
tfma.view.render_plot(eval_result, tfma.SlicingSpec(feature_values={"sex": "male"}))


# %%
eval_artifact


# %%
