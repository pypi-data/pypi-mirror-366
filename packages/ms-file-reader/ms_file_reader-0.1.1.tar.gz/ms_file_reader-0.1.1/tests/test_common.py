"""
Tests for the classes that underlie the file-type-specific processors.
"""

import numpy as np
import pytest

from ms_file_reader.common_ms import MassSpectrum, MassSpectrumLibrary, MassSpectrumFileReader

@pytest.fixture(name="quick_test_library", scope="module")
def quick_test_library_fixture():
    """Generates a generic mass spectrum library object."""
    return MassSpectrumLibrary([
        MassSpectrum({"F1": "Yes", "F2": "Yes", "F3": "Dunno"}, np.array([[10,10]])),
        MassSpectrum({"F1": "Yes", "F2": None}, np.array([[20,200]])),
        MassSpectrum({"F1": "No", "F2": "No", "F3": "Dunno"}, np.array([[30,300]])),
        MassSpectrum({"F1": "No", "F3": "Yes"}, np.array([[40,100]]))
    ])

def test_spectrum_rescale():
    """Tests whether spectrum rescaling works correctly."""
    test_spectrum = MassSpectrum({}, np.array([[1,5],[2,10],[3,1]]))
    test_spectrum.rescale_spectrum(100)
    assert np.all(test_spectrum.spectrum[:,1] == np.array([50, 100, 10]))

def test_field_counting(quick_test_library):
    """
    Tests whether counting fields works correctly.  Input object should not have each field appear
    in each spectrum.
    """
    counts = quick_test_library.count_all_fields()
    assert counts == {"F1": 4, "F2": 3, "F3": 3}

def test_field_value_count(quick_test_library):
    """
    Tests counting of values for a specific field.  Selected field should not exist for all spectra
    in the library.
    """
    counts = quick_test_library.count_field_values("F3")
    assert counts == {"Dunno": 2, "Yes": 1}

def test_processor_good_input():
    """Tests the processing of a list of strings into a NumPy array for the spectrum."""
    good_input = ["1 14 9.7", "2 24 13.8", "5 33 16.9"]
    processor = MassSpectrumFileReader(mz_field=0, intensity_field=2)
    spectrum = processor.process_spectrum_lines(good_input)
    assert np.all(spectrum == np.array([[1, 9.7], [2, 13.8], [5, 16.9]]))

def test_processor_bad_number_of_entries():
    """Tests whether an error is thrown for a bad number of entries in a spectrum peak."""
    bad_input = ["1 14 9.7", "2 24", "5 33 16.9"]
    processor = MassSpectrumFileReader(mz_field=0, intensity_field=2)
    with pytest.raises(ValueError):
        processor.process_spectrum_lines(bad_input)
