"""Multiple testing correction methods for controlling Type I errors.

This module implements various multiple comparison procedures to control the
Family-Wise Error Rate (FWER) and False Discovery Rate (FDR) when conducting
multiple statistical tests simultaneously.

Key Features:
- Bonferroni correction (FWER control, most conservative)
- Benjamini-Hochberg procedure (FDR control)
- Holm-Bonferroni step-down procedure (FWER control, less conservative)
- Šidák correction (FWER control, exact under independence)
- Integration with StatisticalResult objects
- Error rate estimation and validation

Mathematical Background:
When conducting m simultaneous tests, the probability of at least one Type I
error (FWER) increases. Multiple testing procedures adjust p-values or significance
thresholds to maintain desired error control.

Example:
    >>> import numpy as np
    >>> from abjax.core.corrections import bonferroni_correction
    >>> p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
    >>> result = bonferroni_correction(p_values, alpha=0.05)
    >>> print(f"Rejected hypotheses: {result.rejected_hypotheses}")
    >>> print(f"FWER controlled at: {result.family_wise_error_rate:.3f}")
"""

import warnings
from copy import deepcopy
from dataclasses import dataclass
from typing import List

import jax.numpy as jnp
import numpy as np
from jax import jit

from .stats import StatisticalResult


@dataclass
class CorrectionResult:
    """Result of multiple testing correction procedure.

    Attributes:
        original_p_values: Original uncorrected p-values
        corrected_p_values: Adjusted p-values after correction
        significant: Boolean flags indicating significance after correction
        alpha: Significance level used
        method: Name of correction method used
        rejected_hypotheses: Number of rejected null hypotheses
        family_wise_error_rate: Estimated family-wise error rate
    """

    original_p_values: List[float]
    corrected_p_values: List[float]
    significant: List[bool]
    alpha: float
    method: str
    rejected_hypotheses: int
    family_wise_error_rate: float

    def number_of_comparisons(self) -> int:
        """Return the total number of comparisons made."""
        return len(self.original_p_values)

    def number_rejected(self) -> int:
        """Return the number of rejected hypotheses."""
        return self.rejected_hypotheses

    def proportion_rejected(self) -> float:
        """Return the proportion of hypotheses rejected."""
        if self.number_of_comparisons() == 0:
            return 0.0
        return self.rejected_hypotheses / self.number_of_comparisons()

    def estimated_true_discoveries(self) -> int:
        """Estimate the number of true discoveries.

        For FDR procedures, this estimates true positives.
        For FWER procedures, returns rejected hypotheses.
        """
        if "benjamini_hochberg" in self.method:
            # For FDR: E[True discoveries] ≈ R * (1 - FDR)
            estimated_fdr = min(self.alpha, 1.0)  # Conservative estimate
            return max(0, int(self.rejected_hypotheses * (1 - estimated_fdr)))
        else:
            # For FWER procedures, assume all discoveries are true if FWER controlled
            return self.rejected_hypotheses

    def summary(self) -> str:
        """Return a summary of the correction results."""
        return (
            f"{self.method.title()} Correction Summary:\n"
            f"  Total comparisons: {self.number_of_comparisons()}\n"
            f"  Rejected hypotheses: {self.rejected_hypotheses}\n"
            f"  Proportion rejected: {self.proportion_rejected():.3f}\n"
            f"  Family-wise error rate: {self.family_wise_error_rate:.6f}\n"
            f"  Significance level: {self.alpha}"
        )


@jit
def _bonferroni_adjust_jax(p_values: jnp.ndarray, m: int) -> jnp.ndarray:
    """JAX-compiled Bonferroni adjustment (internal function)."""
    return jnp.minimum(p_values * m, 1.0)


