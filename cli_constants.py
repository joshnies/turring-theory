from theory.nn.hyperparams import Hyperparams

DEFAULT_HYPERPARAMS = Hyperparams(
    epochs=100,
    buffer_size=20000,
    batch_size=256,
    num_layers=4,
    d_model=128,
    dff=512,
    num_heads=8,
    dropout_rate=0.1
)
