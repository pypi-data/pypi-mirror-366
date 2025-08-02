"""Core statistical functions for AB testing analysis.

This module provides JAX-accelerated statistical tests commonly used in AB testing,
including t-tests, z-tests, and non-parametric tests. All functions are designed
for high performance and can be JIT-compiled for optimal speed.

Statistical Tests:
    - Welch's t-test (unequal variances)
    - Student's t-test (equal variances)
    - Z-test (large samples)
    - Mann-Whitney U test (non-parametric)

Example:
    >>> import numpy as np
    >>> from abjax.core.stats import welch_ttest
    >>> control = np.random.normal(100, 15, 1000)
    >>> treatment = np.random.normal(105, 15, 1000)
    >>> result = welch_ttest(control, treatment)
    >>> print(f"p-value: {result.p_value:.4f}")
"""

import warnings
from dataclasses import dataclass
from typing import Tuple
from typing import Union

import jax.numpy as jnp
import numpy as np
from jax import jit
from scipy import stats as scipy_stats


@dataclass
class StatisticalResult:
    """Result of a statistical test.

    Attributes:
        statistic: The test statistic value
        p_value: The p-value of the test
        confidence_interval: Tuple of (lower, upper) confidence bounds
        effect_size: Standardised effect size (Cohen's d)
        method: Name of the statistical method used
    """

    statistic: float
    p_value: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    method: str

    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if result is statistically significant at given alpha level.

        Args:
            alpha: Significance level (default 0.05)

        Returns:
            True if p_value < alpha, False otherwise
        """
        return self.p_value < alpha


@jit
def _calculate_cohens_d(group1: jnp.ndarray, group2: jnp.ndarray) -> float:
    """Calculate Cohen's d effect size.

    Args:
        group1: First group data
        group2: Second group data

    Returns:
        Cohen's d effect size
    """
    mean1 = jnp.mean(group1)
    mean2 = jnp.mean(group2)

    # Pooled standard deviation
    n1, n2 = len(group1), len(group2)
    var1 = jnp.var(group1, ddof=1)
    var2 = jnp.var(group2, ddof=1)

    pooled_std = jnp.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    # Handle case where pooled standard deviation is zero
    return jnp.where(pooled_std == 0, 0.0, (mean2 - mean1) / pooled_std)


@jit
def _welch_ttest_statistic(group1: jnp.ndarray, group2: jnp.ndarray) -> Tuple[float, float, float]:
    """Calculate Welch's t-test statistic and degrees of freedom.

    Args:
        group1: Control group data
        group2: Treatment group data

    Returns:
        Tuple of (t_statistic, degrees_of_freedom, mean_difference)
    """
    n1, n2 = len(group1), len(group2)
    mean1, mean2 = jnp.mean(group1), jnp.mean(group2)
    var1, var2 = jnp.var(group1, ddof=1), jnp.var(group2, ddof=1)

    # Welch's t-statistic
    mean_diff = mean2 - mean1
    se_diff = jnp.sqrt(var1/n1 + var2/n2)

    # Handle edge case where both groups have zero variance
    t_stat = jnp.where(se_diff == 0, 0.0, mean_diff / se_diff)

    # Welch-Satterthwaite degrees of freedom
    # Handle edge case to avoid division by zero
    numerator = (var1/n1 + var2/n2)**2
    denominator = (var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1)
    df = jnp.where(denominator == 0, n1 + n2 - 2, numerator / denominator)

    return t_stat, df, mean_diff


@jit
def _student_ttest_statistic(group1: jnp.ndarray, group2: jnp.ndarray) -> Tuple[float, float, float]:
    """Calculate Student's t-test statistic assuming equal variances.

    Args:
        group1: Control group data
        group2: Treatment group data

    Returns:
        Tuple of (t_statistic, degrees_of_freedom, mean_difference)
    """
    n1, n2 = len(group1), len(group2)
    mean1, mean2 = jnp.mean(group1), jnp.mean(group2)
    var1, var2 = jnp.var(group1, ddof=1), jnp.var(group2, ddof=1)

    # Pooled variance
    pooled_var = ((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2)

    # Student's t-statistic
    mean_diff = mean2 - mean1
    se_diff = jnp.sqrt(pooled_var * (1/n1 + 1/n2))

    # Handle edge case where pooled variance is zero
    t_stat = jnp.where(se_diff == 0, 0.0, mean_diff / se_diff)

    df = n1 + n2 - 2

    return t_stat, df, mean_diff


@jit
def _ztest_statistic(group1: jnp.ndarray, group2: jnp.ndarray) -> Tuple[float, float]:
    """Calculate z-test statistic for large samples.

    Args:
        group1: Control group data
        group2: Treatment group data

    Returns:
        Tuple of (z_statistic, mean_difference)
    """
    n1, n2 = len(group1), len(group2)
    mean1, mean2 = jnp.mean(group1), jnp.mean(group2)
    var1, var2 = jnp.var(group1, ddof=1), jnp.var(group2, ddof=1)

    # Z-statistic
    mean_diff = mean2 - mean1
    se_diff = jnp.sqrt(var1/n1 + var2/n2)

    # Handle edge case where variance is zero
    z_stat = jnp.where(se_diff == 0, 0.0, mean_diff / se_diff)

    return z_stat, mean_diff


def _confidence_interval_welch(
    mean_diff: float, se_diff: float, df: float, alpha: float = 0.05
) -> Tuple[float, float]:
    """Calculate confidence interval for Welch's t-test.

    Args:
        mean_diff: Difference in means
        se_diff: Standard error of difference
        df: Degrees of freedom
        alpha: Significance level

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    t_critical = scipy_stats.t.ppf(1 - alpha/2, df)
    margin_error = t_critical * se_diff

    return (mean_diff - margin_error, mean_diff + margin_error)


