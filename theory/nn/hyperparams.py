class Hyperparams:
    """Hyperparameters configuration object."""

    def __init__(self, buffer_size: int, batch_size: int, num_layers: int, d_model: int, dff: int, num_heads: int,
                 dropout_rate: float, epochs: int = 10):
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.num_layers = num_layers
        self.d_model = d_model
        self.dff = dff
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate
        self.epochs = epochs

    def __str__(self):
        return '| ' + '-' * 78 + '\n' + \
               '| Hyperparameters:\n'+ \
               '| ' + '-' * 78 + '\n' + \
               f'| Epochs: {self.epochs}\n' + \
               f'| Buffer size: {self.buffer_size}\n' + \
               f'| Batch size: {self.batch_size}\n' + \
               f'| Number of layers: {self.num_layers}\n' + \
               f'| Model dimensionality: {self.d_model}\n' + \
               f'| Dense feed-forward network size (neurons): {self.dff}\n' + \
               f'| Number of heads: {self.num_heads}\n' + \
               f'| Dropout rate: {self.dropout_rate}\n' + \
               '| ' + '-' * 78
