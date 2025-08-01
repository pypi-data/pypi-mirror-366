"""Tools for post-processing and statistical analysis of `Qtable` data.

All functions in this module take a `Qtable` object and modify its data in place. The
module provides functionality for data evaluation, normalization, imputation of missing
values, and statistical testing, including integration with R's LIMMA package.
"""

import warnings
from typing import Iterable, Optional, Protocol, Sequence

import numpy as np
import pandas as pd
from typing_extensions import Self

import msreport.normalize
from msreport.errors import OptionalDependencyError
from msreport.helper import find_sample_columns
from msreport.qtable import Qtable

try:
    import msreport.rinterface

    _rinterface_available = True
    _rinterface_error = ""
except OptionalDependencyError as err:
    _rinterface_available = False
    _rinterface_error = str(err)


class Transformer(Protocol):
    def fit(self, table: pd.DataFrame) -> Self:
        """Fits the Transformer and returns a fitted Transformer instance."""

    def is_fitted(self) -> bool:
        """Returns True if the Transformer has been fitted."""

    def transform(self, table: pd.DataFrame) -> pd.DataFrame:
        """Transform values in 'table'."""


class CategoryTransformer(Protocol):
    def fit(self, table: pd.DataFrame) -> Self:
        """Fits the Transformer and returns a fitted Transformer instance."""

    def is_fitted(self) -> bool:
        """Returns True if the Transformer has been fitted."""

    def transform(self, table: pd.DataFrame) -> pd.DataFrame:
        """Transform values in 'table'."""

    def get_category_column(self) -> str:
        """Returns the name of the category column."""


def analyze_missingness(qtable: Qtable) -> None:
    """Quantifies missing values of expression columns.

    Adds additional columns to the qtable; for the number of missing values per sample
    "Missing sample_name", per experiment "Missing experiment_name" and in total
    "Missing total"; and for the number of quantification events per experiment
    "Events experiment_name" and in total "Events total".

    Requires expression columns to be set. Missing values in expression columns must be
    present as NaN, and not as zero or an empty string.

    Args:
        qtable: A Qtable instance.
    """
    # TODO: not tested #
    missing_events = pd.DataFrame()
    quant_events = pd.DataFrame()
    table = qtable.make_expression_table(samples_as_columns=True)
    num_missing = np.isnan(table).sum(axis=1)
    num_events = np.isfinite(table).sum(axis=1)
    quant_events["Events total"] = num_events
    missing_events["Missing total"] = num_missing
    for experiment in qtable.get_experiments():
        exp_samples = qtable.get_samples(experiment)
        num_events = np.isfinite(table[exp_samples]).sum(axis=1)
        quant_events[f"Events {experiment}"] = num_events
        num_missing = np.isnan(table[exp_samples]).sum(axis=1)
        missing_events[f"Missing {experiment}"] = num_missing
    for sample in qtable.get_samples():
        sample_missing = np.isnan(table[sample])
        missing_events[f"Missing {sample}"] = sample_missing
    qtable.add_expression_features(missing_events)
    qtable.add_expression_features(quant_events)


