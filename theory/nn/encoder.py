import tensorflow as tf

from .brain_common import positional_encoding
from .encoder_layer import EncoderLayer


class Encoder(tf.keras.layers.Layer):
    """Encoder."""

    def __init__(self, num_layers, d_model, num_heads, dff, input_vocab_size, maximum_position_encoding,
                 dropout_rate=0.1):
        """
        :param num_layers: Number of hidden layers.
        :param d_model: Model dimensionality.
        :param num_heads: Number of attention heads.
        :param dff: Feed-forward network dimensionality.
        :param input_vocab_size: Input vocabulary size.
        :param maximum_position_encoding: Maximum positional encoding.
        :param dropout_rate: Dropout rate.
        """

        super(Encoder, self).__init__()

        self.d_model = d_model
        self.num_layers = num_layers

        self.embedding = tf.keras.layers.Embedding(input_vocab_size, d_model)
        self.pos_encoding = positional_encoding(maximum_position_encoding, self.d_model)

        self.enc_layers = [EncoderLayer(d_model, num_heads, dff, dropout_rate) for _ in range(num_layers)]

        self.dropout = tf.keras.layers.Dropout(dropout_rate)

    def call(self, x, training, mask):
        """
        :param x: X value (input)
        :param training: Whether the model is in training mode.
        :param mask: Mask.

        :returns: Encoder output. Shape: (batch_size, input_seq_len, d_model)
        """

        seq_len = tf.shape(x)[1]

        # adding embedding and position encoding.
        x = self.embedding(x)  # (batch_size, input_seq_len, d_model)
        x *= tf.math.sqrt(tf.cast(self.d_model, tf.float32))
        x += self.pos_encoding[:, :seq_len, :]

        x = self.dropout(x, training=training)

        for i in range(self.num_layers):
            x = self.enc_layers[i](x, training, mask)

        return x  # (batch_size, input_seq_len, d_model)
