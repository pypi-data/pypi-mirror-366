"""Tests for core statistical functions."""

import jax
import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from scipy import stats as scipy_stats

from abjax.core.stats import StatisticalResult
from abjax.core.stats import mannwhitney_u
from abjax.core.stats import student_ttest
from abjax.core.stats import welch_ttest
from abjax.core.stats import ztest


class TestStatisticalResult:
    """Test the StatisticalResult dataclass."""

    def test_result_creation(self):
        """Test creation of StatisticalResult."""
        result = StatisticalResult(
            statistic=2.5,
            p_value=0.012,
            confidence_interval=(0.5, 3.2),
            effect_size=0.3,
            method="welch_ttest",
        )

        assert result.statistic == 2.5
        assert result.p_value == 0.012
        assert result.confidence_interval == (0.5, 3.2)
        assert result.effect_size == 0.3
        assert result.method == "welch_ttest"

    def test_result_significance(self):
        """Test significance property."""
        significant_result = StatisticalResult(
            statistic=2.5, p_value=0.01, confidence_interval=(0.5, 3.2),
            effect_size=0.3, method="welch_ttest"
        )
        non_significant_result = StatisticalResult(
            statistic=1.2, p_value=0.08, confidence_interval=(-0.1, 2.5),
            effect_size=0.1, method="welch_ttest"
        )

        assert significant_result.is_significant(alpha=0.05)
        assert not non_significant_result.is_significant(alpha=0.05)
        assert non_significant_result.is_significant(alpha=0.1)


class TestWelchTTest:
    """Test Welch's t-test implementation."""

    def test_welch_ttest_basic(self, sample_ab_data):
        """Test basic Welch's t-test functionality."""
        control_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "control"
        )["metric"].to_numpy()
        treatment_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "treatment"
        )["metric"].to_numpy()

        result = welch_ttest(control_data, treatment_data)

        assert isinstance(result, StatisticalResult)
        assert result.method == "welch_ttest"
        assert isinstance(result.statistic, float)
        assert isinstance(result.p_value, float)
        assert 0 <= result.p_value <= 1
        assert len(result.confidence_interval) == 2
        assert result.confidence_interval[0] <= result.confidence_interval[1]

    def test_welch_ttest_against_scipy(self):
        """Test Welch's t-test against SciPy reference implementation."""
        key = jax.random.PRNGKey(42)
        key1, key2 = jax.random.split(key)

        # Generate test data with known difference
        control = jax.random.normal(key1, (100,)) * 1.0 + 0.0
        treatment = jax.random.normal(key2, (100,)) * 1.0 + 0.5  # Small effect

        # Our implementation
        result = welch_ttest(np.array(control), np.array(treatment))

        # SciPy reference (note: order matters for sign)
        scipy_stat, scipy_p = scipy_stats.ttest_ind(
            treatment, control, equal_var=False
        )

        # Compare results (allowing for numerical differences due to implementation)
        assert abs(result.statistic - scipy_stat) < 1e-6
        assert abs(result.p_value - scipy_p) < 1e-6

    def test_welch_ttest_equal_groups(self):
        """Test Welch's t-test with identical groups."""
        key = jax.random.PRNGKey(123)
        data = jax.random.normal(key, (50,))

        result = welch_ttest(np.array(data), np.array(data))

        assert abs(result.statistic) < 1e-6  # Should be approximately 0
        assert result.p_value > 0.99  # Should be very high p-value
        assert result.confidence_interval[0] < 0 < result.confidence_interval[1]

    @given(
        st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=10, max_size=100),
        st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=10, max_size=100),
    )
    def test_welch_ttest_properties(self, group1, group2):
        """Property-based test for Welch's t-test."""
        # Filter out any NaN or infinite values and ensure some variance
        group1 = [x for x in group1 if np.isfinite(x)]
        group2 = [x for x in group2 if np.isfinite(x)]

        if len(group1) < 2 or len(group2) < 2:
            pytest.skip("Need at least 2 observations per group")

        # Skip if all values are identical (zero variance case)
        if len(set(group1)) == 1 and len(set(group2)) == 1 and group1[0] == group2[0]:
            pytest.skip("All values identical, skip zero variance case")

        result = welch_ttest(np.array(group1), np.array(group2))

        # Basic properties
        assert 0 <= result.p_value <= 1 or np.isclose(result.p_value, 1.0)
        assert len(result.confidence_interval) == 2
        assert result.confidence_interval[0] <= result.confidence_interval[1] or np.isclose(result.confidence_interval[0], result.confidence_interval[1])
        assert result.method == "welch_ttest"

        # Effect size should be finite
        assert np.isfinite(result.effect_size) or result.effect_size == 0.0

    def test_welch_ttest_small_samples(self, small_ab_data):
        """Test Welch's t-test with small sample sizes."""
        control_data = small_ab_data.filter(
            small_ab_data["variant"] == "control"
        )["metric"].to_numpy()
        treatment_data = small_ab_data.filter(
            small_ab_data["variant"] == "treatment"
        )["metric"].to_numpy()

        result = welch_ttest(control_data, treatment_data)

        assert isinstance(result, StatisticalResult)
        assert 0 <= result.p_value <= 1
        # With small samples, confidence intervals should be wider
        ci_width = result.confidence_interval[1] - result.confidence_interval[0]
        assert ci_width > 0


