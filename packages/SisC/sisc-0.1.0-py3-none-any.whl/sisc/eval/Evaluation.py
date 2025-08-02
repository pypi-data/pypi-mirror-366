import logging
from rapidfuzz.distance import Levenshtein
import statistics
import re

logger = logging.getLogger(__name__)


def eval_txt(text_1: str, text_2: str):
    matching_count = 0

    for c1, c2 in zip(text_1, text_2):

        if c1 == '-' or c2 == '-':
            matching_count += 1
        elif c1 == c2:
            matching_count += 1

    logger.info(f'Ratio 1: {matching_count/len(text_1)}\nRatio 2: {matching_count/len(text_2)}')


def eval_xml(filename, element_tree_1, element_tree_2,  include_tags=None, exclude_tags=None):
    logger.info(f'\n\n{filename}')

    root_1 = element_tree_1.getroot()
    body_elem_1 = root_1.find('.//{*}body')

    root_2 = element_tree_2.getroot()
    body_elem_2 = root_2.find('.//{*}body')

    ratio = __compare_element(body_elem_1, body_elem_2)
    logger.info(f'\n\n-------------------------------------------------------'
                f'\nAverage Levenshtein distance: {statistics.mean(ratio):.3f}'
                f'\n-------------------------------------------------------')

    return statistics.mean(ratio)


def __compare_element(element_1, element_2):
    assert len(element_1) == len(element_2)
    assert element_1.tag == element_2.tag
    ratios = []

    text_1 = element_1.text
    text_2 = element_2.text

    tail_1 = element_1.tail
    tail_2 = element_2.tail

    if text_1 and text_2:
        text_1 = re.sub(r'\W', '', text_1, flags=re.DOTALL)
        text_2 = re.sub(r'\W', '', text_2, flags=re.DOTALL)
        if len(text_1) > 0 or len(text_2) > 0:
            ratio = Levenshtein.normalized_similarity(text_1, text_2)
            ratios.append(ratio)
    elif (text_1 and not text_2) or (not text_1 and text_2):
        ratios.append(0)

    if tail_1 and tail_2:
        tail_1 = re.sub(r'\W', '', tail_1, flags=re.DOTALL)
        tail_2 = re.sub(r'\W', '', tail_2, flags=re.DOTALL)
        if len(tail_1) > 0 or len(tail_2) > 0:
            ratio = Levenshtein.normalized_similarity(tail_1, tail_2)
            ratios.append(ratio)
    elif (tail_1 and not tail_2) or (not tail_1 and tail_2):
        ratios.append(0)

    for child_1, child_2 in zip(element_1, element_2):
        sub_ratios = __compare_element(child_1, child_2)
        ratios.extend(sub_ratios)

    return ratios


# def __compare_complete_text(element_1, element_2):
#     assert len(element_1) == len(element_2)
#     assert element_1.tag == element_2.tag
#
#     text_1 = __get_text(element_1)
#     text_2 = __get_text(element_2)
#
#     if not text_1:
#         text_1 = ''
#
#     if not text_2:
#         text_2 = ''
#
#     text_1 = re.sub(r'\W', '', text_1, flags=re.DOTALL)
#     text_2 = re.sub(r'\W', '', text_2, flags=re.DOTALL)
#     ratio = Levenshtein.normalized_similarity(text_1, text_2)
#     return [ratio]


# def __compare_element_old(element_1, element_2, include_tags, exclude_tags):
#     assert len(element_1) == len(element_2)
#     assert element_1.tag == element_2.tag
#     ratios = []
#
#     # First check if tag is excluded
#     if exclude_tags and element_1.tag in exclude_tags:
#         return []
#
#     if not include_tags or element_1.tag in include_tags:
#         text_1 = __get_text(element_1)
#         text_2 = __get_text(element_2)
#
#         if not text_1:
#             text_1 = ''
#
#         if not text_2:
#             text_2 = ''
#
#         text_1 = re.sub(r'\W', '', text_1, flags=re.DOTALL)
#         text_2 = re.sub(r'\W', '', text_2, flags=re.DOTALL)
#         ratio = Levenshtein.normalized_similarity(text_1, text_2)
#         ratios.append(ratio)
#
#         # if ratio < 0.60:
#         #     logging.warning(f'{text_1} -- {text_2}\n{ratio}')
#
#         return ratios
#
#     for child_1, child_2 in zip(element_1, element_2):
#         sub_ratios = __compare_element(child_1, child_2, include_tags, exclude_tags)
#         ratios.extend(sub_ratios)
#
#     return ratios


# def __get_text(element):
#
#     result = ''
#     if element.text:
#         text = element.text
#         result += text
#
#     for child in element:
#         result += __get_text(child)
#
#     if element.tail:
#         result += element.tail
#
#     return result