def validate_proteins(
    qtable: Qtable,
    min_peptides: int = 0,
    min_spectral_counts: int = 0,
    remove_contaminants: bool = True,
    min_events: Optional[int] = None,
    max_missing: Optional[int] = None,
) -> None:
    """Validates protein entries (rows).

    Adds an additional column "Valid" to the qtable, containing Boolean values.

    Requires expression columns to be set. Depending on the arguments requires the
    columns "Total peptides", "Spectral count Combined", "Potential contaminant", and
    the experiment columns "Missing experiment_name" and "Events experiment_name".

    Args:
        qtable: A Qtable instance.
        min_peptides: Minimum number of unique peptides, default 0.
        min_spectral_counts: Minimum number of combined spectral counts, default 0.
        remove_contaminants: If true, the "Potential contaminant" column is used to
            remove invalid entries, default True. If no "Potential contaminant" column
            is present 'remove_contaminants' is ignored.
        min_events: If specified, at least one experiment must have the minimum number
            of quantified events for the protein entry to be valid.
        max_missing: If specified, at least one experiment must have no more than the
            maximum number of missing values.
    """
    valid_entries = np.ones(qtable.data.shape[0], dtype=bool)

    if min_peptides > 0:
        if "Total peptides" not in qtable:
            raise KeyError("'Total peptides' column not present in qtable.data")
        valid_entries = np.all(
            [valid_entries, qtable["Total peptides"] >= min_peptides], axis=0
        )

    if min_spectral_counts > 0:
        if "Spectral count Combined" not in qtable:
            raise KeyError(
                "'Spectral count Combined' column not present in qtable.data"
            )
        valid_entries = np.all(
            [valid_entries, qtable["Spectral count Combined"] >= min_spectral_counts],
            axis=0,
        )

    # TODO: not tested from here #
    if remove_contaminants:
        if "Potential contaminant" not in qtable:
            raise KeyError("'Potential contaminant' column not present in qtable.data")
        valid_entries = np.all(
            [valid_entries, np.invert(qtable["Potential contaminant"])], axis=0
        )

    if max_missing is not None:
        cols = [" ".join(["Missing", e]) for e in qtable.get_experiments()]
        if not pd.Series(cols).isin(qtable.data.columns).all():
            raise Exception(
                f"Not all columns from {cols} are present in qtable.data,"
                " analyze missingness before calling validate_proteins()."
            )
        max_missing_valid = np.any(qtable[cols] <= max_missing, axis=1)
        valid_entries = max_missing_valid & valid_entries

    if min_events is not None:
        cols = [" ".join(["Events", e]) for e in qtable.get_experiments()]
        if not pd.Series(cols).isin(qtable.data.columns).all():
            raise Exception(
                f"Not all columns from {cols} are present in qtable.data,"
                " analyze missingness before calling validate_proteins()."
            )
        min_events_valid = np.any(qtable[cols] >= min_events, axis=1)
        valid_entries = min_events_valid & valid_entries

    qtable["Valid"] = valid_entries


def apply_transformer(
    qtable: Qtable,
    transformer: Transformer,
    tag: str,
    exclude_invalid: bool,
    remove_invalid: bool,
    new_tag: Optional[str] = None,
) -> None:
    """Applies a transformer to the values of a Qtable selected with the tag parameter.

    Args:
        qtable: A Qtable instance, to which the transformer is applied.
        transformer: The transformer to apply.
        tag: The tag used to identify the columns for applying the transformer.
        exclude_invalid: Exclude invalid values from the transformation.
        remove_invalid: Remove invalid values from the table after the transformation.
        new_tag: Optional, if specified than the tag is replaced with this value in the
            column names and the transformed data is stored to these new columns.
    """
    valid = qtable.data["Valid"]
    samples = qtable.get_samples()
    sample_columns = find_sample_columns(qtable.data, tag, samples)

    if not sample_columns:
        raise ValueError(f"No sample columns found for tag '{tag}'.")

    if new_tag is not None:
        sample_columns = [c.replace(tag, new_tag) for c in sample_columns]
    column_mapping = dict(zip(samples, sample_columns))

    data_table = qtable.make_sample_table(tag, samples_as_columns=True)

    if exclude_invalid:
        data_table[valid] = transformer.transform(data_table[valid])
    else:
        data_table = transformer.transform(data_table)

    if remove_invalid:
        data_table[~valid] = np.nan

    data_table.columns = [column_mapping[s] for s in data_table.columns]
    qtable.data[data_table.columns] = data_table


