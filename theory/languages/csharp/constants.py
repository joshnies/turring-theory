import re

CSHARP_USELESS_METHOD_REGEX = re.compile(r'public\s+void\s+(?P<name>[a-zA-Z0-9_]+)\(\)\s*{\s*(?:return;)?\s*}')
