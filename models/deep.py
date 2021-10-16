# %%

import pandas as pd
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split

from utils import df_to_dataset

# %%
LABEL = "species"
# %%

df = pd.read_csv("../data/penguin-e2e/data.csv")
df.columns
# %%
df_numeric = df[
    [
        "bill_length_mm",
        "bill_depth_mm",
        "flipper_length_mm",
        "body_mass_g",
        "year",
        LABEL,
    ]
]
train, test = train_test_split(df_numeric, test_size=0.2)
print(len(train), "train examples")
print(len(test), "test examples")
# %%
train_ds = df_to_dataset(train, LABEL)
test_ds = df_to_dataset(test, LABEL)
train_ds.take(1)
# %%
inputs = []
for f in [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
    "year",
]:
    input = tf.keras.Input(shape=(1,), name=f)
    inputs.append(input)

all_features = tf.keras.layers.concatenate(inputs)
x = tf.keras.layers.Dense(8, activation="relu")(all_features)
x = tf.keras.layers.Dense(8, activation="relu")(x)
output = tf.keras.layers.Dense(3)(x)

model = tf.keras.Model(inputs, output)
model.compile(
    optimizer="adam",
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)

# %%
tf.keras.utils.plot_model(model, show_shapes=True, rankdir="LR")

# %%
model.fit(train_ds, epochs=100, validation_data=test_ds)

# %%
