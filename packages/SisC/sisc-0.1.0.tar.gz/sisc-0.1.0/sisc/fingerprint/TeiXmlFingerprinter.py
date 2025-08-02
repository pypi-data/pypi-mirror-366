from typing import List, Tuple, Optional

from sisc.fingerprint.BaseFingerprinter import BaseFingerprinter
from sisc.fingerprint.Note import Note
from sisc.mask.BaseMasker import BaseMasker
import re
from sisc.util import Constants, Defaults
from lxml.etree import _ElementTree, _Element, SubElement
from lxml import etree


class TeiXmlFingerprinter(BaseFingerprinter[_ElementTree]):
    """
    Represents a class for processing TEI XML data and creating a fingerprint.

    :ivar obfuscater: The obfuscater instance responsible for obfuscating text contents.
    :ivar move_notes: Indicates whether the "note" elements should be moved to specific positions.
    :ivar add_quotation_marks: Specifies whether to add quotation marks around text within "q" tags.
    :ivar keep_tag: Defines the name of the tag to be preserved during fingerprinting.
    """
    def __init__(self, obfuscater: BaseMasker, move_notes: bool = False, add_quotation_marks: bool = False,
                 keep_tag: str = '', root_tag: str = Defaults.ROOT_TAG):
        self.obfuscater = obfuscater
        self.move_notes = move_notes
        self.add_quotation_marks = add_quotation_marks
        self.keep_tag = keep_tag
        self.root_tag = root_tag

    # overriding abstract method
    def fingerprint(self, input_content: _ElementTree) -> _ElementTree:
        """
        Generate a fingerprint from the provided XML document.

        This method processes the given XML input to generate a fingerprint that
        includes masked text content.

        :param input_content: An XML document represented as an ElementTree object. The
            root element of this content will be processed to generate the fingerprint.
        :return: The modified XML document with an added 'standOff' element containing
            the generated fingerprint.
        """
        root = input_content.getroot()
        body_elem = root.find(f'.//{{*}}{self.root_tag}')

        text, _, tag_positions = self.__annotate_element(body_elem, 0, [], False)
        text = self.obfuscater.mask(text, tag_positions)

        fingerprint = SubElement(root, 'standOff')
        fingerprint.text = text

        return input_content

    def __annotate_element(self, element: _Element, prev_len: int, notes: List[Note], in_footnote: bool):
        result: str = ''
        pb_pos: int = -1
        tag_positions: List[Tuple[int, int]] = []
        tag_start: int
        tag_end: int

        tag = etree.QName(element).localname

        if tag == 'note':
            elem_note_type = element.attrib.get('type')

            if elem_note_type == 'footnote':
                in_footnote = True

        if self.move_notes and tag == 'pb':
            if in_footnote:
                pb_pos = prev_len

        tag_start = prev_len + len(result)
        element.set(Constants.ATTRIB_START, f'{prev_len + len(result)}')

        if self.add_quotation_marks and tag == 'q':
            result += '"'
            element.set(Constants.ATTRIB_OFFSET_START, '1')

        if element.text:
            text = element.text
            element.text = ''
            if text:
                result += self.__clean_text(text)

        for child in element:
            inner_text, inner_pb_pos, inner_tag_positions = self.__annotate_element(child, prev_len + len(result),
                                                                                    notes, in_footnote)
            tag_positions.extend(inner_tag_positions)
            result += inner_text

            if inner_pb_pos != -1:
                pb_pos = inner_pb_pos

        if self.move_notes and tag == 'note':
            elem_note_type = element.attrib.get('type')

            if elem_note_type == 'endnote':
                notes.append(Note(Note.TYPE_ENDNOTE, element, result))
            else:
                if pb_pos == -1:
                    notes.append(Note(Note.TYPE_FOOTNOTE, element, result))
                else:
                    rel_pos = pb_pos - prev_len
                    notes.append(Note(Note.TYPE_FOOTNOTE, element, result[:rel_pos]))
                    notes.append(Note(Note.TYPE_FOOTNOTE, element, result[rel_pos:], True))

            tag_end = prev_len + len(result)
            element.set(Constants.ATTRIB_END, f'{prev_len + len(result)}')
            result = ''
        else:
            if self.add_quotation_marks and tag == 'q':
                result += '"'
                element.set(Constants.ATTRIB_OFFSET_END, '-1')

            tag_end = prev_len + len(result)
            element.set(Constants.ATTRIB_END, f'{prev_len + len(result)}')

        if self.move_notes and tag == 'pb':
            if not in_footnote:
                note_text = self.__add_notes(Note.TYPE_FOOTNOTE, notes, prev_len + len(result))
                result += note_text
                element.set(Constants.ATTRIB_SKIP, f'{len(note_text)}')

        if self.move_notes and tag == f'{self.root_tag}':
            note_text = self.__add_notes(None, notes, prev_len + len(result))
            result += note_text
            tag_end = prev_len + len(result)
            element.set(Constants.ATTRIB_END, f'{prev_len + len(result)}')
            element.set(Constants.ATTRIB_SKIP, f'{len(note_text)}')

        if tag != f'{self.root_tag}':
            text = element.tail
            element.tail = ''
            if text:
                result += self.__clean_text(text)

        if tag == self.keep_tag:
            tag_positions.append((tag_start, tag_end))

        return result, pb_pos, tag_positions

    def __add_notes(self, note_type: Optional[int], notes, prev_len: int) -> str:
        result = ''
        clear = False
        for note in notes:
            if note_type and note.type != note_type:
                continue
            clear = True

            if note.next_page:
                continue

            page_length = -1
            if not Constants.ATTRIB_TEXT_START in note.node.attrib:
                text_start = prev_len + len(result)
                note.node.set(Constants.ATTRIB_TEXT_START, f'{text_start}')
            else:
                old_end = int(note.node.attrib[Constants.ATTRIB_TEXT_END])
                page_length = prev_len - old_end

            result += note.text
            text_end = prev_len + len(result)

            note.node.set(Constants.ATTRIB_TEXT_END, f'{text_end}')

            parent_start = int(note.node.attrib[Constants.ATTRIB_START])
            text_start = int(note.node.attrib[Constants.ATTRIB_TEXT_START])

            after_pb = False
            for sub_elem in note.node:
                sub_pb = self.__add_text_pos(sub_elem, parent_start, text_start, page_length, after_pb)
                if sub_pb:
                    after_pb = True

        if clear:
            # modify the list in-place
            notes[:] = [x for x in notes if x.next_page]
            for note in notes:
                note.next_page = False

        return result

    def __check_pb(self, node: _Element) -> bool:
        tag = etree.QName(node).localname
        if tag == 'pb':
            return True

        for child in node:
            sub_pb = self.__check_pb(child)

            if sub_pb:
                return True

        return False

    def __add_text_pos(self, node: _Element, parent_start: int, parent_text_start: int, page_length: int,
                       after_pb: bool) -> bool:
        contains_pb = self.__check_pb(node)

        if Constants.ATTRIB_TEXT_START in node.attrib:
            tag = etree.QName(node).localname
            if tag == 'pb':
                node.set(Constants.ATTRIB_SKIP, f'{page_length}')
                after_pb = True
            elif after_pb:
                old_start = int(node.attrib[Constants.ATTRIB_TEXT_START])
                new_start = old_start + page_length
                node.set(Constants.ATTRIB_TEXT_START, f'{new_start}')

                old_end = int(node.attrib[Constants.ATTRIB_TEXT_END])
                new_end = old_end + page_length
                node.set(Constants.ATTRIB_TEXT_END, f'{new_end}')
            elif contains_pb:
                old_start = int(node.attrib[Constants.ATTRIB_TEXT_START])
                old_end = int(node.attrib[Constants.ATTRIB_TEXT_END])
                if old_start < old_end:
                    new_end = old_end + page_length
                    node.set(Constants.ATTRIB_TEXT_END, f'{new_end}')
        else:
            node_start = int(node.attrib[Constants.ATTRIB_START])
            node_end = int(node.attrib[Constants.ATTRIB_END])
            diff_start = node_start - parent_start
            diff_end = node_end - parent_start

            node.set(Constants.ATTRIB_TEXT_START, f'{parent_text_start + diff_start}')
            node.set(Constants.ATTRIB_TEXT_END, f'{parent_text_start + diff_end}')

        for child in node:
            sub_after_pb = self.__add_text_pos(child, parent_start, parent_text_start, page_length, after_pb)
            if sub_after_pb:
                after_pb = True

        return after_pb

    @staticmethod
    def __clean_text(text: str) -> str:
        result = re.sub(' *\n *', '\n', text, flags=re.DOTALL)
        return result