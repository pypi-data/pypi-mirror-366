from sisc.fingerprint.BaseFingerprinter import BaseFingerprinter
from sisc.mask.BaseMasker import BaseMasker


class TextFingerprinter(BaseFingerprinter[str]):

    def __init__(self, obfuscater: BaseMasker):
        self.obfuscater = obfuscater

    # overriding abstract method
    def fingerprint(self, text: str) -> str:
        return self.obfuscater.mask(text, [])