import re


class TemplateProcessor:
    """Base template processor."""

    def __init__(self):
        # Define template file path
        self.template_file_path = 'target_templates/'

        # Map of delineator regexes to template tags
        self.delineator_map = {}

        # Default map for tags to replacement content (used for reset)
        self.default_tag_content = {}

        # Current map for tags to replacement content
        self.tag_content = {}

        # Current tag
        self.current_tag = ''

        # Tag to be set as current on the next line
        self.next_tag = None

    def reset(self):
        """Reset state."""

        self.delineator_map = {}
        self.default_tag_content = {}
        self.tag_content = {}
        self.current_tag = ''
        self.next_tag = None

    def update(self, line: str):
        """
        Update template state. Should be ran for each translated line.

        :param line: Translated line. **Assumed to be stripped of whitespace.**
        """

        # Add line to state for current tag
        self.tag_content[self.current_tag].append(line)

    def update_delineator(self, src_line: str, indent: int):
        """
        Update template delineator state. Should be ran for each original source line pre-translation.

        :param src_line: Original source line (before masking). **Assumed to be stripped of whitespace.**
        :param indent: Indentation length of the original source line.
        """

        # Check for deferred tag
        if self.next_tag is not None:
            self.current_tag = self.next_tag
            self.next_tag = None

        # Check if line is a delineator
        for regex, tag in self.delineator_map.items():
            if re.match(regex, src_line) is not None:
                self.current_tag = tag
                break

    def build(self) -> str:
        """
        Build template string from state.

        :returns: Template string.
        """

        # Read template file
        template_contents = open(self.template_file_path).read()

        # Replace tags with content
        for tag, content in self.tag_content.items():
            # Remove empty strings from content
            while '' in content:
                content.remove('')

            # Replace tag with content
            content_str = '\n'.join(content)
            template_contents = template_contents.replace(
                f'<{tag}>', content_str)

        return template_contents

    def reset(self):
        """Reset state."""

        self.tag_content = self.default_tag_content.copy()
        self.current_tag = list(self.delineator_map.values())[0]

    def defer_current_tag(self):
        """Defer current tag to next line."""

        self.next_tag = self.current_tag
