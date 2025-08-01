"""Provides tools for importing and standardizing quantitative proteomics data.

This module offers software-specific reader classes to import raw result tables (e.g.,
proteins, peptides, ions) from various proteomics software (MaxQuant, FragPipe,
Spectronaut) and convert them into a standardized `msreport` format. Additionally, it
provides functions for annotating imported data with biological metadata, such as
protein information (e.g., sequence length, molecular weight) and peptide positions,
extracted from a ProteinDatabase (FASTA file).

New columns added to imported protein tables:
- Representative protein
- Leading proteins
- Protein reported by software

Standardized column names for quantitative values (if available in the software output):
- Spectral count "sample name"
- Unique spectral count "sample name"
- Total spectral count "sample name"
- Intensity "sample name"
- LFQ intensity "sample name"
- iBAQ intensity "sample name"
"""

import os
import pathlib
import warnings
from collections import OrderedDict, defaultdict
from typing import Any, Callable, Iterable, Optional, Protocol

import numpy as np
import pandas as pd

import msreport.helper as helper
import msreport.peptidoform
from msreport.errors import ProteinsNotInFastaWarning
from msreport.helper.temp import extract_window_around_position


class Protein(Protocol):
    """Abstract protein entry"""

    # identifier: str
    header: str
    sequence: str
    header_fields: dict[str, str]


class ProteinDatabase(Protocol):
    """Abstract protein database"""

    def __getitem__(self, identifier: str) -> Protein: ...

    def __contains__(self, identifier: str) -> bool: ...


class ResultReader:
    """Base Reader class, is by itself not functional."""

    data_directory: str
    filenames: dict[str, str]
    default_filenames: dict[str, str]
    protected_columns: list[str]
    column_mapping: dict[str, str]
    column_tag_mapping: OrderedDict[str, str]
    sample_column_tags: list[str]

    def __init__(self):
        self.data_directory = ""
        self.filenames = {}

    def _read_file(self, which: str, sep: str = "\t") -> pd.DataFrame:
        """Read a result table.

        Args:
            which: Lookup the filename in self.filenames. If 'which' is not present in
                self.filenames, 'which' is used as the filename.
            sep: Delimiter to use when reading the file
        """
        if which in self.filenames:
            filename = self.filenames[which]
        else:
            filename = which
        filepath = os.path.join(self.data_directory, filename)
        df = pd.read_csv(filepath, sep=sep, low_memory=False)
        str_cols = df.select_dtypes(include=["object"]).columns
        df.loc[:, str_cols] = df.loc[:, str_cols].fillna("")
        return df

    def _rename_columns(self, df: pd.DataFrame, prefix_tag: bool) -> pd.DataFrame:
        """Returns a new dataframe with renamed columns.

        First columns are renamed according to self.column_mapping. Next, tags in
        columns are renamed according to self.column_tag_mapping. Then, for columns
        containing sample names, sample names are and tags are rearranged. Columns from
        self.protected_column_positions are not modified.

        Note that it is essential to rename column names before attempting to rename
        sample columns, as e.g. in FragPipe the "Intensity" substring is present in
        multiple columns.
        """
        new_df = df.copy()

        # Store positions of protected columns
        protected_column_positions = {}
        for col in self.protected_columns:
            if col in new_df.columns:
                protected_column_positions[col] = new_df.columns.get_loc(col)

        # Rename columns
        new_df.rename(columns=self.column_mapping, inplace=True)
        for old_tag, new_tag in self.column_tag_mapping.items():
            new_df.columns = [c.replace(old_tag, new_tag) for c in new_df.columns]

        for tag in self.sample_column_tags:
            # Original columns have already been replaced with new names
            tag = self.column_tag_mapping.get(tag, tag).strip()
            new_df = _rearrange_column_tag(new_df, tag, prefix_tag)

        # Rename protected columns to the original name
        protected_column_mapping = {}
        for col, col_idx in protected_column_positions.items():
            protected_column_mapping[new_df.columns[col_idx]] = col
        new_df.rename(columns=protected_column_mapping, inplace=True)
        return new_df

    def _drop_columns(
        self, df: pd.DataFrame, columns_to_drop: list[str]
    ) -> pd.DataFrame:
        """Returns a new data frame without the specified columns."""
        remaining_columns = []
        for column in df.columns:
            if column not in columns_to_drop:
                remaining_columns.append(column)
        return df[remaining_columns].copy()

    def _drop_columns_by_tag(self, df: pd.DataFrame, tag: str) -> pd.DataFrame:
        """Returns a new data frame without columns containing 'tag'."""
        columns = helper.find_columns(df, tag, must_be_substring=False)
        return self._drop_columns(df, columns)

    def _add_data_directory(self, path) -> None:
        self.data_directory = path