def apply_category_transformer(
    qtable: Qtable,
    transformer: CategoryTransformer,
    tag: str,
    exclude_invalid: bool,
    remove_invalid: bool,
    new_tag: Optional[str] = None,
) -> None:
    """Apply a category transformer to Qtable columns selected by tag.

    Args:
        qtable: A Qtable instance, to which the transformer is applied.
        transformer: The CategoryTransformer to apply.
        tag: The tag used to identify the columns for applying the transformer.
        exclude_invalid: Exclude invalid values from the transformation.
        remove_invalid: Remove invalid values from the table after the transformation.
        new_tag: Optional, if specified than the tag is replaced with this value in the
            column names and the transformed data is stored to these new columns.

    Raises:
        KeyError: If the category column of the `transformer` is not found in the
            `qtable.data`.
        ValueError: If no sample columns are found for the specified tag.
    """
    category_column = transformer.get_category_column()
    if category_column not in qtable.data.columns:
        raise KeyError(
            f'The category column "{category_column}" in the transformer '
            f"is not found in `qtable.data`."
        )

    valid = qtable.data["Valid"]
    samples = qtable.get_samples()
    sample_columns = find_sample_columns(qtable.data, tag, samples)

    if not sample_columns:
        raise ValueError(f"No sample columns found for tag '{tag}'.")

    if new_tag is not None:
        sample_columns = [c.replace(tag, new_tag) for c in sample_columns]
    column_mapping = dict(zip(samples, sample_columns))

    data_table = qtable.make_sample_table(tag, samples_as_columns=True)
    data_table[category_column] = qtable.data[category_column]

    if exclude_invalid:
        data_table.loc[valid, :] = transformer.transform(data_table.loc[valid, :])
    else:
        data_table = transformer.transform(data_table)
    data_table = data_table.drop(columns=[category_column])

    if remove_invalid:
        data_table[~valid] = np.nan

    data_table.columns = [column_mapping[s] for s in data_table.columns]
    qtable.data[data_table.columns] = data_table


def normalize_expression(
    qtable: Qtable,
    normalizer: Transformer,
    exclude_invalid: bool = True,
) -> None:
    """Normalizes expression values in qtable.

    Normalizes values present in the qtable expression columns, requires that expression
    columns are defined. The normalizer will be fit with the expression values if it has
    not been fitted already.

    Args:
        qtable: A Qtable instance, which expression values will be normalized.
        normalizer: A Normalizer instance from the msreport.normalize module. Note that
            if an already fitted normalizer is passed, it has to be fitted with a
            dataframe which column names correspond to the sample names present in
            qtable.design. A not fitted normalizer is fitted with the expression values
            present in the qtable.
        exclude_invalid: If true, the column "Valid" is used to filter which expression
            rows are used for fitting a not fitted normalizer; default True. Independent
            of if exclude_invalid is True or False, all expression values will be
            normalized.
    """
    table = qtable.make_expression_table(samples_as_columns=True, features=["Valid"])
    sample_columns = table.columns.drop("Valid")
    expression_columns = [qtable.get_expression_column(s) for s in sample_columns]

    raw_data = table[sample_columns]
    if not normalizer.is_fitted():
        if exclude_invalid:
            normalizer.fit(raw_data[table["Valid"]])
        else:
            normalizer = normalizer.fit(raw_data)

    transformed_data = normalizer.transform(raw_data)
    qtable[expression_columns] = transformed_data[sample_columns]


def create_site_to_protein_normalizer(
    qtable: Qtable, category_column: str = "Representative protein"
) -> msreport.normalize.CategoricalNormalizer:
    """Creates a fitted `CategoricalNormalizer` for site-to-protein normalization.

    The `CategoricalNormalizer` is fitted to protein expression profiles of the provided
    `qtable`. The protein expression profiles are calculated by subtracting the mean
    expression value of each protein from the protein expression values. Expression
    values must be log transformed. The generated `CategoricalNormalizer` can be used to
    normalize ion, peptide or site qtables based on protein categories.

    Args:
        qtable: Qtable instance containing protein values for fitting the normalizer.
        category_column: The name of the column containing the protein categories.

    Returns:
        A fitted `CategoricalNormalizer` object.
    """
    reference_expression = qtable.make_expression_table(
        samples_as_columns=True,
        features=[category_column],
    )
    completely_quantified = ~reference_expression[qtable.get_samples()].isna().any(
        axis=1
    )
    reference_expression = reference_expression[completely_quantified]

    sample_columns = qtable.get_samples()
    reference_profiles = reference_expression[sample_columns].sub(
        reference_expression[sample_columns].mean(axis=1), axis=0
    )
    reference_profiles[category_column] = reference_expression[category_column]

    normalizer = msreport.normalize.CategoricalNormalizer(category_column)
    normalizer = normalizer.fit(reference_profiles)

    return normalizer


