import logging
import re

from cli import log
from theory.lvp import LVP


class DependencyGenerator:
    """Dependency generator."""

    @staticmethod
    def generate(lvp: LVP, file_path: str):
        """
        Generate and add dependencies to the top of a file.

        :param lvp: LVP.
        :param file_path: File path.
        """

        if lvp == LVP.CPP_17_TO_NODEJS_14 or lvp == LVP.JAVA_14_TO_NODEJS_14:
            return DependencyGenerator.__generate_nodejs(file_path)
        elif lvp == LVP.COBOL_TO_CSHARP_9:
            return DependencyGenerator.__generate_cobol_to_cs(file_path)

        log(f'Unhandled LVP "{lvp.value}" for dependency generation.', level=logging.WARNING)

    @staticmethod
    def __generate_nodejs(file_path: str):
        """Generate dependencies for targeted Node.js LVPs."""

        deps = list()

        # Read file
        with open(file_path) as file:
            file_contents = file.read()

            # native-console
            if re.search(re.compile(r'nativeConsole'), file_contents) is not None:
                deps.append("const nativeConsole = require('native-console');")

        # Skip writing if no dependencies found
        if len(deps) == 0:
            return

        # Add dependencies to text
        with open(file_path, 'w') as file:
            file.write('\n'.join(deps) + f'\n{file_contents}')

    @staticmethod
    def __generate_cobol_to_cs(file_path: str):
        """Generate dependencies for COBOL to C# LVPs."""

        deps = ['using System;']

        # Read file
        with open(file_path) as file:
            file_contents = file.read()

            # System.IO
            if re.search(re.compile(r'FileStream|StreamReader|StreamWriter|FileMode|FileAccess'),
                         file_contents) is not None:
                deps.append("using System.IO;")

            # System.Collections.Generic
            if re.search(re.compile(r'List'), file_contents) is not None:
                deps.append("using System.Collections.Generic;")

            # System.Linq
            if re.search(re.compile(r'Enumerable'), file_contents) is not None:
                deps.append("using System.Linq;")

            # TheoryKitCOBOL
            if re.search(re.compile(r'COBOLFile|COBOLGroup|COBOLUtils|COBOLVar|DatabaseConnection|SQLQueryBuilder'),
                         file_contents) is not None:
                deps.append("using TheoryKitCOBOL;")

        # Skip writing if no dependencies found
        if len(deps) == 0:
            return

        # Add dependencies to text
        with open(file_path, 'w') as file:
            file.write('\n'.join(deps) + f'\n{file_contents}')
