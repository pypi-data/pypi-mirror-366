"""CUPED (Controlled-experiment Using Pre-Experiment Data) variance reduction.

This module implements CUPED variance reduction techniques that can significantly
reduce the variance of AB test estimates by leveraging pre-experiment covariates.
CUPED can reduce sample size requirements by 25-50% when covariates are well correlated.

Key Features:
- Automatic covariate selection and optimal θ calculation
- Variance reduction quantification
- Integration with all statistical tests
- Regression adjustment methods
- JAX-accelerated computations

Mathematical Background:
CUPED works by adjusting the outcome metric using a pre-experiment covariate:
Y_adjusted = Y - θ * (X - E[X])

Where θ = Cov(Y,X) / Var(X) minimises the variance of the adjusted metric.

Example:
    >>> import numpy as np
    >>> from abjax.core.cuped import cuped_analysis
    >>> control_metric = np.random.normal(100, 15, 1000)
    >>> treatment_metric = np.random.normal(105, 15, 1000)
    >>> control_covariate = np.random.normal(95, 12, 1000)
    >>> treatment_covariate = np.random.normal(95, 12, 1000)
    >>> result = cuped_analysis(control_metric, treatment_metric,
    ...                        control_covariate, treatment_covariate)
    >>> print(f"Variance reduction: {result.variance_reduction:.1%}")
"""

from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

import jax.numpy as jnp
import numpy as np
from jax import jit

from .stats import StatisticalResult
from .stats import student_ttest
from .stats import welch_ttest
from .stats import ztest


