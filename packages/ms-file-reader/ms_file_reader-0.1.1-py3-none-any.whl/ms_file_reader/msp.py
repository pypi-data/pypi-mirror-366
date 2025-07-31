"""
Functions for processing MSP mass spectrum files.  This is one of the more
common file extensions that I come across, though as far as I know this isn't a
well-standardized format.
"""

import warnings

import numpy as np

from ms_file_reader.common_ms import MassSpectrum, MassSpectrumFileReader, MassSpectrumLibrary


class MSPFileReader(MassSpectrumFileReader):
    """
    This class is for taking the contents of a mass spectral .msp file and performing
    some basic extraction of the spectra inside.  This is currently assuming that the
    contents of the file in question have been read into memory already -- the files
    that I've been dealing with so far are all easy to read into memory, so this isn't
    an issue yet, but it may need a more streaming-like solution in the future.

    Arguments:
    - intensity_field -- In the peak list, this is the zero-indexed field that contains the peak's
    intensity.  Default is 1 for the second value on the line.
    - keep_empty_fields -- Boolean to choose whether to keep fields without values.  If True, fields
    that are empty in the file will have a value of None in the mass spectrum's field dictionary; if
    False, they won't appear in the dictionary at all.
    - max_intensity -- If supplied, all spectra in the library will have their peaks' intensities
    rescaled so that max_intensity is the largest value.
    - mz_field -- In the peak list, this is the zero-indexed field that contains the peak's m/z
    value.  Default is 0 for the first value on the line.
    - num_peaks_text -- Text string prefacing the number of peaks in the spectrum; used to identify
    when the list of peaks starts.  Default is "Num Peaks"; beware the capitalization, as I've seen
    different files with different capitalizations.
    - peak_delimiter -- Delimiter between the m/z and intensity values for a peak.  Leaving as None
    splits on any non-line-breaking whitespace.
    - spectrum_delimiter -- Delimiter between individual spectra in the file.
    """

    def __init__(
        self,
        intensity_field=1,
        keep_empty_fields=True,
        max_intensity=None,
        mz_field=0,
        num_peaks_text="Num Peaks",
        peak_delimiter=None,
        spectrum_delimiter="\n\n"
    ):
        super().__init__(intensity_field=intensity_field, mz_field=mz_field, peak_delimiter=peak_delimiter, max_intensity=max_intensity)
        self.num_peaks_text = num_peaks_text
        self.keep_empty_fields = keep_empty_fields
        self.spectrum_delimiter = spectrum_delimiter


    def __repr__(self):
        return (
            "MSPFileReader(\n"
            f"  intensity_field={self.intensity_field}\n"
            f"  keep_empty_fields={self.keep_empty_fields}\n"
            f"  max_intensity={self.max_intensity}\n"
            f"  mz_field={self.mz_field}\n"
            f"  num_peaks_text={repr(self.num_peaks_text)}\n"
            f"  peak_delimiter={repr(self.peak_delimiter)}\n"
            f"  spectrum_delimiter={repr(self.spectrum_delimiter)}\n"
            ")"
        )


    def process_file(self, file_text):
        """
        Processes the text of a JCAMP-DX file into a library of mass spectra.  Outputs a
        MassSpectrumLibrary object containing the file's spectra.
        """
        spectrum_texts = [s.strip() for s in file_text.split(self.spectrum_delimiter) if s.strip()]

        spectrum_object_list = []

        for i, text in enumerate(spectrum_texts):
            spectrum_start_line = 0
            num_peaks = 0
            fields = {}

            # Process the spectrum line by line
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for n, l in enumerate(lines):
                if l.startswith(self.num_peaks_text):
                    # Found the line prefacing the peak list
                    spectrum_start_line = n + 1
                    num_peaks = int(l.split(":")[1])
                    break
                elif ":" in l:
                    # Found a field
                    field_name, value = l.split(":", maxsplit=1)
                    if value.strip():
                        # field has a value
                        fields[field_name.strip()] = value.strip()
                    elif self.keep_empty_fields:
                        # field doesn't have a value, but its existence should be included
                        fields[field_name.strip()] = None
                    else:
                        # field doesn't have a value, and don't want the entry
                        pass
                else:
                    warnings.warn(f"Line with un-delimited content '{l}' found.")

            if num_peaks == 0:
                warnings.warn(f"No spectrum found in text for spectrum number {i+1}.")
                spectrum = np.empty((0,2))
            else:
                spectrum_lines = lines[spectrum_start_line:(spectrum_start_line + num_peaks + 1)]
                spectrum = self.process_spectrum_lines(spectrum_lines)
            spectrum_object = MassSpectrum(fields=fields, spectrum=spectrum)
            if self.max_intensity:
                spectrum_object.rescale_spectrum(self.max_intensity)

            spectrum_object_list.append(MassSpectrum(fields=fields, spectrum=spectrum))

        return MassSpectrumLibrary(spectrum_object_list)
