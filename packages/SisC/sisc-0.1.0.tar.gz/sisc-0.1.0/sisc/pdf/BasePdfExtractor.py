from abc import ABC, abstractmethod


class BasePdfExtractor(ABC):

    @abstractmethod
    def extract(self, pdf_path: str, lang: str = 'deu', first_page: int = 1, last_page: int = -1) -> str:
        pass