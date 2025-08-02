"""ABJAX: High-performance AB testing analysis library with JAX and FastAPI.

ABJAX combines the statistical rigour of advanced variance reduction techniques
with the computational power of JAX. The library provides native CUPED
implementation, Bayesian and frequentist approaches, sequential testing
capabilities, and modern Python development practices.

Key Features:
- Native CUPED (Controlled-experiment Using Pre-Experiment Data) implementation
- JAX-powered statistical computations for high performance
- FastAPI backend for production deployment
- Bayesian and frequentist hypothesis testing
- Sequential testing with early stopping
- Polars integration for efficient data processing

Example usage:
    >>> from abjax import ABTest
    >>> test = ABTest(data=df, variant_col='variant', metric_col='revenue')
    >>> result = test.analyze(method='ttest', variance_reduction='cuped')
"""

__version__ = "0.0.1"
__author__ = "ABJAX Team"
__email__ = "team@abjax.dev"

# Import main classes and functions
from .core.corrections import CorrectionResult
from .core.corrections import apply_correction_to_results
from .core.corrections import benjamini_hochberg_fdr
from .core.corrections import bonferroni_correction
from .core.cuped import CupedResult
from .core.cuped import automatic_covariate_selection
from .core.cuped import calculate_theta
from .core.cuped import cuped_analysis
from .core.cuped import variance_reduction_ratio
from .core.stats import StatisticalResult
from .core.stats import mannwhitney_u
from .core.stats import student_ttest
from .core.stats import welch_ttest
from .core.stats import ztest

# Import main classes when they're implemented
# from .core.abtest import ABTest

__all__ = [
    "__version__",
    "StatisticalResult",
    "welch_ttest",
    "student_ttest",
    "ztest",
    "mannwhitney_u",
    "CupedResult",
    "cuped_analysis",
    "calculate_theta",
    "variance_reduction_ratio",
    "automatic_covariate_selection",
    "CorrectionResult",
    "bonferroni_correction",
    "benjamini_hochberg_fdr",
    "apply_correction_to_results",
    # "ABTest",
]