def create_ibaq_transformer(
    qtable: Qtable,
    category_column: str = "Representative protein",
    ibaq_column: str = "iBAQ peptides",
) -> msreport.normalize.CategoricalNormalizer:
    """Creates a fitted `CategoricalNormalizer` for iBAQ transformation.

    The `CategoricalNormalizer` is fitted to iBAQ peptide counts of the provided
    `qtable`, and can be used to transform protein intensities by dividing them by the
    corresponding iBAQ peptide counts. Missing iBAQ peptide counts are replaced by 1 and
    values smaller than 1 are replaced by 1. iBAQ peptide counts are then log2
    transformed because the `CategoryTransformer` expects log2 transformed values.

    Args:
        qtable: Qtable instance containing iBAQ peptide counts for fitting the
            normalizer.
        category_column: The name of the column containing the protein categories.
        ibaq_column: The name of the column containing the iBAQ peptide counts.

    Returns:
        A fitted `CategoricalNormalizer` object.
    """
    category_values = qtable[category_column].copy()
    ibaq_factor_values = qtable[ibaq_column].copy()
    sample_columns = qtable.get_samples()

    ibaq_factor_values = ibaq_factor_values.fillna(1)
    ibaq_factor_values[ibaq_factor_values < 1] = 1
    ibaq_factor_values = np.log2(ibaq_factor_values)

    reference_table = pd.DataFrame(dict.fromkeys(sample_columns, ibaq_factor_values))
    reference_table[category_column] = category_values

    normalizer = msreport.normalize.CategoricalNormalizer(category_column)
    normalizer = normalizer.fit(reference_table)

    return normalizer


def normalize_expression_by_category(
    qtable: Qtable, normalizer: CategoryTransformer
) -> None:
    """Normalizes expression values in a Qtable based on categories.

    Args:
        qtable: A Qtable instance, which expression values will be normalized.
        normalizer: A `CategoryTransformer` object used for normalization.

    Raises:
        KeyError: If the category column of the `CategoryTransformer` object is not
            found in the `qtable.data`.
    """
    category_column = normalizer.get_category_column()
    if category_column not in qtable.data.columns:
        raise KeyError(
            f'The category column "{category_column}" in the normalizer '
            f"is not found in `qtable.data`."
        )

    table = qtable.make_expression_table(
        samples_as_columns=True, features=[category_column]
    )
    sample_columns = table.columns.drop(category_column)
    expression_columns = [qtable.get_expression_column(s) for s in sample_columns]

    raw_data = table[sample_columns.append(pd.Index([category_column]))]
    transformed_data = normalizer.transform(raw_data)
    qtable.data[expression_columns] = transformed_data[sample_columns]


def impute_missing_values(
    qtable: Qtable,
    imputer: Transformer,
    exclude_invalid: bool = True,
) -> None:
    """Imputes missing expression values in qtable.

    Imputes missing values (nan) present in the qtable expression columns, requires
    that the qtable has defined expression columns. If the passed imputer object is not
    yet fitted, it will be fit with the expression values. If 'exclude_invalid' is True,
    only valid expression values will be used for fitting the imputer.

    Args:
        qtable: A Qtable instance, which missing expression values will be imputed.
        imputer: An Imputer instance from the msreport.impute module. Note that if an
            already fitted imputer is passed, it has to be fitted with a dataframe which
            column names correspond to the sample names present in qtable.design. A not
            fitted imputer is fitted with the expression values present in the qtable.
        exclude_invalid: If true, the column "Valid" is used to determine for which rows
            imputation is performed. Default True.
    """
    table = qtable.make_expression_table(samples_as_columns=True, features=["Valid"])
    sample_columns = table.columns.drop("Valid")
    expression_columns = [qtable.get_expression_column(s) for s in sample_columns]
    if exclude_invalid:
        valid_mask = table["Valid"]
    else:
        valid_mask = np.ones_like(table["Valid"], dtype=bool)

    raw_data = table.loc[valid_mask, sample_columns]
    if not imputer.is_fitted():
        imputer = imputer.fit(raw_data)

    imputed_data = imputer.transform(raw_data)
    imputed_data.rename(
        columns=dict(zip(sample_columns, expression_columns)), inplace=True
    )
    qtable.data.loc[valid_mask, expression_columns] = imputed_data


def calculate_experiment_means(qtable: Qtable) -> None:
    """Calculates mean expression values for each experiment.

    Adds a new column "Expression experiment_name" for each experiment, containing the
    mean expression values of the corresponding samples.

    Args:
        qtable: A Qtable instance, which mean experiment expression values will be
            calculated.
    """
    experiment_means = {}
    for experiment in qtable.get_experiments():
        samples = qtable.get_samples(experiment)
        columns = [qtable.get_expression_column(s) for s in samples]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            row_means = np.nanmean(qtable[columns], axis=1)
        experiment_means[f"Expression {experiment}"] = row_means
    qtable.add_expression_features(pd.DataFrame(experiment_means))


