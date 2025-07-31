[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

This is a small library intended to read different types of mass spectrometry files, store them as (somewhat) standardized objects, and run some exploratory checks on the spectra as a whole.  The focus is on open, text-based file formats for already-processed spectra.  Functionality has been added for reading MSP, JCAMP-DX, and MassBank EU-styled files.

I wrote this because of a project that grabbed collections of mass spectra from a variety of sources.  A number of these sources had  inconsistencies within their libraries -- sometimes due to fields that don't appear in all spectra, sometimes becuase the field does always appear but it has some sort of null value in the field, and so on.  Some exploration of the data was usually necessary, and much of it was repetetive.  This library was written to streamline some of that work for anyone else in the same position.

NumPy is the only dependency for this library.

Feedback on other real-world edge cases is welcome.

# Usage

Install from PyPI:

```
pip install ms-file-reader
```

To import the individual readers:

```
from ms_file_reader.jcamp import JCAMPFileReader
from ms_file_reader.massbank import MassBankFileReader
from ms_file_reader.msp import MSPFileReader
```

The individual readers -- mostly the ones for JCAMP-DX and MSP -- come with options for trying to deal with any non-standardness of files; see the docstrings for argument details.  Processing is done by a `process_file()` method associated with each class.  The method acts on text objects instead of file handles or paths, so the content of a file has to be read in first.

A basic example:

```
from ms_file_reader.msp import MSPFileReader
with open("test.msp", "r", encoding="utf-8") as f:
    file_text = f.read()

reader = MSPFileReader(keep_empty_fields=False, max_intensity=100)
spectrum_library = reader.process_file(file_text)
```