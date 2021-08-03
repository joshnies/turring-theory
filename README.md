# Turring Theory

Source code translator using the power of deep learning.

## Environment

Create a new `.env` file in the root project directory with the following dotenv schema:

```text
# ---------------------------------------
# Theory API
# ---------------------------------------
#
# Debug mode (verbose output)
DEBUG=1
# Language-version pair this API instance is dedicated to
LVP=cobol_to_csharp_9
# Output directory path containing saved checkpoints and tokenizer vocabularies
OUTPUT_DIR=output
# Training dataset path
TRAIN_DATASET_PATH=data/cobol_to_csharp_9_train.csv
# Validation dataset path
VALID_DATASET_PATH=data/cobol_to_csharp_9_valid.csv

# ---------------------------------------
# Theory neural network hyperparameters
# ---------------------------------------
#
# Buffer size
BUFFER_SIZE=20000
# Batch size
BATCH_SIZE=256
# Number of layers
NUM_LAYERS=6
# Model dimensionality
D_MODEL=512
# Dense feed-forward neural network units/neurons
DFF=2048
# Number of attention heads
NUM_HEADS=8
# Dropout rate
DROPOUT_RATE=0.1

# ---------------------------------------
# AWS
# ---------------------------------------
#
# Access key ID
AWS_ACCESS_KEY_ID=
# Secret access key
AWS_SECRET_ACCESS_KEY=
# S3 bucket name
AWS_STORAGE_BUCKET_NAME=
```

## Train neural network

```shell
python train.py \
  # * Saved model and checkpoint directory
  --out="output"
  # * LVP name
  --lvp=cobol_to_csharp_9
  # Training dataset path
  --train-data="data/train.csv"
  # Validation dataset path
  --valid-data="data/valid.csv"
  # Epochs
  --epochs=1000
  # Buffer size
  --buffer-size=20000
  # Batch size
  --batch-size=256
  # Number of layers
  --layers=6
  # Model dimensionality
  --d-model=512
  # Dense forward-feed network size (units/neurons)
  --dff=2048
  # Number of attention heads
  --heads=8
  # Dropout rate
  --dropout=0.1
  # Whether to enable Weights & Biases (wandb) integration
  # See here for more info: https://docs.wandb.ai/quickstart
  --wandb=True

# * = optional
```

## Run API

```shell
python run_api.py
```

For endpoint documentation, please see the Postman collection.

## Helper scripts

### Mask file

This script masks a given file and outputs it as `MASKED_<name>` in the same directory.

```shell
python run_mask.py \
  # Language-version pair
  --lvp cobol_to_csharp_9 \
  # Source file path
  --file="path/to/file.cs"
```

### Generate case data

This script masks a file and creates a data generator with all unique lines (for use with theory_data_gen).

```shell
python create_data_generator.py \
  # Language-version pair
  --lvp cobol_to_csharp_9 \
  # Source file path
  --file="path/to/file.cs" \
  # Source code repo or project name
  --name="author/name" \
  # Target name (added to comments in output file)
  --target="C# 9"
```

---

Copyright © 2021 Autumn Labs, Inc. All Rights Reserved.
