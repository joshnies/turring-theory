import re

# Standard member scope regex
STD_MEMBER_SCOPE_REGEX = re.compile(r'(?:class|interface)\s+.*')

# Standard variable regex
STD_VAR_REGEX = re.compile(r'^[^(){};]+\s+[^(){};]+;$')

# Standard function regex
STD_FUNC_REGEX = re.compile(r'^[^(){};]+\s+[^(){};]+\(.*\)\s+{$')

# Standard single-line comment regex
STD_SINGLE_COMMENT_REGEX = re.compile(r'\/\/(?P<content>.*)')

# Standard multi-line (block) comment regex
STD_BLOCK_COMMENT_REGEX = re.compile(r'\/\*(?!%mask_\d*%)(?P<content>(?:\*(?!\/)|[^*])*)\*\/', re.DOTALL)

# Standard regex for splitting same-line comments from functional code
STD_COMMENT_SPLIT_REGEX = re.compile(r'(?P<indent>[ \t]*)(?P<other>.+)(?P<comment>(?:\/\/|\/\*).*(?:\*\/)?)')

# Standard comment regex group name
STD_COMMENT_REGEX_GROUP = 'content'

# Standard string regex
STD_STR_REGEX = re.compile(r'["\'`](?!%mask_\d+%)(?P<content>[^"\']*)["\'`]', re.DOTALL)

# Standard masked string regex
STD_MASKED_STR_REGEX = re.compile(r'["\'`]%mask_\d+%["\'`]')
