#  Explore if this step can be part of the tfx pipeline
from config import pipe_config
import urllib.request
import os
import pandas as pd


_data_url = "https://storage.googleapis.com/download.tensorflow.org/data/palmer_penguins/penguins.csv"
_data_filepath = os.path.join(pipe_config.SCHEMA_DATA_ROOT, "data.csv")
urllib.request.urlretrieve(_data_url, _data_filepath)

dataset_df = pd.read_csv(_data_filepath)
print(dataset_df.shape)
# Name of the label column.
label = "species"
classes = dataset_df[label].unique().tolist()
print(f"Label classes: {classes}")
dataset_df[label] = dataset_df[label].map(classes.index)
clean_df = dataset_df.dropna()
print(clean_df.shape)
clean_df.to_csv(_data_filepath, index=False)