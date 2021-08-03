import tensorflow as tf

from .brain_common import point_wise_feed_forward_network
from .mha import MultiHeadAttention


class DecoderLayer(tf.keras.layers.Layer):
    """Decoder layer."""

    def __init__(self, d_model, num_heads, dff, dropout_rate=0.1):
        """
        :param d_model: Model dimensionality.
        :param num_heads: Number of attention heads.
        :param dff: Feed-forward network dimensionality.
        :param dropout_rate: Dropout rate.
        """

        super(DecoderLayer, self).__init__()

        self.mha1 = MultiHeadAttention(d_model, num_heads)
        self.mha2 = MultiHeadAttention(d_model, num_heads)

        self.ffn = point_wise_feed_forward_network(d_model, dff)

        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm3 = tf.keras.layers.LayerNormalization(epsilon=1e-6)

        self.dropout1 = tf.keras.layers.Dropout(dropout_rate)
        self.dropout2 = tf.keras.layers.Dropout(dropout_rate)
        self.dropout3 = tf.keras.layers.Dropout(dropout_rate)

    def call(self, x, enc_output, training, look_ahead_mask, padding_mask):
        """
        :param x: X value (input).
        :param enc_output: Encoder output.
        :param training: Whether the model is in training mode.
        :param look_ahead_mask: Look-ahead mask.
        :param padding_mask: Padding mask.

        :returns: [Tuple] Output, block 1 attentions weights, block 2 attention weights
        """

        # enc_output.shape: (batch_size, input_seq_len, d_model)

        attn1, attn_weights_block1 = self.mha1(x, x, x, look_ahead_mask)  # (batch_size, target_seq_len, d_model)
        attn1 = self.dropout1(attn1, training=training)
        out1 = self.layernorm1(attn1 + x)

        attn2, attn_weights_block2 = self.mha2(enc_output, enc_output, out1,
                                               padding_mask)  # (batch_size, target_seq_len, d_model)
        attn2 = self.dropout2(attn2, training=training)
        out2 = self.layernorm2(attn2 + out1)  # (batch_size, target_seq_len, d_model)

        ffn_output = self.ffn(out2)  # (batch_size, target_seq_len, d_model)
        ffn_output = self.dropout3(ffn_output, training=training)
        out3 = self.layernorm3(ffn_output + out2)  # (batch_size, target_seq_len, d_model)

        return out3, attn_weights_block1, attn_weights_block2
