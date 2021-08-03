import logging

import flask
from flask import request, jsonify
# from kombu.utils.url import safequote
# import boto3
# import progressbar
# from botocore.exceptions import ClientError
# from flask import url_for
# from celery import Celery

from cli import log
from theory.core import Theory
from theory.nn.hyperparams import Hyperparams

from .config import *
from .services.translation import TranslationService

# Initialize flask app
app = flask.Flask(__name__)
app.app_context().push()

# Initialize AWS
# aws_access_key = safequote(AWS_ACCESS_KEY_ID)
# aws_secret_key = safequote(AWS_SECRET_ACCESS_KEY)
# broker_url = f'sqs://{aws_access_key}:{aws_secret_key}@'

# Initialize celery
# celery -A api.app.celery worker --loglevel=debug
# celery = Celery(app.name, broker=broker_url, backend='rpc://')
# celery.conf.update(app.config)

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

    # Run translation task async using celery
    # task = translate_task.apply_async([input_path])

    # return a URL for checking status
    # return jsonify({'status_url': url_for('task_status', task_id=task.id)})

# @celery.task()
# def translate_task(input_path):
#     """Background task that runs the translator."""
#
#     # self.update_state(state='STARTED')
#
#     # Translate file
#     TranslationService.translate(theory, input_path)

# @app.route('/status/<task_id>')
# def task_status(task_id):
#     task = translate_task.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         # job did not start yet
#         response = {
#             'state': task.state,
#             'current': 0,
#             'total': 1,
#             'status': 'Pending...'
#         }
#     elif task.state == 'STARTED':
#         response = {
#             'state': task.state,
#             'status': 'Started...'
#         }
#     elif task.state != 'FAILURE':
#         response = {
#             'state': task.state,
#             'current': task.info.get('current', 0),
#             'total': task.info.get('total', 1),
#             'status': task.info.get('status', '')
#         }
#         if 'result' in task.info:
#             response['result'] = task.info['result']
#     else:
#         # something went wrong in the background job
#         response = {
#             'state': task.state,
#             'current': 1,
#             'total': 1,
#             'status': str(task.info),  # this is the exception raised
#         }
#
#     return jsonify(response)
