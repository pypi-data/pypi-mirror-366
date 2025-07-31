"""
Tests specifically for the MassBank EU file reader.
"""

import pytest

from ms_file_reader.massbank import MassBankFileReader


@pytest.fixture(name="good_test_file1")
def good_test_file1_fixture():
    """
    Loads file test file pulled from MassBank EU's data repository.
    """
    with open("tests/test_files/massbank/MSBNK-UvA_IBED-UI000101.txt", "r", encoding="utf-8") as f:
        return f.read()


def test_read_good_file(good_test_file1):
    """Basic check for whether the processor reads a file correctly."""
    reader = MassBankFileReader()
    spectrum = reader.process_file(good_test_file1)
    assert len(spectrum.spectrum) == 17
    assert "CHROMATOGRAPHY - FLOW_RATE" in list(spectrum.fields.keys())
    assert len(spectrum.fields["NAME"]) == 1
