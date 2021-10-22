from typing import List
from absl import logging
import tensorflow as tf
from tensorflow import keras
import tensorflow_transform as tft


from tfx import v1 as tfx

# from tfx_bsl.public import tfxio
from tfx_bsl.tfxio import dataset_options


_LABEL_KEY = "species"
_NUMERIC_KEYS = [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]
_CATEGORY_KEYS = ["island", "sex", "year"]


_TRAIN_BATCH_SIZE = 32
_EVAL_BATCH_SIZE = 32


def _transformed_name(key):
    return key + "_xf"


# This function will apply the same transform operation to training data
#      and serving requests.
def _apply_preprocessing(raw_features, tft_layer):
    transformed_features = tft_layer(raw_features)
    if _LABEL_KEY in raw_features:
        transformed_label = transformed_features.pop(_transformed_name(_LABEL_KEY))
        return transformed_features, transformed_label
    else:
        return transformed_features, None


def preprocessing_fn(inputs):
    outputs = {}
    for key in _NUMERIC_KEYS:
        outputs[_transformed_name(key)] = tft.scale_to_z_score(inputs[key])
    for key in _CATEGORY_KEYS:
        outputs[_transformed_name(key)] = tft.compute_and_apply_vocabulary(inputs[key])
    outputs[_transformed_name(_LABEL_KEY)] = tft.compute_and_apply_vocabulary(
        inputs[_LABEL_KEY]
    )

    return outputs


def _input_fn(
    file_pattern: List[str],
    data_accessor: tfx.components.DataAccessor,
    tf_transform_output: tft.TFTransformOutput,
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
        dataset_options.TensorFlowDatasetOptions(batch_size=batch_size, num_epochs=1),
        schema=tf_transform_output.raw_metadata.schema,
    )

    tft_layer = tf_transform_output.transform_features_layer()

    def apply_transform(raw_features):
        return _apply_preprocessing(raw_features, tft_layer)

    # return dataset
    return dataset.map(apply_transform)


# keras model
def _build_keras_model():
    inputs = [
        keras.layers.Input(shape=(1,), name=_transformed_name(f))
        for f in _NUMERIC_KEYS + _CATEGORY_KEYS
    ]
    d = keras.layers.concatenate(inputs)
    for _ in range(2):
        d = keras.layers.Dense(8, activation="relu")(d)
    outputs = keras.layers.Dense(3)(d)  # number of classes

    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    model.summary(print_fn=logging.info)
    return model


# TFX Trainer will call this function.
def run_fn(fn_args: tfx.components.FnArgs):
    """Train the model based on given args.

    Args:
      fn_args: Holds args used to train the model as name/value pairs.
    """
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_output)
    train_dataset = _input_fn(
        fn_args.train_files,
        fn_args.data_accessor,
        tf_transform_output,
        batch_size=_TRAIN_BATCH_SIZE,
    )

    eval_dataset = _input_fn(
        fn_args.eval_files,
        fn_args.data_accessor,
        tf_transform_output,
        batch_size=_EVAL_BATCH_SIZE,
    )

    # Keras models
    model = _build_keras_model()
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=fn_args.model_run_dir)
    model.fit(
        train_dataset,
        validation_data=eval_dataset,
        epochs=30,
        callbacks=[tensorboard_callback],
    )

    # The result of the training should be saved in `fn_args.serving_model_dir`
    # directory.
    model.save(fn_args.serving_model_dir, save_format="tf")

    # This function will create a handler function which gets a serialized
    #  tf.example, preprocess and run an inference with it.
    def _get_serve_tf_examples_fn(model, tf_transform_output):
        # We must save the tft_layer to the model to ensure its assets are kept and
        # tracked.
        model.tft_layer = tf_transform_output.transform_features_layer()

        @tf.function(
            input_signature=[
                tf.TensorSpec(shape=[None], dtype=tf.string, name="examples")
            ]
        )
        def serve_tf_examples_fn(serialized_tf_examples):
            # Expected input is a string which is serialized tf.Example format.
            feature_spec = tf_transform_output.raw_feature_spec()
            # Because input schema includes unnecessary fields like 'species' and
            # 'island', we filter feature_spec to include required keys only.
            required_feature_spec = {
                k: v
                for k, v in feature_spec.items()
                if k in _NUMERIC_KEYS + _CATEGORY_KEYS
            }
            parsed_features = tf.io.parse_example(
                serialized_tf_examples, required_feature_spec
            )

            # Preprocess parsed input with transform operation defined in
            # preprocessing_fn().
            transformed_features, _ = _apply_preprocessing(
                parsed_features, model.tft_layer
            )
            # Run inference with ML model.
            return model(transformed_features)

        return serve_tf_examples_fn

    # TFT: Save a computation graph including transform layer.
    signatures = {
        "serving_default": _get_serve_tf_examples_fn(model, tf_transform_output),
    }
    model.save(fn_args.serving_model_dir, save_format="tf", signatures=signatures)