class TestStudentTTest:
    """Test Student's t-test implementation."""

    def test_student_ttest_basic(self, sample_ab_data):
        """Test basic Student's t-test functionality."""
        control_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "control"
        )["metric"].to_numpy()
        treatment_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "treatment"
        )["metric"].to_numpy()

        result = student_ttest(control_data, treatment_data)

        assert isinstance(result, StatisticalResult)
        assert result.method == "student_ttest"
        assert isinstance(result.statistic, float)
        assert isinstance(result.p_value, float)
        assert 0 <= result.p_value <= 1

    def test_student_ttest_against_scipy(self):
        """Test Student's t-test against SciPy reference implementation."""
        key = jax.random.PRNGKey(42)
        key1, key2 = jax.random.split(key)

        # Generate test data with same variance
        control = jax.random.normal(key1, (100,)) * 1.0 + 0.0
        treatment = jax.random.normal(key2, (100,)) * 1.0 + 0.3

        # Our implementation
        result = student_ttest(np.array(control), np.array(treatment))

        # SciPy reference (note: order matters for sign)
        scipy_stat, scipy_p = scipy_stats.ttest_ind(
            treatment, control, equal_var=True
        )

        # Compare results (allowing for numerical differences due to implementation)
        assert abs(result.statistic - scipy_stat) < 1e-6
        assert abs(result.p_value - scipy_p) < 1e-6


class TestZTest:
    """Test Z-test implementation."""

    def test_ztest_basic(self, large_ab_data):
        """Test basic Z-test functionality with large samples."""
        control_data = large_ab_data.filter(
            large_ab_data["variant"] == "control"
        )["metric"].to_numpy()
        treatment_data = large_ab_data.filter(
            large_ab_data["variant"] == "treatment"
        )["metric"].to_numpy()

        result = ztest(control_data, treatment_data)

        assert isinstance(result, StatisticalResult)
        assert result.method == "ztest"
        assert isinstance(result.statistic, float)
        assert isinstance(result.p_value, float)
        assert 0 <= result.p_value <= 1

    def test_ztest_against_statsmodels(self):
        """Test Z-test against reference implementation."""
        # Skip if statsmodels not available
        pytest.importorskip("statsmodels")
        from statsmodels.stats.weightstats import ztest as sm_ztest

        key = jax.random.PRNGKey(42)
        key1, key2 = jax.random.split(key)

        # Large samples for Z-test
        control = jax.random.normal(key1, (1000,)) * 1.0 + 0.0
        treatment = jax.random.normal(key2, (1000,)) * 1.0 + 0.2

        # Our implementation
        result = ztest(np.array(control), np.array(treatment))

        # Statsmodels reference
        sm_stat, sm_p = sm_ztest(control, treatment)

        # Compare results (allowing for small numerical differences)
        assert abs(result.statistic - sm_stat) < 1e-6
        assert abs(result.p_value - sm_p) < 1e-6

    def test_ztest_small_sample_warning(self, small_ab_data):
        """Test that Z-test raises warning for small samples."""
        control_data = small_ab_data.filter(
            small_ab_data["variant"] == "control"
        )["metric"].to_numpy()
        treatment_data = small_ab_data.filter(
            small_ab_data["variant"] == "treatment"
        )["metric"].to_numpy()

        with pytest.warns(UserWarning, match="small sample size"):
            result = ztest(control_data, treatment_data)
            assert isinstance(result, StatisticalResult)


