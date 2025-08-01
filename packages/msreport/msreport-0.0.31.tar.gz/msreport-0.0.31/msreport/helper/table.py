import re
from typing import Iterable, Sequence, Union

import numpy as np
import pandas as pd


def guess_design(table: pd.DataFrame, tag: str) -> pd.DataFrame:
    """Extracts sample name, experiment, and replicate from specified sample columns.

    "Total" and "Combined", and their lower case variants, are not allowed as sample
    names and will be ignored.

    First a subset of columns containing a column tag are identified. Then sample names
    are extracted by removing the column tag from each column name. And finally, sample
    names are split into experiment and replicate at the last underscore.

    This requires that the naming of samples follows a specific convention. Sample names
    must begin with the experiment name, followed by an underscore and a unique
    identifier of the sample, for example the replicate number. The experiment name can
    also contain underscores, as it is split only by the last underscore.

    For example "ExpA_r1" would be split into experiment "ExpA" and replicate "r1",
    "Exp_A_1" would be experiment "Exp_A" and replicate "1".

    Args:
        table: Dataframe which columns are used for extracting sample names.
        tag: Column names containing the 'tag' are selected for sample extraction.

    Returns:
        A dataframe containing the columns "Sample", "Experiment", and "Replicate"
    """
    sample_entries = []
    for column in find_columns(table, tag, must_be_substring=True):
        sample = column.replace(tag, "").strip()
        if sample.lower() in ["total", "combined"]:
            continue
        experiment = "_".join(sample.split("_")[:-1])
        experiment = experiment if experiment else sample
        replicate = sample.split("_")[-1]
        replicate = replicate if replicate is not sample else "-1"
        sample_entries.append([sample, experiment, replicate])
    design = pd.DataFrame(sample_entries, columns=["Sample", "Experiment", "Replicate"])
    return design


def intensities_in_logspace(data: Union[pd.DataFrame, np.ndarray, Iterable]) -> bool:
    """Evaluates whether intensities are likely to be log transformed.

    Assumes that intensities are log transformed if all values are smaller or equal to
    64. Intensities values (and intensity peak areas) reported by tandem mass
    spectrometry typically range from 10^3 to 10^12. To reach log2 transformed values
    greater than 64, intensities would need to be higher than 10^19, which seems to be
    very unlikely to be ever encountered.

    Args:
        data: Dataset that contains only intensity values, can be any iterable,
            a numpy.array or a pandas.DataFrame, multiple dimensions or columns
            are allowed.

    Returns:
        True if intensity values in 'data' appear to be log transformed.
    """
    data = np.array(data, dtype=float)
    mask = np.isfinite(data)
    return bool(np.all(data[mask].flatten() <= 64))


