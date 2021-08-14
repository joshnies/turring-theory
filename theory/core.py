from os import path
import logging
from typing import Optional, List
from tqdm.contrib import tenumerate

from api.config import DEBUG
from cli import log
from .lvps.base_mtl import MTL
from .lvps.cobol_to_csharp_9.mtl import COBOLToCSharp9MTL
from .nn.brain import Brain
from .nn.hyperparams import Hyperparams
from theory.lvps.base_itl import ITL
from .languages.constants import lvp_tar_file_extension_map
from .lvp import LVP
from .lvps.base_store import Store
from .lvps.base_template_processor import TemplateProcessor
from .lvps.cobol_to_csharp_9.itl import COBOLToCSharp9ITL
from .lvps.cobol_to_csharp_9.template_processor import COBOLToCSharp9TemplateProcessor
from .lvps.cobol_to_csharp_9.postprocessor import COBOLToCSharp9Postprocessor
from .lvps.cobol_to_csharp_9.store import COBOLToCSharp9Store
from .lvps.cpp_17_to_nodejs_14.itl import CPP17ToNodeJS14ITL
from .lvps.java_14_to_nodejs_14.itl import Java14ToNodeJS14ITL
from .lvps.java_14_to_python_3.itl import Java14ToPython3ITL
from .utils import log_translation
from .veil import Veil
from .lvps.base_postprocessor import Postprocessor
from .dependency_generator import DependencyGenerator
from .lang_utils import get_language_definition


