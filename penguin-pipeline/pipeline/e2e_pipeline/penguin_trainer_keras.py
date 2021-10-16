from typing import List
from absl import logging
import tensorflow as tf
from tensorflow import keras

from tfx import v1 as tfx

# from tfx_bsl.public import tfxio
from tfx_bsl.tfxio import dataset_options
from tensorflow_metadata.proto.v0 import schema_pb2


_LABEL_KEY = "species"

_TRAIN_BATCH_SIZE = 100
_EVAL_BATCH_SIZE = 10


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
    ).repeat()
    return dataset


# keras model
def _build_keras_model(schema: schema_pb2.Schema):
    inputs = [
        keras.layers.Input(shape=(1,), name=f.name)
        for f in schema.feature
        if f.name != _LABEL_KEY and f.type != schema_pb2.FeatureType.BYTES
    ]
    d = keras.layers.concatenate(inputs)
    for _ in range(2):
        d = keras.layers.Dense(8, activation="relu")(d)
    outputs = keras.layers.Dense(3, activation="softmax")(d)  # number of classes

    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(1e-2),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[keras.metrics.SparseCategoricalAccuracy()],
    )

    model.summary(print_fn=logging.info)
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

    # Keras models
    model = _build_keras_model(schema)
    tensorboard_callback = tf.keras.callbacks.TensorBoard(
        log_dir=fn_args.model_run_dir, update_freq="batch"
    )
    model.fit(
        train_dataset,
        steps_per_epoch=fn_args.train_steps,
        validation_data=eval_dataset,
        validation_steps=fn_args.eval_steps,
        callbacks=[tensorboard_callback],
    )

    # The result of the training should be saved in `fn_args.serving_model_dir`
    # directory.
    model.save(fn_args.serving_model_dir, save_format="tf")
