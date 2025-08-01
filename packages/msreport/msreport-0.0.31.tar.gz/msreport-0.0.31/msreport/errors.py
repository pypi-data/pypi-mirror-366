class MsreportError(Exception): ...


class NotFittedError(ValueError, AttributeError):
    """Exception class to raise if Normalizer is used before fitting."""


class ProteinsNotInFastaWarning(UserWarning):
    """Warning raised when queried proteins are absent from a FASTA file."""


class OptionalDependencyError(ImportError):
    """Raised when an optional dependency is required but not installed."""