class MaxQuantReader(ResultReader):
    """MaxQuant result reader.

    Methods:
        import_proteins: Reads a "proteinGroups.txt" file and returns a processed
            dataframe, conforming to the MsReport naming convention.
        import_peptides: Reads a "peptides.txt" file and returns a processed
            dataframe, conforming to the MsReport naming convention.
        import_ion_evidence: Reads an "evidence.xt" file and returns a processed
            dataframe, conforming to the MsReport naming convention.

    Attributes:
        default_filenames: (class attribute) Look up of filenames for the result files
            generated by MaxQuant.
        sample_column_tags: (class attribute) Column tags for which an additional column
            is present per sample.
        column_mapping: (class attribute) Used to rename original column names from
            MaxQuant according to the MsReport naming convention.
        column_tag_mapping: (class attribute) Mapping of original sample column tags
            from MaxQuant to column tags according to the MsReport naming convention,
            used to replace column names containing the original column tag.
        protein_info_columns: (class attribute) List of columns that contain protein
            specific information. Used to allow removing all protein specific
            information prior to changing the representative protein.
        protein_info_tags: (class attribute) List of tags present in columns that
            contain protein specific information per sample.
        data_directory (str): Location of the MaxQuant "txt" folder
        filenames (list[str]): Look up of filenames generated by MaxQuant
        contamination_tag (str): Substring present in protein IDs to identify them as
            potential contaminants.
    """

    default_filenames: dict[str, str] = {
        "proteins": "proteinGroups.txt",
        "peptides": "peptides.txt",
        "ion_evidence": "evidence.txt",
    }
    protected_columns: list[str] = ["iBAQ peptides"]
    sample_column_tags: list[str] = [
        "LFQ intensity",
        "Intensity",
        "iBAQ",
        "MS/MS count",
        "Sequence coverage",
    ]
    column_mapping: dict[str, str] = {
        "Peptides": "Total peptides",
        "Sequence coverage [%]": "Sequence coverage",
        "MS/MS count": "Spectral count Combined",  # proteinGroups, evidence
        "MS/MS Count": "Spectral count Combined",  # peptides
        "Sequence": "Peptide sequence",  # peptides, evidence
        "Sequence length": "Protein length",
        "Mol. weight [kDa]": "Molecular weight [kDa]",
        "Experiment": "Sample",
    }
    column_tag_mapping: OrderedDict[str, str] = OrderedDict(
        [("MS/MS count", "Spectral count"), ("iBAQ", "iBAQ intensity")]
    )
    protein_info_columns: list[str] = [
        "Protein names",
        "Gene names",
        "Fasta headers",
        "Sequence coverage [%]",
        "Unique + razor sequence coverage [%]",
        "Unique sequence coverage [%]",
        "Mol. weight [kDa]",
        "Sequence length",
        "Sequence lengths",
        "iBAQ peptides",
    ]
    protein_info_tags: list[str] = ["iBAQ", "Sequence coverage", "site positions"]

    def __init__(
        self, directory: str, isobar: bool = False, contaminant_tag: str = "CON__"
    ) -> None:
        """Initializes the MaxQuantReader.

        Args:
            directory: Location of the MaxQuant "txt" folder.
            isobar: Set to True if quantification strategy was TMT, iTRAQ or similar.
            contaminant_tag: Prefix of Protein ID entries to identify contaminants.
        """
        self._add_data_directory(directory)
        self.filenames: dict[str, str] = self.default_filenames
        self._isobar: bool = isobar
        self._contaminant_tag: str = contaminant_tag

    def import_proteins(
        self,
        filename: Optional[str] = None,
        rename_columns: bool = True,
        prefix_column_tags: bool = True,
        drop_decoy: bool = True,
        drop_idbysite: bool = True,
        drop_protein_info: bool = False,
    ) -> pd.DataFrame:
        """Reads a "proteinGroups.txt" file and returns a processed dataframe.

        Adds three new protein entry columns to comply with the MsReport convention:
        "Protein reported by software", "Leading proteins", "Representative protein".

        "Protein reported by software" contains the first protein ID from the "Majority
        protein IDs" column. "Leading proteins" contain all entries from the "Majority
        protein IDs" column that have the same and highest number of mapped peptides in
        the "Peptide counts (all)" column, multiple protein entries are separated by
        ";". "Representative protein" contains the first entry form "Leading proteins".

        Several columns in the "combined_protein.tsv" file contain information specific
        for the protein entry of the "Protein" column. If leading proteins will be
        re-sorted later, it is recommended to remove columns containing protein specific
        information by setting 'drop_protein_info=True'.

        Args:
            filename: allows specifying an alternative filename, otherwise the default
                filename is used.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            prefix_column_tags: If True, column tags such as "Intensity" are added
                in front of the sample names, e.g. "Intensity sample_name". If False,
                column tags are added afterwards, e.g. "Sample_name Intensity"; default
                True.
            drop_decoy: If True, decoy entries are removed and the "Reverse" column is
                dropped; default True.
            drop_idbysite: If True, protein groups that were only identified by site are
                removed and the "Only identified by site" columns is dropped; default
                True.
            drop_protein_info: If True, columns containing protein specific information,
                such as "Gene names", "Sequence coverage [%]" or "iBAQ peptides". See
                MaxQuantReader.protein_info_columns and MaxQuantReader.protein_info_tags
                for a full list of columns that will be removed. Default False.

        Returns:
            A dataframe containing the processed protein table.
        """
        df = self._read_file("proteins" if filename is None else filename)
        df = self._add_protein_entries(df)

        if drop_decoy:
            df = self._drop_decoy(df)
        if drop_idbysite:
            df = self._drop_idbysite(df)
        if drop_protein_info:
            df = self._drop_columns(df, self.protein_info_columns)
            for tag in self.protein_info_tags:
                df = self._drop_columns_by_tag(df, tag)
        if rename_columns:
            df = self._rename_columns(df, prefix_column_tags)
        return df

    def import_peptides(
        self,
        filename: Optional[str] = None,
        rename_columns: bool = True,
        prefix_column_tags: bool = True,
        drop_decoy: bool = True,
    ) -> pd.DataFrame:
        """Reads a "peptides.txt" file and returns a processed dataframe.

        Adds new columns to comply with the MsReport convention:
        "Protein reported by software" and "Representative protein", both contain the
        first entry from "Leading razor protein".

        Args:
            filename: allows specifying an alternative filename, otherwise the default
                filename is used.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            prefix_column_tags: If True, column tags such as "Intensity" are added
                in front of the sample names, e.g. "Intensity sample_name". If False,
                column tags are added afterwards, e.g. "Sample_name Intensity"; default
                True.
            drop_decoy: If True, decoy entries are removed and the "Reverse" column is
                dropped; default True.

        Returns:
            A dataframe containing the processed peptide table.
        """
        # TODO: not tested
        df = self._read_file("peptides" if filename is None else filename)
        df["Protein reported by software"] = _extract_protein_ids(
            df["Leading razor protein"]
        )
        df["Representative protein"] = df["Protein reported by software"]
        # Note that _add_protein_entries would need to be adapted for the peptide table.
        # df = self._add_protein_entries(df)
        if drop_decoy:
            df = self._drop_decoy(df)
        if rename_columns:
            df = self._rename_columns(df, prefix_column_tags)
        return df

    def import_ion_evidence(
        self,
        filename: Optional[str] = None,
        rename_columns: bool = True,
        rewrite_modifications: bool = True,
        drop_decoy: bool = True,
    ) -> pd.DataFrame:
        """Reads an "evidence.txt" file and returns a processed dataframe.

        Adds new columns to comply with the MsReport convention. "Modified sequence",
        "Modifications columns", "Modification localization string". "Protein reported
        by software" and "Representative protein", both contain the first entry from
        "Leading razor protein". "Ion ID" contains unique entries for each ion, which
        are generated by concatenating the "Modified sequence" and "Charge" columns, and
        if present, the "Compensation voltage" column.

        "Modified sequence" entries contain modifications within square brackets.
        "Modification" entries are strings in the form of "position:modification_tag",
        multiple modifications are joined by ";". An example for a modified sequence and
        a modification entry: "PEPT[Phospho]IDO[Oxidation]", "4:Phospho;7:Oxidation".

        "Modification localization string" contains localization probabilities in the
        format "Mod1@Site1:Probability1,Site2:Probability2;Mod2@Site3:Probability3",
        e.g. "15.9949@11:1.000;79.9663@3:0.200,4:0.800". Refer to
        `msreport.peptidoform.make_localization_string` for details.

        Args:
            filename: Allows specifying an alternative filename, otherwise the default
                filename is used.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            rewrite_modifications: If True, the peptide format in "Modified sequence" is
                changed according to the MsReport convention, and a "Modifications" is
                added to contains the amino acid position for all modifications.
                Requires 'rename_columns' to be true. Default True.
            drop_decoy: If True, decoy entries are removed and the "Reverse" column is
                dropped; default True.

        Returns:
            A dataframe containing the processed ion table.
        """
        # TODO: not tested
        df = self._read_file("ion_evidence" if filename is None else filename)
        df["Protein reported by software"] = _extract_protein_ids(
            df["Leading razor protein"]
        )
        df["Representative protein"] = df["Protein reported by software"]

        if drop_decoy:
            df = self._drop_decoy(df)
        if rename_columns:
            # Actually there are no column tags as the table is in long format
            df = self._rename_columns(df, prefix_tag=True)
        if rewrite_modifications and rename_columns:
            df = self._add_peptide_modification_entries(df)
            df = self._add_modification_localization_string(df)
            df["Ion ID"] = df["Modified sequence"] + "_c" + df["Charge"].astype(str)
            if "Compensation voltage" in df.columns:
                _cv = df["Compensation voltage"].astype(str)
                df["Ion ID"] = df["Ion ID"] + "_cv" + _cv
        return df

    def _add_protein_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds standardized protein entry columns to the data frame.

        Adds new columns to comply with the MsReport convention. "Protein reported by
        software" contains the first protein ID from the "Majority protein IDs" column.
        "Leading proteins" contain all entries from the "Majority protein IDs" column
        that have the same and highest number of mapped peptides in the "Peptide counts
        (all)" column, multiple protein entries are separated by ";". "Representative
        protein" contains the first entry form "Leading proteins". "Potential
        contaminant" contains Boolean values.

        Args:
            df: Dataframe containing a MaxQuant result table.

        Returns:
            A copy of the input dataframe with updated columns.
        """
        # NOTE: not tested directly, only via integration #
        leading_protein_entries = self._collect_leading_protein_entries(df)
        protein_entry_table = _process_protein_entries(
            leading_protein_entries, self._contaminant_tag
        )
        for key in protein_entry_table:
            df[key] = protein_entry_table[key]
        return df

    def _collect_leading_protein_entries(self, df: pd.DataFrame) -> list[list[str]]:
        """Generates a list of leading proteins from the "Majority protein IDs" column.

        Each entry in the list contains a list of all entries from the "Majority
        protein IDs" column that have the same and highest number of mapped peptides in
        the "Peptide counts (all)" column.

        Can only be used for "proteinGroups.txt" tables.

        Args:
            df: Dataframe containing a "proteinGroups.txt" table.

        Returns:
            A list of the same length as the input dataframe. Each position contains a
            list of leading protein entries, which a minimum of one entry.
        """
        leading_protein_entries = []
        for majority_ids_entry, count_entry in zip(
            df["Majority protein IDs"], df["Peptide counts (all)"]
        ):
            proteins = majority_ids_entry.split(";")
            counts = [int(i) for i in count_entry.split(";")]
            highest_count = max(counts)
            protein_entries = [
                f for f, c in zip(proteins, counts) if c >= highest_count
            ]
            leading_protein_entries.append(protein_entries)
        return leading_protein_entries

    def _add_peptide_modification_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds standardized "Modified sequence" and "Modifications columns".

        "Modified sequence" entries contain modifications within square brackets.
        "Modification" entries are strings in the form of "position:modification_text",
        multiple modifications are joined by ";". An example for a modified sequence and
        a modification entry: "PEPT[Phospho]IDO[Oxidation]", "4:Phospho;7:Oxidation".

        Requires the columns "Peptide sequence" and "Modified sequence" from the
        software output.

        Args:
            df: Dataframe containing "Peptide sequence" and "Modified sequence" columns.

        Returns:
            A copy of the input dataframe with updated columns.
        """
        # TODO: not tested
        mod_sequences = df["Modified sequence"].str.split("_").str[1]
        mod_entries = _generate_modification_entries(
            df["Peptide sequence"], mod_sequences, "(", ")"
        )
        new_df = df.copy()
        new_df["Modified sequence"] = mod_entries["Modified sequence"]
        new_df["Modifications"] = mod_entries["Modifications"]
        return new_df

    def _add_modification_localization_string(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds modification localization string columns.

        Extracts localization probabilities from all "MODIFICATION Probabilities"
        columns, converts them into the standardized modification localization string
        format used by msreport, and adds new columns with the tag
        "Modification localization string". Probabilities are written in the format
        "Mod1@Site1:Probability1,Site2:Probability2;Mod2@Site3:Probability3",
        e.g. "15.9949@11:1.000;79.9663@3:0.200,4:0.800". Refer to
        `msreport.peptidoform.make_localization_string` for details.

        Args:
            df: Dataframe containing a "MODIFICATION Probabilities" columns.

        Returns:
            A copy of the input dataframe with updated columns.
        """
        # TODO: not tested
        new_df = df.copy()
        mod_probability_columns = msreport.helper.find_columns(new_df, "Probabilities")
        localization_string_column = "Modification localization string"

        mod_localization_probabilities: list[dict[str, dict[int, float]]] = [
            {} for _ in range(new_df.shape[0])
        ]
        for probability_column in mod_probability_columns:
            # FUTURE: Type should be checked and enforced during the import
            if not pd.api.types.is_string_dtype(new_df[probability_column].dtype):
                new_df[probability_column] = (
                    new_df[probability_column].astype(str).replace("nan", "")
                )
            mod_tag = probability_column.split("Probabilities")[0].strip()

            for row_idx, entry in enumerate(new_df[probability_column]):
                mod_probabilities = extract_maxquant_localization_probabilities(entry)
                if mod_probabilities:
                    mod_localization_probabilities[row_idx][mod_tag] = mod_probabilities

        localization_strings = []
        for mod_localization_entry in mod_localization_probabilities:
            localization_string = msreport.peptidoform.make_localization_string(
                mod_localization_entry
            )
            localization_strings.append(localization_string)
        new_df[localization_string_column] = localization_strings
        return new_df

    def _drop_decoy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Returns a dataframe not containing decoy entries.

        Also removes the "Reverse" column.
        """
        return self._drop_columns(df.loc[df["Reverse"] != "+"], ["Reverse"])

    def _drop_idbysite(self, df: pd.DataFrame) -> pd.DataFrame:
        """Returns a dataframe not containing entries only identified by site.

        Also removes the "Only identified by site" column.
        """
        return self._drop_columns(
            df.loc[df["Only identified by site"] != "+"], ["Only identified by site"]
        )


class FragPipeReader(ResultReader):
    """FragPipe result reader.

    Methods:
        import_design: Reads a "fragpipe-files.fp-manifest" file and returns a
            processed design dataframe.
        import_proteins: Reads a "combined_protein.tsv" or "protein.tsv" file and
            returns a processed dataframe, conforming to the MsReport naming
            convention.
        import_peptides: Reads a "combined_peptide.tsv" or "peptide.tsv" file and
            returns a processed dataframe, conforming to the MsReport naming
            convention.
        import_ions: Reads a "combined_ion.tsv" or "ion.tsv" file and returns a
            processed dataframe, conforming to the MsReport naming convention.
        import_ion_evidence: Reads and concatenates all "ion.tsv" files and returns a
            processed dataframe, conforming to the MsReport naming convention.

    Attributes:
        default_filenames: (class attribute) Look up of default filenames of the result
            files generated by FragPipe.
        isobar_filenames: (class attribute) Look up of default filenames of the result
            files generated by FragPipe, which are relevant when using isobaric
            quantification.
        sample_column_tags: (class attribute) Tags (column name substrings) that
            idenfity sample columns. Sample columns are those, for which one unique
            column is present per sample, for example intensity columns.
        column_mapping: (class attribute) Used to rename original column names from
            FragPipe according to the MsReport naming convention.
        column_tag_mapping: (class attribute) Mapping of original sample column tags
            from FragPipe to column tags according to the MsReport naming convention,
            used to replace column names containing the original column tag.
        protein_info_columns: (class attribute) List of columns that contain information
            specific to the leading protein.
        protein_info_tags: (class attribute) List of substrings present in columns that
            contain information specific to the leading protein.
        data_directory (str): Location of the folder containing FragPipe result files.
        filenames (dict[str, str]): Look up of FragPipe result filenames used for
            importing protein or other tables.
        contamination_tag (str): Substring present in protein IDs to identify them as
            potential contaminants.
    """

    default_filenames: dict[str, str] = {
        "proteins": "combined_protein.tsv",
        "peptides": "combined_peptide.tsv",
        "ions": "combined_ion.tsv",
        "ion_evidence": "ion.tsv",
        "psm_evidence": "psm.tsv",
        "design": "fragpipe-files.fp-manifest",
    }
    isobar_filenames: dict[str, str] = {
        "proteins": "protein.tsv",
        "peptides": "peptide.tsv",
        "ions": "ion.tsv",
    }
    sil_filenames: dict[str, str] = {
        "proteins": "combined_protein_label_quant.tsv",
        "peptides": "combined_modified_peptide_label_quant.tsv",
        "ions": "combined_ion_label_quant.tsv",
    }

    protected_columns: list[str] = []
    sample_column_tags: list[str] = [
        "Spectral Count",
        "Unique Spectral Count",
        "Total Spectral Count",
        "Intensity",
        "MaxLFQ Intensity",
    ]
    column_mapping: dict[str, str] = {
        "Peptide": "Peptide sequence",  # PSM
        "Modified Peptide": "Modified sequence",  # PSM
        "Protein Start": "Start position",  # PSM
        "Protein End": "End position",  # PSM
        "Number of Missed Cleavages": "Missed cleavage",  # PSM
        "PeptideProphet Probability": "Probability",  # PSM
        "Compensation Voltage": "Compensation voltage",  # PSM and ion
        "Peptide Sequence": "Peptide sequence",  # Peptide and ion
        "Modified Sequence": "Modified sequence",  # Modified peptide and ion
        "Start": "Start position",  # Peptide and ion
        "End": "End position",  # Peptide and ion
        "Mapped Proteins": "Mapped proteins",  # All PSM, ion, and peptide tables
        "Combined Total Peptides": "Total peptides",  # From LFQ
        "Total Peptides": "Total peptides",  # From TMT
        "Description": "Protein name",
        "Protein Length": "Protein length",
        "Entry Name": "Protein entry name",
        "Gene": "Gene name",
    }
    column_tag_mapping: OrderedDict[str, str] = OrderedDict(
        [
            ("MaxLFQ Intensity", "LFQ intensity"),
            ("Total Spectral Count", "Total spectral count"),
            ("Unique Spectral Count", "Unique spectral count"),
            ("Spectral Count", "Spectral count"),
        ]
    )
    protein_info_columns: list[str] = [
        "Protein",
        "Protein ID",
        "Entry Name",
        "Gene",
        "Protein Length",
        "Organism",
        "Protein Existence",
        "Description",
        "Indistinguishable Proteins",
    ]
    protein_info_tags: list[str] = []

    def __init__(
        self,
        directory: str,
        isobar: bool = False,
        sil: bool = False,
        contaminant_tag: str = "contam_",
    ) -> None:
        """Initializes the FragPipeReader.

        Args:
            directory: Location of the FragPipe result folder
            isobar: Set to True if quantification strategy was TMT, iTRAQ or similar;
                default False.
            sil: Set to True if the FragPipe result files are from a stable isotope
                labeling experiment, such as SILAC; default False.
            contaminant_tag: Prefix of Protein ID entries to identify contaminants;
                default "contam_".
        """
        if sil and isobar:
            raise ValueError("Cannot set both 'isobar' and 'sil' to True.")
        self._add_data_directory(directory)
        self._isobar: bool = isobar
        self._sil: bool = sil
        self._contaminant_tag: str = contaminant_tag
        if isobar:
            self.filenames = self.isobar_filenames
        elif sil:
            self.filenames = self.sil_filenames
        else:
            self.filenames = self.default_filenames

    def import_design(
        self, filename: Optional[str] = None, sort: bool = False
    ) -> pd.DataFrame:
        """Read a 'fp-manifest' file and returns a processed design dataframe.

        The manifest columns "Path", "Experiment", and "Bioreplicate" are mapped to the
        design table columns "Rawfile", "Experiment", and "Replicate". The "Rawfile"
        column is extracted as the filename from the full path. The "Sample" column is
        generated by combining "Experiment" and "Replicate" with an underscore
        (e.g., "Experiment_Replicate"), except when "Replicate" is empty, in which case
        "Sample" is set to "Experiment". If "Experiment" is missing, it is set to "exp"
        by default.

        Args:
            filename: Allows specifying an alternative filename, otherwise the default
                filename is used.
            sort: If True, the design dataframe is sorted by "Experiment" and
                "Replicate"; default False.

        Returns:
            A dataframe containing the processed design table with columns:
            "Sample", "Experiment", "Replicate", "Rawfile".

        Raises:
            FileNotFoundError: If the specified manifest file does not exist.
        """
        if filename is None:
            filepath = os.path.join(self.data_directory, self.filenames["design"])
        else:
            filepath = os.path.join(self.data_directory, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"File '{filepath}' does not exist. Please check the file path."
            )
        fp_manifest = (
            pd.read_csv(
                filepath, sep="\t", header=None, na_values=[""], keep_default_na=False
            )
            .fillna("")
            .astype(str)
        )
        fp_manifest.columns = ["Path", "Experiment", "Bioreplicate", "Data type"]

        design = pd.DataFrame(
            {
                "Sample": "",
                "Experiment": fp_manifest["Experiment"],
                "Replicate": fp_manifest["Bioreplicate"],
                "Rawfile": fp_manifest["Path"].apply(
                    # Required to handle Windows and Unix style paths on either system
                    lambda x: x.replace("\\", "/").split("/")[-1]
                ),
            }
        )
        # FragPipe uses "exp" for missing 'Experiment' values
        design.loc[design["Experiment"] == "", "Experiment"] = "exp"
        # FragPipe combines 'Experiment' + "_" + 'Replicate' into 'Sample', except when
        # 'Replicate' is empty, in which case 'Sample' is set to 'Experiment'.
        design["Sample"] = design["Experiment"] + "_" + design["Replicate"]
        design.loc[design["Replicate"] == "", "Sample"] = design["Experiment"]

        if sort:
            design.sort_values(by=["Experiment", "Replicate"], inplace=True)
            design.reset_index(drop=True, inplace=True)
        return design

    def import_proteins(
        self,
        filename: Optional[str] = None,
        rename_columns: bool = True,
        prefix_column_tags: bool = True,
        drop_protein_info: bool = False,
    ) -> pd.DataFrame:
        """Reads a "combined_protein.tsv" or "protein.tsv" file and returns a processed
        dataframe.

        Adds four protein entry columns to comply with the MsReport convention:
        "Protein reported by software", "Leading proteins", "Representative protein",
        "Potential contaminant".

        "Protein reported by software" contains the protein ID extracted from the
        "Protein" column. "Leading proteins" contains the combined protein IDs extracted
        from the "Protein" and "Indistinguishable Proteins" columns, multiple entries
        are separated by ";". "Representative protein" contains the first entry form
        "Leading proteins".

        Several columns in the "combined_protein.tsv" file contain information specific
        for the protein entry of the "Protein" column. If leading proteins will be
        re-sorted later, it is recommended to remove columns containing protein specific
        information by setting 'drop_protein_info=True'..

        Args:
            filename: Allows specifying an alternative filename, otherwise the default
                filename is used.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            prefix_column_tags: If True, column tags such as "Intensity" are added
                in front of the sample names, e.g. "Intensity sample_name". If False,
                column tags are added afterwards, e.g. "Sample_name Intensity"; default
                True.
            drop_protein_info: If True, columns containing protein specific information,
                such as "Gene" or "Protein Length". See
                FragPipeReader.protein_info_columns and FragPipeReader.protein_info_tags
                for a full list of columns that will be removed. Default False.

        Returns:
            A dataframe containing the processed protein table.
        """
        df = self._read_file("proteins" if filename is None else filename)
        df = self._add_protein_entries(df)
        if drop_protein_info:
            df = self._drop_columns(df, self.protein_info_columns)
            for tag in self.protein_info_tags:
                df = self._drop_columns_by_tag(df, tag)
        if rename_columns:
            df = self._rename_columns(df, prefix_column_tags)
        return df

    def import_peptides(
        self,
        filename: Optional[str] = None,
        rename_columns: bool = True,
        prefix_column_tags: bool = True,
    ) -> pd.DataFrame:
        """Reads a "combined_peptides.txt" file and returns a processed dataframe.

        Adds a new column to comply with the MsReport convention:
        "Protein reported by software"

        Args:
            filename: allows specifying an alternative filename, otherwise the default
                filename is used.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            prefix_column_tags: If True, column tags such as "Intensity" are added
                in front of the sample names, e.g. "Intensity sample_name". If False,
                column tags are added afterwards, e.g. "Sample_name Intensity"; default
                True.

        Returns:
            A dataframe containing the processed peptide table.
        """
        # TODO: not tested
        df = self._read_file("peptides" if filename is None else filename)
        df["Protein reported by software"] = _extract_protein_ids(df["Protein"])
        df["Representative protein"] = df["Protein reported by software"]
        df["Mapped Proteins"] = self._collect_mapped_proteins(df)
        # Note that _add_protein_entries would need to be adapted for the peptide table.
        # df = self._add_protein_entries(df)
        if rename_columns:
            df = self._rename_columns(df, prefix_column_tags)
        return df

    def import_ions(
        self,
        filename: Optional[str] = None,
        rename_columns: bool = True,
        rewrite_modifications: bool = True,
        prefix_column_tags: bool = True,
    ) -> pd.DataFrame:
        """Reads a "combined_ion.tsv" or "ion.tsv" file and returns a processed
        dataframe.

        Adds new columns to comply with the MsReport convention. "Modified sequence"
        and "Modifications columns". "Protein reported by software" and "Representative
        protein", both contain the first entry from "Leading razor protein". "Ion ID"
        contains unique entries for each ion, which are generated by concatenating the
        "Modified sequence" and "Charge" columns, and if present, the
        "Compensation voltage" column.

        "Modified sequence" entries contain modifications within square brackets.
        "Modification" entries are strings in the form of "position:modification_text",
        multiple modifications are joined by ";". An example for a modified sequence and
        a modification entry: "PEPT[Phospho]IDO[Oxidation]", "4:Phospho;7:Oxidation".

        Note that currently the format of the modification itself, as well as the
        site localization probability are not modified; and no protein site entries are
        added.

        Args:
            filename: Allows specifying an alternative filename, otherwise the default
                filename is used.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            rewrite_modifications: If True, the peptide format in "Modified sequence" is
                changed according to the MsReport convention, and a "Modifications" is
                added to contains the amino acid position for all modifications.
                Requires 'rename_columns' to be true. Default True.
            prefix_column_tags: If True, column tags such as "Intensity" are added
                in front of the sample names, e.g. "Intensity sample_name". If False,
                column tags are added afterwards, e.g. "Sample_name Intensity"; default
                True.

        Returns:
            A DataFrame containing the processed ion table.
        """
        # TODO: not tested #
        df = self._read_file("ions" if filename is None else filename)

        # FUTURE: replace this by _add_protein_entries(df, False) if FragPipe adds
        #         'Indistinguishable Proteins' to the ion table.
        df["Protein reported by software"] = _extract_protein_ids(df["Protein"])
        df["Representative protein"] = df["Protein reported by software"]
        df["Mapped Proteins"] = self._collect_mapped_proteins(df)

        if rename_columns:
            df = self._rename_columns(df, prefix_column_tags)
        if rewrite_modifications and rename_columns:
            df = self._add_peptide_modification_entries(df)
            df = self._add_modification_localization_string(df, prefix_column_tags)
            df["Ion ID"] = df["Modified sequence"] + "_c" + df["Charge"].astype(str)
            if "Compensation voltage" in df.columns:
                _cv = df["Compensation voltage"].astype(str)
                df["Ion ID"] = df["Ion ID"] + "_cv" + _cv

        return df

    def import_ion_evidence(
        self,
        filename: Optional[str] = None,
        rename_columns: bool = True,
        rewrite_modifications: bool = True,
        prefix_column_tags: bool = True,
    ) -> pd.DataFrame:
        """Reads and concatenates all "ion.tsv" files and returns a processed dataframe.

        Adds new columns to comply with the MsReport convention. "Modified sequence",
        "Modifications", and "Modification localization string" columns. "Protein
        reported by software" and "Representative protein", both contain the first entry
        from "Leading razor protein". "Ion ID" contains unique entries for each ion,
        which are generated by concatenating the "Modified sequence" and "Charge"
        columns, and if present, the "Compensation voltage" column.

        "Modified sequence" entries contain modifications within square brackets.
        "Modification" entries are strings in the form of "position:modification_text",
        multiple modifications are joined by ";". An example for a modified sequence and
        a modification entry: "PEPT[Phospho]IDO[Oxidation]", "4:Phospho;7:Oxidation".

        "Modification localization string" contains localization probabilities in the
        format "Mod1@Site1:Probability1,Site2:Probability2;Mod2@Site3:Probability3",
        e.g. "15.9949@11:1.000;79.9663@3:0.200,4:0.800". Refer to
        `msreport.peptidoform.make_localization_string` for details.

        Args:
            filename: Allows specifying an alternative filename, otherwise the default
                filename is used.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            rewrite_modifications: If True, the peptide format in "Modified sequence" is
                changed according to the MsReport convention, and a "Modifications" is
                added to contains the amino acid position for all modifications.
                Requires 'rename_columns' to be true. Default True.
            prefix_column_tags: If True, column tags such as "Intensity" are added
                in front of the sample names, e.g. "Intensity sample_name". If False,
                column tags are added afterwards, e.g. "Sample_name Intensity"; default
                True.

        Returns:
            A DataFrame containing the processed ion table.
        """
        # TODO: not tested #

        # --- Get paths of all ion.tsv files --- #
        if filename is None:
            filename = self.default_filenames["ion_evidence"]

        ion_table_paths = []
        for path in pathlib.Path(self.data_directory).iterdir():
            ion_table_path = path / filename
            if path.is_dir() and ion_table_path.exists():
                ion_table_paths.append(ion_table_path)

        # --- like self._read_file --- #
        ion_tables = []
        for filepath in ion_table_paths:
            table = pd.read_csv(filepath, sep="\t", low_memory=False)
            str_cols = table.select_dtypes(include=["object"]).columns
            table.loc[:, str_cols] = table.loc[:, str_cols].fillna("")

            table["Sample"] = filepath.parent.name
            ion_tables.append(table)
        df = pd.concat(ion_tables, ignore_index=True)

        # --- Process dataframe --- #
        df["Ion ID"] = df["Modified Sequence"] + "_c" + df["Charge"].astype(str)
        if "Compensation Voltage" in df.columns:
            df["Ion ID"] = df["Ion ID"] + "_cv" + df["Compensation Voltage"].astype(str)
        # FUTURE: replace this by _add_protein_entries(df, False) if FragPipe adds
        #         'Indistinguishable Proteins' to the ion table.
        df["Protein reported by software"] = _extract_protein_ids(df["Protein"])
        df["Representative protein"] = df["Protein reported by software"]
        df["Mapped Proteins"] = self._collect_mapped_proteins(df)

        if rename_columns:
            df = self._rename_columns(df, prefix_column_tags)
        if rewrite_modifications and rename_columns:
            df = self._add_peptide_modification_entries(df)
            df = self._add_modification_localization_string(df, prefix_column_tags)
        return df

    def import_psm_evidence(
        self,
        filename: Optional[str] = None,
        rename_columns: bool = True,
        rewrite_modifications: bool = True,
    ) -> pd.DataFrame:
        """Concatenate all "psm.tsv" files and return a processed dataframe.

        Args:
            filename: Allows specifying an alternative filename, otherwise the default
                filename is used.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            rewrite_modifications: If True, the peptide format in "Modified sequence" is
                changed according to the MsReport convention, and a "Modifications" is
                added to contains the amino acid position for all modifications.
                Requires 'rename_columns' to be true. Default True.

        Returns:
            A DataFrame containing the processed psm evidence tables.
        """
        if filename is None:
            filename = self.default_filenames["psm_evidence"]

        psm_table_paths = []
        for path in pathlib.Path(self.data_directory).iterdir():
            psm_table_path = path / filename
            if path.is_dir() and psm_table_path.exists():
                psm_table_paths.append(psm_table_path)

        psm_tables = []
        for filepath in psm_table_paths:
            table = pd.read_csv(filepath, sep="\t", low_memory=False)
            str_cols = table.select_dtypes(include=["object"]).columns
            table.loc[:, str_cols] = table.loc[:, str_cols].fillna("")

            table["Sample"] = filepath.parent.name
            psm_tables.append(table)
        df = pd.concat(psm_tables, ignore_index=True)

        df["Protein reported by software"] = _extract_protein_ids(df["Protein"])
        df["Representative protein"] = df["Protein reported by software"]
        df["Mapped Proteins"] = self._collect_mapped_proteins(df)

        if rename_columns:
            df = self._rename_columns(df, prefix_tag=True)
        if rewrite_modifications and rename_columns:
            mod_entries = _generate_modification_entries_from_assigned_modifications(
                df["Peptide sequence"], df["Assigned Modifications"]
            )
            df["Modified sequence"] = mod_entries["Modified sequence"]
            df["Modifications"] = mod_entries["Modifications"]
        return df

    def _add_protein_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds standardized protein entry columns to the data frame.

        Adds new columns to comply with the MsReport convention. "Protein reported by
        software" contains the protein ID extracted from the "Protein" column. "Leading
        proteins" contains the combined protein IDs extracted from the "Protein" and
        "Indistinguishable Proteins" columns, multiple entries are separated by ";".
        "Representative protein" contains the first entry form "Leading proteins".
        "Potential contaminant" contains Boolean values.

        Args:
            df: Dataframe containing a FragPipe result table.

        Returns:
            A copy of the input dataframe with updated columns.
        """
        leading_protein_entries = self._collect_leading_protein_entries(df)
        protein_entry_table = _process_protein_entries(
            leading_protein_entries, self._contaminant_tag
        )
        for key in protein_entry_table:
            df[key] = protein_entry_table[key]
        return df

    def _collect_mapped_proteins(self, df: pd.DataFrame) -> list[str]:
        """Generates a list of mapped proteins entries.

        This method extracts protein IDs from the 'Representative protein' and the
        'Mapped Proteins' column and combines them into a single string for each row,
        where multiple protein IDs are separated by semicolons.

        Args:
            df: DataFrame containing the 'Mapped Proteins' column.

        Returns:
            A list of mapped proteins entries.
        """
        mapped_proteins_entries = []
        for protein, mapped_protein_fp in zip(
            df["Representative protein"],
            df["Mapped Proteins"].astype(str).replace("nan", ""),
            strict=True,
        ):
            if mapped_protein_fp == "":
                mapped_proteins = [protein]
            else:
                additional_mapped_proteins = msreport.reader._extract_protein_ids(
                    mapped_protein_fp.split(", ")
                )
                mapped_proteins = [protein] + additional_mapped_proteins
            mapped_proteins_entries.append(";".join(mapped_proteins))
        return mapped_proteins_entries

    def _collect_leading_protein_entries(self, df: pd.DataFrame) -> list[list[str]]:
        """Generates a list of leading protein entries.

        Each entry in the list contains a list of all entries from the "Protein" and
        "Indistinguishable Proteins" columns.

        Can only be used for "combined_protein.tsv" and "protein.tsv" tables.

        Args:
            df: Dataframe containing a protein table.

        Returns:
            A list of the same length as the input dataframe. Each position contains a
            list of leading protein entries, which a minimum of one entry.
        """
        if self._sil:  # No "Indistinguishable Proteins" columns in 'SIL' data
            return [[p] for p in df["Protein"]]

        leading_protein_entries = []
        for protein_entry, indist_protein_entry in zip(
            df["Protein"], df["Indistinguishable Proteins"].fillna("").astype(str)
        ):
            protein_entries = [protein_entry]
            if indist_protein_entry:
                for entry in indist_protein_entry.split(", "):
                    protein_entries.append(entry)
            leading_protein_entries.append(protein_entries)
        return leading_protein_entries

    def _add_peptide_modification_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds standardized "Modified sequence" and "Modifications columns".

        "Modified sequence" entries contain modifications within square brackets.
        "Modification" entries are strings in the form of "position:modification_text",
        multiple modifications are joined by ";". An example for a modified sequence and
        a modification entry: "PEPT[Phospho]IDO[Oxidation]", "4:Phospho;7:Oxidation".

        Requires the columns "Peptide sequence" and "Modified sequence" from the
        software output.

        Args:
            df: Dataframe containing "Peptide sequence" and "Modified sequence" columns.

        Returns:
            A copy of the input dataframe with updated columns.
        """
        # TODO: not tested
        mod_sequences = (
            df["Modified sequence"]
            .str.replace("n[", "[", regex=False)
            .str.replace("c[", "[", regex=False)
        )
        mod_entries = _generate_modification_entries(
            df["Peptide sequence"], mod_sequences, "[", "]"
        )
        new_df = df.copy()
        new_df["Modified sequence"] = mod_entries["Modified sequence"]
        new_df["Modifications"] = mod_entries["Modifications"]
        return new_df

    def _add_modification_localization_string(
        self,
        df: pd.DataFrame,
        prefix_column_tag: bool,
    ) -> pd.DataFrame:
        """Adds modification localization string columns.

        Extracts localization probabilities from "Localization" or "SAMPLE Localization"
        columns, converts them into the standardized modification localization string
        format used by msreport, and adds new columns with the tag
        "Modification localization string". Probabilities are written in the format
        "Mod1@Site1:Probability1,Site2:Probability2;Mod2@Site3:Probability3",
        e.g. "15.9949@11:1.000;79.9663@3:0.200,4:0.800". Refer to
        `msreport.peptidoform.make_localization_string` for details.

        Args:
            df: Dataframe containing a "Localization" column.
            prefix_column_tag: If True, the "Modification localization string" tag is
                added in front of the sample name. If False, it is added afterwards.

        Returns:
            A copy of the input dataframe with updated columns.
        """
        # TODO: not tested
        new_df = df.copy()
        column_mapping = {}
        for column in msreport.helper.find_columns(new_df, "Localization"):
            if column == "Localization":
                new_column = "Modification localization string"
            else:
                sample = column.replace("Localization", "").strip()
                if prefix_column_tag:
                    new_column = f"Modification localization string {sample}"
                else:
                    new_column = f"{sample} Modification localization string"
            column_mapping[column] = new_column

        for localization_column, new_column in column_mapping.items():
            # FUTURE: Type should be checked and enforced during the import
            if not pd.api.types.is_string_dtype(new_df[localization_column].dtype):
                new_df[localization_column] = (
                    new_df[localization_column].astype(str).replace("nan", "")
                )

            localization_strings = []
            for localization in new_df[localization_column]:
                localization_probabilities = (
                    msreport.reader.extract_fragpipe_localization_probabilities(
                        localization
                    )
                )
                localization_string = msreport.peptidoform.make_localization_string(
                    localization_probabilities
                )
                localization_strings.append(localization_string)
            new_df[new_column] = localization_strings
        return new_df


class SpectronautReader(ResultReader):
    """Spectronaut result reader.

    Methods:
        import_proteins: Reads a LFQ protein report file and returns a processed
            dataframe, conforming to the MsReport naming convention.
        import_design: Reads a ConditionSetup file and returns a processed dataframe,
            containing the default columns of an MsReport experimental design table.

    Attributes:
        default_filetags: (class attribute) Look up of default file tags for the outputs
            generated by Spectronaut.
        sample_column_tags: (class attribute) Tags (column name substrings) that
            idenfity sample columns. Sample columns are those, for which one unique
            column is present per sample, for example intensity columns.
        column_mapping: (class attribute) Used to rename original column names from
            Spectronaut according to the MsReport naming convention.
        column_tag_mapping: (class attribute) Mapping of original sample column tags
            from Spectronaut to column tags according to the MsReport naming convention,
            used to replace column names containing the original column tag.
        protein_info_columns: (class attribute) List of columns that contain information
            specific to the leading protein.
        protein_info_tags: (class attribute) List of substrings present in columns that
            contain information specific to the leading protein.
        data_directory (str): Location of the folder containing Spectronaut result
            files.
        filetags (dict[str, str]): Look up of file tags used for matching files during
            the import of protein or other tables.
        contamination_tag (str): Substring present in protein IDs to identify them as
            potential contaminants.
    """

    default_filetags: dict[str, str] = {
        "proteins": "report",
        "design": "conditionsetup",
    }
    protected_columns: list[str] = []
    column_mapping: dict[str, str] = {
        "R.FileName": "Filename",
        "R.Label": "Sample",
        "PG.Qvalue": "Protein qvalue",
        "PG.Cscore": "Protein cscore",
        "PG.NrOfStrippedSequencesIdentified (Experiment-wide)": "Total peptides",
        "PG.NrOfPrecursorsIdentified (Experiment-wide)": "Total ions",
        "PEP.StrippedSequence": "Peptide sequence",
        "PEP.AllOccurringProteinAccessions": "Mapped proteins",
        "EG.ModifiedSequence": "Modified sequence",
        "EG.CompensationVoltage": "Compensation voltage",
        "EG.Qvalue": "Qvalue",
        "EG.ApexRT": "Apex retention time",
        "EG.DatapointsPerPeak": "Datapoints per peak",
        "EG.FWHM": "FWHM",
        "EG.SignalToNoise": "Signal to noise",
        "FG.FragmentCount": "Fragment count",
        "FG.Charge": "Charge",
        "FG.MS1Quantity": "MS1 intensity",
        "FG.MS1RawQuantity": "MS1 raw intensity",
        "FG.MS2Quantity": "MS2 intensity",
        "FG.MS2RawQuantity": "MS2 raw intensity",
        "FG.MeasuredMz": "Observed m/z",
        "FG.TheoreticalMz": "Theoretical m/z",
        "FG.CalibratedMz": "Calibrated m/z",
    }
    sample_column_tags: list[str] = [
        ".PG.NrOfPrecursorsIdentified",
        ".PG.IBAQ",
        ".PG.Quantity",
        ".PG.NrOfPrecursorsUsedForQuantification",
        ".PG.NrOfStrippedSequencesUsedForQuantification",
    ]
    column_tag_mapping: OrderedDict[str, str] = OrderedDict(
        [
            (".PG.NrOfPrecursorsIdentified", " Ion count"),
            (".PG.IBAQ", " iBAQ intensity"),
            (".PG.Quantity", " Intensity"),
            (".PG.NrOfPrecursorsUsedForQuantification", " Quantified ion count"),
            (
                ".PG.NrOfStrippedSequencesUsedForQuantification",
                " Total quantified peptides",
            ),
            (".PEP.Quantity", " Intensity"),  # Ions
        ]
    )
    protein_info_columns: list[str] = [
        "PG.ProteinGroups",
        "PG.ProteinAccessions",
        "PG.Genes",
        "PG.Organisms",
        "PG.ProteinDescriptions",
        "PG.UniProtIds",
        "PG.ProteinNames",
        "PG.FastaHeaders",
        "PG.OrganismId",
        "PG.MolecularWeight",
    ]
    protein_info_tags: list[str] = []

    def __init__(self, directory: str, contaminant_tag: str = "contam_") -> None:
        """Initializes the SpectronautReader.

        Args:
            directory: Location of the Spectronaut result folder.
            contaminant_tag: Prefix of Protein ID entries to identify contaminants;
                default "contam_".
        """
        self.data_directory = directory
        self.filetags: dict[str, str] = self.default_filetags
        self.filenames = {}
        self._contaminant_tag: str = contaminant_tag

    def import_design(
        self, filename: Optional[str] = None, filetag: Optional[str] = None
    ) -> pd.DataFrame:
        """Reads a ConditionSetup file and returns an experimental design table.

        The following columns from the Spectronaut ConditionSetup file will be imported
        to the design table and renamed:
            Replicate -> Replicate
            Condition -> Experiment
            File Name -> Filename
            Run Label -> Run label

        In addition, a "Sample" is added containing values from the Experiment and
        Replicate columns, separated by an underscore.

        If neither filename nor filetag is specified, the default file tag
        "conditionsetup" is used to select a file from the data directory. If no file
        or multiple files match, an exception is thrown. The check for the presence of
        the file tag is not case sensitive.

        Args:
            filename: Optional, allows specifying a specific file that will be imported.
            filetag: Optional, can be used to select a file that contains the filetag as
                a substring, instead of specifying a filename.

        Returns:
            A dataframe containing the processed design table.
        """
        filetag = self.filetags["design"] if filetag is None else filetag
        filenames = _find_matching_files(
            self.data_directory,
            filename=filename,
            filetag=filetag,
            extensions=["xls", "tsv", "csv"],
        )
        if len(filenames) == 0:
            raise FileNotFoundError("No matching file found.")
        elif len(filenames) > 1:
            exception_message_lines = [
                f"Multiple matching files found in: {self.data_directory}",
                "One of the report filenames must be specified manually:",
            ]
            exception_message_lines.extend(filenames)
            exception_message = "\n".join(exception_message_lines)
            raise ValueError(exception_message)
        else:
            filename = filenames[0]

        df = self._read_file(filename)
        df["Sample"] = df["Condition"].astype(str) + "_" + df["Replicate"].astype(str)
        df = pd.DataFrame(
            {
                "Sample": df["Sample"].astype(str),
                "Replicate": df["Replicate"].astype(str),
                "Experiment": df["Condition"].astype(str),
                "Filename": df["File Name"].astype(str),
                "Run label": df["Run Label"].astype(str),
            }
        )
        return df

    def import_proteins(
        self,
        filename: Optional[str] = None,
        filetag: Optional[str] = None,
        rename_columns: bool = True,
        prefix_column_tags: bool = True,
        drop_protein_info: bool = True,
    ) -> pd.DataFrame:
        """Reads a Spectronaut protein report file and returns a processed DataFrame.

        Adds four protein entry columns to comply with the MsReport convention:
        "Protein reported by software", "Leading proteins", "Representative protein",
        "Potential contaminant".

        "Protein reported by software" and "Representative protein" contain the first
        entry from the "PG.ProteinAccessions" column, and "Leading proteins" contains
        all entries from this column. Multiple leading protein entries are separated by
        ";".

        Several columns in the Spectronaut report file can contain information specific
        for the leading protein entry. If leading proteins will be re-sorted later, it
        is recommended to remove columns containing protein specific information by
        setting 'drop_protein_info=True'.

        Args:
            filename: Optional, allows specifying a specific file that will be imported.
            filetag: Optional, can be used to select a file that contains the filetag as
                a substring, instead of specifying a filename.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            prefix_column_tags: If True, column tags such as "Intensity" are added
                in front of the sample names, e.g. "Intensity sample_name". If False,
                column tags are added afterwards, e.g. "Sample_name Intensity"; default
                True.
            drop_protein_info: If True, columns containing protein specific information,
                such as "Gene" or "Protein Length". See
                SpectronautReader.protein_info_columns and
                SpectronautReader.protein_info_tags for a full list of columns that will
                be removed. Default False.

        Returns:
            A dataframe containing the processed protein table.
        """
        filetag = self.filetags["proteins"] if filetag is None else filetag
        filenames = _find_matching_files(
            self.data_directory,
            filename=filename,
            filetag=filetag,
            extensions=["xls", "tsv", "csv"],
        )
        if len(filenames) == 0:
            raise FileNotFoundError("No matching file found.")
        elif len(filenames) > 1:
            exception_message_lines = [
                f"Multiple matching files found in: {self.data_directory}",
                "One of the report filenames must be specified manually:",
            ]
            exception_message_lines.extend(filenames)
            exception_message = "\n".join(exception_message_lines)
            raise ValueError(exception_message)
        else:
            filename = filenames[0]

        df = self._read_file(filename)
        df = self._tidy_up_sample_columns(df)
        df = self._add_protein_entries(df)
        if drop_protein_info:
            df = self._drop_columns(df, self.protein_info_columns)
            for tag in self.protein_info_tags:
                df = self._drop_columns_by_tag(df, tag)
        if rename_columns:
            df = self._rename_columns(df, prefix_column_tags)
        return df

    def import_peptides(
        self,
        filename: Optional[str] = None,
        filetag: Optional[str] = None,
        rename_columns: bool = True,
        prefix_column_tags: bool = True,
    ) -> pd.DataFrame:
        """Reads a Spectronaut peptide report file and returns a processed DataFrame.

        Uses and renames the following Spectronaut report columns:
        PG.ProteinAccessions, PEP.Quantity, PEP.StrippedSequence, and
        PEP.AllOccurringProteinAccessions

        Adds four protein entry columns to comply with the MsReport convention:
        "Protein reported by software", "Leading proteins", "Representative protein",
        "Potential contaminant".

        "Protein reported by software" and "Representative protein" contain the first
        entry from the "PG.ProteinAccessions" column, and "Leading proteins" contains
        all entries from this column. Multiple leading protein entries are separated by
        ";".

        Args:
            filename: Optional, allows specifying a specific file that will be imported.
            filetag: Optional, can be used to select a file that contains the filetag as
                a substring, instead of specifying a filename.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            prefix_column_tags: If True, column tags such as "Intensity" are added
                in front of the sample names, e.g. "Intensity sample_name". If False,
                column tags are added afterwards, e.g. "Sample_name Intensity"; default
                True.

        Returns:
            A dataframe containing the processed protein table.
        """
        filenames = _find_matching_files(
            self.data_directory,
            filename=filename,
            filetag=filetag,
            extensions=["xls", "tsv", "csv"],
        )
        if len(filenames) == 0:
            raise FileNotFoundError("No matching file found.")
        elif len(filenames) > 1:
            exception_message_lines = [
                f"Multiple matching files found in: {self.data_directory}",
                "One of the report filenames must be specified manually:",
            ]
            exception_message_lines.extend(filenames)
            exception_message = "\n".join(exception_message_lines)
            raise ValueError(exception_message)
        else:
            filename = filenames[0]

        df = self._read_file(filename)
        df = self._tidy_up_sample_columns(df)
        df = self._add_protein_entries(df)
        if rename_columns:
            df = self._rename_columns(df, prefix_column_tags)
        return df

    def import_ions(self) -> None:
        raise NotImplementedError

    def import_ion_evidence(
        self,
        filename: Optional[str] = None,
        filetag: Optional[str] = None,
        rename_columns: bool = True,
        rewrite_modifications: bool = True,
    ) -> pd.DataFrame:
        """Reads an ion evidence file (long format) and returns a processed dataframe.

        Adds new columns to comply with the MsReport convention. "Protein reported
        by software" and "Representative protein", both contain the first entry from
        "PG.ProteinAccessions". "Ion ID" contains unique entries for each ion, which are
        generated by concatenating the "Modified sequence" and "Charge" columns, and if
        present, the "Compensation voltage" column.

        "Modified sequence" entries contain modifications within square brackets.
        "Modification" entries are strings in the form of "position:modification_tag",
        multiple modifications are joined by ";". An example for a modified sequence and
        a modification entry: "PEPT[Phospho]IDO[Oxidation]", "4:Phospho;7:Oxidation".

        "Modification localization string" contains localization probabilities in the
        format "Mod1@Site1:Probability1,Site2:Probability2;Mod2@Site3:Probability3",
        e.g. "15.9949@11:1.000;79.9663@3:0.200,4:0.800". Refer to
        `msreport.peptidoform.make_localization_string` for details.

        Args:
            filename: Optional, allows specifying a specific file that will be imported.
            filetag: Optional, can be used to select a file that contains the filetag as
                a substring, instead of specifying a filename.
            rename_columns: If True, columns are renamed according to the MsReport
                convention; default True.
            rewrite_modifications: If True, the peptide format in "Modified sequence" is
                changed according to the MsReport convention, and a "Modifications" is
                added to contains the amino acid position for all modifications.
                Requires 'rename_columns' to be true. Default True.

        Returns:
            A dataframe containing the processed ion table.
        """
        filenames = _find_matching_files(
            self.data_directory,
            filename=filename,
            filetag=filetag,
            extensions=["xls", "tsv", "csv"],
        )
        if len(filenames) == 0:
            raise FileNotFoundError("No matching file found.")
        elif len(filenames) > 1:
            exception_message_lines = [
                f"Multiple matching files found in: {self.data_directory}",
                "One of the report filenames must be specified manually:",
            ]
            exception_message_lines.extend(filenames)
            exception_message = "\n".join(exception_message_lines)
            raise ValueError(exception_message)
        else:
            filename = filenames[0]
        df = self._read_file(filename)
        df = self._tidy_up_sample_columns(df)
        df = self._add_protein_entries(df)
        if rename_columns:
            df = self._rename_columns(df, True)
        if rewrite_modifications and rename_columns:
            df = self._add_peptide_modification_entries(df)
            df = self._add_modification_localization_string(df)
            df["Ion ID"] = df["Modified sequence"] + "_c" + df["Charge"].astype(str)
            if "Compensation voltage" in df.columns:
                _cv = df["Compensation voltage"].astype(str)
                df["Ion ID"] = df["Ion ID"] + "_cv" + _cv

        return df

    def _tidy_up_sample_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes leading brackets, such as "[1]", from columns."""
        tidy_df = df.copy()
        tidy_df.columns = tidy_df.columns.str.replace(r"^\[[0-9]+\] ", "", regex=True)
        return tidy_df

    def _add_protein_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds standardized protein entry columns to the data frame.

        Adds new columns to comply with the MsReport convention. "Protein reported by
        software" contains the protein ID extracted from the "Protein" column. "Leading
        proteins" contains the combined protein IDs extracted from the "Protein" and
        "Indistinguishable Proteins" columns, multiple entries are separated by ";".
        "Representative protein" contains the first entry form "Leading proteins".
        "Potential contaminant" contains Boolean values.

        Args:
            df: Dataframe containing a FragPipe result table.

        Returns:
            A copy of the input dataframe with updated columns.
        """
        leading_protein_entries = self._collect_leading_protein_entries(df)
        protein_entry_table = _process_protein_entries(
            leading_protein_entries, self._contaminant_tag
        )
        for key in protein_entry_table:
            df[key] = protein_entry_table[key]
        return df

    def _collect_leading_protein_entries(self, df: pd.DataFrame) -> list[list[str]]:
        """Generates a list of leading protein entries.

        Each entry in the list contains a list of protein entries extracted by splitting
        the values from the "PG.ProteinAccessions" column on ";".

        Args:
            df: Dataframe containing a protein table.

        Returns:
            A list of the same length as the input dataframe. Each position contains a
            list of leading protein entries, which a minimum of one entry.
        """
        leading_protein_entries = df["PG.ProteinAccessions"].str.split(";").tolist()
        return leading_protein_entries

    def _add_peptide_modification_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds standardized "Modified sequence" and "Modifications" columns.

        "Modified sequence" entries contain modifications within square brackets.
        "Modifications" entries are strings in the form of "position:modification_text",
        multiple modifications are joined by ";". An example for a modified sequence and
        a modification entry: "PEPT[Phospho]IDO[Oxidation]", "4:Phospho;7:Oxidation".

        Requires the columns "Peptide sequence" and "Modified sequence" from the
        software output.

        Args:
            df: Dataframe containing "Peptide sequence" and "Modified sequence" columns.

        Returns:
            A copy of the input dataframe with updated columns.
        """
        # TODO: not tested
        mod_sequences = df["Modified sequence"].str[1:-1]  # Remove sourrounding "_"
        mod_entries = _generate_modification_entries(
            df["Peptide sequence"], mod_sequences, "[", "]"
        )
        new_df = df.copy()
        new_df["Modified sequence"] = mod_entries["Modified sequence"]
        new_df["Modifications"] = mod_entries["Modifications"]
        return new_df

    def _add_modification_localization_string(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds modification localization string columns.

        Extracts localization probabilities from the "EG.PTMLocalizationProbabilities"
        column, converts them into the standardized modification localization string
        format used by msreport, and adds new column "Modification localization string".

        Probabilities are written in the format
        "Mod1@Site1:Probability1,Site2:Probability2;Mod2@Site3:Probability3",
        e.g. "15.9949@11:1.000;79.9663@3:0.200,4:0.800". Refer to
        `msreport.peptidoform.make_localization_string` for details.

        Args:
            df: Dataframe containing a "EG.PTMLocalizationProbabilities" column.

        Returns:
            A copy of the input dataframe with the added column
            "Modification localization string".
        """
        # TODO: not tested
        new_df = df.copy()
        localization_strings = []
        for localization_entry in new_df["EG.PTMLocalizationProbabilities"]:
            if localization_entry == "":
                localization_strings.append("")
                continue

            localization_probabilities = extract_spectronaut_localization_probabilities(
                localization_entry
            )
            localization_string = msreport.peptidoform.make_localization_string(
                localization_probabilities
            )
            localization_strings.append(localization_string)
        new_df["Modification localization string"] = localization_strings
        return new_df


def sort_leading_proteins(
    table: pd.DataFrame,
    alphanumeric: bool = True,
    penalize_contaminants: bool = True,
    special_proteins: Optional[list[str]] = None,
    database_order: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Returns a copy of 'table' with sorted leading proteins.

    "Leading proteins" are sorted according to the selected options. The first entry
    of the sorted leading proteins is selected as the new "Representative protein". If
    the columns are present, also the entries of "Leading proteins database origin" and
    "Leading potential contaminants" are reordered, and "Potential contaminant" is
    reassigned according to the representative protein.

    Additional protein annotation columns, refering to a representative protein that has
    been changed, will no longer be valid. It is therefore recommended to remove all
    columns containing protein specific information by enabling 'drop_protein_info'
    during the import of protein tables or to update protein annotation columns if
    possible.

    Args:
        table: Dataframe in which "Leading proteins" will be sorted.
        alphanumeric: If True, protein entries are sorted alpha numerical.
        penalize_contaminants: If True, protein contaminants are sorted to the back.
        special_proteins: Optional, allows specifying a list of protein IDs that
            will always be sorted to the beginning.
        database_order: Optional, allows specifying an order of protein databases that
            will be considered for sorting. Database names that are not present in
            'database_order' are sorted to the end. The protein database of a fasta
            entry is written in the very beginning of the fasta header, e.g. "sp" from
            the fasta header ">sp|P60709|ACTB_HUMAN Actin".

    Returns:
        A copy of the 'table', containing sorted leading protein entries.
    """
    sorted_entries = defaultdict(list)
    contaminants_present = "Leading potential contaminants" in table
    db_origins_present = "Leading proteins database origin" in table

    if database_order is not None:
        database_encoding: dict[str, int] = defaultdict(lambda: 999)
        database_encoding.update({db: i for i, db in enumerate(database_order)})
    if penalize_contaminants is not None:
        contaminant_encoding = {"False": 0, "True": 1, False: 0, True: 1}

    for _, row in table.iterrows():
        protein_ids = row["Leading proteins"].split(";")

        sorting_info: list[list] = [[] for _ in protein_ids]
        if special_proteins is not None:
            for i, _id in enumerate(protein_ids):
                sorting_info[i].append(_id not in special_proteins)
        if penalize_contaminants:
            for i, is_contaminant in enumerate(
                row["Leading potential contaminants"].split(";")
            ):
                sorting_info[i].append(contaminant_encoding[is_contaminant])
        if database_order is not None:
            for i, db_origin in enumerate(
                row["Leading proteins database origin"].split(";")
            ):
                sorting_info[i].append(database_encoding[db_origin])
        if alphanumeric:
            for i, _id in enumerate(protein_ids):
                sorting_info[i].append(_id)
        sorting_order = [
            i[0] for i in sorted(enumerate(sorting_info), key=lambda x: x[1])
        ]

        protein_ids = [protein_ids[i] for i in sorting_order]
        sorted_entries["Representative protein"].append(protein_ids[0])
        sorted_entries["Leading proteins"].append(";".join(protein_ids))

        if contaminants_present:
            contaminants = row["Leading potential contaminants"].split(";")
            contaminants = [contaminants[i] for i in sorting_order]
            potential_contaminant = contaminants[0] == "True"
            contaminants = ";".join(contaminants)
            sorted_entries["Potential contaminant"].append(potential_contaminant)
            sorted_entries["Leading potential contaminants"].append(contaminants)

        if db_origins_present:
            db_origins = row["Leading proteins database origin"].split(";")
            db_origins = ";".join([db_origins[i] for i in sorting_order])
            sorted_entries["Leading proteins database origin"].append(db_origins)

    sorted_table = table.copy()
    for key in sorted_entries:
        sorted_table[key] = sorted_entries[key]
    return sorted_table


def add_protein_annotation(
    table: pd.DataFrame,
    protein_db: ProteinDatabase,
    id_column: str = "Representative protein",
    gene_name: bool = False,
    protein_name: bool = False,
    protein_entry: bool = False,
    protein_length: bool = False,
    molecular_weight: bool = False,
    fasta_header: bool = False,
    ibaq_peptides: bool = False,
    database_origin: bool = False,
) -> pd.DataFrame:
    """Uses a FASTA protein database to add protein annotation columns.

    Args:
        table: Dataframe to which the protein annotations are added.
        protein_db: A protein database containing entries from one or multiple FASTA
            files.
        id_column: Column in 'table' that contains protein uniprot IDs, which will be
            used to look up entries in the 'protein_db'.
        gene_name: If True, adds a "Gene name" column.
        protein_name: If True, adds "Protein name" column.
        protein_entry: If True, adds "Protein entry name" column.
        protein_length: If True, adds a "Protein length" column.
        molecular_weight: If True, adds a "Molecular weight [kDa]" column. The molecular
            weight is calculated as the monoisotopic mass in kilo Dalton, rounded to two
            decimal places. Note that there is an opinionated behaviour for non-standard
            amino acids code. "O" is Pyrrolysine, "U" is Selenocysteine, "B" is treated
            as "N", "Z" is treated as "Q", and "X" is ignored.
        fasta_header: If True, adds a "Fasta header" column.
        ibaq_peptides: If True, adds a "iBAQ peptides" columns. The number of iBAQ
            peptides is calculated as the theoretical number of tryptic peptides with
            a length between 7 and 30.
        database_origin: If True, adds a "Database origin" column.

    Returns:
        The updated 'table' dataframe.
    """
    # not tested #
    proteins = table[id_column].to_list()

    proteins_not_in_db = []
    for protein_id in proteins:
        if protein_id not in protein_db:
            proteins_not_in_db.append(protein_id)
    if proteins_not_in_db:
        warnings.warn(
            f"Some proteins could not be annotated: {repr(proteins_not_in_db)}",
            ProteinsNotInFastaWarning,
            stacklevel=2,
        )

    annotations = {}
    if gene_name:
        annotations["Gene name"] = _create_protein_annotations_from_db(
            proteins, protein_db, _get_annotation_gene_name, ""
        )
    if protein_name:
        annotations["Protein name"] = _create_protein_annotations_from_db(
            proteins, protein_db, _get_annotation_protein_name, ""
        )
    if protein_entry:
        annotations["Protein entry name"] = _create_protein_annotations_from_db(
            proteins, protein_db, _get_annotation_protein_entry_name, ""
        )
    if protein_length:
        annotations["Protein length"] = _create_protein_annotations_from_db(
            proteins, protein_db, _get_annotation_sequence_length, -1
        )
    if molecular_weight:
        annotations["Molecular weight [kDa]"] = _create_protein_annotations_from_db(
            proteins, protein_db, _get_annotation_molecular_weight, np.nan
        )
    if fasta_header:
        annotations["Fasta header"] = _create_protein_annotations_from_db(
            proteins, protein_db, _get_annotation_fasta_header, ""
        )
    if database_origin:
        annotations["Database origin"] = _create_protein_annotations_from_db(
            proteins, protein_db, _get_annotation_db_origin, ""
        )
    if ibaq_peptides:
        annotations["iBAQ peptides"] = _create_protein_annotations_from_db(
            proteins, protein_db, _get_annotation_ibaq_peptides, -1
        )
    for column in annotations.keys():
        table[column] = annotations[column]
    return table


def add_protein_site_annotation(
    table: pd.DataFrame,
    protein_db: ProteinDatabase,
    protein_column: str = "Representative protein",
    site_column: str = "Protein site",
) -> pd.DataFrame:
    """Uses a FASTA protein database to add protein site annotation columns.

    Adds the columns "Modified residue", which corresponds to the amino acid at the
    protein site position, and "Sequence window", which contains sequence windows of
    eleven amino acids surrounding the protein site. Sequence windows are centered on
    the respective protein site; missing amino acids due to the position being close to
    the beginning or end of the protein sequence are substituted with "-".

    Args:
        table: Dataframe to which the protein site annotations are added.
        protein_db: A protein database containing entries from one or multiple FASTA
            files.
        protein_column: Column in 'table' that contains protein identifiers, which will
            be used to look up entries in the 'protein_db'.
        site_column: Column in 'table' that contains protein sites, which will be used
            to extract information from the protein sequence. Protein sites are
            one-indexed, meaining the first amino acid of the protein is position 1.

    Returns:
        The updated 'table' dataframe.
    """
    # TODO not tested
    proteins = table[protein_column].to_list()
    proteins_not_in_db = []
    for protein_id in proteins:
        if protein_id not in protein_db:
            proteins_not_in_db.append(protein_id)
    if proteins_not_in_db:
        warnings.warn(
            f"Some proteins could not be annotated: {repr(proteins_not_in_db)}",
            ProteinsNotInFastaWarning,
            stacklevel=2,
        )

    annotations: dict[str, list[str]] = {
        "Modified residue": [],
        "Sequence window": [],
    }
    for protein, site in zip(table[protein_column], table[site_column]):
        protein_sequence = protein_db[protein].sequence

        modified_residue = protein_sequence[site - 1]
        annotations["Modified residue"].append(modified_residue)

        sequence_window = extract_window_around_position(protein_sequence, site)
        annotations["Sequence window"].append(sequence_window)

    for column, annotation_values in annotations.items():
        table[column] = annotation_values
    return table


def add_leading_proteins_annotation(
    table: pd.DataFrame,
    protein_db: ProteinDatabase,
    id_column: str = "Leading proteins",
    gene_name: bool = False,
    protein_entry: bool = False,
    protein_length: bool = False,
    fasta_header: bool = False,
    ibaq_peptides: bool = False,
    database_origin: bool = False,
) -> pd.DataFrame:
    """Uses a FASTA protein database to add leading protein annotation columns.

    Generates protein annotations for multi protein entries, where each entry can
    contain one or multiple protein ids, multiple protein ids are separated by ";".

    Args:
        table: Dataframe to which the protein annotations are added.
        protein_db: A protein database containing entries from one or multiple FASTA
            files.
        id_column: Column in 'table' that contains leading protein uniprot IDs, which
            will be used to look up entries in the 'protein_db'.
        gene_name: If True, adds a "Leading proteins gene name" column.
        protein_entry: If True, adds "Leading proteins entry name" column.
        protein_length: If True, adds a "Leading proteins length" column.
        fasta_header: If True, adds a "Leading proteins fasta header" column.
        ibaq_peptides: If True, adds a "Leading proteins iBAQ peptides" columns. The
            number of iBAQ peptides is calculated as the theoretical number of tryptic
            peptides with a length between 7 and 30.
        database_origin: If True, adds a "Leading proteins database origin" column.

    Returns:
        The updated 'table' dataframe.
    """
    # not tested #
    leading_protein_entries = table[id_column].to_list()

    proteins_not_in_db = []
    for leading_entry in leading_protein_entries:
        for protein_id in leading_entry.split(";"):
            if protein_id not in protein_db:
                proteins_not_in_db.append(protein_id)
    if proteins_not_in_db:
        warnings.warn(
            f"Some proteins could not be annotated: {repr(proteins_not_in_db)}",
            ProteinsNotInFastaWarning,
            stacklevel=2,
        )

    annotations = {}
    if gene_name:
        annotation = _create_multi_protein_annotations_from_db(
            leading_protein_entries, protein_db, _get_annotation_gene_name
        )
        annotations["Leading proteins gene name"] = annotation
    if protein_entry:
        annotation = _create_multi_protein_annotations_from_db(
            leading_protein_entries, protein_db, _get_annotation_protein_entry_name
        )
        annotations["Leading proteins entry name"] = annotation
    if protein_length:
        annotation = _create_multi_protein_annotations_from_db(
            leading_protein_entries, protein_db, _get_annotation_sequence_length
        )
        annotations["Leading proteins length"] = annotation
    if fasta_header:
        annotation = _create_multi_protein_annotations_from_db(
            leading_protein_entries, protein_db, _get_annotation_fasta_header
        )
        annotations["Leading proteins fasta header"] = annotation
    if ibaq_peptides:
        annotation = _create_multi_protein_annotations_from_db(
            leading_protein_entries, protein_db, _get_annotation_ibaq_peptides
        )
        annotations["Leading proteins iBAQ peptides"] = annotation
    if database_origin:
        annotation = _create_multi_protein_annotations_from_db(
            leading_protein_entries, protein_db, _get_annotation_db_origin
        )
        annotations["Leading proteins database origin"] = annotation
    for column in annotations.keys():
        table[column] = annotations[column]
    return table


def add_protein_site_identifiers(
    table: pd.DataFrame,
    protein_db: ProteinDatabase,
    site_column: str,
    protein_name_column: str,
):
    """Adds a "Protein site identifier" column to the 'table'.

    The "Protein site identifier" is generated by concatenating the protein name
    with the amino acid and position of the protein site or sites, e.g. "P12345 - S123"
    or "P12345 - S123 / T125". The amino acid is extracted from the protein sequence at
    the position of the site. If the protein name is not available, the
    "Representative protein" entry is used instead.

    Args:
        table: Dataframe to which the protein site identifiers are added.
        protein_db: A protein database containing entries from one or multiple FASTA
            files. Protein identifiers in the 'table' column "Representative protein"
            are used to look up entries in the 'protein_db'.
        site_column: Column in 'table' that contains protein site positions. Positions
            are one-indexed, meaning the first amino acid of the protein is position 1.
            Multiple sites in a single entry should be separated by ";".
        protein_name_column: Column in 'table' that contains protein names, which will
            be used to generate the identifier. If no name is available, the accession
            is used instead.

    Raises:
        ValueError: If the "Representative protein", 'protein_name_column' or
            'site_column' is not found in the 'table'.
    """
    if site_column not in table.columns:
        raise ValueError(f"Column '{site_column}' not found in the table.")
    if protein_name_column not in table.columns:
        raise ValueError(f"Column '{protein_name_column}' not found in the table.")
    if "Representative protein" not in table.columns:
        raise ValueError("Column 'Representative protein' not found in the table.")

    site_identifiers = []
    for accession, sites, name in zip(
        table["Representative protein"],
        table[site_column].astype(str),
        table[protein_name_column],
    ):
        protein_sequence = protein_db[accession].sequence
        protein_identifier = name if name else accession
        aa_sites = []
        for site in sites.split(";"):
            aa = protein_sequence[int(site) - 1]
            aa_sites.append(f"{aa}{site}")
        aa_site_tag = " / ".join(aa_sites)
        site_identifier = f"{protein_identifier} - {aa_site_tag}"
        site_identifiers.append(site_identifier)
    table["Protein site identifier"] = site_identifiers


def add_sequence_coverage(
    protein_table: pd.DataFrame,
    peptide_table: pd.DataFrame,
    id_column: str = "Protein reported by software",
) -> None:
    """Calculates "Sequence coverage" and adds a new column to the 'protein_table'.

    Sequence coverage is represented as a percentage, with values ranging from 0 to 100.
    Requires the columns "Start position" and "End position" in the 'peptide_table', and
    "Protein length" in the 'protein_table'. For protein entries where the sequence
    coverage cannot be calculated, a value of -1 is added.

    Args:
        protein_table: Dataframe to which the "Sequence coverage" column is added.
        peptide_table: Dataframe which contains peptide information required for
            calculation of the protein sequence coverage.
        id_column: Column used to match entries between the 'protein_table' and the
            'peptide_table', must be present in both tables. Default
            "Protein reported by software".
    """
    peptide_positions = {}
    for protein_id, peptide_group in peptide_table.groupby(by=id_column):
        positions = list(
            zip(peptide_group["Start position"], peptide_group["End position"])
        )
        peptide_positions[protein_id] = sorted(positions)

    sequence_coverages = []
    for protein_id, protein_length in zip(
        protein_table[id_column], protein_table["Protein length"]
    ):
        can_calculate_coverage = True
        if protein_id not in peptide_positions:
            can_calculate_coverage = False
        if protein_length < 1:
            can_calculate_coverage = False
        try:
            protein_length = int(protein_length)
        except ValueError:
            can_calculate_coverage = False

        if can_calculate_coverage:
            sequence_coverage = helper.calculate_sequence_coverage(
                protein_length, peptide_positions[protein_id], ndigits=1
            )
        else:
            sequence_coverage = np.nan
        sequence_coverages.append(sequence_coverage)
    protein_table["Sequence coverage"] = sequence_coverages


def add_ibaq_intensities(
    table: pd.DataFrame,
    normalize: bool = True,
    ibaq_peptide_column: str = "iBAQ peptides",
    intensity_tag: str = "Intensity",
    ibaq_tag: str = "iBAQ intensity",
) -> None:
    """Adds iBAQ intensity columns to the 'table'.

    Requires a column containing the theoretical number of iBAQ peptides.

    Args:
        table: Dataframe to which the iBAQ intensity columns are added.
        normalize: Scales iBAQ intensities per sample so that the sum of all iBAQ
            intensities is equal to the sum of all Intensities.
        ibaq_peptide_column: Column in 'table' containing the number of iBAQ peptides.
            No iBAQ intensity is calculated for rows with negative values or zero in the
            ibaq_peptide_column.
        intensity_tag: Substring used to identify intensity columns from the 'table'
            that are used to calculate iBAQ intensities.
        ibaq_tag: Substring used for naming the new 'table' columns containing the
            calculated iBAQ intensities. The column names are generated by replacing
            the 'intensity_tag' with the 'ibaq_tag'.
    """
    for intensity_column in helper.find_columns(table, intensity_tag):
        ibaq_column = intensity_column.replace(intensity_tag, ibaq_tag)
        valid = table[ibaq_peptide_column] > 0

        table[ibaq_column] = np.nan
        table.loc[valid, ibaq_column] = (
            table.loc[valid, intensity_column] / table.loc[valid, ibaq_peptide_column]
        )

        if normalize:
            total_intensity = table.loc[valid, intensity_column].sum()
            total_ibaq = table.loc[valid, ibaq_column].sum()
            factor = total_intensity / total_ibaq
            table.loc[valid, ibaq_column] = table.loc[valid, ibaq_column] * factor


def add_peptide_positions(
    table: pd.DataFrame,
    protein_db: ProteinDatabase,
    peptide_column: str = "Peptide sequence",
    protein_column: str = "Representative protein",
) -> None:
    """Adds peptide "Start position" and "End position" positions to the table.

    For entries where the protein is absent from the FASTA or the peptide sequence
    could not be matched to the protein sequence, start and end positions of -1 are
    added.

    Args:
        table: Dataframe to which the protein annotations are added.
        protein_db: A protein database containing entries from one or multiple FASTA
            files.
        peptide_column: Column in 'table' that contains the peptide sequence. Peptide
            sequences must only contain amino acids and no other symbols.
        protein_column: Column in 'table' that contains protein IDs that are used to
            find matching entries in the FASTA files.
    """
    # not tested #
    peptide_positions: dict[str, list[int]] = {"Start position": [], "End position": []}
    proteins_not_in_db = []
    for peptide, protein_id in zip(table[peptide_column], table[protein_column]):
        if protein_id in protein_db:
            sequence = protein_db[protein_id].sequence
            start = sequence.find(peptide) + 1
            end = start + len(peptide) - 1
            if start == 0:
                start, end = -1, -1
        else:
            proteins_not_in_db.append(protein_id)
            start, end = -1, -1
        peptide_positions["Start position"].append(start)
        peptide_positions["End position"].append(end)

    for key in peptide_positions:
        table[key] = peptide_positions[key]

    if proteins_not_in_db:
        warnings.warn(
            f"Some peptides could not be annotated: {repr(proteins_not_in_db)}",
            ProteinsNotInFastaWarning,
            stacklevel=2,
        )


def add_protein_modifications(table: pd.DataFrame):
    """Adds a "Protein sites" column.

    To generate the "Protein modifications" the positions from the "Modifications"
    column are increase according to the peptide positions ("Start position"] column).

    Args:
        table: Dataframe to which the "Protein modifications" column is added.
    """
    protein_modification_entries = []
    for mod_entry, start_pos in zip(table["Modifications"], table["Start position"]):
        if mod_entry:
            protein_mods = []
            for peptide_site, mod in [m.split(":") for m in mod_entry.split(";")]:
                protein_site = int(peptide_site) + start_pos - 1
                protein_mods.append([str(protein_site), mod])
            protein_mod_string = ";".join([f"{pos}:{mod}" for pos, mod in protein_mods])
        else:
            protein_mod_string = ""
        protein_modification_entries.append(protein_mod_string)
    table["Protein modifications"] = protein_modification_entries


def propagate_representative_protein(
    target_table: pd.DataFrame, source_table: pd.DataFrame
) -> None:
    """Propagates "Representative protein" column from the source to the target table.

    The column "Protein reported by software" is used to match entries between the two
    tables. Then entries from "Representative protein" are propagated from the
    'source_table' to matching rows in the 'target_table'.

    Args:
        target_table: Dataframe to which "Representative protein" entries will be added.
        source_table: Dataframe from which "Representative protein" entries are
            propagated.
    """
    # not tested #
    protein_lookup = {}
    for old, new in zip(
        source_table["Protein reported by software"],
        source_table["Representative protein"],
    ):
        protein_lookup[old] = new

    new_protein_ids = []
    for old in target_table["Protein reported by software"]:
        new_protein_ids.append(protein_lookup[old] if old in protein_lookup else old)
    target_table["Representative protein"] = new_protein_ids


def extract_sample_names(df: pd.DataFrame, tag: str) -> list[str]:
    """Extracts sample names from columns containing the 'tag' substring.

    Sample names are extracted from column names containing the 'tag' string, by
    splitting the column name with the 'tag', and removing all trailing and leading
    white spaces from the resulting strings.

    Args:
        df: Column names from this dataframe are used for extracting sample names.
        tag: Column names containing the 'tag' are selected for extracting sample names.

    Returns:
        A list of sample names.
    """
    columns = helper.find_columns(df, tag)
    sample_names = _find_remaining_substrings(columns, tag)
    return sample_names


def _rearrange_column_tag(df: pd.DataFrame, tag: str, prefix: bool) -> pd.DataFrame:
    """Moves the column 'tag' to the beginning or end of each column name.

    Args:
        df: Rearrange columns in this dataframe.
        tag: A substring that when found in column names should be moved to the
            beginning or end of the column name.
        prefix: If true, the tag string is moved to the beginning of the new column
            names, else to the end.
    """
    old_columns = helper.find_columns(df, tag)
    new_columns = []
    for column_name in old_columns:
        column_name = column_name.replace(tag, "").strip()
        if prefix:
            new_column_name = " ".join([tag, column_name]).strip()
        else:
            new_column_name = " ".join([column_name, tag]).strip()
        new_columns.append(new_column_name)
    column_lookup = dict(zip(old_columns, new_columns))
    df = df.rename(columns=column_lookup, inplace=False)
    return df


def _find_remaining_substrings(strings: list[str], split_with: str) -> list[str]:
    """Finds the remaining part from several strings after splitting."""
    substrings = []
    for string in strings:
        substrings.extend([s.strip() for s in string.split(split_with)])
    # Remove empty entries
    substrings = sorted(set(filter(None, substrings)))
    return substrings


def _add_potential_contaminants(df: pd.DataFrame, contaminant_tag: str) -> pd.DataFrame:
    """Adds a "Potential contaminant" column to the data frame.

    "Potential contaminant" will be True if the "Representative protein" entry contains
    the 'contaminant_tag', and otherwise False.

    Args:
        df: Dataframe to which the "Potential contaminant" column will be added.
        contaminant_tag: String used to identify potential contaminants.

    Returns:
        A copy of the input dataframe, containing the "Potential contaminant" column.
    """
    # not tested #
    df = df.copy()
    df["Potential contaminant"] = df["Representative protein"].str.contains(
        contaminant_tag
    )
    return df


def _find_matching_files(
    directory: str,
    filename: Optional[str] = None,
    filetag: Optional[str] = None,
    extensions: Optional[list[str]] = None,
) -> list[str]:
    """Returns all filenames matching the specified pattern.

    Either filename or filetag must be specified. If filename is specified, it is only
    checked if this specific file exists. When a filetag but no filename is specified,
    all files containing the filetag are selected. The check for the presence of the
    file tag is not case sensitive.

    Args:
        directory: Files from this directory are used for matching.
        filename: Optional, allows specifying a specific filename.
        filetag: Optional, can be used to select files containing the filetag as a
            substring, instead of specifying a filename.
        extensions: Optional, if a list of extensions is specified, matched filenames
            must end with one of the extensions.

    Returns:
        A list of matched filenames. If no files could be matched, an empty list is
        returned.
    """
    if filename is not None:
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        else:
            matched_filenames = [filename]
    elif filetag is not None:
        if extensions is not None:
            potential_files = set()
            for current_filename in os.listdir(directory):
                for extension in extensions:
                    if current_filename.lower().endswith(f".{extension}"):
                        potential_files.add(current_filename)
        else:
            potential_files = set(os.listdir(directory))
        matched_filenames = [
            fn for fn in potential_files if filetag.lower() in fn.lower()
        ]
    else:
        raise ValueError("Either a filename or a filetag must be specified.")
    return matched_filenames


def _process_protein_entries(
    leading_protein_entries: list[list[str]],
    contaminant_tag: str,
) -> pd.DataFrame:
    """Returns a dataframe containing standardized protein entry columns.

    For each entry of 'leading_protein_entries', a list of protein IDs is extracted. The
    first entry of the protein IDs is added to the "Protein reported by software"
    column. Multiple protein IDs are sorted if 'sort_proteins' is enabled. Multiple
    protein IDs are joined with ";" and added to the "Leading proteins" column. The
    first protein ID from the "Leading proteins" entry is added to the "Representative
    protein" column. If the "Representative protein" protein ID contains the
    'contaminant_tag' then True is added to the "Potential contaminant" column,
    otherwise False is added.

    Args:
        leading_protein_entries: A list containing lists of leading protein entries.
        contaminant_tag: String used to identify potential contaminants.

    Returns:
        A dataframe containing the columns "Protein reported by software",
        "Leading proteins", "Representative protein", and "Potential contaminant".
    """
    new_entries: dict[str, list[str | bool]] = {
        "Protein reported by software": [],
        "Representative protein": [],
        "Potential contaminant": [],
        "Leading proteins": [],
        "Leading potential contaminants": [],
    }

    for leading_proteins in leading_protein_entries:
        protein_ids = _extract_protein_ids(leading_proteins)
        potential_contaminants = _mark_contaminants(leading_proteins, contaminant_tag)

        new_entries["Protein reported by software"].append(protein_ids[0])
        new_entries["Representative protein"].append(protein_ids[0])
        new_entries["Potential contaminant"].append(potential_contaminants[0])
        new_entries["Leading proteins"].append(";".join(protein_ids))
        new_entries["Leading potential contaminants"].append(
            ";".join(map(str, potential_contaminants))
        )

    table = pd.DataFrame(new_entries)
    return table


def _generate_modification_entries(
    sequences: Iterable[str],
    modified_sequences: Iterable[str],
    tag_start: str,
    tag_close: str,
) -> dict[str, list]:
    """Creates standardized "Modified sequence" and "Modifications" values.

    Uses 'tag_start' and 'tag_close' for extracting modifications and their positions
    from 'modified_sequences' entries. The extracted modifications are then used
    together with the 'sequences' entries to generate modified sequences according to
    the MsReport convention, where each modification is surrounded by square brackets.

    Requires that modifications in the 'modified_sequences' entries are surrounded by
    symbols such as "()" or "[]".

    Args:
        sequences: A list of plain amino acid sequences.
        modified_sequences: A list of modified amino acid sequences.
        tag_start: String indicating the beginning of a modification in
            'modified_sequences' entries.
        tag_close: String indicating the ending of a modification in
            'modified_sequences' entries.

    Returns:
        A dictionary containing a "Modified sequence" list and a "Modifications" list.
        "Modified sequence" entries contain modifications within square brackets.
        "Modification" entries are strings in the form of "position:modification_text",
        multiple modifications are joined by ";". An example for a modified sequence and
        a modification entry: "PEPT[Phospho]IDO[Oxidation]", "4:Phospho;7:Oxidation".
    """
    # TODO: not tested
    modified_sequence_entries = []
    modification_entries = []
    for sequence, modified_sequence in zip(sequences, modified_sequences):
        modifications = helper.extract_modifications(
            modified_sequence, tag_start, tag_close
        )
        modified_sequence = helper.modify_peptide(sequence, modifications)
        modification_entry = ";".join([f"{pos}:{mod}" for pos, mod in modifications])
        modified_sequence_entries.append(modified_sequence)
        modification_entries.append(modification_entry)
    entries = {
        "Modified sequence": modified_sequence_entries,
        "Modifications": modification_entries,
    }
    return entries


def _generate_modification_entries_from_assigned_modifications(
    sequences: Iterable[str],
    assigned_modifications: Iterable[str],
) -> dict[str, list[str]]:
    modified_sequence_entries = []
    modification_entries = []
    for sequence, modifications_entry in zip(sequences, assigned_modifications):
        modifications = _extract_fragpipe_assigned_modifications(
            modifications_entry, sequence
        )
        modified_sequence = helper.modify_peptide(sequence, modifications)
        modification_entry = ";".join([f"{pos}:{mod}" for pos, mod in modifications])
        modified_sequence_entries.append(modified_sequence)
        modification_entries.append(modification_entry)

    entries = {
        "Modified sequence": modified_sequence_entries,
        "Modifications": modification_entries,
    }
    return entries


def _extract_fragpipe_assigned_modifications(
    modifications_entry: str,
    sequence: str,
) -> list[tuple[int, str]]:
    """Extracts modifications from a FragPipe "Modifications" entry.

    Example for a modification entry: "N-term(42.0106),8C(57.0215)"

    Returns:
        A list of tuples, where each tuple contains the position of the modification and
        the modification text. The position is one-indexed, meaning that the first amino
        acid position is 1. N-term and C-term are represented as 0 and len(sequence)
        respectively.
    """
    if modifications_entry == "":
        return []
    modifications = []
    for mod_entry in modifications_entry.split(","):
        position_entry, modification = mod_entry.split(")")[0].split("(")
        if position_entry == "N-term":
            position = 0
        elif position_entry == "C-term":
            position = len(sequence)
        else:
            position = int(position_entry[:-1])
        modifications.append((position, modification))
    return modifications


def extract_maxquant_localization_probabilities(
    localization_entry: str,
) -> dict[int, float]:
    """Extract localization probabilites from a MaxQuant "Probabilities" entry.

    Args:
        localization_entry: Entry from the "Probabilities" columns of a MaxQuant
            msms.txt, evidence.txt or Sites.txt table.

    Returns:
        A dictionary of {position: probability} mappings. Positions are one-indexed,
        which means that the first amino acid position is 1.

    Example:
    >>> extract_maxquant_localization_probabilities("IRT(0.989)AMNS(0.011)IER")
    {3: 0.989, 7: 0.011}
    """
    _, probabilities = msreport.peptidoform.parse_modified_sequence(
        localization_entry, "(", ")"
    )
    site_probabilities = {
        site: float(probability) for site, probability in probabilities
    }
    return site_probabilities


def extract_fragpipe_localization_probabilities(localization_entry: str) -> dict:
    """Extract localization probabilites from a FragPipe "Localization" entry.

    Args:
        localization_entry: Entry from the "Localization" column of a FragPipe
            ions.tsv or combined_ions.tsv table.

    Returns:
        A dictionary of modifications containing a dictionary of {position: probability}
        mappings. Positions are one-indexed, which means that the first amino acid
        position is 1.

    Example:
    >>> extract_fragpipe_localization_probabilities(
    ...     "M:15.9949@FIM(1.000)TPTLK;STY:79.9663@FIMT(0.334)PT(0.666)LK;"
    ... )
    {'15.9949': {3: 1.0}, '79.9663': {4: 0.334, 6: 0.666}}
    """
    modification_probabilities: dict[str, dict[int, float]] = {}
    for modification_entry in filter(None, localization_entry.split(";")):
        specified_modification, probability_sequence = modification_entry.split("@")
        _, modification = specified_modification.split(":")
        _, probabilities = msreport.peptidoform.parse_modified_sequence(
            probability_sequence, "(", ")"
        )
        if modification not in modification_probabilities:
            modification_probabilities[modification] = {}
        modification_probabilities[modification].update(
            {site: float(probability) for site, probability in probabilities}
        )
    return modification_probabilities


def extract_spectronaut_localization_probabilities(localization_entry: str) -> dict:
    """Extract localization probabilites from a Spectronaut localization entry.

    Args:
        localization_entry: Entry from the "EG.PTMLocalizationProbabilities" column of a
            spectronaut elution group (EG) output table.

    Returns:
        A dictionary of modifications containing a dictionary of {position: probability}
        mappings. Positions are one-indexed, which means that the first amino acid
        position is 1.

    Example:
    >>> extract_spectronaut_localization_probabilities(
    ...     "_HM[Oxidation (M): 100%]S[Phospho (STY): 45.5%]GS[Phospho (STY): 54.5%]PG_"
    ... )
    {'Oxidation (M)': {2: 1.0}, 'Phospho (STY)': {3: 0.455, 5: 0.545}}
    """
    modification_probabilities: dict[str, dict[int, float]] = {}
    localization_entry = localization_entry.strip("_")
    _, raw_probability_entries = msreport.peptidoform.parse_modified_sequence(
        localization_entry, "[", "]"
    )

    for site, mod_probability_entry in raw_probability_entries:
        modification, probability_entry = mod_probability_entry.split(": ")
        if modification not in modification_probabilities:
            modification_probabilities[modification] = {}
        probability = float(probability_entry.replace("%", "")) / 100.0
        modification_probabilities[modification][site] = probability
    return modification_probabilities


def _extract_protein_ids(entries: list[str]) -> list[str]:
    """Returns a list of protein IDs, extracted from protein entries.

    If a protein entry contains two "|" it is considered a FASTA header and the string
    between the first two "|" is extracted as the protein ID. Otherwise the entry is
    directly used as a protein ID.

    Args:
        entries: A list of protein entries.

    Returns:
        A list of protein IDs
    """
    # not tested #
    protein_ids = []
    for protein_entry in entries:
        if protein_entry.count("|") >= 2:
            protein_id = protein_entry.split("|")[1]
        else:
            protein_id = protein_entry
        protein_ids.append(protein_id)
    return protein_ids


def _mark_contaminants(entries: list[str], tag: str) -> list[bool]:
    """Returns a list of booleans, True for each entry that contains the tag.

    Args:
        entries: List of protein entries.
        tag: String used to identify potential contaminants.

    Returns:
        A list of booleans with the same length as 'entries'.
    """
    # TODO: not tested #
    return [True if tag in entry else False for entry in entries]


def _create_protein_annotations_from_db(
    protein_ids: Iterable[str],
    protein_db: ProteinDatabase,
    query_function: Callable,
    default_value: Any,
) -> list[Any]:
    """Returns a list of multi protein entry annotations.

    Used to generate protein annotations for protein entries. For each protein id an
    annotation is generated by looking up the protein entry in the protein database,
    which is then submitted to the specified query function.

    Args:
        protein_ids: Iterable of protein ids.
        protein_db: A protein database containing entries from one or multiple FASTA
            files.
        query_function: Function that gets as arguments an msreport.helper.temp.Protein
            instance and a default return value and returns either a string or float.
        default_value: Default value if a protein is absent from the 'protein_db' or
            the query_function cannot extract an annotation.

    Returns:
        A list of multi protein annotations, where each entry can either correspond to
        the annotation of one or multiple proteins, which are separated by ";".
    """
    # not tested #
    annotation_values = []
    for protein_id in protein_ids:
        query_result = []
        if protein_id in protein_db:
            db_entry = protein_db[protein_id]
            query_result = query_function(db_entry, default_value)
            annotation_values.append(query_result)
        else:
            annotation_values.append(default_value)
    return annotation_values


def _create_multi_protein_annotations_from_db(
    protein_entries: Iterable[str],
    protein_db: ProteinDatabase,
    query_function: Callable,
) -> list[str]:
    """Returns a list of multi protein entry annotations.

    Can be used to generate protein annotations for multi protein entries, where each
    entry can contain one or multiple protein ids, multiple protein ids are separated
    by ";". For each protein id an annotation is generated by looking up the protein
    entry in the protein database, which is then submitted to the specified query
    function. If a protein id is not present in the protein database or if the query
    function cannot extract an annotation from the database entry, an empty string will
    be used.

    Args:
        protein_entries: Iterable of protein entries. Each protein entry correpsonds to
            one or multiple protein ids, separated by ";".
        protein_db: A protein database containing entries from one or multiple FASTA
            files.
        query_function: Function that gets as arguments an msreport.helper.temp.Protein
            instance and a default return value and returns either a string or float.

    Returns:
        A list of multi protein annotations, where each entry can either correspond to
        the annotation of one or multiple proteins, which are separated by ";".
    """
    annotation_values = []
    default_value = ""
    for protein_query in protein_entries:
        query_result = []
        for protein_id in protein_query.split(";"):
            if protein_id in protein_db:
                db_entry = protein_db[protein_id]
                query_result.append(query_function(db_entry, default_value))
            else:
                query_result.append(default_value)
        annotation_value = ";".join(map(str, query_result))
        annotation_values.append(annotation_value)
    return annotation_values


def _get_annotation_sequence_length(protein_entry: Protein, default_value: Any) -> Any:
    return len(protein_entry.sequence)


def _get_annotation_fasta_header(protein_entry: Protein, default_value: Any) -> Any:
    return protein_entry.header


def _get_annotation_gene_name(protein_entry: Protein, default_value: Any) -> Any:
    return protein_entry.header_fields.get("gene_name", default_value)


def _get_annotation_protein_name(protein_entry: Protein, default_value: Any) -> Any:
    return protein_entry.header_fields.get("protein_name", default_value)


def _get_annotation_protein_entry_name(
    protein_entry: Protein, default_value: Any
) -> Any:
    return protein_entry.header_fields.get("entry_name", default_value)


def _get_annotation_db_origin(protein_entry: Protein, default_value: Any) -> Any:
    return protein_entry.header_fields.get("db", default_value)


def _get_annotation_ibaq_peptides(protein_entry: Protein, default_value: Any) -> Any:
    return helper.calculate_tryptic_ibaq_peptides(protein_entry.sequence)


def _get_annotation_molecular_weight(protein_entry: Protein, default_value: Any) -> Any:
    """Returns moleculare weight in kilo Dalton, rounded to two decimal places."""
    monoisotopic_mass = helper.calculate_monoisotopic_mass(protein_entry.sequence)
    molecular_weight_kda = round(monoisotopic_mass / 1000, 2)
    return molecular_weight_kda
