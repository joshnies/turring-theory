import os
from dotenv import load_dotenv

from theory.lvp import LVP

# Get environment config
load_dotenv()
__debug = os.environ.get('DEBUG')
DEBUG = bool(int(__debug)) if __debug is not None else False

# Neural network
MODEL_DIR = 'model'
TRAIN_DATASET_PATH = os.environ.get('TRAIN_DATASET_PATH')
VALID_DATASET_PATH = os.environ.get('VALID_DATASET_PATH')
DATA_MAP_PATH = os.environ.get('DATA_MAP_PATH')
BUFFER_SIZE = int(os.environ.get('BUFFER_SIZE'))
BATCH_SIZE = int(os.environ.get('BATCH_SIZE'))
NUM_LAYERS = int(os.environ.get('NUM_LAYERS'))
D_MODEL = int(os.environ.get('D_MODEL'))
DFF = int(os.environ.get('DFF'))
NUM_HEADS = int(os.environ.get('NUM_HEADS'))
DROPOUT_RATE = float(os.environ.get('DROPOUT_RATE'))

# AWS
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

# Get LVP
__lvp_name = os.environ.get('LVP')
try:
    CURRENT_LVP = LVP[__lvp_name.upper()]
except Exception:
    raise Exception(f'Unknown language-version pair "{__lvp_name}".')
