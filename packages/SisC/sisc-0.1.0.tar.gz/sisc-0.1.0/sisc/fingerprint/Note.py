from dataclasses import dataclass
from lxml.etree import _Element

@dataclass
class Note:
    TYPE_FOOTNOTE = 1
    TYPE_ENDNOTE = 2

    type: int
    node: _Element
    text: str
    next_page: bool = False
