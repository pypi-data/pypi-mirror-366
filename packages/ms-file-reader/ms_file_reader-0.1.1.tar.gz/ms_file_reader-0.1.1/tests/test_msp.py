"""
Tests specifically for the MSP file processor.
"""

import pytest

from ms_file_reader.msp import MSPFileReader


@pytest.fixture(name="good_test_file")
def good_test_file_fixture():
    with open("tests/test_files/msp/test1.msp", "r", encoding="utf-8") as f:
        return f.read()

def test_read_good_file(good_test_file):
    """Basic check for whether the processor reads a file correctly."""
    reader = MSPFileReader(keep_empty_fields=True, num_peaks_text="Num_Peaks")
    library = reader.process_file(good_test_file)
    assert len(library.spectra) == 3

def test_filter_null_fields(good_test_file):
    """Tests whether the keep_empty_fields filter works correctly."""
    reader1 = MSPFileReader(keep_empty_fields=True, num_peaks_text="Num_Peaks")
    library1 = reader1.process_file(good_test_file)
    field_counts1 = library1.count_all_fields()
    assert field_counts1["InChIKey"] == 3

    reader2 = MSPFileReader(keep_empty_fields=False, num_peaks_text="Num_Peaks")
    library2 = reader2.process_file(good_test_file)
    field_counts2 = library2.count_all_fields()
    assert field_counts2["InChIKey"] == 2

def test_count_field_values(good_test_file):
    """
    Tests the counting of field values.
    """
    reader = MSPFileReader(keep_empty_fields=True, num_peaks_text="Num_Peaks")
    library = reader.process_file(good_test_file)
    ion_modes = library.count_field_values("Ion Mode")
    assert set(ion_modes.keys()) == {"Positive", "Unknown"}
