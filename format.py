import argparse
import os

from theory.lang_utils import get_language_definition
from theory.lvp import LVP

# Get command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--lvp', help='Language-version pair', required=True)
parser.add_argument('-f', '--file', help='Path to source code file', required=True)
parser.add_argument('-t', '--is-target', help="Whether to format the file as the LVP's target language instead",
                    action='store_true', default=False)
parser.add_argument('--cobol-copy-path', help="Default copybooks path for COBOL source LVPs")
args = parser.parse_args()

# Get LVP from args
try:
    lvp = LVP[args.lvp.upper()]
except Exception:
    raise Exception(f'Unknown language-version pair "{args.lvp}".')

# Get language definition for LVP
lang_def = get_language_definition(lvp, is_target=args.is_target)

# Duplicate file
src_contents = open(args.file).read()
os.makedirs('temp', exist_ok=True)
out_file_path = 'temp/formatted.txt'
with open(out_file_path, 'w') as out_file:
    out_file.write(src_contents)

# Run formatter on file
lang_def.format_file(out_file_path, {'cobol_default_copybooks_path': args.cobol_copy_path})
