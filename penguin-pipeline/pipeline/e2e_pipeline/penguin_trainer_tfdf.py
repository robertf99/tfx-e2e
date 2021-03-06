import tensorflow_decision_forests as tfdf
from typing import List
from absl import logging
import tensorflow as tf
from tensorflow import keras

from tfx import v1 as tfx

# from tfx_bsl.public import tfxio
from tfx_bsl.tfxio import dataset_options
from tensorflow_metadata.proto.v0 import schema_pb2


_LABEL_KEY = "species"

_TRAIN_BATCH_SIZE = 238
_EVAL_BATCH_SIZE = 95


def _input_fn(
    file_pattern: List[str],
    data_accessor: tfx.components.DataAccessor,
    schema: schema_pb2.Schema,
    batch_size: int = 200,
) -> tf.data.Dataset:
    """Generates features and label for training.

    Args:
      file_pattern: List of paths or patterns of input tfrecord files.
      data_accessor: DataAccessor for converting input to RecordBatch.
      schema: schema of the input data.
      batch_size: representing the number of consecutive elements of returned
        dataset to combine in a single batch

    Returns:
      A dataset that contains (features, indices) tuple where features is a
        dictionary of Tensors, and indices is a single Tensor of label indices.
    """

    dataset = data_accessor.tf_dataset_factory(
        file_pattern,
        dataset_options.TensorFlowDatasetOptions(
            batch_size=batch_size, label_key=_LABEL_KEY, num_epochs=1
        ),
        schema,
    )
    return dataset


def _build_tfdf_model():
    # model = tfdf.keras.RandomForestModel(
    #     num_trees=300,
    # )
    model = tfdf.keras.CartModel()

    model.compile(metrics=["accuracy"])
    return model



# TFX Trainer will call this function.
def run_fn(fn_args: tfx.components.FnArgs):
    """Train the model based on given args.

    Args:
      fn_args: Holds args used to train the model as name/value pairs.
    """

    schema = tfx.utils.parse_pbtxt_file(fn_args.schema_path, schema_pb2.Schema())
    train_dataset = _input_fn(
        fn_args.train_files, fn_args.data_accessor, schema, batch_size=_TRAIN_BATCH_SIZE
    )

    eval_dataset = _input_fn(
        fn_args.eval_files, fn_args.data_accessor, schema, batch_size=_EVAL_BATCH_SIZE
    )

    # TF-DF models
    model = _build_tfdf_model()
    model.fit(
        train_dataset,
        validation_data=eval_dataset,
    )
    print(model.summary())
    model.make_inspector().export_to_tensorboard(fn_args.model_run_dir)

    # The result of the training should be saved in `fn_args.serving_model_dir`
    # directory.
    model.save(fn_args.serving_model_dir, save_format="tf")
