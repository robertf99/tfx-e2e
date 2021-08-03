import tensorflow_decision_forests as tfdf
from typing import List
from absl import logging
import tensorflow as tf
from tensorflow import keras

from tfx import v1 as tfx

# from tfx_bsl.public import tfxio
from tfx_bsl.tfxio import dataset_options
from tensorflow_metadata.proto.v0 import schema_pb2

from wurlitzer import sys_pipes

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

    # def prepare_label(feature_dict):
    #     # label_dict = tf.sparse.to_dense(
    #     #     feature_dict.pop(_LABEL_KEY),
    #     #     default_value=None,
    #     #     validate_indices=True,
    #     #     name=None,
    #     # )
    #     label_dict = feature_dict.pop(_LABEL_KEY)

    #     return feature_dict, label_dict

    # dataset = dataset.map(prepare_label)
    return dataset


def _build_tfdf_model():
    model = tfdf.keras.RandomForestModel()
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
    #   for features, label in train_dataset.take(1):  # only take first element of dataset
    #     print('*************')
    #     print(features)
    #     print(label)
    eval_dataset = _input_fn(
        fn_args.eval_files, fn_args.data_accessor, schema, batch_size=_EVAL_BATCH_SIZE
    )

    model = _build_tfdf_model()
    with sys_pipes():
        model.fit(
            train_dataset,
            # steps_per_epoch=fn_args.train_steps,
            validation_data=eval_dataset,
        )
        # validation_steps=fn_args.eval_steps)
        print(model.summary())

    model.make_inspector().export_to_tensorboard(fn_args.model_run_dir)
    # The result of the training should be saved in `fn_args.serving_model_dir`
    # directory.
    model.save(fn_args.serving_model_dir, save_format="tf")