def rename_sample_columns(table: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Renames sample names according to the mapping in a cautious manner.

    In general, this function allows the use of 'mapping' with keys that are substrings
    of any other keys, as well as values that are substrings of any of the keys.

    Importantly, if the mapping keys (sample names) are substrings of other column names
    within the table, unintended renaming of those columns will occur. For instance,
    when renaming columns ["Abundance", "Intensity A"] with the mapping
    {"A": "Sample Alpha"}, the columns will be renamed to ["Sample Alphabundance",
    "Intensity Sample Alpha"].

    Args:
        table: Dataframe which columns will be renamed.
        mapping: A mapping of old to new sample names that will be used to replace
            matching substrings in the columns from table.

    Returns:
        A copy of the table with renamed columns.
    """
    sorted_mapping_keys = sorted(mapping, key=len, reverse=True)

    renamed_columns = []
    for column in table.columns:
        for sample_name in sorted_mapping_keys:
            if sample_name in column:
                column = column.replace(sample_name, mapping[sample_name])
                break
        renamed_columns.append(column)

    renamed_table = table.copy()
    renamed_table.columns = renamed_columns
    return renamed_table


def rename_mq_reporter_channels(
    table: pd.DataFrame, channel_names: Sequence[str]
) -> None:
    """Renames reporter channel numbers with sample names.

    MaxQuant writes reporter channel names either in the format "Reporter intensity 1"
    or "Reporter intensity 1 Experiment Name", dependent on whether an experiment name
    was specified. Renames "Reporter intensity", "Reporter intensity count", and
    "Reporter intensity corrected" columns.

    NOTE: This might not work for the peptides.txt table, as there are columns present
    with the experiment name and also without it.
    """
    pattern = re.compile("Reporter intensity [0-9]+")
    reporter_columns = list(filter(pattern.match, table.columns.tolist()))
    assert len(reporter_columns) == len(channel_names)

    column_mapping = {}
    base_name = "Reporter intensity "
    for column, channel_name in zip(reporter_columns, channel_names):
        for tag in ["", "count ", "corrected "]:
            old_column = column.replace(f"{base_name}", f"{base_name}{tag}")
            new_column = f"{base_name}{tag}{channel_name}"
            column_mapping[old_column] = new_column
    table.rename(columns=column_mapping, inplace=True)


def apply_intensity_cutoff(
    table: pd.DataFrame, column_tag: str, threshold: float
) -> None:
    """Sets values below the threshold to NA.

    Args:
        table: Dataframe to which the protein annotations are added.
        column_tag: Substring used to identify intensity columns from the 'table' to
            which the intensity cutoff is applied.
        threshold: Values below the treshold will be set to NA.
    """
    for column in find_columns(table, column_tag):
        table.loc[table[column] < threshold, column] = np.nan


def find_columns(
    table: pd.DataFrame, substring: str, must_be_substring: bool = False
) -> list[str]:
    """Returns a list column names containing the substring.

    Args:
        table: Columns of this datafram are queried.
        substring: String that must be part of column names.
        must_be_substring: If true than column names are not reported if they
            are exactly equal to the substring.

    Returns:
        A list of column names.
    """
    matched_columns = [col for col in table.columns if substring in col]
    if must_be_substring:
        matched_columns = [col for col in matched_columns if col != substring]
    return matched_columns


def find_sample_columns(
    table: pd.DataFrame, substring: str, samples: Iterable[str]
) -> list[str]:
    """Returns column names that contain the substring and any entry of 'samples'.

    Args:
        table: Columns of this dataframe are queried.
        substring: String that must be part of column names.
        samples: List of strings from which at least one must be present in matched
            columns.

    Returns:
        A list of column names containing the substring and any entry of 'samples'.
        Columns are returned in the order of entries in 'samples'.
    """
    WHITESPACE_CHARS = " ."

    matched_columns = []
    substring_columns = find_columns(table, substring)
    for sample in samples:
        sample_columns = [c for c in substring_columns if sample in c]
        for col in sample_columns:
            column_remainder = (
                col.replace(substring, "").replace(sample, "").strip(WHITESPACE_CHARS)
            )
            if column_remainder == "":
                matched_columns.append(col)
                break
    return matched_columns


def keep_rows_by_partial_match(
    table: pd.DataFrame, column: str, values: Iterable[str]
) -> pd.DataFrame:
    """Filter a table to keep only rows partially matching any of the specified values.

    Args:
        table: The input table that will be filtered.
        column: The name of the column in the 'table' which entries are checked for
            partial matches to the values. This column must have the datatype 'str'.
        modifications: An iterable of strings that are used to filter the table. Any of
            the specified values must have at least a partial match to an entry from the
            specified 'column' for a row to be kept in the filtered table.

    Returns:
        A new DataFrame containing only the rows that have a partial or complete match
        with any of the specified 'values'.

    Example:
        >>> df = pd.DataFrame({"Modifications": ["phos", "acetyl;phos", "acetyl"]})
        >>> keep_rows_by_partial_match(df, "Modifications", ["phos"])
          Modifications
        0          phos
        1   acetyl;phos
    """
    value_masks = [table[column].str.contains(value, regex=False) for value in values]
    target_mask = np.any(value_masks, axis=0)
    filtered_table = table[target_mask].copy()
    return filtered_table


def remove_rows_by_partial_match(
    table: pd.DataFrame, column: str, values: Iterable[str]
) -> pd.DataFrame:
    """Filter a table to remove rows partially matching any of the specified values.

    Args:
        table: The input table that will be filtered.
        column: The name of the column in the 'table' which entries are checked for
            partial matches to the values. This column must have the datatype 'str'.
        modifications: An iterable of strings that are used to filter the table. Any of
            the specified values must have at least a partial match to an entry from the
            specified 'column' for a row to be removed in the filtered table.

    Returns:
        A new DataFrame containing no rows that have a partial or complete match with
        any of the specified 'values'.

    Example:
        >>> df = pd.DataFrame({"Modifications": ["phos", "acetyl;phos", "acetyl"]})
        >>> remove_rows_by_partial_match(df, "Modifications", ["phos"])
          Modifications
        2        acetyl
    """
    value_masks = [table[column].str.contains(value, regex=False) for value in values]
    target_mask = ~np.any(value_masks, axis=0)
    filtered_table = table[target_mask].copy()
    return filtered_table


def join_tables(
    tables: Sequence[pd.DataFrame], reset_index: bool = False
) -> pd.DataFrame:
    """Returns a joined dataframe.

    Dataframes are merged iteratively on their index using an outer join, beginning with
    the first entry from 'tables'. Can only join dataframes with different columns.

    Args:
        tables: Dataframes that will be merged together.
        reset_index: If True, the index of the joined dataframe is reset.

    Returns:
        A merged dataframe.
    """
    merged_table = tables[0]
    for table in tables[1:]:
        merged_table = merged_table.join(table, how="outer")
    if reset_index:
        merged_table.reset_index(inplace=True)
    return merged_table
