import logging
from sisc.pdf.BasePdfExtractor import BasePdfExtractor


logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str, extractor: BasePdfExtractor, lang: str = 'deu', first_page: int = 1,
                          last_page: int = -1) -> str:

    __check_page_range(first_page, last_page)
    return extractor.extract(pdf_path, lang, first_page, last_page)

def __check_page_range(first_page: int, last_page: int):
    if first_page < 1:
        raise ValueError(f'Invalid page: {first_page}')

    if last_page > -1 and 0 < last_page < first_page:
        raise ValueError(f'Invalid page range: {first_page} to {last_page}')