def calculate_multi_group_comparison(
    qtable: Qtable,
    experiment_pairs: Iterable[Iterable[str]],
    exclude_invalid: bool = True,
) -> None:
    """Calculates average expression and ratios for multiple comparison groups.

    For each experiment pair, adds new columns
    "Average expression Experiment_1 vs Experiment_2" and
    "Ratio [log2] Experiment_1 vs Experiment_2" to the qtable. Expression values must be
    log transformed.

    Args:
        qtable: Qtable instance that contains expression values for calculating group
            comparisons.
        experiment_pairs: A list containing one or multiple experiment pairs for which
            the group comparison should be calculated. The specified experiments must
            correspond to entries from qtable.design["Experiment"].
        exclude_invalid: If true, the column "Valid" is used to determine which rows are
            used for calculating the group comparisons; default True.

    Raises:
        ValueError: If 'experiment_pairs' contains invalid entries. Each experiment pair
            must have exactly two entries and the two entries must not be the same. All
            experiments must be present in qtable.design. No duplicate experiment pairs
            are allowed.
    """
    _validate_experiment_pairs(qtable, experiment_pairs)

    table = qtable.make_expression_table(samples_as_columns=True, features=["Valid"])
    comparison_tag = " vs "

    if exclude_invalid:
        invalid = np.invert(table["Valid"].to_numpy())
    else:
        invalid = np.zeros(table.shape[0], dtype=bool)

    for experiment_pair in experiment_pairs:
        comparison_group = comparison_tag.join(experiment_pair)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            group_expressions = []
            for experiment in experiment_pair:
                samples = qtable.get_samples(experiment)
                group_expressions.append(np.nanmean(table[samples], axis=1))
            ratios = group_expressions[0] - group_expressions[1]
            average_expressions = np.nanmean(group_expressions, axis=0)

        comparison_table = pd.DataFrame(
            {
                f"Average expression {comparison_group}": average_expressions,
                f"Ratio [log2] {comparison_group}": ratios,
            }
        )
        comparison_table[invalid] = np.nan
        qtable.add_expression_features(comparison_table)


def two_group_comparison(
    qtable: Qtable, experiment_pair: Iterable[str], exclude_invalid: bool = True
) -> None:
    """Calculates comparison values for two experiments.

    Adds new columns "Average expression Experiment_1 vs Experiment_2" and
    "Ratio [log2] Experiment_1 vs Experiment_2" to the qtable. Expects that expression
    values are log2 transformed.

    Args:
        qtable: A Qtable instance, containing expression values.
        experiment_pair: The two experiments that will be compared, experiments must be
            present in qtable.design
        exclude_invalid: If true, the column "Valid" is used to determine for which rows
            comparison values are calculated.
    """
    calculate_multi_group_comparison(
        qtable, experiment_pairs=[experiment_pair], exclude_invalid=exclude_invalid
    )


