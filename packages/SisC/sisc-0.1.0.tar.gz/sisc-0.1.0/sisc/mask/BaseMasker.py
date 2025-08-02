from abc import ABC, abstractmethod
from typing import List, Tuple



class BaseMasker(ABC):
    """
    An abstract base class for creating masking strategies. This class defines the interface for masking text.
    """

    @abstractmethod
    def mask(self, text: str, positions: List[Tuple[int,int]]) -> str:
        pass