@dataclass
class CupedResult:
    """Result of CUPED variance reduction analysis.

    Attributes:
        adjusted_statistic: Test statistic after CUPED adjustment
        adjusted_p_value: P-value after CUPED adjustment
        original_statistic: Original test statistic without adjustment
        original_p_value: Original p-value without adjustment
        theta: Optimal CUPED adjustment parameter (θ = Cov(Y,X)/Var(X))
        variance_reduction: Proportion of variance reduced (0-1)
        confidence_interval: Confidence interval for adjusted effect
        effect_size: Effect size (Cohen's d) after adjustment
        covariate_correlation: Correlation between metric and covariate
        method: Statistical method used with CUPED adjustment
    """

    adjusted_statistic: float
    adjusted_p_value: float
    original_statistic: float
    original_p_value: float
    theta: float
    variance_reduction: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    covariate_correlation: float
    method: str

    def power_improvement(self) -> float:
        """Calculate the relative improvement in statistical power.

        Returns:
            Ratio of adjusted to original test statistic (power proxy)
        """
        if self.original_statistic == 0:
            return 1.0
        return abs(self.adjusted_statistic) / abs(self.original_statistic)

    def statistical_power_gained(self) -> float:
        """Calculate the statistical power gained from CUPED.

        Returns:
            Improvement in statistical power (as a ratio)
        """
        # Handle edge case where original statistic is zero
        if self.original_statistic == 0:
            return 0.0

        # Power is approximately proportional to the square of the test statistic
        power_ratio = (self.adjusted_statistic / self.original_statistic) ** 2
        return max(0.0, power_ratio - 1.0)

    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if adjusted result is statistically significant.

        Args:
            alpha: Significance level (default 0.05)

        Returns:
            True if adjusted p_value < alpha, False otherwise
        """
        return self.adjusted_p_value < alpha


@jit
def _calculate_theta_jax(metric: jnp.ndarray, covariate: jnp.ndarray) -> jnp.ndarray:
    """JAX-compiled theta calculation (internal function).

    Args:
        metric: Outcome metric data
        covariate: Pre-experiment covariate data

    Returns:
        Theta as JAX scalar array
    """
    # Calculate covariance and variance using JAX
    metric_centered = metric - jnp.mean(metric)
    covariate_centered = covariate - jnp.mean(covariate)

    covariance = jnp.mean(metric_centered * covariate_centered)
    covariate_variance = jnp.mean(covariate_centered**2)

    # Handle edge case where covariate has zero variance
    theta = jnp.where(covariate_variance == 0, 0.0, covariance / covariate_variance)

    return theta


def calculate_theta(metric: jnp.ndarray, covariate: jnp.ndarray) -> float:
    """Calculate optimal CUPED adjustment parameter θ.

    The optimal θ that minimises variance is: θ = Cov(Y,X) / Var(X)

    Args:
        metric: Outcome metric data
        covariate: Pre-experiment covariate data

    Returns:
        Optimal theta value for variance reduction

    Raises:
        ValueError: If arrays have different lengths
    """
    if len(metric) != len(covariate):
        raise ValueError("Metric and covariate must have the same length")

    theta_jax = _calculate_theta_jax(metric, covariate)
    return float(theta_jax)


@jit
def _apply_cuped_adjustment(
    metric: jnp.ndarray, covariate: jnp.ndarray, theta: Union[float, jnp.ndarray]
) -> jnp.ndarray:
    """Apply CUPED adjustment to metric data.

    Args:
        metric: Original metric data
        covariate: Covariate data for adjustment
        theta: CUPED adjustment parameter (float or JAX array)

    Returns:
        CUPED-adjusted metric data
    """
    covariate_mean = jnp.mean(covariate)
    adjusted_metric = metric - theta * (covariate - covariate_mean)
    return adjusted_metric


@jit
def _variance_reduction_ratio_jax(metric: jnp.ndarray, covariate: jnp.ndarray) -> jnp.ndarray:
    """JAX-compiled variance reduction calculation (internal function)."""
    # Calculate theta
    theta = _calculate_theta_jax(metric, covariate)

    # Apply adjustment
    adjusted_metric = _apply_cuped_adjustment(metric, covariate, theta)

    # Calculate variance reduction
    original_var = jnp.var(metric)
    adjusted_var = jnp.var(adjusted_metric)

    # Handle edge case
    reduction_ratio = jnp.where(
        original_var == 0,
        0.0,
        (original_var - adjusted_var) / original_var
    )

    return jnp.clip(reduction_ratio, 0.0, 1.0)


def variance_reduction_ratio(metric: np.ndarray, covariate: np.ndarray) -> float:
    """Calculate the proportion of variance reduced by CUPED.

    Args:
        metric: Outcome metric data
        covariate: Pre-experiment covariate data

    Returns:
        Variance reduction ratio (0-1, where 1 = 100% reduction)
    """
    # Convert to JAX arrays
    metric_jax = jnp.asarray(metric)
    covariate_jax = jnp.asarray(covariate)

    reduction_ratio_jax = _variance_reduction_ratio_jax(metric_jax, covariate_jax)
    return float(reduction_ratio_jax)


def automatic_covariate_selection(
    metric: np.ndarray,
    covariates: Dict[str, np.ndarray],
    min_correlation: float = 0.1,
) -> Tuple[Optional[str], Dict[str, float]]:
    """Automatically select the best covariate for CUPED adjustment.

    Selects the covariate that provides the highest variance reduction
    while meeting the minimum correlation threshold.

    Args:
        metric: Outcome metric data
        covariates: Dictionary of covariate name -> data arrays
        min_correlation: Minimum correlation required for selection

    Returns:
        Tuple of (selected_covariate_name, selection_statistics)
        Returns (None, {}) if no covariate meets criteria
    """
    if not covariates:
        return None, {}

    best_covariate = None
    best_reduction = 0.0
    selection_stats = {}

    for name, covariate_data in covariates.items():
        if len(covariate_data) != len(metric):
            continue

        # Calculate correlation safely
        # Check if either array has zero variance
        metric_var = np.var(metric)
        covariate_var = np.var(covariate_data)

        if metric_var == 0 or covariate_var == 0:
            # Zero variance means no correlation possible
            correlation = 0.0
        else:
            correlation = float(np.corrcoef(metric, covariate_data)[0, 1])

        # Skip if correlation is too low
        if abs(correlation) < min_correlation:
            continue

        # Calculate variance reduction
        reduction = variance_reduction_ratio(metric, covariate_data)

        # Track the best covariate
        if reduction > best_reduction:
            best_reduction = reduction
            best_covariate = name
            selection_stats = {
                "correlation": correlation,
                "variance_reduction": reduction,
                "theta": calculate_theta(jnp.asarray(metric), jnp.asarray(covariate_data)),
            }

    return best_covariate, selection_stats


@jit
def _regression_adjustment_jax(metric: jnp.ndarray, covariate: jnp.ndarray) -> jnp.ndarray:
    """JAX-compiled regression adjustment (internal function)."""
    # Calculate optimal theta
    theta = _calculate_theta_jax(metric, covariate)

    # Apply adjustment
    adjusted_metric = _apply_cuped_adjustment(metric, covariate, theta)

    return adjusted_metric


def regression_adjustment(metric: np.ndarray, covariate: np.ndarray) -> np.ndarray:
    """Apply regression adjustment to remove covariate effect.

    This is equivalent to CUPED adjustment and removes the linear
    relationship between the metric and covariate.

    Args:
        metric: Outcome metric data
        covariate: Covariate data for adjustment

    Returns:
        Regression-adjusted metric data
    """
    # Convert to JAX arrays
    metric_jax = jnp.asarray(metric)
    covariate_jax = jnp.asarray(covariate)

    # Apply adjustment using JAX
    adjusted_metric_jax = _regression_adjustment_jax(metric_jax, covariate_jax)

    return np.array(adjusted_metric_jax)


def cuped_adjusted_ttest(
    control_metric: np.ndarray,
    treatment_metric: np.ndarray,
    control_covariate: np.ndarray,
    treatment_covariate: np.ndarray,
    test_method: str = "welch_ttest",
    alpha: float = 0.05,
) -> StatisticalResult:
    """Perform CUPED-adjusted t-test.

    Applies CUPED adjustment to both groups and then performs
    the specified statistical test.

    Args:
        control_metric: Control group metric data
        treatment_metric: Treatment group metric data
        control_covariate: Control group covariate data
        treatment_covariate: Treatment group covariate data
        test_method: Statistical test method ("welch_ttest", "student_ttest", "ztest")
        alpha: Significance level for confidence intervals

    Returns:
        StatisticalResult with CUPED-adjusted analysis
    """
    # Combine data to calculate global theta
    combined_metric = np.concatenate([control_metric, treatment_metric])
    combined_covariate = np.concatenate([control_covariate, treatment_covariate])

    # Calculate theta using combined data
    theta = calculate_theta(jnp.asarray(combined_metric), jnp.asarray(combined_covariate))

    # Apply CUPED adjustment to each group
    control_adjusted = _apply_cuped_adjustment(
        jnp.asarray(control_metric), jnp.asarray(control_covariate), theta
    )
    treatment_adjusted = _apply_cuped_adjustment(
        jnp.asarray(treatment_metric), jnp.asarray(treatment_covariate), theta
    )

    # Perform statistical test on adjusted data
    if test_method == "welch_ttest":
        result = welch_ttest(np.array(control_adjusted), np.array(treatment_adjusted), alpha)
    elif test_method == "student_ttest":
        result = student_ttest(np.array(control_adjusted), np.array(treatment_adjusted), alpha)
    elif test_method == "ztest":
        result = ztest(np.array(control_adjusted), np.array(treatment_adjusted), alpha)
    else:
        raise ValueError(f"Unsupported test method: {test_method}")

    # Update method name to indicate CUPED adjustment
    result.method = f"cuped_adjusted_{test_method}"

    return result


def cuped_analysis(
    control_metric: np.ndarray,
    treatment_metric: np.ndarray,
    control_covariate: np.ndarray,
    treatment_covariate: np.ndarray,
    test_method: str = "welch_ttest",
    alpha: float = 0.05,
) -> CupedResult:
    """Perform comprehensive CUPED variance reduction analysis.

    This is the main CUPED analysis function that compares original
    and CUPED-adjusted statistical tests, providing detailed metrics
    on variance reduction and power improvement.

    Args:
        control_metric: Control group metric data
        treatment_metric: Treatment group metric data
        control_covariate: Control group covariate data
        treatment_covariate: Treatment group covariate data
        test_method: Statistical test method ("welch_ttest", "student_ttest", "ztest")
        alpha: Significance level for confidence intervals

    Returns:
        CupedResult with comprehensive analysis results

    Raises:
        ValueError: If arrays have inconsistent lengths or invalid test method
    """
    # Validate inputs
    if len(control_metric) != len(control_covariate):
        raise ValueError("Control metric and covariate must have same length")
    if len(treatment_metric) != len(treatment_covariate):
        raise ValueError("Treatment metric and covariate must have same length")

    # Perform original analysis without CUPED
    if test_method == "welch_ttest":
        original_result = welch_ttest(control_metric, treatment_metric, alpha)
    elif test_method == "student_ttest":
        original_result = student_ttest(control_metric, treatment_metric, alpha)
    elif test_method == "ztest":
        original_result = ztest(control_metric, treatment_metric, alpha)
    else:
        raise ValueError(f"Unsupported test method: {test_method}")

    # Perform CUPED-adjusted analysis
    adjusted_result = cuped_adjusted_ttest(
        control_metric,
        treatment_metric,
        control_covariate,
        treatment_covariate,
        test_method,
        alpha,
    )

    # Calculate CUPED metrics
    combined_metric = np.concatenate([control_metric, treatment_metric])
    combined_covariate = np.concatenate([control_covariate, treatment_covariate])

    theta = calculate_theta(jnp.asarray(combined_metric), jnp.asarray(combined_covariate))
    variance_reduction = variance_reduction_ratio(combined_metric, combined_covariate)

    # Calculate correlation safely
    metric_var = np.var(combined_metric)
    covariate_var = np.var(combined_covariate)

    if metric_var == 0 or covariate_var == 0:
        # Zero variance means no correlation possible
        covariate_correlation = 0.0
    else:
        covariate_correlation = float(np.corrcoef(combined_metric, combined_covariate)[0, 1])

    return CupedResult(
        adjusted_statistic=adjusted_result.statistic,
        adjusted_p_value=adjusted_result.p_value,
        original_statistic=original_result.statistic,
        original_p_value=original_result.p_value,
        theta=float(theta),
        variance_reduction=variance_reduction,
        confidence_interval=adjusted_result.confidence_interval,
        effect_size=adjusted_result.effect_size,
        covariate_correlation=covariate_correlation,
        method=f"cuped_{test_method}",
    )


# Export main functions
__all__ = [
    "CupedResult",
    "cuped_analysis",
    "calculate_theta",
    "variance_reduction_ratio",
    "automatic_covariate_selection",
    "cuped_adjusted_ttest",
    "regression_adjustment",
]