class TestMannWhitneyU:
    """Test Mann-Whitney U test implementation."""

    def test_mannwhitney_basic(self, sample_ab_data):
        """Test basic Mann-Whitney U test functionality."""
        control_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "control"
        )["metric"].to_numpy()
        treatment_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "treatment"
        )["metric"].to_numpy()

        result = mannwhitney_u(control_data, treatment_data)

        assert isinstance(result, StatisticalResult)
        assert result.method == "mannwhitney_u"
        assert isinstance(result.statistic, float)
        assert isinstance(result.p_value, float)
        assert 0 <= result.p_value <= 1

    def test_mannwhitney_against_scipy(self):
        """Test Mann-Whitney U against SciPy reference implementation."""
        key = jax.random.PRNGKey(42)
        key1, key2 = jax.random.split(key)

        # Generate non-normal data for non-parametric test
        control = jax.random.exponential(key1, (100,))
        treatment = jax.random.exponential(key2, (100,)) * 1.2  # Different scale

        # Our implementation
        result = mannwhitney_u(np.array(control), np.array(treatment))

        # SciPy reference
        scipy_stat, scipy_p = scipy_stats.mannwhitneyu(
            control, treatment, alternative="two-sided"
        )

        # Compare results (allowing for numerical differences due to implementation)
        assert abs(result.statistic - scipy_stat) < 1e-6
        assert abs(result.p_value - scipy_p) < 1e-6

    def test_mannwhitney_tied_values(self):
        """Test Mann-Whitney U with tied values."""
        control = np.array([1, 1, 2, 2, 3, 3])
        treatment = np.array([2, 2, 3, 3, 4, 4])

        result = mannwhitney_u(control, treatment)

        assert isinstance(result, StatisticalResult)
        assert 0 <= result.p_value <= 1


class TestStatisticalValidation:
    """Integration tests for statistical correctness."""

    def test_type_i_error_rate(self):
        """Test that Type I error rate is controlled at alpha level."""
        key = jax.random.PRNGKey(123)
        alpha = 0.05
        n_simulations = 1000

        significant_results = 0

        for i in range(n_simulations):
            key, subkey = jax.random.split(key)
            key1, key2 = jax.random.split(subkey)

            # Generate data from same distribution (null hypothesis true)
            control = jax.random.normal(key1, (50,))
            treatment = jax.random.normal(key2, (50,))

            result = welch_ttest(np.array(control), np.array(treatment))

            if result.is_significant(alpha):
                significant_results += 1

        # Type I error rate should be approximately alpha
        empirical_alpha = significant_results / n_simulations

        # Allow for some variation (within 2 standard errors)
        se = np.sqrt(alpha * (1 - alpha) / n_simulations)
        assert abs(empirical_alpha - alpha) < 2 * se

    @pytest.mark.slow
    def test_power_analysis_validation(self):
        """Test statistical power with known effect size."""
        key = jax.random.PRNGKey(456)
        alpha = 0.05
        effect_size = 0.5  # Medium effect size
        n_simulations = 1000

        significant_results = 0

        for i in range(n_simulations):
            key, subkey = jax.random.split(key)
            key1, key2 = jax.random.split(subkey)

            # Generate data with known effect size
            control = jax.random.normal(key1, (100,))
            treatment = jax.random.normal(key2, (100,)) + effect_size

            result = welch_ttest(np.array(control), np.array(treatment))

            if result.is_significant(alpha):
                significant_results += 1

        empirical_power = significant_results / n_simulations

        # Expected power for effect size 0.5, n=100 per group is approximately 0.94
        # Allow for reasonable variation
        assert empirical_power > 0.85
