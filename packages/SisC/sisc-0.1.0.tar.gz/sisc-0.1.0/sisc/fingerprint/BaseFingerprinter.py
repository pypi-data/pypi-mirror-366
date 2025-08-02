from abc import ABC, abstractmethod
from typing import TypeVar, Generic, overload

T = TypeVar('T')
V = TypeVar('V')


class BaseFingerprinter(ABC, Generic[T]):
    """
    Abstract base class for creating custom fingerprinters.

    The BaseFingerprinter provides a blueprint for classes that
    generate fingerprints for input content. Classes inheriting
    from this base class must implement the `fingerprint` method
    to define their specific fingerprinting logic.

    :ivar T: Type of input content that the fingerprinter processes.
    """
    @abstractmethod
    def fingerprint(self, input_content: T) -> T:
        pass