def bonferroni_correction(
    p_values: List[float], alpha: float = 0.05
) -> CorrectionResult:
    """Apply Bonferroni correction for multiple testing.

    The Bonferroni correction is the most conservative multiple testing procedure.
    It controls the Family-Wise Error Rate (FWER) by adjusting p-values:
    p_adjusted = min(p * m, 1.0) where m is the number of tests.

    Args:
        p_values: List of original p-values
        alpha: Significance level (default 0.05)

    Returns:
        CorrectionResult with adjusted p-values and significance flags

    Raises:
        ValueError: If p_values contain invalid values or alpha is invalid

    Example:
        >>> p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        >>> result = bonferroni_correction(p_values, 0.05)
        >>> print(result.rejected_hypotheses)
        1
    """
    # Validate inputs
    if not 0 < alpha < 1:
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")

    if not p_values:
        return CorrectionResult(
            original_p_values=[],
            corrected_p_values=[],
            significant=[],
            alpha=alpha,
            method="bonferroni",
            rejected_hypotheses=0,
            family_wise_error_rate=0.0,
        )

    p_array = np.array(p_values)
    if np.any((p_array < 0) | (p_array > 1)) or np.any(np.isnan(p_array)):
        raise ValueError("All p-values must be between 0 and 1")

    m = len(p_values)

    # Apply Bonferroni correction using JAX
    p_jax = jnp.array(p_values)
    corrected_jax = _bonferroni_adjust_jax(p_jax, m)
    corrected_p_values = corrected_jax.tolist()

    # Determine significance
    significant = [p <= alpha for p in corrected_p_values]
    rejected_hypotheses = sum(significant)

    # Calculate actual FWER for Bonferroni (should be <= alpha)
    family_wise_error_rate = min(alpha, 1.0)  # Bonferroni guarantees FWER <= alpha

    return CorrectionResult(
        original_p_values=p_values,
        corrected_p_values=corrected_p_values,
        significant=significant,
        alpha=alpha,
        method="bonferroni",
        rejected_hypotheses=rejected_hypotheses,
        family_wise_error_rate=family_wise_error_rate,
    )


def benjamini_hochberg_fdr(
    p_values: List[float], alpha: float = 0.05
) -> CorrectionResult:
    """Apply Benjamini-Hochberg procedure for FDR control.

    The Benjamini-Hochberg (BH) procedure controls the False Discovery Rate
    rather than the Family-Wise Error Rate, making it less conservative than
    Bonferroni. It uses a step-up procedure based on sorted p-values.

    Args:
        p_values: List of original p-values
        alpha: Significance level (default 0.05)

    Returns:
        CorrectionResult with FDR-controlled significance decisions

    Raises:
        ValueError: If p_values contain invalid values or alpha is invalid

    Example:
        >>> p_values = [0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205]
        >>> result = benjamini_hochberg_fdr(p_values, 0.05)
        >>> print(f"FDR-controlled rejections: {result.rejected_hypotheses}")
    """
    # Validate inputs
    if not 0 < alpha < 1:
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")

    if not p_values:
        return CorrectionResult(
            original_p_values=[],
            corrected_p_values=[],
            significant=[],
            alpha=alpha,
            method="benjamini_hochberg",
            rejected_hypotheses=0,
            family_wise_error_rate=0.0,
        )

    p_array = np.array(p_values)
    if np.any((p_array < 0) | (p_array > 1)) or np.any(np.isnan(p_array)):
        raise ValueError("All p-values must be between 0 and 1")

    m = len(p_values)
    n_tests = np.arange(1, m + 1)

    # Get original order indices
    original_indices = np.arange(m)

    # Sort p-values and keep track of original indices
    sorted_indices = np.argsort(p_values)
    sorted_p_values = np.array(p_values)[sorted_indices]

    # Apply BH step-up procedure
    # For each i, test if P(i) <= (i/m) * alpha
    bh_thresholds = (n_tests / m) * alpha
    significant_sorted = sorted_p_values <= bh_thresholds

    # Find largest i such that P(i) <= (i/m) * alpha
    rejection_indices = np.where(significant_sorted)[0]
    if len(rejection_indices) > 0:
        # Reject all hypotheses up to and including the largest qualifying index
        max_rejection_index = np.max(rejection_indices)
        significant_sorted[:max_rejection_index + 1] = True
        significant_sorted[max_rejection_index + 1:] = False
    else:
        significant_sorted[:] = False

    # Map back to original order
    significant = [False] * m
    for i, sorted_idx in enumerate(sorted_indices):
        significant[sorted_idx] = significant_sorted[i]

    # Calculate adjusted p-values using step-down method
    corrected_p_values = [0.0] * m
    for i, sorted_idx in enumerate(sorted_indices):
        # BH adjusted p-value: min(m * P(i) / i, 1.0) for i-th smallest p-value
        bh_adjusted = min(m * sorted_p_values[i] / (i + 1), 1.0)
        corrected_p_values[sorted_idx] = bh_adjusted

    # Ensure monotonicity (adjusted p-values should be non-decreasing when sorted)
    corrected_sorted = [corrected_p_values[i] for i in sorted_indices]
    for i in range(1, m):
        corrected_sorted[i] = max(corrected_sorted[i], corrected_sorted[i - 1])

    # Map back to original order
    for i, sorted_idx in enumerate(sorted_indices):
        corrected_p_values[sorted_idx] = corrected_sorted[i]

    rejected_hypotheses = sum(significant)

    # Estimate FWER for BH procedure (will be > alpha unless all nulls are true)
    family_wise_error_rate = min(rejected_hypotheses * alpha, 1.0)

    return CorrectionResult(
        original_p_values=p_values,
        corrected_p_values=corrected_p_values,
        significant=significant,
        alpha=alpha,
        method="benjamini_hochberg",
        rejected_hypotheses=rejected_hypotheses,
        family_wise_error_rate=family_wise_error_rate,
    )


