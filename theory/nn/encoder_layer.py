import tensorflow as tf

from .brain_common import point_wise_feed_forward_network
from .mha import MultiHeadAttention


class EncoderLayer(tf.keras.layers.Layer):
    """Encoder layer."""

    def __init__(self, d_model, num_heads, dff, dropout_rate=0.1):
        """
        :param d_model: Model dimensionality.
        :param num_heads: Number of attention heads.
        :param dff: Feed-forward network dimensionality.
        :param dropout_rate: Dropout rate.
        """

        super(EncoderLayer, self).__init__()

        self.mha = MultiHeadAttention(d_model, num_heads)
        self.ffn = point_wise_feed_forward_network(d_model, dff)

        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)

        self.dropout1 = tf.keras.layers.Dropout(dropout_rate)
        self.dropout2 = tf.keras.layers.Dropout(dropout_rate)

    def call(self, x, training, mask):
        """
        :param x: X value (input).
        :param training: Whether the model is in training mode.
        :param mask: Mask.

        :returns: Output.
        """

        attn_output, _ = self.mha(x, x, x, mask)  # (batch_size, input_seq_len, d_model)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)  # (batch_size, input_seq_len, d_model)

        ffn_output = self.ffn(out1)  # (batch_size, input_seq_len, d_model)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.layernorm2(out1 + ffn_output)  # (batch_size, input_seq_len, d_model)

        return out2