def _confidence_interval_z(
    mean_diff: float, se_diff: float, alpha: float = 0.05
) -> Tuple[float, float]:
    """Calculate confidence interval for z-test.

    Args:
        mean_diff: Difference in means
        se_diff: Standard error of difference
        alpha: Significance level

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    z_critical = scipy_stats.norm.ppf(1 - alpha/2)
    margin_error = z_critical * se_diff

    return (mean_diff - margin_error, mean_diff + margin_error)


def welch_ttest(
    control: Union[np.ndarray, jnp.ndarray],
    treatment: Union[np.ndarray, jnp.ndarray],
    alpha: float = 0.05
) -> StatisticalResult:
    """Perform Welch's t-test (unequal variances assumed).

    This is the most robust version of the t-test as it doesn't assume
    equal variances between groups. Recommended for most AB testing scenarios.

    Args:
        control: Control group measurements
        treatment: Treatment group measurements
        alpha: Significance level for confidence interval (default 0.05)

    Returns:
        StatisticalResult with test statistic, p-value, confidence interval,
        effect size, and method name

    Raises:
        ValueError: If either group has fewer than 2 observations

    Example:
        >>> control = np.random.normal(100, 15, 1000)
        >>> treatment = np.random.normal(105, 15, 1000)
        >>> result = welch_ttest(control, treatment)
        >>> print(f"Effect size: {result.effect_size:.3f}")
    """
    # Convert to JAX arrays
    control = jnp.asarray(control)
    treatment = jnp.asarray(treatment)

    # Validate inputs
    if len(control) < 2 or len(treatment) < 2:
        raise ValueError("Each group must have at least 2 observations")

    # Calculate test statistic
    t_stat, df, mean_diff = _welch_ttest_statistic(control, treatment)

    # Calculate p-value (two-tailed)
    p_value = 2 * (1 - scipy_stats.t.cdf(abs(t_stat), df))

    # Calculate confidence interval
    n1, n2 = len(control), len(treatment)
    var1, var2 = jnp.var(control, ddof=1), jnp.var(treatment, ddof=1)
    se_diff = jnp.sqrt(var1/n1 + var2/n2)
    ci = _confidence_interval_welch(float(mean_diff), float(se_diff), float(df), alpha)

    # Calculate effect size
    effect_size = _calculate_cohens_d(control, treatment)

    return StatisticalResult(
        statistic=float(t_stat),
        p_value=float(p_value),
        confidence_interval=ci,
        effect_size=float(effect_size),
        method="welch_ttest"
    )


def student_ttest(
    control: Union[np.ndarray, jnp.ndarray],
    treatment: Union[np.ndarray, jnp.ndarray],
    alpha: float = 0.05
) -> StatisticalResult:
    """Perform Student's t-test (equal variances assumed).

    Classic t-test assuming equal population variances. Use only when you're
    confident that variances are equal, otherwise prefer Welch's t-test.

    Args:
        control: Control group measurements
        treatment: Treatment group measurements
        alpha: Significance level for confidence interval (default 0.05)

    Returns:
        StatisticalResult with test statistic, p-value, confidence interval,
        effect size, and method name

    Raises:
        ValueError: If either group has fewer than 2 observations
    """
    # Convert to JAX arrays
    control = jnp.asarray(control)
    treatment = jnp.asarray(treatment)

    # Validate inputs
    if len(control) < 2 or len(treatment) < 2:
        raise ValueError("Each group must have at least 2 observations")

    # Calculate test statistic
    t_stat, df, mean_diff = _student_ttest_statistic(control, treatment)

    # Calculate p-value (two-tailed)
    p_value = 2 * (1 - scipy_stats.t.cdf(abs(t_stat), df))

    # Calculate confidence interval
    n1, n2 = len(control), len(treatment)
    var1, var2 = jnp.var(control, ddof=1), jnp.var(treatment, ddof=1)
    pooled_var = ((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2)
    se_diff = jnp.sqrt(pooled_var * (1/n1 + 1/n2))
    ci = _confidence_interval_welch(float(mean_diff), float(se_diff), float(df), alpha)

    # Calculate effect size
    effect_size = _calculate_cohens_d(control, treatment)

    return StatisticalResult(
        statistic=float(t_stat),
        p_value=float(p_value),
        confidence_interval=ci,
        effect_size=float(effect_size),
        method="student_ttest"
    )


def ztest(
    control: Union[np.ndarray, jnp.ndarray],
    treatment: Union[np.ndarray, jnp.ndarray],
    alpha: float = 0.05
) -> StatisticalResult:
    """Perform z-test for large samples.

    Z-test is appropriate when sample sizes are large (typically n > 30 per group)
    and the Central Limit Theorem applies. More powerful than t-tests for large samples.

    Args:
        control: Control group measurements
        treatment: Treatment group measurements
        alpha: Significance level for confidence interval (default 0.05)

    Returns:
        StatisticalResult with test statistic, p-value, confidence interval,
        effect size, and method name

    Raises:
        ValueError: If either group has fewer than 2 observations

    Warns:
        UserWarning: If sample sizes are small (< 30 per group)
    """
    # Convert to JAX arrays
    control = jnp.asarray(control)
    treatment = jnp.asarray(treatment)

    # Validate inputs
    if len(control) < 2 or len(treatment) < 2:
        raise ValueError("Each group must have at least 2 observations")

    # Warn for small sample sizes
    if len(control) < 30 or len(treatment) < 30:
        warnings.warn(
            f"Z-test with small sample size (n1={len(control)}, n2={len(treatment)}). "
            "Consider using t-test instead.",
            UserWarning
        )

    # Calculate test statistic
    z_stat, mean_diff = _ztest_statistic(control, treatment)

    # Calculate p-value (two-tailed)
    p_value = 2 * (1 - scipy_stats.norm.cdf(abs(z_stat)))

    # Calculate confidence interval
    n1, n2 = len(control), len(treatment)
    var1, var2 = jnp.var(control, ddof=1), jnp.var(treatment, ddof=1)
    se_diff = jnp.sqrt(var1/n1 + var2/n2)
    ci = _confidence_interval_z(float(mean_diff), float(se_diff), alpha)

    # Calculate effect size
    effect_size = _calculate_cohens_d(control, treatment)

    return StatisticalResult(
        statistic=float(z_stat),
        p_value=float(p_value),
        confidence_interval=ci,
        effect_size=float(effect_size),
        method="ztest"
    )


def mannwhitney_u(
    control: Union[np.ndarray, jnp.ndarray],
    treatment: Union[np.ndarray, jnp.ndarray],
    alpha: float = 0.05
) -> StatisticalResult:
    """Perform Mann-Whitney U test (non-parametric).

    Non-parametric alternative to t-test that doesn't assume normal distribution.
    Tests whether the distributions of the two groups are identical vs. one group
    having systematically larger values.

    Args:
        control: Control group measurements
        treatment: Treatment group measurements
        alpha: Significance level for confidence interval (default 0.05)

    Returns:
        StatisticalResult with test statistic, p-value, confidence interval,
        effect size, and method name

    Raises:
        ValueError: If either group has fewer than 1 observation

    Note:
        Effect size for Mann-Whitney U is calculated as rank-biserial correlation.
        Confidence interval is estimated using Hodges-Lehmann estimator.
    """
    # Convert to numpy for scipy compatibility
    control = np.asarray(control)
    treatment = np.asarray(treatment)

    # Validate inputs
    if len(control) < 1 or len(treatment) < 1:
        raise ValueError("Each group must have at least 1 observation")

    # Use scipy for Mann-Whitney U test
    statistic, p_value = scipy_stats.mannwhitneyu(
        control, treatment, alternative='two-sided'
    )

    # Calculate rank-biserial correlation as effect size
    n1, n2 = len(control), len(treatment)
    u1 = statistic
    u2 = n1 * n2 - u1
    effect_size = 1 - (2 * min(u1, u2)) / (n1 * n2)

    # Estimate confidence interval using Hodges-Lehmann estimator
    # This is a simplified approach; full implementation would be more complex
    combined = np.concatenate([control, treatment])
    median_diff = np.median(treatment) - np.median(control)

    # Bootstrap-style confidence interval (simplified)
    mad_control = np.median(np.abs(control - np.median(control)))
    mad_treatment = np.median(np.abs(treatment - np.median(treatment)))
    se_approx = np.sqrt((mad_control**2/n1) + (mad_treatment**2/n2)) * 1.4826  # MAD to SD conversion

    z_critical = scipy_stats.norm.ppf(1 - alpha/2)
    margin_error = z_critical * se_approx
    ci = (median_diff - margin_error, median_diff + margin_error)

    return StatisticalResult(
        statistic=float(statistic),
        p_value=float(p_value),
        confidence_interval=ci,
        effect_size=float(effect_size),
        method="mannwhitney_u"
    )


# Export main functions
__all__ = [
    "StatisticalResult",
    "welch_ttest",
    "student_ttest",
    "ztest",
    "mannwhitney_u",
]
