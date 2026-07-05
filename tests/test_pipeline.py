import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from pipeline.inference import run_pipeline
from pipeline.date_parser import parse_date

def test_pipeline_import():
    assert callable(run_pipeline)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("EXP: 09/O6/26", "2026-06-09"),
        ("MFG 01/04/2026 EXP 13/11/2026", "2026-11-13"),
        ("Best Before: NOV 2026", "2026-11-01"),
        ("Use by 2026-12-27 Batch A1X9", "2026-12-27"),
        ("NET /2026 03/07 A1X9 Batch:", "2026-07-03"),
        ("BB: 09 Nov Batch: NET 2026", "2026-11-09"),
        ("EXP:Ti/11/2026 A1X9", "2026-11-11"),
    ],
)
def test_parse_date_handles_common_ocr_and_label_formats(text, expected):
    parsed, _match, _method = parse_date(text)
    assert parsed == expected
