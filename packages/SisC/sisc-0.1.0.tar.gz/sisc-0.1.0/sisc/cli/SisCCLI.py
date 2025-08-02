import errno
import json
import logging
import multiprocessing
import os
import statistics
import sys
from argparse import ArgumentParser, Action, BooleanOptionalAction
from os import listdir
from os.path import splitext, basename, join, isfile, isdir, exists
from typing import Optional, Any, List
from lxml import etree

import sisc.core.SisC as SisC
import sisc.util.Defaults as Defaults
from sisc.alignment.BaseFileAligner import BaseFileAligner
from sisc.alignment.JsonAligner import JsonAligner
from sisc.alignment.TxtAligner import TxtAligner
from sisc.alignment.TeiXmlAligner import TeiXmlAligner
from sisc.cli.NotSupportedException import NotSupportedException
from sisc.cli.AlignException import AlignException
from sisc.eval import Evaluation
from sisc.fingerprint.TextFingerprinter import TextFingerprinter
from sisc.fingerprint.TeiXmlFingerprinter import TeiXmlFingerprinter
from sisc.mask.ContextMasker import ContextMasker
from sisc.mask.UniformMasker import UniformMasker

from shutil import which

from sisc.pdf.TesseractException import TesseractException
from sisc.pdf.TesseractExtractor import TesseractExtractor

logger = logging.getLogger(__name__)


class OptionValueCheckAction(Action):

    def __call__(self, parser, namespace, values, option_string=None):

        if option_string == '--max-num-processes':
            if int(values) <= 0:
                parser.error('{0} must be greater 0'.format(option_string))

        setattr(namespace, self.dest, values)


def __run_eval(eval_type: str, file_1_path: str, file_2_path: str, include_tags: List[str]=None, exclude_tags: List[str]=None):
    average_distances = []

    if isfile(file_1_path) and isfile(file_2_path):
        filename = splitext(basename(file_1_path))[0]
        average_levenshtein = __eval_file(filename, eval_type, file_1_path, file_2_path, include_tags, exclude_tags)
        logging.info(f'Average: {average_levenshtein:.3f}')
    elif isdir(file_1_path) and isdir(file_2_path):
        for file_or_folder in listdir(file_1_path):
            full_path = join(file_1_path, file_or_folder)
            filename = splitext(basename(full_path))[0]

            if isfile(full_path):
                full_path_2 = join(file_2_path, f'{filename}_aligned.xml')

                if exists(full_path_2):
                    average_levenshtein = __eval_file(filename, eval_type, full_path, full_path_2, include_tags,
                                                      exclude_tags)
                    average_distances.append(average_levenshtein)

        logging.info(f'\n\nOverall average: {statistics.mean(average_distances):.3f}')


def __eval_file(filename: str, eval_type: str, file_1_path: str, file_2_path: str, include_tags: List[str],
                exclude_tags: List[str]):

    # TODO: handle all cases properly
    if eval_type == 'txt':
        with open(file_1_path, 'r', encoding='utf-8') as text_file:
            text_1 = text_file.read()

        with open(file_2_path, 'r', encoding='utf-8') as text_file:
            text_2 = text_file.read()

        Evaluation.eval_txt(text_1, text_2)
        return 0
    elif eval_type == 'xml':
        element_tree_1 = etree.parse(file_1_path)
        element_tree_2 = etree.parse(file_2_path)
        average_levenshtein = Evaluation.eval_xml(filename, element_tree_1, element_tree_2, include_tags, exclude_tags)
        return average_levenshtein
    elif eval_type == 'json':
        return 0

    return 0


