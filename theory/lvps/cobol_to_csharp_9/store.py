import json
import re
from benedict import benedict

from api.config import DEBUG
from .template_processor import TEMPL_MEMBER_VAR_ASSIGNMENTS, TEMPL_MEMBER_VARS, TEMPL_MEMBER_FUNCS
from ..base_store import Store
from ..base_template_processor import TemplateProcessor
from ...languages.cobol.constants import COBOL_GROUP_ITEM_REGEX, COBOL_ELEM_ITEM_REGEX, COBOL_RESERVED_TOKENS
from ...languages.cobol.definition import CobolDefinition
from ...veil import Veil

GROUP_ITEM_SCOPE = 'GROUP_ITEM_SCOPE'


class COBOLToCSharp9Store(Store):
    """State storage for COBOL to C# 9."""

    def __init__(self, template_processor: TemplateProcessor, veil: Veil):
        """
        :param template_processor: Template processor.
        """

        self.template_processor = template_processor
        self.veil = veil
        self.method_names = list()
        self.file_data_map = dict()

        self.layout = benedict()
        self.is_layout_built = False
        self.current_layout_keypath = ''
        self.current_layout_level = 1
        self.last_item_name = None
        self.deferred_last_item_name = None
        self.__member_var_defs = list()
        self.__member_var_assignments = list()
        self.__deferred_translation = None
        self.__last_layout_item_built_was_root = False

    def scan(self, file_path: str):
        for src_line in open(file_path):
            line = src_line[6:72]
            # Build function list/order
            # Get regex match, stripping right whitespace to implicitly validate indent
            match = re.match(r'^\s(?P<name>[0-9a-zA-Z\-:]+)(?:\s+SECTION)?\.(?:\s+EXIT\.)?$', line.rstrip())

            if match is not None:
                name = match.group('name')
                if name not in COBOL_RESERVED_TOKENS:
                    name = CobolDefinition.name_to_title_case(name)
                    self.method_names.append(name)

                continue

    def update(self, line: str):
        """
        Update state.

        :param line: Original source line. **Assumed to be stripped of whitespace.**
        """

        # Update layout
        if self.template_processor.current_tag == TEMPL_MEMBER_VAR_ASSIGNMENTS:
            # if re.match(COBOL_CUSTOM_SECTION_REGEX, line) is None:
            group_match = re.match(COBOL_GROUP_ITEM_REGEX, line)
            if group_match is not None:
                # Add new group to layout
                level = int(group_match.group('lvl'))
                name = CobolDefinition.name_to_title_case(group_match.group('name'))

                if level == 1:
                    self.current_layout_keypath = ''
                elif level < self.current_layout_level:
                    self.__up_keypath()

                # Update current level
                self.current_layout_level = level

                # Traverse down the keypath, adding depth
                self.__down_keypath(name)
                # Defer setting "last item name" until after translation, since the current "last item name"
                # is still expected within the ITL.
                self.deferred_last_item_name = name
            else:
                # Add child to current group (if any)
                var_match = re.match(COBOL_ELEM_ITEM_REGEX, line)
                if var_match is not None:
                    level = int(var_match.group('lvl'))
                    name = CobolDefinition.name_to_title_case(var_match.group('name'))

                    if level != 88:
                        if level == 1:
                            self.current_layout_keypath = ''
                        elif level < self.current_layout_level:
                            self.__up_keypath()

                        # Update current level
                        self.current_layout_level = level

                    # Defer adding item to layout until it's been translated
                    self.__deferred_translation = name
                    # Defer setting "last item name" until after translation, since the current "last item name"
                    # is still expected within the ITL.
                    self.deferred_last_item_name = name
        elif self.template_processor.current_tag == TEMPL_MEMBER_FUNCS and not self.is_layout_built:
            # Build layout when done
            self.__build_layout()

    def post_translation_hook(self, seq: str):
        # Add translated item to layout
        if self.__deferred_translation is not None:
            self.__add_to_layout(self.__deferred_translation, seq)
            self.__deferred_translation = None

        # Set last item name
        self.last_item_name = self.deferred_last_item_name

    def __down_keypath(self, keypath: str):
        """
        Move down in the keypath.

        :param keypath: Appended keypath.
        """

        self.current_layout_keypath += '' if self.current_layout_keypath == '' else '.'
        self.current_layout_keypath += keypath
        self.layout[self.current_layout_keypath] = dict()

    def __up_keypath(self):
        """Move up in the keypath."""

        # Remove last key from path
        self.current_layout_keypath = '.'.join(self.current_layout_keypath.split('.')[:-1])

    def __add_to_layout(self, key: str, val):
        """
        Add key-value pair to layout.

        :param key: Key.
        :param val: Value.
        """

        keypath = '.'.join([self.current_layout_keypath, key]).strip('.')
        self.layout[keypath] = val

    def __build_layout(self):
        """Build target layout."""

        if DEBUG:
            json_layout = json.dumps(self.layout, indent=4)
            open('temp/layout.json', 'w').write(json_layout)

        # Build layout
        for key in self.layout.keys():
            self.__build_layout_item(key)

        self.template_processor.tag_content[TEMPL_MEMBER_VARS] = self.__member_var_defs
        self.template_processor.tag_content[TEMPL_MEMBER_VAR_ASSIGNMENTS] = self.__member_var_assignments
        self.is_layout_built = True

    def __build_layout_item(self, key: str, trailing_path: str = None):
        keypath = f'{trailing_path}.{key}' if trailing_path is not None else key
        val = self.layout[keypath]
        is_root = keypath == key
        is_var = type(val) is str

        # Add region start before root group
        if is_root and not is_var:
            newline = '\n' if self.__last_layout_item_built_was_root else ''
            region_start = f'{newline}#region {key}'
            self.__member_var_defs.append(region_start)
            self.__member_var_assignments.append(region_start)

        self.__last_layout_item_built_was_root = is_root

        if is_var:
            # Is COBOLVar
            self.__member_var_defs.append(f'private COBOLVar {key};')
            self.__member_var_assignments.append(self.layout[keypath])
            return

        # Is COBOLGroup
        child_keys = val.keys()
        direct_children = ',\n\t'.join(list(child_keys))
        for child in child_keys:
            self.__build_layout_item(child, trailing_path=keypath)

        region_end = '\n#endregion\n' if is_root else '\n'
        self.__member_var_defs.append(f'private COBOLGroup {key};{region_end}')
        self.__member_var_assignments.append(f'{key} = new COBOLGroup(\n\t{direct_children}\n);{region_end}')
