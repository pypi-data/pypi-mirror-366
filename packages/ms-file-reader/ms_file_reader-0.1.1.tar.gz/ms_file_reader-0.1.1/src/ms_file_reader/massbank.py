"""
Functions for processing mass spectrum files that are structured according to MassBank EU's 
requirements.  All the ones I've seen so far just have a standard .txt extension, so some legwork
is required to determine whether the files in question are actually in this format.

Unlike the JCAMP-DX and MSP file formats, MassBank EU files always (as far as I know) consist of a
single mass spectrum.  As such, this is the one case where the file processor object only ever
outputs a MassSpectrum object instead of a MassSpectrumLibrary.

The fact that this file type is well-standardized means that some of the user-facing options that
are needed on the other processors are irrelevant here, so they're hardcoded in the
super().__init__() call.

Specification of the format is available at
https://github.com/MassBank/MassBank-web/blob/main/Documentation/MassBankRecordFormat.md
"""

# import warnings

from ms_file_reader.common_ms import MassSpectrum, MassSpectrumFileReader


class MassBankFileReader(MassSpectrumFileReader):

    """
    Class for a file processor for files from MassBank EU or conforming to its standards.

    This processor has fewer inputs than the other file types' due to the more rigorous format
    specification.

    Arguments:
    - max_intensity -- If supplied, the spectrum in the file will have their peaks' intensities
    rescaled so that max_intensity is the largest value.
    - validate_files -- Boolean flag intended to run some checks to see if the file adheres to
    MassBank EU's file specification.  Currently unused.
    """


    # These field names are sort of categories -- they can appear an arbitrary number of times, and
    # the field name of interest is after the colon, which would otherwise relegate it to the values
    # in the fields object, so these need separate processing
    INFO_FIELDS = {"AC$CHROMATOGRAPHY", "AC$GENERAL", "AC$MASS_SPECTROMETRY", "MS$FOCUSED_ION", "MS$DATA_PROCESSING"}
    LINK_FIELDS = {"CH$LINK", "SP$LINK"}


    def __init__(self, max_intensity=None, validate_files=False):
        super().__init__(peak_delimiter=None, mz_field=0, intensity_field=1, max_intensity=None)
        self.validate_files = validate_files


    def __repr__(self):
        return (
            "MassBankFileReader(\n"
            f"  max_intensity={self.max_intensity}\n"
            f"  validate_files={self.validate_files}\n"
            ")"
        )


    def process_file(self, file_text):
        """
        Processes the text of a MassBank EU file into a mass spectrum object containing the file's
        spectrum.
        """
        fields = {}
        names = []

        lines = [l.strip() for l in file_text.split("\n")]

        for n, l in enumerate(lines):
            if l.startswith("PK$"):
                break

            field_name, value = l.split(":", maxsplit=1)
            if field_name in self.LINK_FIELDS:
                field_name, value = self._process_subtag_line(value.strip())
            elif field_name in self.INFO_FIELDS:
                field_prefix = field_name.split("$")[1]
                field_name, value = self._process_subtag_line(value.strip(), field_prefix)
            elif field_name == "CH$NAME":
                names.append(value)

            fields[field_name] = value

        fields["NAME"] = names

        peak_count_line = next(l for l in lines if l.startswith("PK$NUM_PEAK"))
        num_peaks = int(peak_count_line.split(":")[1])

        spectrum_start_line = 1 + next(n for n,l in enumerate(lines) if l.startswith("PK$PEAK"))
        spectrum_lines = lines[spectrum_start_line:(spectrum_start_line + num_peaks)]
        spectrum = self.process_spectrum_lines(spectrum_lines)

        return MassSpectrum(fields=fields, spectrum=spectrum)


    def _process_subtag_line(self, subtag_value, field_name_prefix=None):
        """
        Acts on a field with a subtag in the specification.

        Per the way the lines are parsed, some field names (everything left of the first colon in a
        line in a file) are duplicated, and attempting to successively add these to a dictionary
        would result in them overwriting each other.  This tries to give them more unique names.
        """
        field_name, value = subtag_value.split(" ", maxsplit=1)
        if field_name_prefix:
            field_name = field_name_prefix + " - " + field_name
        return field_name, value


    def _validate_file_structure(self, file_text):
        """
        Does some validation of the structure of a text file to see if it matches MassBank EU's
        format.  Currently unused.
        """
        REQUIRED_FIELDS = [
            "ACCESSION", "RECORD_TITLE", "DATE", "AUTHORS", "LICENSE", "CH$NAME",
            "CH$COMPOUND_CLASS", "CH$FORMULA", "CH$EXACT_MASS", "CH$SMILES", "CH$IUPAC",
            "AC$INSTRUMENT", "AC$INSTRUMENT_TYPE", "PK$SPLASH", "PK$NUM_PEAK", "PK$PEAK"
        ]

        field_names = {x.split(":")[0] for x in file_text.split("\n")}
        for rf in REQUIRED_FIELDS:
            if rf not in field_names:
                raise ValueError(f"Required MassBank EU field '{rf}' is not present in file text.")
