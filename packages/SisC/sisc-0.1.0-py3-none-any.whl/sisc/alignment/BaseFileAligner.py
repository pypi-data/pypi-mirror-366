from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

T = TypeVar('T')


class BaseFileAligner(ABC, Generic[T]):
    """
    BaseFileAligner is an abstract base class that defines the contract
    for aligning texts with fingerprints. This
    class is designed to be extended by concrete implementations
    tailored to specific data types or formats.

    The base class ensures that all derived classes implement the `align`
    method, which performs the alignment operation.

    :ivar T: The generic type which represents the input content type.
    """
    @abstractmethod
    def align(self, input_content: T, aligned_text: str, aligned_fingerprint: str, text_gap_positions: List[int],
              fingerprint_gap_positions: List[int]) -> T:
        """
        Align the given content using the aligned text and fingerprint.
        :param input_content: The original content to be aligned.
        :param aligned_text:
        :param aligned_fingerprint:
        :param text_gap_positions: List of gap positions in the aligned text
        :param fingerprint_gap_positions: List of gap positions in the aligned fingerprint
        :return:
        """
        pass