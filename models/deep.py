# %%

import pandas as pd
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers
import datetime
from sklearn.model_selection import train_test_split

from utils import df_to_dataset, get_category_encoding_layer,get_normalization_layer

# %%
LABEL = "species"
log_dir = "./logs/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# %%

df = pd.read_csv("../data/penguin-e2e/data.csv")
df.columns
# %%
# df_numeric = df[
#     [
#         "bill_length_mm",
#         "bill_depth_mm",
#         "flipper_length_mm",
#         "body_mass_g",
#         "year",
#         LABEL,
#     ]
# ]
train, test = train_test_split(df, test_size=0.2)
print(len(train), "train examples")
print(len(test), "test examples")
# %%
train_ds = df_to_dataset(train, LABEL)
test_ds = df_to_dataset(test, LABEL)
train_ds.take(1)
# %%
inputs = []
encoded_features=[]
for f in [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]:
    input = tf.keras.Input(shape=(1,), name=f)
    inputs.append(input)
    encoded_features.append(input)

# Numeric features.
# for header in [
#     "bill_length_mm",
#     "bill_depth_mm",
#     "flipper_length_mm",
#     "body_mass_g",
# ]:
#   numeric_col = tf.keras.Input(shape=(1,), name=header)
#   normalization_layer = get_normalization_layer(header, train_ds)
#   encoded_numeric_col = normalization_layer(numeric_col)
#   inputs.append(numeric_col)
#   encoded_features.append(encoded_numeric_col)

# Categorical features encoded as string.
categorical_cols = ['island','sex']
for header in categorical_cols:
    categorical_col = tf.keras.Input(shape=(1,), name=header, dtype='string')
    encoding_layer = get_category_encoding_layer(header, train_ds, dtype='string')
    encoded_categorical_col = encoding_layer(categorical_col)
    inputs.append(categorical_col)
    encoded_features.append(encoded_categorical_col)

year_col = tf.keras.Input(shape=(1,), name='year', dtype='int64')
encoding_layer = get_category_encoding_layer('year', train_ds, dtype='int64')
encoded_year_col = encoding_layer(year_col)
inputs.append(year_col)
encoded_features.append(encoded_year_col)

# %%
all_features = tf.keras.layers.concatenate(encoded_features)
x = tf.keras.layers.Dense(4, activation="relu")(all_features)
x = tf.keras.layers.Dense(4, activation="relu")(x)
output = tf.keras.layers.Dense(3)(x)

model = tf.keras.Model(inputs, output)
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=0)

model.compile(
    optimizer="adam",
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"])

# tf.keras.utils.plot_model(model, show_shapes=True, rankdir="LR")

# %%
model.fit(train_ds, epochs=100, validation_data=test_ds, callbacks=[tensorboard_callback])

# %%
# ! tensorboard --logdir logs/

# %%
