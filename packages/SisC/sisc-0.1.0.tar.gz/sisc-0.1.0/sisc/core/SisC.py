import logging
from typing import Any, Optional

from Bio import Align
from sisc.alignment.BaseFileAligner import BaseFileAligner
from sisc.cli.AlignException import AlignException
from sisc.util import Defaults

logger = logging.getLogger(__name__)


def align_text(input_content: Any, text: str, fingerprint: str, base_aligner: Optional[BaseFileAligner],
               max_text_length: int = Defaults.MAX_TEXT_LENGTH) -> tuple[Optional[str], Optional[Any]]:

    if len(text) > max_text_length:
        raise AlignException(f'Text too long: {len(text)} characters')

    aligner = Align.PairwiseAligner()
    # TODO: make configurable
    aligner.match = 2
    aligner.open_gap_score = -3
    aligner.extend_gap_score = -1
    alignments = aligner.align(text, fingerprint)
    alignment = alignments[0]

    text_gap_positions = [i for i, x in enumerate(alignment.indices[0]) if x == -1]
    fingerprint_gap_positions = [i for i, x in enumerate(alignment.indices[1]) if x == -1]

    aligner_result = None
    if base_aligner:
        aligner_result = base_aligner.align(input_content, alignment[0], alignment[1], text_gap_positions,
                                            fingerprint_gap_positions)

    return alignment[0], aligner_result
