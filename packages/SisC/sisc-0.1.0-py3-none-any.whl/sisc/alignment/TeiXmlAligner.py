from typing import List, Optional
from lxml.etree import _ElementTree, _Element
from sisc.alignment.BaseFileAligner import BaseFileAligner
from sisc.cli.AlignException import AlignException
from sisc.util import Constants, Defaults
from itertools import groupby
from operator import itemgetter


class TeiXmlAligner(BaseFileAligner[_ElementTree]):

    def __init__(self, remove_gap_min_length: int = Defaults.REMOVE_GAP_MIN_LENGTH):
        self.remove_gap_min_length = remove_gap_min_length

    # overriding abstract method
    def align(self, input_content: _ElementTree, aligned_text: str, aligned_fingerprint: str,
              text_gap_positions: List[int], fingerprint_gap_positions: List[int]) -> _ElementTree:
        root = input_content.getroot()
        root_tag = self.__find_main_text_root(root)

        if not root_tag:
            raise AlignException(f'No root tag found')

        self.__update_element(root, fingerprint_gap_positions, aligned_text, -1, False, root_tag)
        return input_content

    def __find_main_text_root(self, element) -> Optional[str]:
        if Constants.ATTRIB_START in element.attrib and Constants.ATTRIB_END in element.attrib:
            return element.tag

        for child in element:
            child_tag =  self.__find_main_text_root(child)

            if child_tag:
                return child_tag

        return None

    def __update_element(self, element: _Element, fingerprint_gap_positions: List[int], aligned_text: str,
                         next_change_position: int, parent_moved_text: bool, root_tag: str):
        """

        :param element: The element to process
        :param fingerprint_gap_positions:
        :param aligned_text:
        :param next_change_position: The position of the next element's start position in case there are siblings.
        If there are no siblings, then the position of the parent closing tag is used. -1 in the case of the root element.
        :param parent_moved_text:
        """

        # check if there is something we need to do with the element
        if not Constants.ATTRIB_START in element.attrib or not Constants.ATTRIB_END in element.attrib:
            for child in element:
                self.__update_element(child, fingerprint_gap_positions, aligned_text, -1, parent_moved_text, root_tag)
            return

        start_attrib = Constants.ATTRIB_START
        end_attrib = Constants.ATTRIB_END

        moved_text = False
        if Constants.ATTRIB_TEXT_START in element.attrib:
            start_attrib = Constants.ATTRIB_TEXT_START
            end_attrib = Constants.ATTRIB_TEXT_END
            moved_text = True

        start = int(element.attrib[start_attrib])
        start = self.__calculate_new_value(start, fingerprint_gap_positions)
        end = int(element.attrib[end_attrib])
        end = self.__calculate_new_value(end, fingerprint_gap_positions)

        offset_start = 0
        offset_end = 0
        if Constants.ATTRIB_OFFSET_START in element.attrib:
            offset_start = int(element.attrib[Constants.ATTRIB_OFFSET_START])
        if Constants.ATTRIB_OFFSET_END in element.attrib:
            offset_end = int(element.attrib[Constants.ATTRIB_OFFSET_END])

        # special case for last element
        if element.tag == root_tag and Constants.ATTRIB_SKIP in element.attrib:
            skip_length = int(element.attrib.get(Constants.ATTRIB_SKIP))
            end -= skip_length

        if len(element) > 0:
            child_start = int(element[0].attrib[start_attrib])
            child_start = self.__calculate_new_value(child_start, fingerprint_gap_positions)
            element.text = self.__remove_big_gaps(aligned_text, start + offset_start, child_start, fingerprint_gap_positions)

            # temp_next_change_pos refers to the next relevant end position, so either the next child start position, if there
            # are siblings, or the overall end position, i.e., the parent closing tag if there are no more siblings.

            for child_pos, child in enumerate(element):
                if child_pos + 1 < len(element):
                    temp_next_change_pos = int(element[child_pos + 1].attrib[start_attrib])
                    temp_next_change_pos = self.__calculate_new_value(temp_next_change_pos, fingerprint_gap_positions)
                else:
                    temp_next_change_pos = end + offset_end

                self.__update_element(child, fingerprint_gap_positions, aligned_text, temp_next_change_pos, moved_text,
                                      root_tag)
        else:
            element.text = self.__remove_big_gaps(aligned_text, start + offset_start, end + offset_end, fingerprint_gap_positions)

        if next_change_position > -1:
            # Get the text after the current element end and next element start position. There are different cases
            # We need to handle pagebreaks in footnotes and elements spanning over footnotes, i.e., elements with
            # pagebreaks and move_text == True
            if Constants.ATTRIB_SKIP in element.attrib:
                skip_cnt = int(element.attrib[Constants.ATTRIB_SKIP])
                current_element_end = end + skip_cnt
                element.tail = self.__remove_big_gaps(aligned_text, current_element_end, next_change_position, fingerprint_gap_positions)
            elif not parent_moved_text and moved_text:
                # only necessary if the text was not already modified because of the parent
                # The original start point of the footnote before moving is the start point of the text after moving
                current_element_org_start = int(element.attrib[Constants.ATTRIB_START])
                current_element_org_start = self.__calculate_new_value(current_element_org_start, fingerprint_gap_positions)
                element.tail = self.__remove_big_gaps(aligned_text, current_element_org_start, next_change_position, fingerprint_gap_positions)
            else:
                # default case: end of the current element to the next end
                element.tail = self.__remove_big_gaps(aligned_text, end, next_change_position, fingerprint_gap_positions)

        element.attrib.pop(Constants.ATTRIB_START, None)
        element.attrib.pop(Constants.ATTRIB_END, None)
        element.attrib.pop(Constants.ATTRIB_TEXT_START, None)
        element.attrib.pop(Constants.ATTRIB_TEXT_END, None)
        element.attrib.pop(Constants.ATTRIB_SKIP, None)
        element.attrib.pop(Constants.ATTRIB_OFFSET_START, None)
        element.attrib.pop(Constants.ATTRIB_OFFSET_END, None)

    def __calculate_new_value(self, value: int, fingerprint_gap_positions: List[int]) -> int:
        count_before = self.__count_before(value, fingerprint_gap_positions)
        return value + count_before

    @staticmethod
    def __count_before(value: int, gap_positions: List[int]) -> int:
        count_before = 0
        for pos in gap_positions:
            if pos < value + count_before:
                count_before += 1
            else:
                break

        return count_before

    def __remove_big_gaps(self, input_text: str, start: int, end: int, gap_positions: List[int]) -> str:
        """
        Takes an input text and extracts a portion of it based on specified start and end indices.
        Based on the given gap positions, large gaps are removed from the extracted portion.

        :param input_text: The original text.
        :param start: The starting index of the portion of text to process.
        :param end: The ending index of the portion of text to process.
        :param gap_positions: A list of indices within the `input_text` that are gaps.
        :return: The modified text.
        """
        text = input_text[start:end]

        data = []
        for pos in gap_positions:
            if start <= pos <= end:
                data.append(pos)

        remove_ranges = []
        for k, g in groupby(enumerate(data), lambda ix : ix[0] - ix[1]):
            numbers = list(map(itemgetter(1), g))

            if len(numbers) >= self.remove_gap_min_length:
                remove_ranges.append((numbers[0], numbers[-1]))

        for rm_start, rm_end in reversed(remove_ranges):
            text = text[:rm_start - start] + text[rm_end - end:]

        return text