def calculate_multi_group_limma(
    qtable: Qtable,
    experiment_pairs: Sequence[Iterable[str]],
    exclude_invalid: bool = True,
    batch: bool = False,
    limma_trend: bool = True,
) -> None:
    """Uses limma to perform a differential expression analysis of multiple experiments.

    For each experiment pair specified in 'experiment_pairs' the following new columns
    are added to the qtable:
    - "P-value Experiment_1 vs Experiment_2"
    - "Adjusted p-value Experiment_1 vs Experiment_2"
    - "Average expression Experiment_1 vs Experiment_2"
    - "Ratio [log2] Experiment_1 vs Experiment_2"

    Requires that expression columns are set, and expression values are log2 transformed
    All rows with missing values are ignored, impute missing values to allow
    differential expression analysis of all rows.

    Args:
        qtable: Qtable instance that contains expression values for differential
            expression analysis.
        experiment_pairs: A list containing lists of experiment pairs for which the
            results of the differential expression analysis should be reported. The
            specified experiment pairs must correspond to entries from
            qtable.design["Experiment"].
        exclude_invalid: If true, the column "Valid" is used to determine which rows are
            used for the differential expression analysis; default True.
        batch: If true batch effects are considered for the differential expression
            analysis. Batches must be specified in the design in a "Batch" column.
        limma_trend: If true, an intensity-dependent trend is fitted to the prior
            variance during calculation of the moderated t-statistics, refer to
            limma.eBayes for details; default True.

    Raises:
        ValueError: If 'experiment_pairs' contains invalid entries. Each experiment pair
            must have exactly two entries and the two entries must not be the same. All
            experiments must be present in qtable.design. No duplicate experiment pairs
            are allowed.
        KeyError: If the "Batch" column is not present in the qtable.design when
            'batch' is set to True.
        ValueError: If all values from qtable.design["Batch"] are identical when 'batch'
            is set to True.
    """
    if not _rinterface_available:
        raise OptionalDependencyError(_rinterface_error)

    _validate_experiment_pairs(qtable, experiment_pairs)
    # TODO: not tested #
    if batch and "Batch" not in qtable.get_design():
        raise KeyError(
            "When using calculate_multi_group_limma(batch=True) a"
            ' "Batch" column must be present in qtable.design'
        )
    if batch and qtable.get_design()["Batch"].nunique() == 1:
        raise ValueError(
            "When using calculate_multi_group_limma(batch=True), not all values from"
            ' qtable.design["Batch"] are allowed to be identical.'
        )

    design = qtable.get_design()
    table = qtable.make_expression_table(samples_as_columns=True)
    table.index = table.index.astype(str)  # It appears that a string is required for R
    comparison_tag = " vs "

    if exclude_invalid:
        valid = qtable["Valid"]
    else:
        valid = np.full(table.shape[0], True)
    not_nan = table.isna().sum(axis=1) == 0
    mask = np.all([valid, not_nan], axis=0)

    # Exchange experiment names with names that are guaranteed to be valid in R
    experiment_to_r = {}
    for i, experiment in enumerate(design["Experiment"].unique()):
        experiment_to_r[experiment] = f".EXPERIMENT__{i:04d}"
    r_to_experiment = {v: k for k, v in experiment_to_r.items()}

    r_experiment_pairs: list[str] = []
    for exp1, exp2 in experiment_pairs:
        r_experiment_pairs.append(f"{experiment_to_r[exp1]}-{experiment_to_r[exp2]}")

    design.replace({"Experiment": experiment_to_r}, inplace=True)

    # Run limma and join results for all comparison groups
    limma_results = msreport.rinterface.multi_group_limma(
        table[mask], design, r_experiment_pairs, batch, limma_trend
    )
    for r_comparison_group, limma_result in limma_results.items():
        experiment_pair = [r_to_experiment[s] for s in r_comparison_group.split("-")]
        comparison_group = comparison_tag.join(experiment_pair)
        mapping = {col: f"{col} {comparison_group}" for col in limma_result.columns}
        limma_result.rename(columns=mapping, inplace=True)

    limma_table = pd.DataFrame(index=table.index)
    limma_table = limma_table.join(list(limma_results.values()))
    limma_table.fillna(np.nan, inplace=True)
    qtable.add_expression_features(limma_table)

    # Average expression from limma is the whole row mean, overwrite with the average
    # expression of the experiment group
    for experiment_pair in experiment_pairs:
        two_group_comparison(qtable, experiment_pair, exclude_invalid=exclude_invalid)


