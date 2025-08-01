"""Transformer classes for imputing missing values in quantitative proteomics data.

This module defines transformer classes that can be fitted to a table containing
quantitative values to learn imputation parameters. Once fitted, these transformers can
then be applied to another table to transform it by filling in missing values. The
transformation returns a new copy of the table with the imputed values, leaving the
original table unchanged.
"""

from typing import Any, Optional

import numpy as np
import pandas as pd
from typing_extensions import Self

from msreport.errors import NotFittedError


class FixedValueImputer:
    """Imputer for completing missing values with a fixed value.

    Replace missing values using a constant value or with an integer that is smaller
    than the minimum value of each column or smaller than the minimum value of the whole
    array.
    """

    def __init__(
        self,
        strategy: str,
        fill_value: float = 0.0,
        column_wise: bool = True,
    ):
        """Initializes the FixedValueImputer.

        Args:
            strategy: The imputation strategy.
                - If "constant", replace missing values with 'fill_value'.
                - If "below", replace missing values with an integer that is smaller
                  than the minimal value of the fitted dataframe. Minimal values are
                  calculated per column if 'column_wise' is True, otherwise the minimal
                  value is calculated for all columns.
            fill_value: When strategy is "constant", 'fill_value' is used to replace all
                occurrences of missing_values.
            column_wise: If True, imputation is performed independently for each column,
                otherwise the whole dataframe is imputed togeter. Default True.

        """
        self.strategy = strategy
        self.fill_value = fill_value
        self.column_wise = column_wise
        self._sample_fill_values: dict[str, float] = {}

    def fit(self, table: pd.DataFrame) -> Self:
        """Fits the FixedValueImputer.

        Args:
            table: Input Dataframe for generating fill values for each column.

        Returns:
            Returns the fitted FixedValueImputer instance.
        """
        if self.strategy == "constant":
            fill_values = dict.fromkeys(table.columns, self.fill_value)
        elif self.strategy == "below":
            if self.column_wise:
                fill_values = {}
                for column in table.columns:
                    fill_values[column] = _calculate_integer_below_min(table[column])
            else:
                int_below_min = _calculate_integer_below_min(table)
                fill_values = dict.fromkeys(table.columns, int_below_min)
        self._sample_fill_values = fill_values
        return self

    def is_fitted(self) -> bool:
        """Returns True if the FixedValueImputer has been fitted."""
        return len(self._sample_fill_values) != 0

    def transform(self, table: pd.DataFrame) -> pd.DataFrame:
        """Impute all missing values in 'table'.

        Args:
            table: A dataframe of numeric values that will be completed. Each column
                name must correspond to a column name from the table that was used for
                the fitting.

        Returns:
            'table' with imputed missing values.
        """
        _confirm_is_fitted(self)

        _table = table.copy()
        for column in _table.columns:
            column_data = np.array(_table[column], dtype=float)
            mask = ~np.isfinite(column_data)
            column_data[mask] = self._sample_fill_values[column]
            _table[column] = column_data
        return _table


class GaussianImputer:
    """Imputer for completing missing values by drawing from a gaussian distribution."""

    def __init__(self, mu: float, sigma: float, seed: Optional[int] = None):
        """Initializes the GaussianImputer.

        Args:
            mu: Mean of the gaussian distribution.
            sigma: Standard deviation of the gaussian distribution, must be positive.
            seed: Optional, allows specifying a number for initializing the random
                number generator. Using the same seed for the same input table will
                generate the same set of imputed values each time. Default is None,
                which results in different imputed values being generated each time.
        """
        self.mu = mu
        self.sigma = sigma
        self.seed = seed

    def fit(self, table: pd.DataFrame) -> Self:
        """Fits the GaussianImputer, altough this is not necessary.

        Args:
            table: Input Dataframe for fitting.

        Returns:
            Returns the fitted GaussianImputer instance.
        """
        return self

    def is_fitted(self) -> bool:
        """Returns always True, as the GaussianImputer does not need to be fitted."""
        return True

    def transform(self, table: pd.DataFrame) -> pd.DataFrame:
        """Impute all missing values in 'table'.

        Args:
            table: A dataframe of numeric values that will be completed. Each column
                name must correspond to a column name from the table that was used for
                the fitting.

        Returns:
            'table' with imputed missing values.
        """
        _confirm_is_fitted(self)
        np.random.seed(self.seed)

        _table = table.copy()
        for column in _table.columns:
            column_data = np.array(_table[column], dtype=float)
            mask = ~np.isfinite(column_data)
            column_data[mask] = np.random.normal(
                loc=self.mu, scale=self.sigma, size=mask.sum()
            )
            _table[column] = column_data
        return _table