class Theory:
    """Theory core."""

    def __init__(
        self,
        lvp: LVP,
        hyperparams: Hyperparams,
        output_dir_path: str,
        base_dataset_path: str = 'data',
        train_dataset_path: str = None,
        valid_dataset_path: str = None,
        data_map_path: str = None,
        debug: bool = False,
    ):
        """
        :param lvp: LVP for translation.
        :param hyperparams: Hyperparameters of the transformer model.
        :param output_dir_path: Path to output directory for the saved model and
            checkpoints.
        :param base_dataset_path: Base dataset path.
        :param train_dataset_path: Training dataset path.
        :param valid_dataset_path: Validation dataset path.
        :param data_map_path: Data map path.
        :param debug: Whether to enable debug mode.
        """

        self.debug = debug
        self.lvp = lvp
        self.train_dataset_path = \
            path.join(base_dataset_path,
                      f'{lvp.value.lower()}_train.csv') if train_dataset_path is None else train_dataset_path
        self.valid_dataset_path = \
            path.join(base_dataset_path,
                      f'{lvp.value.lower()}_valid.csv') if valid_dataset_path is None else valid_dataset_path
        self.data_map_path = \
            path.join(
                base_dataset_path, f'{lvp.value.lower()}_map.csv') if data_map_path is None else data_map_path

        self.case_name = path.basename(self.train_dataset_path).replace(
            '.csv', '').replace('_train', '')
        self.output_dir_path = path.join(output_dir_path, self.case_name)

        # Initialize brain
        self.brain = Brain(
            lvp,
            hyperparams,
            self.output_dir_path,
            train_dataset_path=self.train_dataset_path,
            valid_dataset_path=self.valid_dataset_path,
            debug=debug,
        )

        # Initialize Veil
        self.veil = Veil(self.lvp)

        # Initialize template processor
        self.template_processor = self.__get_template_processor(self.lvp)
        self.has_template_processor = self.template_processor is not None

        # Initialize store
        self.store = self.__get_store()
        self.has_store = self.store is not None

        # Initialize ITL (Immediate Translation Layer)
        self.itl = self.__get_itl()

        # Initialize MTL (Macro Translation Layer)
        self.mtl = self.__get_mtl()
        self.has_mtl = self.mtl is not None

        # Initialize post-processor
        self.postprocessor = self.__get_postprocessor()

        # Get language definitions
        self.src_lang_def = get_language_definition(lvp, is_target=False)
        self.tar_lang_def = get_language_definition(lvp, is_target=True)

    def restore(self):
        """Restore brain's latest checkpoint."""

        self.brain.restore_checkpoint()

    def translate(self, input_file_path: str, output_file_path: str = None, request_data=None):
        """
        Translate input file.

        :param input_file_path: Path to input source code file to translate.
        :param output_file_path: Path to output source code file to translate.
            If `None`, the translated text will be returned.
        :param request_data: Request body data from "/translate" API endpoint.
        :returns: Translated text if `output_file_path` is specified, otherwise
            `None`.
        """

        rel_input_file_path = input_file_path[12:]

        # Clear states
        self.veil.reset()
        self.template_processor.reset()
        self.store.reset()
        self.itl.reset()

        # Scan masked file contents to build initial store
        log('Scanning file...')
        self.store.scan(input_file_path)
        log('Scan successful.')

        # Pre-format file
        log('Formatting...')
        input_lines = self.src_lang_def.format_file(
            input_file_path, request_data=request_data)
        log('Formatting successful.')
        formatted_file_contents = '\n'.join(input_lines)

        # Output formatted input file if debug mode
        if DEBUG:
            open('temp/formatted.txt', 'w').write(formatted_file_contents)

        # Preprocess file contents and save to memory
        masked_lines = self.veil.mask(
            text=formatted_file_contents, request_data=request_data)
        masked_file_contents = '\n'.join(masked_lines)

        # Log warning if line counts don't match
        if len(masked_lines) != len(input_lines):
            log(
                'Masked line count does not match input line count. ' +
                f'Input: {len(input_lines)}, Masked: {len(masked_lines)}',
                level=logging.WARNING
            )

        # Output masked input file if debug mode
        if DEBUG:
            open('temp/masked.txt', 'w').write(masked_file_contents)

        # Run MTL
        if self.has_mtl:
            masked_lines = self.mtl.translate_all(
                masked_file_contents).splitlines()

        # Log warning if line counts don't match
        if len(masked_lines) != len(input_lines):
            log(
                'Post-MTL masked line count does not match input line count. ' +
                f'Input: {len(input_lines)}, Masked: {len(masked_lines)}',
                level=logging.WARNING
            )

        # Output masked input after MTL file if debug mode
        if DEBUG:
            open('temp/masked_w_mtl.txt', 'w').write('\n'.join(masked_lines))

        output_lines = list()
        can_write = output_file_path is not None

        # Open/create output file for writing
        writer = open(output_file_path, 'w',
                      newline='') if output_file_path is not None else None

        incorrect_translation_count = 0

        # Translate masked lines
        serialized_file_path = "/".join(rel_input_file_path.split("/")[1:])
        translation_desc = f'Translating: {serialized_file_path}'
        for i, line in tenumerate(masked_lines, desc=translation_desc):
            input_line = input_lines[i].strip()
            input_line_indent = len(
                input_lines[i]) - len(input_lines[i].lstrip())
            line_indent = len(line) - len(line.lstrip())
            line = line.strip()

            # Skip empty lines
            if line == '':
                if not self.has_template_processor:
                    if can_write:
                        writer.write('\n')
                    else:
                        output_lines.append('\n')
                continue

            log('=' * 80, level=logging.DEBUG)
            log(f'- Line: {i + 1}', level=logging.DEBUG)

            try:
                # Replace global mask tokens with relative versions
                line = self.veil.to_relative(line)

                # Update template processor delineator state
                if self.has_template_processor:
                    self.template_processor.update_delineator(
                        input_line, input_line_indent)

                # Update store
                if self.has_store:
                    self.store.update(input_line)

                # Send line through the Immediate Translation Layer (ITL)
                translated = self.itl.translate(line, line_indent)

                if translated is None:
                    # Try to translate line with map
                    translated = self.itl.map(line)

                    # Translate line via neural network if ITL had no available
                    # translation
                    if translated is None:
                        translated = self.brain.translate(line)
                        log_translation('NN', line, translated)
                    else:
                        log_translation('ITL (Map)', line, translated)
                else:
                    log_translation('ITL (Algorithm)', line, translated)

                # Skip further processing if translated to empty string
                if translated:
                    # Post-process translated line
                    translated = self.postprocessor.postprocess_line(
                        translated)

                    # Replace relative mask tokens with global versions
                    translated = self.veil.from_relative(translated)

                    # Unmask line
                    translated = self.veil.unmask(translated)

                # Update store with translated sequence (if required)
                if self.has_store:
                    self.store.post_translation_hook(translated)
            except Exception as e:
                src_line = input_lines[i].strip('\n').strip()

                if DEBUG:
                    log(f'Failed to translate:', level=logging.WARNING)
                    log(f'\tMasked: {line}', level=logging.WARNING)
                    log(f'\tSource: {src_line}', level=logging.WARNING)
                    log(f'Error:', level=logging.WARNING)
                    log(e, level=logging.WARNING)

                commented_inp_line = self.tar_lang_def.to_single_line_comment(
                    src_line)
                err_comment = self.tar_lang_def.to_single_line_comment(
                    f'[Turring Theory] ERROR: Failed to translate.')
                translated = f'{commented_inp_line}\t{err_comment}'
                incorrect_translation_count += 1

            if self.has_template_processor:
                # Update template processor sequence state
                self.template_processor.update(translated)
            elif can_write:
                # Output line to output file
                writer.write(translated + '\n')
            else:
                # Save output line
                output_lines.append(translated)

            log('=' * 80 + '\n', level=logging.DEBUG)

        # Build template (if applicable)
        if self.has_template_processor:
            result = self.template_processor.build()
            result = self.postprocessor.postprocess_file(result)
            writer.write(result)
        elif can_write:
            # TODO: Postprocess file if can write and has no template processor
            pass
        else:
            # TODO: Postprocess file contents if cannot write and has no template processor
            pass

        writer.close()

        # Generate dependencies
        DependencyGenerator.generate(self.lvp, output_file_path)

        # Post-format file
        self.tar_lang_def.format_file(output_file_path)

        log(f'🎉 Successfully translated "{serialized_file_path}".')

        # Output neural network accuracy
        nn_accuracy = (len(masked_lines) -
                       incorrect_translation_count) / len(masked_lines) * 100
        log('📈 Estimated accuracy: {:.4f}%\n'.format(nn_accuracy))

        return '\n'.join(output_lines)

    def translate_direct(
        self,
        line: str,
        from_relative: bool = True,
        unmask: bool = True,
    ) -> str:
        """
        Translate line without keeping state.

        :param line: Source line to translate. **Assumed to be relatively masked.**
        :param from_relative: Whether to return the globally-masked translated line.
        :param unmask: Whether to unmask the translated line.
        :returns: Translated line.
        """

        # Try ITL translation
        translated_line = self.itl.translate(line)

        if translated_line is None:
            # Try map-based translation
            translated_line = self.itl.map(line)

            if translated_line is None:
                # Translate using neural network
                translated_line = self.brain.translate(line)

        translated_line = self.postprocessor.postprocess_line(translated_line)

        if from_relative:
            translated_line = self.veil.from_relative(translated_line)

        if unmask:
            translated_line = self.veil.unmask(translated_line)

        return translated_line

    def create_project_files(
        self,
        project_path: str,
        added_file_paths: List[str],
    ) -> str:
        """
        Create project files.

        :param project_path: Project path.
        :param added_file_paths: List of paths for files to add to project.
        :returns: Project path.
        """

        return self.tar_lang_def.create_project_files(
            project_path,
            added_file_paths,
        )

    def get_target_file_extension(self) -> str:
        """
        Get target file extension for current LVP.

        :returns: File extension.
        """

        try:
            return lvp_tar_file_extension_map[self.lvp]
        except:
            raise Exception(
                f'No target file extension mapping for LVP "{self.lvp.value}".')

    @staticmethod
    def __get_template_processor(lvp) -> Optional[TemplateProcessor]:
        """
        Get a template processor instance for the current LVP if available.

        :returns: Template processor instance.
        """
        if lvp == LVP.COBOL_TO_CSHARP_9:
            return COBOLToCSharp9TemplateProcessor()

        return None

    def __get_itl(self) -> ITL:
        """
        Get a Immediate Translation Layer (ITL) instance for the current LVP.

        :returns: ITL instance.
        """

        if self.lvp == LVP.COBOL_TO_CSHARP_9:
            lvp_class = COBOLToCSharp9ITL
        elif self.lvp == LVP.CPP_17_TO_NODEJS_14:
            lvp_class = CPP17ToNodeJS14ITL
        elif self.lvp == LVP.JAVA_14_TO_NODEJS_14:
            lvp_class = Java14ToNodeJS14ITL
        elif self.lvp == LVP.JAVA_14_TO_PYTHON_3:
            lvp_class = Java14ToPython3ITL
        else:
            raise Exception(f'No ITL found for LVP "{self.lvp}".')

        return lvp_class(
            self.data_map_path,
            self.veil,
            self.store,
            self.template_processor,
            self.translate_direct,
        )

    def __get_mtl(self) -> Optional[MTL]:
        """
        Get a Macro Translation Layer (MTL) instance for the current LVP.

        :returns: MTL instance.
        """

        if self.lvp == LVP.COBOL_TO_CSHARP_9:
            return COBOLToCSharp9MTL(self.itl, self.veil)

        raise None

    def __get_store(self) -> Optional[Store]:
        """
        Get a store instance for the current LVP if available.

        :returns: Store instance.
        """

        if self.lvp == LVP.COBOL_TO_CSHARP_9:
            return COBOLToCSharp9Store(self.template_processor, self.veil)

        return None

    def __get_postprocessor(self) -> Optional[Postprocessor]:
        """
        Get postprocessor instance for the current LVP.

        :returns: Postprocessor instance.
        """

        if self.lvp == LVP.COBOL_TO_CSHARP_9:
            return COBOLToCSharp9Postprocessor(self.itl)

        return Postprocessor()