def calculate_two_group_limma(
    qtable: Qtable,
    experiment_pair: Sequence[str],
    exclude_invalid: bool = True,
    limma_trend: bool = True,
) -> None:
    """Uses limma to perform a differential expression analysis of two experiments.

    Adds new columns "P-value Experiment_1 vs Experiment_2",
    "Adjusted p-value Experiment_1 vs Experiment_2",
    "Average expression Experiment_1 vs Experiment_2", and
    "Ratio [log2] Experiment_1 vs Experiment_2" to the qtable.

    Requires that expression columns are set, and expression values are log2
    transformed. All rows with missing values are ignored, impute missing values to
    allow differential expression analysis of all rows.

    Args:
        qtable: Qtable instance that contains expression values for differential
            expression analysis.
        experiment_pair: The names of the two experiments that will be compared,
            experiments must be present in qtable.design
        exclude_invalid: If true, the column "Valid" is used to determine which rows are
            used for the differential expression analysis; default True.
        limma_trend: If true, an intensity-dependent trend is fitted to the prior
            variances; default True.
    Raises:
        ValueError: If 'experiment_pair' contains invalid entries. The experiment pair
            must have exactly two entries and the two entries must not be the same. Both
            experiments must be present in qtable.design.
    """
    if not _rinterface_available:
        raise OptionalDependencyError(_rinterface_error)

    _validate_experiment_pair(qtable, experiment_pair)
    # TODO: LIMMA function not tested #
    table = qtable.make_expression_table(samples_as_columns=True)
    comparison_tag = " vs "

    if exclude_invalid:
        valid = qtable["Valid"]
    else:
        valid = np.full(table.shape[0], True)

    samples_to_experiment = {}
    for experiment in experiment_pair:
        mapping = dict.fromkeys(qtable.get_samples(experiment), experiment)
        samples_to_experiment.update(mapping)

    # Keep only samples that are present in the 'experiment_pair'
    table = table[samples_to_experiment.keys()]
    table.index = table.index.astype(str)  # It appears that a string is required for R
    not_nan = table.isna().sum(axis=1) == 0

    mask = np.all([valid, not_nan], axis=0)
    experiments = list(samples_to_experiment.values())

    # Note that the order of experiments for calling limma is reversed
    limma_result = msreport.rinterface.two_group_limma(
        table[mask], experiments, experiment_pair[1], experiment_pair[0], limma_trend
    )

    # For adding expression features to the qtable it is necessary that the
    # the limma_results have the same number of rows.
    limma_table = pd.DataFrame(index=table.index, columns=limma_result.columns)
    limma_table[mask] = limma_result
    limma_table.fillna(np.nan, inplace=True)

    comparison_group = comparison_tag.join(experiment_pair)
    mapping = {col: f"{col} {comparison_group}" for col in limma_table.columns}
    limma_table.rename(columns=mapping, inplace=True)
    qtable.add_expression_features(limma_table)


def _validate_experiment_pairs(
    qtable: Qtable, exp_pairs: Iterable[Iterable[str]]
) -> None:
    """Validates that experiment pairs are valid and raises an error if not.

    - All 'exp_pairs' entries must have a length of exactly 2.
    - All experiments must be present in the qtable.design.
    - No duplicate experiments are allowed in a pair.
    - No duplicate experiment pairs are allowed.

    Args:
        qtable: Qtable instance containing experiment data.
        exp_pairs: Iterable of experiment pairs to validate.

    Raises:
        ValueError: If any of the validation checks fail.
    """
    all_experiments = {exp for pair in exp_pairs for exp in pair}
    missing_experiments = all_experiments - set(qtable.get_experiments())
    if missing_experiments:
        raise ValueError(
            f"Experiments '{missing_experiments}' not found in qtable.design."
        )
    for experiment_pair in exp_pairs:
        _validate_experiment_pair(qtable, experiment_pair)

    if len(list(exp_pairs)) != len({tuple(pair) for pair in exp_pairs}):
        raise ValueError(
            f"Some experiment pairs in {exp_pairs} have been specified multiple "
            "times. Each pair must occur only once."
        )


def _validate_experiment_pair(qtable: Qtable, exp_pair: Iterable[str]) -> None:
    """Validates the experiment pair is valid and raises an error if not.

    - The experiment pair must contain exactly two entries
    - The two entries of the experiment pair must be different.
    - Both  experiments must be present in the qtable.design.

    Args:
        qtable: Qtable instance containing experiment data.
        experiment_pairs: Iterable of experiment pairs to validate.

    Raises:
        ValueError: If any of the validation checks fail.
    """
    if len(list(exp_pair)) != 2:
        raise ValueError(
            f"Experiment pair '{exp_pair}' contains more than two entries."
        )
    if len(list(exp_pair)) != len(set(exp_pair)):
        raise ValueError(f"Experiment pair '{exp_pair}' contains the same entry twice.")
    if set(exp_pair) - set(qtable.get_experiments()):
        raise ValueError(
            f"Experiments '{set(exp_pair) - set(qtable.get_experiments())}' "
            "not found in qtable.design."
        )
