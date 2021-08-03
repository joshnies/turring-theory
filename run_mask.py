import argparse
from os import path
from yaspin import yaspin

from theory.lvp import LVP
from theory.veil import Veil

# Get command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--lvp', help='Language-version pair', required=True)
parser.add_argument('-f', '--file', help='Path to source code file', required=True)
args = parser.parse_args()

# Get LVP from args
try:
    lvp = LVP[args.lvp.upper()]
except Exception:
    raise Exception(f'Unknown language-version pair "{args.lvp}".')

# Create output file writer
out_filename = path.join(path.dirname(args.file), f'MASKED_{path.basename(args.file)}.txt')
out_file = open(out_filename, 'w')

# Mask file
veil = Veil(lvp)
with yaspin(text='Masking...', color='magenta'):
    lines = veil.mask(file_path=args.file)

print('✅ Masked')

# Write masked lines to output file
with yaspin(text='Writing to output file...', color='magenta'):
    out_file.writelines(map(lambda l: f'{l}\n', lines))

print(f'✅ Output to "{args.file}"')
