import tensorflow as tf

from .brain_common import positional_encoding
from .decoder_layer import DecoderLayer


class Decoder(tf.keras.layers.Layer):
    """Decoder."""

    def __init__(self, num_layers, d_model, num_heads, dff, target_vocab_size,
                 maximum_position_encoding, dropout_rate=0.1):
        """
        :param num_layers: Number of hidden layers.
        :param d_model: Model dimensionality.
        :param num_heads: Number of attention heads.
        :param dff: Feed-forward network dimensionality.
        :param target_vocab_size: Target vocabulary size.
        :param maximum_position_encoding: Maximum positional encoding.
        :param dropout_rate: Dropout rate.
        """

        super(Decoder, self).__init__()

        self.d_model = d_model
        self.num_layers = num_layers

        self.embedding = tf.keras.layers.Embedding(target_vocab_size, d_model)
        self.pos_encoding = positional_encoding(maximum_position_encoding, d_model)

        self.dec_layers = [DecoderLayer(d_model, num_heads, dff, dropout_rate) for _ in range(num_layers)]
        self.dropout = tf.keras.layers.Dropout(dropout_rate)

    def call(self, x, enc_output, training, look_ahead_mask, padding_mask):
        """
        :param x: X value (input).
        :param enc_output: Encoder output.
        :param training: Whether the model is in training mode.
        :param look_ahead_mask: Look-ahead mask.
        :param padding_mask: Padding mask.

        :returns: Tuple of decoder output and attention weights.
        Shape of `x`: (batch_size, target_seq_len, d_model)
        """

        seq_len = tf.shape(x)[1]
        attention_weights = {}

        x = self.embedding(x)  # (batch_size, target_seq_len, d_model)
        x *= tf.math.sqrt(tf.cast(self.d_model, tf.float32))
        x += self.pos_encoding[:, :seq_len, :]

        x = self.dropout(x, training=training)

        for i in range(self.num_layers):
            x, block1, block2 = self.dec_layers[i](x, enc_output, training, look_ahead_mask, padding_mask)
            attention_weights['decoder_layer{}_block1'.format(i + 1)] = block1
            attention_weights['decoder_layer{}_block2'.format(i + 1)] = block2

        # x.shape: (batch_size, target_seq_len, d_model)
        return x, attention_weights
