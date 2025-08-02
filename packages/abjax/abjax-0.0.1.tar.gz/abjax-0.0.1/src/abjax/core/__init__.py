"""Core statistical methods for AB testing analysis.

This module contains the core statistical functions for AB testing,
including hypothesis testing, variance reduction techniques, and
sequential analysis capabilities.

Modules:
    stats: Basic statistical tests (t-tests, z-tests, Mann-Whitney U)
    cuped: CUPED variance reduction implementation
    corrections: Multiple testing corrections (Bonferroni, FDR)
    abtest: Main ABTest class with scikit-learn style API
    sequential: Sequential testing framework
    bayesian: Bayesian analysis methods
"""

from .corrections import CorrectionResult
from .corrections import apply_correction_to_results
from .corrections import benjamini_hochberg_fdr
from .corrections import bonferroni_correction
from .corrections import estimate_fdr
from .corrections import estimate_fwer
from .corrections import holm_bonferroni_correction
from .corrections import sidak_correction
from .cuped import CupedResult
from .cuped import automatic_covariate_selection
from .cuped import calculate_theta
from .cuped import cuped_adjusted_ttest
from .cuped import cuped_analysis
from .cuped import regression_adjustment
from .cuped import variance_reduction_ratio
from .stats import StatisticalResult
from .stats import mannwhitney_u
from .stats import student_ttest
from .stats import welch_ttest
from .stats import ztest

__all__ = [
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
    "cuped_adjusted_ttest",
    "regression_adjustment",
    "CorrectionResult",
    "bonferroni_correction",
    "benjamini_hochberg_fdr",
    "holm_bonferroni_correction",
    "sidak_correction",
    "apply_correction_to_results",
    "estimate_fdr",
    "estimate_fwer",
]