def __align_file(input_path: str, fingerprint_path: str, annotation_path: str, output_path: str, key_to_update,
                 first_page, last_page, max_text_length, lang, tess_path, poppler_path, remove_gap_min_length) -> None:

    filename = splitext(basename(input_path))[0]
    logger.info(f'Aligning file {filename}')

    _, input_file_ext = splitext(input_path)

    if input_file_ext == '.txt':
        with open(input_path, 'r', encoding='utf-8') as text_file:
            text = text_file.read()
    elif input_file_ext == '.pdf':
        extractor = TesseractExtractor(tess_path, poppler_path)
        text = extractor.extract(input_path, lang, first_page, last_page)
    else:
        return

    fingerprint: Optional[str] = None
    fingerprint_ext = splitext(fingerprint_path)[1]

    input_content: Any
    aligner: Optional[BaseFileAligner] = None

    if fingerprint_ext == '.txt':
        with open(fingerprint_path, 'r', encoding='utf-8') as fingerprint_file:
            fingerprint = fingerprint_file.read()
    elif fingerprint_ext == '.xml':
        input_content = etree.parse(fingerprint_path)
        aligner = TeiXmlAligner(remove_gap_min_length)
        root = input_content.getroot()
        fingerprint_node = root.find(f'.//{{*}}standOff')

        if fingerprint_node is not None:
            fingerprint = fingerprint_node.text
            root.remove(fingerprint_node)
    else:
        return

    if not fingerprint:
        logger.error(f'Could not load fingerprint')
        return

    if annotation_path:
        annotation_ext = splitext(annotation_path)[1]

        if annotation_ext == '.json':
            with open(annotation_path, 'r', encoding='utf-8') as anno_file:
                json_input = anno_file.read()
            input_content = json.loads(json_input)
            aligner = JsonAligner(key_to_update)
        elif annotation_ext == '.txt':
            with open(annotation_path, 'r', encoding='utf-8') as anno_file:
                input_content = anno_file.read()
            aligner = TxtAligner()
        else:
            logger.error(f'Unexpected annotation format: {annotation_ext}')
            return

    # TODO: Need to make sure that input_content is specified for txt and json

    try:
        al1, al2 = SisC.align_text(input_content, text, fingerprint, aligner, max_text_length=max_text_length)
    except AlignException as e:
        logger.error(f'Could not align {filename}. Reason: {e.reason}')
        return

    with open(join(output_path, f'{filename}_aligned_content.txt'), 'w', encoding='utf-8') as out_file:
        out_file.write(al1)

    if al2 and fingerprint_ext == '.xml':
        with open(join(output_path, f'{filename}_aligned.xml'), 'wb') as out_file:
            al2.write(out_file, encoding='utf-8', xml_declaration=True)
    elif al2 and annotation_path:
        annotation_ext = splitext(annotation_path)[1]

        if annotation_ext == '.txt':
            with open(join(output_path, f'{filename}_aligned_text.txt'), 'w', encoding='utf-8') as out_file:
                out_file.write(al2)
        elif annotation_ext == '.json':
            with open(join(output_path, f'{filename}_aligned.json'), 'w', encoding='utf-8') as out_file:
                out_file.write(json.dumps(al2))


def __fingerprint_xml(xml_file_path: str, output_path: str, fingerprint_type: str, symbol: str, move_notes: bool,
                      add_quotation_marks: bool, distance: int, keep_count: int, context_size: int, keep_tag: str,
                      keep_text: bool, root_tag: str, keep_space_only: bool):
    filename = splitext(basename(xml_file_path))[0]
    element_tree = etree.parse(xml_file_path)

    if fingerprint_type == 'uniform':
        masker = UniformMasker(symbol=symbol, keep_count=keep_count, distance=distance, keep_space_only=keep_space_only)
    elif fingerprint_type == 'context':
        masker = ContextMasker(symbol=symbol, context_size=context_size, keep_text=keep_text)
    else:
        logger.fatal(f'Unknown fingerprint type: {fingerprint_type}')
        return

    fingerprinter = TeiXmlFingerprinter(masker, move_notes=move_notes, add_quotation_marks=add_quotation_marks,
                                        keep_tag=keep_tag, root_tag=root_tag)
    element_tree = fingerprinter.fingerprint(element_tree)

    with open(join(output_path, f'{filename}_fingerprint.xml'), 'wb') as out_file:
        element_tree.write(out_file, encoding='utf-8', xml_declaration=False)


def __fingerprint_txt(text_file_path: str, output_path: str, fingerprint_type: str, symbol:str, distance: int,
                      keep_count: int) -> None:
    filename = splitext(basename(text_file_path))[0]
    with open(text_file_path, 'r', encoding='utf-8') as text_file:
        text_1 = text_file.read()

    if fingerprint_type == 'uniform':
        masker = UniformMasker(symbol=symbol, keep_count=keep_count, distance=distance)
    elif fingerprint_type == 'context':
        logger.error(f'Fingerprint type {fingerprint_type} is not supported for Txt files.')
        return
    else:
        logger.error(f'Unknown fingerprint type: {fingerprint_type}')
        return

    fingerprinter = TextFingerprinter(masker)
    fingerprint = fingerprinter.fingerprint(text_1)

    with open(join(output_path, f'{filename}_fingerprint.txt'), 'w', encoding='utf-8') as out_file:
        out_file.write(fingerprint)


