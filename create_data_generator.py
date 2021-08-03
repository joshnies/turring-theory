import argparse
import os
import re
from os import path
from yaspin import yaspin

from theory.lvp import LVP
from theory.utils import replace_str_range
from theory.veil import Veil

# Get command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name', help='Generator name', required=True)
parser.add_argument('-t', '--target', help='Target language and/or framework name', required=True)
parser.add_argument('--link', help='Link to original source code repository or storage location (used for annotation)')
parser.add_argument('-l', '--lvp', help='Language-version pair', required=True)
parser.add_argument('-i', '--input', help='Path to input source code file', required=True)
parser.add_argument('--out-dir', help='Path to output directory', default='generated')
parser.add_argument('--out-file', help='Path to generated Python output file', default='generator.py')
args = parser.parse_args()

# Get LVP from args
try:
    lvp = LVP[args.lvp.upper()]
except Exception:
    raise Exception(f'Unknown language-version pair "{args.lvp}".')

# Create output directory if it doesn't exist yet
if not path.exists(args.out_dir):
    os.makedirs(args.out_dir)

# Mask file
veil = Veil(lvp)
with yaspin(text='Masking...', color='magenta'):
    lines = veil.mask(file_path=args.input)
    lines = map(lambda global_line: veil.to_relative(global_line), lines)

# Generate Python data generator items
with yaspin(text='Generating items...', color='magenta'):
    # Read input file
    original_lines = open(args.input).readlines()

    items = list()
    base_indent = ' ' * 12
    inner_item_index = ' ' * 16

    # Generate items
    for i, l in enumerate(lines):
        stripped_line = l.strip()

        # Skip empty strings
        if stripped_line == '':
            continue

        # Generate item
        item_str = f"{base_indent}gen_item(\n{inner_item_index}'{stripped_line}',\n{inner_item_index}f''\n" + \
                   f"{base_indent}),"

        items.append(item_str)

    # Write generated items to Python output file
    items = '\n'.join(items)
    template_contents = open('py_templates/data_generator_template.txt').read()
    template_start_span = re.search(r'<theory_gen_start>', template_contents).span()
    result_contents = replace_str_range(template_contents, items, template_start_span)

    # Replace file details
    result_contents = result_contents.replace('<theory_gen_name>', args.name)
    result_contents = result_contents.replace('<theory_gen_target>', args.target)

    if args.link is not None:
        result_contents = result_contents.replace('<theory_gen_link>', args.link)

    # Write to output Python file
    out_path = path.join(args.out_dir, args.out_file)
    with open(out_path, 'w') as out_file:
        out_file.write(result_contents)

print(f'🎁 Output file to "{out_path}"')