def holm_bonferroni_correction(
    p_values: List[float], alpha: float = 0.05
) -> CorrectionResult:
    """Apply Holm-Bonferroni step-down correction.

    The Holm procedure is a step-down method that controls FWER but is less
    conservative than the standard Bonferroni correction. It rejects hypotheses
    sequentially, adjusting the significance threshold at each step.

    Args:
        p_values: List of original p-values
        alpha: Significance level (default 0.05)

    Returns:
        CorrectionResult with step-down controlled significance decisions

    Raises:
        ValueError: If p_values contain invalid values or alpha is invalid

    Example:
        >>> p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        >>> result = holm_bonferroni_correction(p_values, 0.05)
        >>> print(f"Step-down rejections: {result.rejected_hypotheses}")
    """
    # Validate inputs
    if not 0 < alpha < 1:
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")

    if not p_values:
        return CorrectionResult(
            original_p_values=[],
            corrected_p_values=[],
            significant=[],
            alpha=alpha,
            method="holm_bonferroni",
            rejected_hypotheses=0,
            family_wise_error_rate=0.0,
        )

    p_array = np.array(p_values)
    if np.any((p_array < 0) | (p_array > 1)) or np.any(np.isnan(p_array)):
        raise ValueError("All p-values must be between 0 and 1")

    m = len(p_values)

    # Sort p-values and keep track of original indices
    sorted_indices = np.argsort(p_values)
    sorted_p_values = np.array(p_values)[sorted_indices]

    # Apply Holm step-down procedure
    significant_sorted = [False] * m
    corrected_sorted = [0.0] * m

    for i in range(m):
        # For i-th smallest p-value, test against alpha/(m-i)
        remaining_tests = m - i
        holm_threshold = alpha / remaining_tests
        holm_adjusted_p = sorted_p_values[i] * remaining_tests

        corrected_sorted[i] = min(holm_adjusted_p, 1.0)

        if sorted_p_values[i] <= holm_threshold:
            significant_sorted[i] = True
        else:
            # Stop at first non-rejection (step-down property)
            break

    # Ensure monotonicity in corrected p-values
    for i in range(1, m):
        corrected_sorted[i] = max(corrected_sorted[i], corrected_sorted[i - 1])

    # Map back to original order
    significant = [False] * m
    corrected_p_values = [0.0] * m

    for i, sorted_idx in enumerate(sorted_indices):
        significant[sorted_idx] = significant_sorted[i]
        corrected_p_values[sorted_idx] = corrected_sorted[i]

    rejected_hypotheses = sum(significant)

    # FWER for Holm procedure is controlled at alpha
    family_wise_error_rate = min(alpha, 1.0)

    return CorrectionResult(
        original_p_values=p_values,
        corrected_p_values=corrected_p_values,
        significant=significant,
        alpha=alpha,
        method="holm_bonferroni",
        rejected_hypotheses=rejected_hypotheses,
        family_wise_error_rate=family_wise_error_rate,
    )


@jit
def _sidak_adjustment_jax(alpha: float, m: int) -> float:
    """JAX-compiled Šidák adjustment (internal function)."""
    return 1.0 - jnp.power(1.0 - alpha, 1.0 / m)


def sidak_correction(p_values: List[float], alpha: float = 0.05) -> CorrectionResult:
    """Apply Šidák correction for multiple testing.

    The Šidák correction provides exact FWER control under independence.
    It's less conservative than Bonferroni and uses the formula:
    alpha_sidak = 1 - (1 - alpha)^(1/m)

    Args:
        p_values: List of original p-values
        alpha: Significance level (default 0.05)

    Returns:
        CorrectionResult with Šidák-adjusted significance decisions

    Raises:
        ValueError: If p_values contain invalid values or alpha is invalid

    Example:
        >>> p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        >>> result = sidak_correction(p_values, 0.05)
        >>> print(f"Šidák rejections: {result.rejected_hypotheses}")
    """
    # Validate inputs
    if not 0 < alpha < 1:
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")

    if not p_values:
        return CorrectionResult(
            original_p_values=[],
            corrected_p_values=[],
            significant=[],
            alpha=alpha,
            method="sidak",
            rejected_hypotheses=0,
            family_wise_error_rate=0.0,
        )

    p_array = np.array(p_values)
    if np.any((p_array < 0) | (p_array > 1)) or np.any(np.isnan(p_array)):
        raise ValueError("All p-values must be between 0 and 1")

    m = len(p_values)

    # Calculate Šidák-adjusted significance level
    alpha_sidak = float(_sidak_adjustment_jax(alpha, m))

    # Apply correction
    significant = [p <= alpha_sidak for p in p_values]
    rejected_hypotheses = sum(significant)

    # Corrected p-values: transform to make them comparable to alpha
    # For Šidák: p_corrected = 1 - (1 - p)^m
    corrected_p_values = [
        min(1.0 - (1.0 - p) ** m, 1.0) if p < 1.0 else 1.0 for p in p_values
    ]

    # FWER for Šidák is exactly alpha under independence
    family_wise_error_rate = alpha

    return CorrectionResult(
        original_p_values=p_values,
        corrected_p_values=corrected_p_values,
        significant=significant,
        alpha=alpha,
        method="sidak",
        rejected_hypotheses=rejected_hypotheses,
        family_wise_error_rate=family_wise_error_rate,
    )