def __is_tesseract_available(path: str) -> bool:

    if path:
        return which(join(path, 'tesseract')) is not None
    else:
        return which('tesseract') is not None


def main(argv=None):

    sisc_description = ('SisC is a tool to automatically separate  annotations from the underlying text. SisC uses a'
                        'fingerprint, that is, a masked version  of the text to merge stand-off annotations with'
                        'another version of the original text, for example, extracted from a PDF file. The fingerprint'
                        'cannot be used on its own to recreate (meaningful parts of) the original text and can'
                        'therefore be shared.')

    argument_parser = ArgumentParser(prog='sisc', description=sisc_description)

    argument_parser.add_argument('--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                                                           'CRITICAL'],
                                 help='Set the logging level (default: %(default)s)', default='WARNING')

    subparsers = argument_parser.add_subparsers(dest='top_subparser')
    subparsers.required = True

    fingerprint_parser_desc = 'Command to create a fingerprint.'
    parser_fingerprint = subparsers.add_parser('fingerprint', help=fingerprint_parser_desc,
                                               description=fingerprint_parser_desc)

    fingerprint_subparsers = parser_fingerprint.add_subparsers(dest='fingerprint_subparser')
    fingerprint_subparsers.required = True

    # uniform masking, parser options
    input_path_help = ('Path to txt or xml file to create fingerprint from. Can be a folder in which case all files'
                       ' will be processed.')
    output_path_help = 'Output folder path.'
    file_type_help = 'The input file type to process. Only used when input_path is a folder (default: %(default)s).'
    move_notes_help = ('This will move footnotes and endnotes to the end of their page/the whole text. Only works with'
                       'XML file which are annotated with footnotes/endnotes and pagebreaks. (default: %(default)s)')
    add_quotation_marks_help = ('Add quotation marks in the fingerprint. Useful when quotations marks are not present in'
                                ' the annotated XML file. (default: %(default)s)')
    symbol_help = 'The character to use for masking (default: %(default)s).'
    root_tag_help = 'The root tag to use for masking (default: %(default)s).'
    keep_space_only_help = 'Keep only whitespace characters (default: %(default)s).'

    uniform_parser_desc = 'Command to use uniform masking for the fingerprint.'
    parser_fingerprint_uniform = fingerprint_subparsers.add_parser('uniform', help=uniform_parser_desc,
                                                                   description=uniform_parser_desc)
    parser_fingerprint_uniform.add_argument('input_path', metavar='input-path',
                                            help=input_path_help)
    parser_fingerprint_uniform.add_argument('output_path', metavar='output-path',
                                            help=output_path_help)
    parser_fingerprint_uniform.add_argument('--file-type', dest='file_type', choices=['txt', 'xml'],
                                            default='xml', help=file_type_help)
    parser_fingerprint_uniform.add_argument('--move-notes', dest='move_notes', default=False,
                                            action=BooleanOptionalAction, help=move_notes_help)
    parser_fingerprint_uniform.add_argument('--add-quotation-marks', dest='add_quotation_marks',
                                            default=False, action=BooleanOptionalAction, help=add_quotation_marks_help)
    parser_fingerprint_uniform.add_argument('-s', '--symbol', type=str, dest='symbol',
                                            default=Defaults.DEFAULT_SYMBOL, help=symbol_help)
    parser_fingerprint_uniform.add_argument('-k', '--keep-count', type=int, dest='keep_count',
                                            default=Defaults.DEFAULT_KEEP_COUNT,
                                            help='Number of characters which not to mask.')
    parser_fingerprint_uniform.add_argument('-d', '--distance', type=int, dest='distance',
                                            default=Defaults.DEFAULT_DISTANCE,
                                            help='The number of characters to mask between not masked characters'
                                                 ' (default: %(default)d)')
    parser_fingerprint_uniform.add_argument('-r', '--root-tag', type=str, dest='root_tag', default=Defaults.ROOT_TAG,
                                            help=root_tag_help)
    parser_fingerprint_uniform.add_argument('--keep-space-only', dest='keep_space_only', default=False,
                                            action=BooleanOptionalAction, help=keep_space_only_help)

    # context masking, parser options
    context_parser_desc = 'Command to use context masking for the fingerprint.'

    parser_fingerprint_context = fingerprint_subparsers.add_parser('context', help=context_parser_desc,
                                                                   description=context_parser_desc)
    parser_fingerprint_context.add_argument('input_path', metavar='input-path',
                                            help=input_path_help)
    parser_fingerprint_context.add_argument('output_path', metavar='output-path',
                                            help=output_path_help)
    parser_fingerprint_context.add_argument('--file-type', dest='file_type', choices=['txt', 'xml'],
                                            default='xml', help=file_type_help)
    parser_fingerprint_context.add_argument('--move-notes', dest='move_notes', default=False,
                                            action=BooleanOptionalAction, help=move_notes_help)
    parser_fingerprint_context.add_argument('--add-quotation-marks', dest='add_quotation_marks', default=False,
                                            action=BooleanOptionalAction, help=add_quotation_marks_help)
    parser_fingerprint_context.add_argument('-s', '--symbol', type=str, dest='symbol',
                                            default=Defaults.DEFAULT_SYMBOL, help=symbol_help)
    parser_fingerprint_context.add_argument('-t', '--tag', type=str, dest='keep_tag', required=True,
                                            help='The tag for which the surrounding context is not masked.')
    parser_fingerprint_context.add_argument('-c', '--context-size', type=int, dest='context_size',
                                            default=Defaults.DEFAULT_CONTEXT_SIZE,
                                            help='Size of the context window which is not masked (default: %(default)d)')
    parser_fingerprint_context.add_argument('-k', '--keep-text', dest='keep_text', default=False,
                                            action=BooleanOptionalAction,
                                            help='Do not mask the text of the tag itself. (default: %(default)s)')
    parser_fingerprint_context.add_argument('-r', '--root-tag', type=str, dest='root_tag', default=Defaults.ROOT_TAG,
                                            help=root_tag_help)

    # Align Options
    align_parser_desc = 'Command to align fingerprint and PDF or text.'
    parse_align = subparsers.add_parser('align', help=align_parser_desc, description=align_parser_desc)

    parse_align.add_argument('content_path', metavar='content-path',
                             help='Path to the file (or folder) with the content for alignment (txt or pdf).')
    parse_align.add_argument('align_source_path', metavar='align-source-path',
                             help='Path to the file (or folder) used as the source for the alignment. This can either be'
                                  ' xml files, which contain the fingerprint together with annotations or txt files'
                                  ' with only a fingerprint. In the second case, the file(s) with the annotations are'
                                  ' then specified with the --auxiliary-path and --auxiliary-type options.')
    parse_align.add_argument('output_path', metavar='output-path',
                             help='Output folder path.')
    parse_align.add_argument('--auxiliary-path', type=str, dest='auxiliary_path',
                             help='Can be used to specify the path to the annotations. Only needed when the annotations'
                                  ' are not part of the files specified in align_source_path.', required=False)
    parse_align.add_argument('--auxiliary-type', choices=['txt', 'json'], dest='auxiliary_type',
                             help='The type of the annotations to process. Only used when content_path is'
                                                 ' a folder. (default: %(default)s).', required=False)
    parse_align.add_argument('-f', '--first-page', type=int, dest='first_page', default=1,
                             required=False, help='Can be used to specify the first page to process. Only used for PDF'
                                                  ' files and when processing a single PDF file (default: %(default)d).')
    parse_align.add_argument('-l', '--last-page', type=int, dest='last_page', default=-1,
                             required=False, help='Can be used to specify the last page to process. Only used for PDF'
                                                  ' files and when processing a single PDF file (default: %(default)d).')
    parse_align.add_argument('-k', '--keys', nargs='+', type=str, dest='keys_to_update',
                             required=False, help='Only used for json standoff annotations. Used to specify json keys'
                                                  ' which represent a position and need to be updated.')
    parse_align.add_argument('--max-num-processes', dest='max_num_processes', action=OptionValueCheckAction,
                             default=1, type=int,
                             help='Maximum number of processes to use for parallel processing (default: %(default)d).')
    parse_align.add_argument('--max-text-length', dest='max_text_length', action=OptionValueCheckAction,
                             default=Defaults.MAX_TEXT_LENGTH, type=int, required=False,
                             help='The maximum length (in characters) of a text to align (default: %(default)d).')
    parse_align.add_argument('--tess-lang', dest='tess_lang', default='deu', type=str, required=False,
                             help='Language to use for PDF processing (default: %(default)s).')
    parse_align.add_argument('--tess-path', dest='tess_path', type=str, required=False,
                             help='Path to Tesseract.')
    parse_align.add_argument('--poppler-path', dest='poppler_path', type=str, required=False,
                             help='Path to Poppler.')
    parse_align.add_argument('--remove-gap-min-length', dest='remove_gap_min_length', type=int,
                             required=False, default=Defaults.REMOVE_GAP_MIN_LENGTH, help='Minimum length of gaps to remove (default: %(default)d).')

    # Eval options
    eval_parser_desc = 'Command to run the evaluation.'
    parse_eval = subparsers.add_parser('eval', help=eval_parser_desc, description=eval_parser_desc)

    parse_eval.add_argument('gold_path', metavar='gold-path',
                            help='Path to the file (or folder) with the gold/ground truth files.')
    parse_eval.add_argument('test_path', metavar='test-path',
                            help='Path the file or (folder) with the files to test.')
    parse_eval.add_argument('type', choices=['txt', 'json', 'xml'], metavar='type',
                            default='xml', help='The type of files to evaluate (default: %(default)s).')
    # parse_eval.add_argument('-i', '--include-tags', nargs='+', type=str, dest='include_tags', required=False,
    #                         help='Only used for evaluation xml files. Specify tags which should be'
    #                               ' included. If left empty, all tags will be included.')
    # parse_eval.add_argument('-e', '--exclude-tags', nargs='+', type=str, dest='exclude_tags', required=False,
    #                         help='Only used for evaluation xml files. Specify tags which should be'
    #                              ' excluded from the evaluation. If set, all matching tags and children will be excluded.')

    args = argument_parser.parse_args(argv)

    log_level = args.log_level
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if args.top_subparser == 'fingerprint':
        if args.fingerprint_subparser == 'uniform' or args.fingerprint_subparser == 'context':
            keep_count = 0
            distance = 0
            context_size = 0
            keep_tag = ''
            keep_text = False
            keep_space_only = False
            fingerprint_type = args.fingerprint_subparser

            if args.fingerprint_subparser == 'uniform':
                input_path = args.input_path
                output_path = args.output_path
                file_type = args.file_type
                symbol = args.symbol
                move_notes = args.move_notes
                add_quotation_marks = args.add_quotation_marks
                keep_count = args.keep_count
                distance = args.distance
                root_tag = args.root_tag
                keep_space_only = args.keep_space_only
            elif args.fingerprint_subparser == 'context':
                input_path = args.input_path
                output_path = args.output_path
                file_type = args.file_type
                move_notes = args.move_notes
                symbol = args.symbol
                add_quotation_marks = args.add_quotation_marks
                context_size = args.context_size
                keep_tag = args.tag
                keep_text = args.keep_text
                root_tag = args.root_tag
            else:
                return

            if not exists(input_path):
                logger.fatal(f'Path does not exist: {input_path}')
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), input_path)

            if not exists(output_path):
                logger.fatal(f'Path does not exist: {output_path}')
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), output_path)

            if isfile(input_path):
                input_file_ext = splitext(input_path)[1]

                if input_file_ext == '.txt':
                    __fingerprint_txt(input_path, output_path, fingerprint_type, symbol, distance, keep_count)
                elif input_file_ext == '.xml':
                    __fingerprint_xml(input_path, output_path, fingerprint_type, symbol, move_notes,
                                      add_quotation_marks, distance, keep_count, context_size, keep_tag, keep_text,
                                      root_tag, keep_space_only)
                else:
                    logger.fatal(f'Unsupported file extension: {input_file_ext}')
                    raise NotSupportedException(f'Unsupported file extension: {input_file_ext}')
            else:
                for file_or_folder in listdir(input_path):
                    full_path = join(input_path, file_or_folder)
                    if isfile(full_path):
                        input_file_ext = splitext(full_path)[1]
                        if input_file_ext == '.txt' and file_type == 'txt':
                            __fingerprint_txt(full_path, output_path, fingerprint_type, symbol, distance, keep_count)
                        elif input_file_ext == '.xml' and file_type == 'xml':
                            __fingerprint_xml(full_path, output_path, fingerprint_type, symbol, move_notes,
                                              add_quotation_marks, distance, keep_count, context_size, keep_tag,
                                              keep_text, root_tag, keep_space_only)

    elif args.top_subparser == 'align':
        content_path = args.content_path
        align_source_path = args.align_source_path
        output_path = args.output_path
        auxiliary_type = args.auxiliary_type
        auxiliary_path = args.auxiliary_path
        key_to_update = args.keys_to_update
        first_page = args.first_page
        last_page = args.last_page
        max_num_processes = args.max_num_processes
        max_text_length = args.max_text_length
        tess_lang = args.tess_lang
        tess_path = args.tess_path
        poppler_path = args.poppler_path
        remove_gap_min_length = args.remove_gap_min_length

        if not exists(content_path):
            logger.fatal(f'Path does not exist: {content_path}')
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), content_path)

        if not exists(align_source_path):
            logger.fatal(f'Path does not exist: {align_source_path}')
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), align_source_path)

        if auxiliary_path and not auxiliary_type:
            argument_parser.error('--auxiliary-path requires --auxiliary-type')

        if isfile(content_path):
            input_file_ext = splitext(content_path)[1]
            if input_file_ext != '.txt' and input_file_ext != '.pdf':
                logger.fatal(f'Unsupported content file extension: {input_file_ext}')
                raise NotSupportedException(f'Unsupported file extension: {input_file_ext}')

            if input_file_ext == '.pdf' and not __is_tesseract_available(tess_path):
                logger.fatal('Tesseract could not be found.')
                raise TesseractException('Could not find tesseract')

            fingerprint_ext = splitext(align_source_path)[1]

            if fingerprint_ext == '.txt' and not auxiliary_path:
                argument_parser.error('Align source path is a txt file but --auxiliary-path is not specified')

            if fingerprint_ext != '.xml' and fingerprint_ext != '.txt':
                logger.fatal(f'Unsupported fingerprint file extension: {fingerprint_ext}')
                raise NotSupportedException(f'Unsupported file extension: {fingerprint_ext}')

            if auxiliary_path:
                anno_file_ext = splitext(auxiliary_path)[1]
                if anno_file_ext != '.json' and anno_file_ext != '.txt':
                    logger.fatal(f'Unsupported annotation file extension: {anno_file_ext}')
                    raise NotSupportedException(f'Unsupported file extension: {anno_file_ext}')

            __align_file(content_path, align_source_path, auxiliary_path, output_path, key_to_update, first_page,
                         last_page, max_text_length, tess_lang, tess_path, poppler_path, remove_gap_min_length)
        else:
            if not isdir(align_source_path):
                logger.fatal('Align source path is not a file and not a directory')
                raise FileNotFoundError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), align_source_path)

            if auxiliary_path and not isdir(auxiliary_path):
                logger.fatal(f'Auxiliary path is not a directory')
                raise FileNotFoundError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), auxiliary_path)

            found_pdf = False
            for file_name in listdir(content_path):
                if file_name.endswith('.pdf'):
                    found_pdf = True
                    break

            if found_pdf and not __is_tesseract_available(tess_path):
                logger.fatal('Tesseract could not be found.')
                raise TesseractException('Could not find tesseract')

            # Only for testing
            # Path(join(output_path, 'pdf_text')).mkdir(parents=True, exist_ok=True)

            pool = multiprocessing.Pool(max_num_processes)

            for file_or_folder in listdir(content_path):
                full_path = join(content_path, file_or_folder)

                if isfile(full_path):
                    filename = splitext(basename(full_path))[0]

                    if not auxiliary_path:
                        fingerprint_file_path = join(align_source_path, f'{filename}_fingerprint.xml')
                    else:
                        fingerprint_file_path = join(auxiliary_path, f'{filename}_fingerprint.txt')

                    annotation_file_path = None
                    if auxiliary_type == 'json':
                        annotation_file_path = join(auxiliary_path, f'{filename}.json')
                    elif auxiliary_type == 'txt':
                        annotation_file_path = join(auxiliary_path, f'{filename}.txt')

                    pool.apply_async(__align_file, args=(full_path, fingerprint_file_path, annotation_file_path, output_path,
                                                         key_to_update, 1, -1, max_text_length, tess_lang, tess_path,
                                                         poppler_path, remove_gap_min_length))

            pool.close()
            pool.join()

    elif args.top_subparser == 'eval':
        gold_path = args.gold_path
        test_path = args.test_path
        eval_type = args.type
        # include_tags = args.include_tags
        # exclude_tags = args.exclude_tags

        __run_eval(eval_type, gold_path, test_path)


if __name__ == '__main__':
    sys.exit(main())
