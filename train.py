import argparse

from cli_constants import DEFAULT_HYPERPARAMS
from theory.lvp import LVP
from theory.nn.brain import Brain
from theory.nn.hyperparams import Hyperparams

# Get command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--base-data-path',
                    help='Base dataset path (e.g. "data")', default='data')
parser.add_argument('--train-data', help='Training dataset file path')
parser.add_argument('--valid-data', help='Validation dataset file path')
parser.add_argument(
    '-o', '--out', help='Saved model and checkpoint directory', default='output')
parser.add_argument('-l', '--lvp', help='Language-version pair', required=True)
parser.add_argument('-e', '--epochs', help='Number of epochs',
                    type=int, default=DEFAULT_HYPERPARAMS.epochs)
parser.add_argument('--buffer-size', help='Buffer size',
                    type=int, default=DEFAULT_HYPERPARAMS.buffer_size)
parser.add_argument('--batch-size', help='Batch size',
                    type=int, default=DEFAULT_HYPERPARAMS.batch_size)
parser.add_argument('--layers', help='Number of layers',
                    type=int, default=DEFAULT_HYPERPARAMS.num_layers)
parser.add_argument('--d-model', help='d-model size',
                    type=int, default=DEFAULT_HYPERPARAMS.d_model)
parser.add_argument('--dff', help='Size of the dense feed-forward neural network', type=int,
                    default=DEFAULT_HYPERPARAMS.dff)
parser.add_argument('--heads', help='Number of attention heads',
                    type=int, default=DEFAULT_HYPERPARAMS.num_heads)
parser.add_argument('--dropout', help='Dropout rate',
                    type=float, default=DEFAULT_HYPERPARAMS.dropout_rate)
parser.add_argument('--disable-wandb', help='Whether to enable Weights & Biases (wandb) integration',
                    action='store_true')
args = parser.parse_args()

# Get LVP from args
lvp = None

try:
    lvp = LVP[args.lvp.upper()]
except Exception:
    raise Exception(f'Unknown language-version pair "{args.lvp}".')

# Initialize Theory
brain = Brain(
    lvp,
    Hyperparams(
        epochs=args.epochs,
        buffer_size=args.buffer_size,
        batch_size=args.batch_size,
        num_layers=args.layers,
        d_model=args.d_model,
        dff=args.dff,
        num_heads=args.heads,
        dropout_rate=args.dropout,
    ),
    base_dataset_path=args.base_data_path,
    model_dir_path=args.out,
    train_dataset_path=args.train_data,
    valid_dataset_path=args.valid_data,
    enable_wandb=not args.disable_wandb,
)

# Restore latest checkpoint
brain.restore_checkpoint()

# Train
brain.train()
