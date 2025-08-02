from sisc.pdf.BasePdfExtractor import BasePdfExtractor
import logging
import subprocess
import tempfile
from errno import ENOENT
from os.path import join
from typing import List, Optional
from pdf2image import convert_from_path
from PIL import Image

from sisc.pdf.TesseractException import TesseractException


logger = logging.getLogger(__name__)


class TesseractExtractor(BasePdfExtractor):

    def __init__(self, tess_path: Optional[str] = None, poppler_path: Optional[str] = None):
        self.tess_path = tess_path
        self.poppler_path = poppler_path

    # overriding abstract method
    def extract(self, pdf_path: str, lang: str = 'deu', first_page: int = 1, last_page: int = -1) -> str:
        pages = self.__extract_pages_from_pdf(pdf_path)
        text = self.__run_tesseract(pages, lang, first_page, last_page)
        return text

    def __extract_pages_from_pdf(self, pdf_path: str) -> List[Image.Image]:
        # TODO: store in temporary folder
        pages = convert_from_path(pdf_path, 300, poppler_path=self.poppler_path)
        return pages

    def __run_tesseract(self, pages: List[Image.Image], tess_lang, first_page, last_page) -> str:
        output_text = ''
        page_count = len(pages)
        img_extension = 'PNG'

        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug(f'created temporary directory {temp_dir}')

            for pos, page in enumerate(pages):
                if pos < first_page - 1:
                    logger.info(f'Skipping page {pos + 1}/{page_count}')
                    continue

                if last_page > 0 and pos > last_page - 1:
                    logger.info(f'Skipping page {pos + 1}/{page_count}')
                    continue

                # logger.info(f'OCR page {pos+1}/{page_count}')

                image_file_name = join(temp_dir, f'page_{pos + 1}.{img_extension}')
                page.save(image_file_name, format=img_extension, **page.info)

                tesseract_cmd = 'tesseract'
                if self.tess_path:
                    tesseract_cmd = join(self.tess_path, 'tesseract')

                try:
                    p_result = subprocess.run([tesseract_cmd, image_file_name, '-', '-l', tess_lang, '--dpi', '300'],
                                              capture_output=True)
                except OSError as e:
                    if e.errno != ENOENT:
                        raise
                    else:
                        raise TesseractException('Could not find tesseract')

                if p_result.returncode != 0:
                    logger.error(f'Could not read page {pos + 1}')
                    continue

                out = p_result.stdout.decode('utf-8')

                if output_text:
                    output_text += '\n'

                output_text += out

        return output_text


