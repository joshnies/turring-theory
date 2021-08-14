import os
from os import path
import time
import tensorflow as tf
import tensorflow_datasets as tfds
import wandb

from cli import log
from theory.lvp import LVP
from api.config import DEBUG
from .custom_schedule import CustomSchedule
from .datasets import load_datasets
from .hyperparams import Hyperparams
from .transformer import Transformer

# Global translation neural network architecture
loss_object = tf.keras.losses.SparseCategoricalCrossentropy(
    from_logits=True, reduction='none'
)


class Brain:
    """Translation neural network abstraction."""

    def __init__(self, lvp: LVP, hyperparams: Hyperparams, output_dir_path: str, base_dataset_path: str = 'data',
                 train_dataset_path: str = None, valid_dataset_path: str = None, enable_wandb: bool = True,
                 debug: bool = False):
        self.lvp = lvp
        self.hyperparams = hyperparams
        self.output_dir_path = output_dir_path
        self.train_dataset_path = \
            path.join(base_dataset_path,
                      f'{lvp.value.lower()}_train.csv') if train_dataset_path is None else train_dataset_path
        self.valid_dataset_path = \
            path.join(base_dataset_path,
                      f'{lvp.value.lower()}_valid.csv') if valid_dataset_path is None else valid_dataset_path
        self.enable_wandb = enable_wandb
        self.debug = debug

        # Load datasets
        self.__load_datasets()

        self.learning_rate = CustomSchedule(self.hyperparams.d_model)
        self.optimizer = tf.keras.optimizers.Adam(
            self.learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9)
        self.transformer = Transformer(self.hyperparams.num_layers, self.hyperparams.d_model,
                                       self.hyperparams.num_heads, self.hyperparams.dff, self.input_vocab_size,
                                       self.target_vocab_size, pe_input=self.input_vocab_size,
                                       pe_target=self.target_vocab_size, rate=self.hyperparams.dropout_rate)

        # Output hyperparams
        if DEBUG:
            # TODO: Use TensorFlow model's `.summary()` method instead
            print(self.hyperparams)

        # Configure checkpoints
        self.checkpoint_path = path.join(self.output_dir_path, 'checkpoints')

        self.ckpt = tf.train.Checkpoint(
            transformer=self.transformer, optimizer=self.optimizer)
        self.ckpt_manager = tf.train.CheckpointManager(
            self.ckpt, self.checkpoint_path, max_to_keep=10)

    def __load_datasets(self):
        """Load and process the training and validation datasets."""

        # Validate dataset paths
        if not path.exists(self.train_dataset_path):
            raise Exception(
                f'Training dataset at path "{self.train_dataset_path}" does not exist.')

        if not path.exists(self.valid_dataset_path):
            raise Exception(
                f'Validation dataset at path "{self.valid_dataset_path}" does not exist.')

        # Load datasets
        train_examples, val_examples = load_datasets(train_path=self.train_dataset_path,
                                                     valid_path=self.valid_dataset_path)

        # Create tokenizers output directory (recursive)
        base_tokenizers_path = path.join(self.output_dir_path, 'tokenizers')
        src_tokenizer_prefix = path.join(base_tokenizers_path, 'src')
        tar_tokenizer_prefix = path.join(base_tokenizers_path, 'tar')

        os.makedirs(base_tokenizers_path, exist_ok=True)

        if path.exists(f'{src_tokenizer_prefix}.subwords'):
            # Load source tokenizer
            log('Loading source tokenizer...')
            self.tokenizer_src = tfds.deprecated.text.SubwordTextEncoder.load_from_file(
                src_tokenizer_prefix
            )
        else:
            # Build and save source tokenizer
            log('Building source tokenizer from corpus...')
            self.tokenizer_src = tfds.deprecated.text.SubwordTextEncoder.build_from_corpus(
                (s.numpy() for s, _ in train_examples), target_vocab_size=2 ** 13)
            self.tokenizer_src.save_to_file(src_tokenizer_prefix)

        if path.exists(f'{tar_tokenizer_prefix}.subwords'):
            # Load target tokenizer
            log('Loading target tokenizer...')
            self.tokenizer_tar = tfds.deprecated.text.SubwordTextEncoder.load_from_file(
                tar_tokenizer_prefix)
        else:
            # Build and save target tokenizer
            log('Building target tokenizer from corpus...')
            self.tokenizer_tar = tfds.deprecated.text.SubwordTextEncoder.build_from_corpus(
                (t.numpy() for _, t in train_examples), target_vocab_size=2 ** 13)
            self.tokenizer_tar.save_to_file(tar_tokenizer_prefix)

        self.input_vocab_size = self.tokenizer_src.vocab_size + 2
        self.target_vocab_size = self.tokenizer_tar.vocab_size + 2

        def encode(lang1, lang2):
            lang1 = [self.tokenizer_src.vocab_size] + self.tokenizer_src.encode(lang1.numpy()) + [
                self.tokenizer_src.vocab_size + 1]

            lang2 = [self.tokenizer_tar.vocab_size] + self.tokenizer_tar.encode(lang2.numpy()) + [
                self.tokenizer_tar.vocab_size + 1]

            return lang1, lang2

        def tf_encode(pt, en):
            result_pt, result_en = tf.py_function(
                encode, [pt, en], [tf.int64, tf.int64])
            result_pt.set_shape([None])
            result_en.set_shape([None])

            return result_pt, result_en

        # Training dataset
        self.train_dataset = train_examples.map(tf_encode)
        self.train_dataset = self.train_dataset.cache()
        self.train_dataset = self.train_dataset.shuffle(self.hyperparams.buffer_size).padded_batch(
            self.hyperparams.batch_size)
        self.train_dataset = self.train_dataset.prefetch(
            tf.data.experimental.AUTOTUNE)

        # Validation dataset
        self.val_dataset = val_examples.map(tf_encode)

    @staticmethod
    def create_padding_mask(seq):
        seq = tf.cast(tf.math.equal(seq, 0), tf.float32)

        # Add extra dimensions to add the padding to the attention logits
        return seq[:, tf.newaxis, tf.newaxis, :]  # (batch_size, 1, 1, seq_len)

    @staticmethod
    def loss_function(real, pred):
        mask = tf.math.logical_not(tf.math.equal(real, 0))
        loss_ = loss_object(real, pred)

        mask = tf.cast(mask, dtype=loss_.dtype)
        loss_ *= mask

        return tf.reduce_sum(loss_) / tf.reduce_sum(mask)

    @staticmethod
    def accuracy_function(real, pred):
        accuracies = tf.equal(real, tf.argmax(pred, axis=2))

        mask = tf.math.logical_not(tf.math.equal(real, 0))
        accuracies = tf.math.logical_and(mask, accuracies)

        accuracies = tf.cast(accuracies, dtype=tf.float32)
        mask = tf.cast(mask, dtype=tf.float32)
        return tf.reduce_sum(accuracies) / tf.reduce_sum(mask)

    @staticmethod
    def create_masks(inp, tar):
        # Encoder padding mask
        enc_padding_mask = Brain.create_padding_mask(inp)

        # Used in the 2nd attention block in the decoder.
        # This padding mask is used to mask the encoder outputs.
        dec_padding_mask = Brain.create_padding_mask(inp)

        # Used in the 1st attention block in the decoder.
        # It is used to pad and mask future tokens in the input received by
        # the decoder.
        look_ahead_mask = Brain.create_look_ahead_mask(tf.shape(tar)[1])
        dec_target_padding_mask = Brain.create_padding_mask(tar)
        combined_mask = tf.maximum(dec_target_padding_mask, look_ahead_mask)

        return enc_padding_mask, combined_mask, dec_padding_mask

    @staticmethod
    def create_look_ahead_mask(size):
        """Create look-ahead mask to mask future tokens in the sequence"""

        mask = 1 - tf.linalg.band_part(tf.ones((size, size)), -1, 0)
        return mask  # (seq_len, seq_len)

    def restore_checkpoint(self):
        """Restore latest checkpoint."""

        if self.ckpt_manager.latest_checkpoint:
            self.ckpt.restore(self.ckpt_manager.latest_checkpoint)
            log(f'Latest checkpoint restored from "{self.checkpoint_path}".')

    def train(self):
        """Train translation neural network."""

        # Initialize wandb
        if self.enable_wandb:
            wandb.init(project='theory', entity='joshnies-turring')
            config = wandb.config
            config.lvp = self.lvp.value
            config.epochs = self.hyperparams.epochs
            config.buffer_size = self.hyperparams.buffer_size
            config.batch_size = self.hyperparams.batch_size
            config.num_layers = self.hyperparams.num_layers
            config.d_model = self.hyperparams.d_model
            config.dff = self.hyperparams.dff
            config.num_heads = self.hyperparams.num_heads
            config.dropout_rate = self.hyperparams.dropout_rate
            config.learning_rate_warmup_steps = self.learning_rate.warmup_steps

        train_loss = tf.keras.metrics.Mean(name='train_loss')
        train_accuracy = tf.keras.metrics.Mean(name='train_accuracy')

        train_step_signature = [
            tf.TensorSpec(shape=(None, None), dtype=tf.int64),
            tf.TensorSpec(shape=(None, None), dtype=tf.int64),
        ]

        @tf.function(input_signature=train_step_signature)
        def train_step(inp, tar):
            """Training step."""

            tar_inp = tar[:, :-1]
            tar_real = tar[:, 1:]

            enc_padding_mask, combined_mask, dec_padding_mask = self.create_masks(
                inp, tar_inp)

            with tf.GradientTape() as tape:
                predictions, _ = self.transformer((inp, tar_inp),
                                                  mask=[
                                                      enc_padding_mask, combined_mask, dec_padding_mask],
                                                  training=True)
                loss = self.loss_function(tar_real, predictions)

            gradients = tape.gradient(
                loss, self.transformer.trainable_variables)
            self.optimizer.apply_gradients(
                zip(gradients, self.transformer.trainable_variables))

            train_loss(loss)
            train_accuracy(self.accuracy_function(tar_real, predictions))

        step = 0

        # Training routine
        for epoch in range(self.hyperparams.epochs):
            start = time.time()

            train_loss.reset_states()
            train_accuracy.reset_states()

            for (batch, (inp, tar)) in enumerate(self.train_dataset):
                train_step(inp, tar)
                step += 1

                if batch % 50 == 0:
                    log('Epoch {} Batch {} Loss {:.4f} Accuracy {:.4f}'.format(epoch + 1, batch, train_loss.result(),
                                                                               train_accuracy.result()))

            # Save checkpoint
            ckpt_save_path = self.ckpt_manager.save()
            log('Saving checkpoint for epoch {} at {}'.format(
                epoch + 1, ckpt_save_path))

            # Log epoch results
            loss = train_loss.result()
            accuracy = train_accuracy.result()
            time_taken = time.time() - start
            log('Epoch {}\tLoss {:.4f}\tAccuracy {:.4f}'.format(
                epoch + 1, loss, accuracy))
            log('Epoch took {}s\n'.format(time_taken))

            if self.enable_wandb:
                wandb.log({
                    'epoch': epoch + 1,
                    'loss': loss,
                    'accuracy': accuracy,
                    'time_taken': time_taken,
                    'step': step,
                    'learning_rate': float(self.learning_rate(tf.Variable(step, dtype=tf.float32)))
                })

            # TODO: Fix
            # Stop training if loss is 0 and accuracy is 100%
            # if loss == float(0) and accuracy == float(1):
            #     log('🎯 Model has converged!')
            #     break

        log('🎉 Training complete!')

    def __evaluate(self, input):
        """Evaluate model."""

        start_token = [self.tokenizer_src.vocab_size]
        end_token = [self.tokenizer_src.vocab_size + 1]

        # Add the start and end token to input sequence
        input = start_token + self.tokenizer_src.encode(input) + end_token
        encoder_input = tf.expand_dims(input, 0)

        # First token sent to the transformer should be the start token
        decoder_input = [self.tokenizer_tar.vocab_size]
        output = tf.expand_dims(decoder_input, 0)

        # NOTE: Arbitrary max length of 512
        for _ in range(512):
            enc_padding_mask, combined_mask, dec_padding_mask = self.create_masks(
                encoder_input, output)

            # predictions.shape: (batch_size, seq_len, vocab_size)
            predictions, _ = self.transformer((encoder_input, output),
                                              mask=[
                                                  enc_padding_mask, combined_mask, dec_padding_mask],
                                              training=False)

            # Select the last word from the seq_len dimension
            predictions = predictions[:, -1:, :]  # (batch_size, 1, vocab_size)

            predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)

            # Return result if "predicted_id" is the end token
            if predicted_id == self.tokenizer_tar.vocab_size + 1:
                return tf.squeeze(output, axis=0)

            # Concatenate the predicted_id to the output which is given to the decoder
            # as its input.
            output = tf.concat([output, predicted_id], axis=-1)

        return tf.squeeze(output, axis=0)

    def translate(self, input: str) -> str:
        """Translate input sequence to target LVP."""

        # Translate
        result = self.__evaluate(input.strip())
        result = self.tokenizer_tar.decode(
            [i for i in result if i < self.tokenizer_tar.vocab_size])

        return result
