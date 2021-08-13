import logging
import flask
from flask import request, jsonify

from cli import log
from theory.core import Theory
from theory.nn.hyperparams import Hyperparams

from .config import *
from .services.translation import TranslationService

# Initialize flask app
app = flask.Flask(__name__)
app.app_context().push()

# Initialize Theory
theory = Theory(
    CURRENT_LVP,
    Hyperparams(
        epochs=1,  # arbitrary for non-training envs
        buffer_size=BUFFER_SIZE,
        batch_size=BATCH_SIZE,
        num_layers=NUM_LAYERS,
        d_model=D_MODEL,
        dff=DFF,
        num_heads=NUM_HEADS,
        dropout_rate=DROPOUT_RATE
    ),
    output_dir_path=OUTPUT_DIR,
    train_dataset_path=TRAIN_DATASET_PATH,
    valid_dataset_path=VALID_DATASET_PATH,
    data_map_path=DATA_MAP_PATH,
    debug=DEBUG
)

# Restore latest checkpoint
theory.restore()

if DEBUG:
    log('DEBUG MODE ACTIVE', level=logging.WARNING)

log('🚀 API ready.\n')


@app.route('/translate', methods=['POST'])
def translate():
    """
    Translate a directory or file.

    Data schema:
        input_path*: Relative path to the input (source) file or folder in the S3 bucket.
        cobol_default_copybook_path: [COBOL Sources Only] Relative path to the folder in S3 containing the relevant copybook
            input files.
        cobol_copybook_ext: [COBOL Sources Only] Copybook file extension.

        * = required
    """

    data = request.json
    input_path = data['input_path']

    # Run translation
    output_path = TranslationService.translate(theory, input_path, data)
    return jsonify({'output_path': output_path})
