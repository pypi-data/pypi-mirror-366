from typing import List, Tuple

from sisc.mask.BaseMasker import BaseMasker
from sisc.util import Defaults
import re


class UniformMasker(BaseMasker):

    def __init__(self, symbol: str = Defaults.DEFAULT_SYMBOL, keep_count: int = Defaults.DEFAULT_KEEP_COUNT,
                 distance: int = Defaults.DEFAULT_DISTANCE, keep_space_only: bool = Defaults.KEEP_SPACE_ONLY):
        self.symbol = symbol
        self.keep_count = keep_count
        self.distance = distance
        self.keep_space_only = keep_space_only

    # overriding abstract method
    def mask(self, text: str, positions: List[Tuple[int,int]]) -> str:
        """
        Masks the given text by replacing certain characters with a specified symbol.

        This method processes the input `text` and replaces characters at specified positions
        with a symbol defined in the class. The masking follows a pattern where a certain
        number of characters are kept visible, followed by a certain number of characters being masked.

        :param text: The input string to be masked.
        :param positions: Not used.

        :return: The masked version of the input text.
        """

        text_list = list(text)

        show_count = self.keep_count
        hide_count = self.distance

        for pos in range(len(text_list)):

            if show_count > 0:
                show_count -= 1
            elif hide_count > 0:
                hide_count -= 1

                if self.keep_space_only:
                    if not re.match(r'\s', text_list[pos]):
                        text_list[pos] = self.symbol
                else:
                    if not re.match(r'\W', text_list[pos]):
                        text_list[pos] = self.symbol

            if show_count == 0 and hide_count == 0:
                show_count = self.keep_count
                hide_count = self.distance

        return ''.join(text_list)