def apply_correction_to_results(
    results: List[StatisticalResult],
    method: str = "bonferroni",
    alpha: float = 0.05,
) -> List[StatisticalResult]:
    """Apply multiple testing correction to StatisticalResult objects.

    Takes a list of StatisticalResult objects and applies the specified
    multiple testing correction, returning new StatisticalResult objects
    with corrected p-values.

    Args:
        results: List of StatisticalResult objects
        method: Correction method ("bonferroni", "benjamini_hochberg",
               "holm_bonferroni", "sidak")
        alpha: Significance level for correction

    Returns:
        List of StatisticalResult objects with corrected p-values

    Raises:
        ValueError: If method is not supported

    Example:
        >>> results = [welch_ttest(group1, group2) for group1, group2 in test_pairs]
        >>> corrected = apply_correction_to_results(results, "benjamini_hochberg")
    """
    if not results:
        return []

    # Extract p-values
    p_values = [result.p_value for result in results]

    # Apply correction
    if method == "bonferroni":
        correction_result = bonferroni_correction(p_values, alpha)
    elif method == "benjamini_hochberg":
        correction_result = benjamini_hochberg_fdr(p_values, alpha)
    elif method == "holm_bonferroni":
        correction_result = holm_bonferroni_correction(p_values, alpha)
    elif method == "sidak":
        correction_result = sidak_correction(p_values, alpha)
    else:
        raise ValueError(
            f"Unsupported correction method: {method}. "
            f"Choose from: bonferroni, benjamini_hochberg, holm_bonferroni, sidak"
        )

    # Create new StatisticalResult objects with corrected p-values
    corrected_results = []
    for i, (original_result, corrected_p_value) in enumerate(
        zip(results, correction_result.corrected_p_values)
    ):
        # Create a deep copy to avoid modifying original
        corrected_result = deepcopy(original_result)

        # Update p-value and method name
        corrected_result.p_value = corrected_p_value
        corrected_result.method = f"{original_result.method}_{method}"

        corrected_results.append(corrected_result)

    return corrected_results


def estimate_fdr(
    p_values: List[float], alpha: float = 0.05, method: str = "benjamini_hochberg"
) -> float:
    """Estimate the False Discovery Rate for given p-values.

    Args:
        p_values: List of p-values
        alpha: Significance level
        method: FDR estimation method

    Returns:
        Estimated false discovery rate (0-1)
    """
    if not p_values:
        return 0.0

    if method == "benjamini_hochberg":
        # Conservative FDR estimate for BH procedure
        result = benjamini_hochberg_fdr(p_values, alpha)
        if result.rejected_hypotheses == 0:
            return 0.0

        # Estimate FDR as alpha * (expected false discoveries / total discoveries)
        m = len(p_values)
        expected_false_discoveries = alpha * m
        estimated_fdr = min(expected_false_discoveries / result.rejected_hypotheses, 1.0)
        return estimated_fdr
    else:
        warnings.warn(f"FDR estimation not implemented for method: {method}")
        return alpha  # Conservative fallback


def estimate_fwer(p_values: List[float], alpha: float = 0.05) -> float:
    """Estimate the Family-Wise Error Rate for uncorrected tests.

    Uses the Bonferroni inequality: FWER ≤ m * alpha where m is number of tests.

    Args:
        p_values: List of p-values
        alpha: Significance level per test

    Returns:
        Estimated family-wise error rate (0-1)
    """
    if not p_values:
        return 0.0

    m = len(p_values)
    # Conservative estimate using Bonferroni inequality
    estimated_fwer = min(m * alpha, 1.0)

    return estimated_fwer


# Export main functions
__all__ = [
    "CorrectionResult",
    "bonferroni_correction",
    "benjamini_hochberg_fdr",
    "holm_bonferroni_correction",
    "sidak_correction",
    "apply_correction_to_results",
    "estimate_fdr",
    "estimate_fwer",
]
