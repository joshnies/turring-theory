import tensorflow as tf


def load_datasets(train_path: str, valid_path: str):
    """
    Load datasets.

    :param train_path: Path to training dataset file.
    :param valid_path: Path to validation dataset file.
    :returns: Tuple of TensorFlow CSV datasets for training and validation.
    """

    record_defaults = ['', '']
    train_dataset = tf.data.experimental.CsvDataset(train_path, record_defaults)
    valid_dataset = tf.data.experimental.CsvDataset(valid_path, record_defaults)

    return train_dataset, valid_dataset
