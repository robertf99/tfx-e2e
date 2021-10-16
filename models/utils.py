import tensorflow as tf


def df_to_dataset(dataframe, label, shuffle=True, batch_size=32):
    dataframe = dataframe.copy()
    labels = dataframe.pop(label)
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(dataframe))
    ds = ds.batch(batch_size)
    ds = ds.prefetch(batch_size)
    return ds