class PerseusImputer:
    """Imputer for completing missing values as implemented in Perseus.

    Perseus-style imputation replaces missing values by random numbers drawn from a
    normal distribution. Sigma and mu of this distribution are calculated from the
    standard deviation and median of the observed values.
    """

    def __init__(
        self,
        median_downshift: float = 1.8,
        std_width: float = 0.3,
        column_wise: bool = True,
        seed: Optional[int] = None,
    ):
        """Initializes the GaussianImputer.

        Args:
            median_downshift: Times of standard deviations the observed median is
                downshifted for calulating mu of the normal distribution. Default is 1.8
            std_width: Factor for adjusting the standard deviation of the observed
                values to obtain sigma of the normal distribution. Default is 0.3
            column_wise: If True, imputation is performed independently for each column,
                otherwise the whole dataframe is imputed togeter. Default True.
            seed: Optional, allows specifying a number for initializing the random
                number generator. Using the same seed for the same input table will
                generate the same set of imputed values each time. Default is None,
                which results in different imputed values being generated each time.

        """
        self.median_downshift = median_downshift
        self.std_width = std_width
        self.column_wise = column_wise
        self.seed = seed
        self._column_params: dict[str, dict[str, float]] = {}

    def fit(self, table: pd.DataFrame) -> Self:
        """Fits the PerseusImputer.

        Args:
            table: Input Dataframe for calculating mu and sigma of the gaussian
                distribution.

        Returns:
            Returns the fitted PerseusImputer instance.
        """
        for column in table.columns:
            if self.column_wise:
                median = np.nanmedian(table[column])
                std = np.nanstd(table[column])
            else:
                median = np.nanmedian(table)
                std = np.nanstd(table)

            mu = median - (std * self.median_downshift)
            sigma = std * self.std_width

            self._column_params[column] = {"mu": mu, "sigma": sigma}
        return self

    def is_fitted(self) -> bool:
        """Returns True if the PerseusImputer has been fitted."""
        return len(self._column_params) != 0

    def transform(self, table: pd.DataFrame) -> pd.DataFrame:
        """Impute all missing values in 'table'.

        Args:
            table: A dataframe of numeric values that will be completed. Each column
                name must correspond to a column name from the table that was used for
                the fitting.

        Returns:
            'table' with imputed missing values.
        """
        _confirm_is_fitted(self)
        np.random.seed(self.seed)

        _table = table.copy()
        for column in _table.columns:
            column_data = np.array(_table[column], dtype=float)
            mask = ~np.isfinite(column_data)
            column_data[mask] = np.random.normal(
                loc=self._column_params[column]["mu"],
                scale=self._column_params[column]["sigma"],
                size=mask.sum(),
            )
            _table[column] = column_data
        return _table


def _confirm_is_fitted(imputer: Any, msg: Optional[str] = None) -> None:
    """Perform is_fitted validation for imputer instances.

    Checks if the imputer is fitted by verifying the presence of fitted attributes
    and otherwise raises a NotFittedError with the given message.

    Args:
        msg : str, default=None
            The default error message is, "This %(name) instance is not fitted
            yet. Call 'fit' with appropriate arguments before using this
            normalizer."
    """
    if msg is None:
        msg = (
            "This %(name)s instance is not fitted yet. Call 'fit' with "
            "appropriate arguments before using this imputer."
        )

    if not hasattr(imputer, "is_fitted"):
        raise TypeError(f"{imputer} is not an imputer instance.")
    else:
        fitted = imputer.is_fitted()

    if not fitted:
        raise NotFittedError(msg % {"name": type(imputer).__name__})


def _calculate_integer_below_min(table: pd.DataFrame) -> int:
    minimal_value = np.nanmin(table.to_numpy().flatten())
    below_minimal = np.floor(minimal_value)
    if minimal_value <= below_minimal:
        below_minimal = below_minimal - 1
    return int(below_minimal)
