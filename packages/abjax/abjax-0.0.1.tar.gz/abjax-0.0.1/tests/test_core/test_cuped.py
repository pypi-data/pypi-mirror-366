"""Tests for CUPED variance reduction functionality."""

import jax
import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from abjax.core.cuped import CupedResult
from abjax.core.cuped import automatic_covariate_selection
from abjax.core.cuped import calculate_theta
from abjax.core.cuped import cuped_adjusted_ttest
from abjax.core.cuped import cuped_analysis
from abjax.core.cuped import regression_adjustment
from abjax.core.cuped import variance_reduction_ratio
from abjax.core.stats import StatisticalResult
from abjax.core.stats import welch_ttest


class TestCupedResult:
    """Test the CupedResult dataclass."""

    def test_result_creation(self):
        """Test creation of CupedResult."""
        result = CupedResult(
            adjusted_statistic=2.8,
            adjusted_p_value=0.008,
            original_statistic=2.1,
            original_p_value=0.025,
            theta=0.75,
            variance_reduction=0.35,
            confidence_interval=(1.2, 4.5),
            effect_size=0.4,
            covariate_correlation=0.82,
            method="cuped_welch_ttest",
        )

        assert result.adjusted_statistic == 2.8
        assert result.adjusted_p_value == 0.008
        assert result.theta == 0.75
        assert result.variance_reduction == 0.35
        assert result.covariate_correlation == 0.82

    def test_result_improvement_metrics(self):
        """Test improvement calculation methods."""
        result = CupedResult(
            adjusted_statistic=3.2,
            adjusted_p_value=0.005,
            original_statistic=2.1,
            original_p_value=0.035,
            theta=0.68,
            variance_reduction=0.45,
            confidence_interval=(1.5, 5.2),
            effect_size=0.52,
            covariate_correlation=0.85,
            method="cuped_welch_ttest",
        )

        assert result.power_improvement() > 1.0  # Should show improvement
        assert 0 < result.variance_reduction < 1  # Should be percentage
        assert result.statistical_power_gained() > 0


class TestThetaCalculation:
    """Test optimal theta calculation."""

    def test_calculate_theta_basic(self, sample_ab_data):
        """Test basic theta calculation."""
        metric_data = sample_ab_data["metric"].to_numpy()
        covariate_data = sample_ab_data["pre_experiment_metric"].to_numpy()

        theta = calculate_theta(metric_data, covariate_data)

        assert isinstance(theta, float)
        assert 0 <= abs(theta) <= 1  # Theta should be bounded by correlation

    def test_calculate_theta_perfect_correlation(self):
        """Test theta with perfect positive correlation."""
        # Create perfectly correlated data
        key = jax.random.PRNGKey(42)
        x = jax.random.normal(key, (100,))
        y = x + jax.random.normal(jax.random.PRNGKey(123), (100,)) * 0.01  # Almost identical

        theta = calculate_theta(np.array(x), np.array(y))

        assert abs(theta) > 0.9  # Should be close to 1 for high correlation

    def test_calculate_theta_no_correlation(self):
        """Test theta with no correlation."""
        key = jax.random.PRNGKey(42)
        key1, key2 = jax.random.split(key)

        x = jax.random.normal(key1, (1000,))  # Large sample for stable estimate
        y = jax.random.normal(key2, (1000,))  # Independent

        theta = calculate_theta(np.array(x), np.array(y))

        assert abs(theta) < 0.1  # Should be close to 0 for no correlation

    @given(
        st.lists(st.floats(min_value=-10, max_value=10, allow_nan=False), min_size=20, max_size=100),
        st.floats(min_value=0.1, max_value=2.0),
    )
    def test_calculate_theta_properties(self, base_data, noise_factor):
        """Property-based test for theta calculation."""
        if len(base_data) < 10:
            pytest.skip("Need sufficient data for stable theta estimate")

        base_array = np.array(base_data)
        # Create correlated covariate
        noise = np.random.normal(0, noise_factor, len(base_data))
        covariate = base_array * 0.7 + noise  # Partial correlation

        theta = calculate_theta(base_array, covariate)

        # Theta should be finite and reasonable
        assert np.isfinite(theta)
        assert abs(theta) <= 1.5  # Allow some flexibility for numerical issues


class TestVarianceReduction:
    """Test variance reduction calculations."""

    def test_variance_reduction_ratio(self, sample_ab_data):
        """Test variance reduction ratio calculation."""
        metric_data = sample_ab_data["metric"].to_numpy()
        covariate_data = sample_ab_data["pre_experiment_metric"].to_numpy()

        reduction_ratio = variance_reduction_ratio(metric_data, covariate_data)

        assert isinstance(reduction_ratio, float)
        assert 0 <= reduction_ratio <= 1  # Should be between 0 and 1

    def test_variance_reduction_high_correlation(self):
        """Test variance reduction with highly correlated covariate."""
        key = jax.random.PRNGKey(42)
        base = jax.random.normal(key, (500,))

        # High correlation covariate
        covariate = base + jax.random.normal(jax.random.PRNGKey(123), (500,)) * 0.1
        metric = base + jax.random.normal(jax.random.PRNGKey(456), (500,)) * 0.2

        reduction_ratio = variance_reduction_ratio(np.array(metric), np.array(covariate))

        assert reduction_ratio > 0.5  # Should show significant reduction

    def test_variance_reduction_no_correlation(self):
        """Test variance reduction with uncorrelated covariate."""
        key = jax.random.PRNGKey(42)
        key1, key2 = jax.random.split(key)

        metric = jax.random.normal(key1, (500,))
        covariate = jax.random.normal(key2, (500,))  # Independent

        reduction_ratio = variance_reduction_ratio(np.array(metric), np.array(covariate))

        assert reduction_ratio < 0.1  # Should show minimal reduction


class TestAutomaticCovariateSelection:
    """Test automatic covariate selection."""

    def test_single_covariate_selection(self, sample_ab_data):
        """Test selection with single covariate."""
        metric_data = sample_ab_data["metric"].to_numpy()
        covariates = {
            "pre_experiment": sample_ab_data["pre_experiment_metric"].to_numpy()
        }

        selected_covariate, selection_stats = automatic_covariate_selection(
            metric_data, covariates, min_correlation=0.01  # Very low threshold for random test data
        )

        assert selected_covariate in covariates
        assert "correlation" in selection_stats
        assert "variance_reduction" in selection_stats
        assert isinstance(selection_stats["correlation"], float)

    def test_multiple_covariate_selection(self):
        """Test selection among multiple covariates."""
        key = jax.random.PRNGKey(42)
        n_samples = 200

        # Create base metric
        metric = jax.random.normal(key, (n_samples,))

        # Create covariates with different correlation levels
        covariates = {
            "weak_covariate": jax.random.normal(jax.random.PRNGKey(1), (n_samples,)),
            "strong_covariate": metric + jax.random.normal(jax.random.PRNGKey(2), (n_samples,)) * 0.1,
            "medium_covariate": metric * 0.5 + jax.random.normal(jax.random.PRNGKey(3), (n_samples,)) * 0.3,
        }

        # Convert to numpy
        metric_np = np.array(metric)
        covariates_np = {k: np.array(v) for k, v in covariates.items()}

        selected_covariate, selection_stats = automatic_covariate_selection(
            metric_np, covariates_np
        )

        # Should select the strongest covariate
        assert selected_covariate == "strong_covariate"
        assert selection_stats["variance_reduction"] > 0.3

    def test_covariate_selection_threshold(self):
        """Test covariate selection with correlation threshold."""
        key = jax.random.PRNGKey(42)
        n_samples = 200

        metric = jax.random.normal(key, (n_samples,))

        # All weak covariates
        covariates = {
            "weak1": jax.random.normal(jax.random.PRNGKey(1), (n_samples,)),
            "weak2": jax.random.normal(jax.random.PRNGKey(2), (n_samples,)),
        }

        metric_np = np.array(metric)
        covariates_np = {k: np.array(v) for k, v in covariates.items()}

        selected_covariate, selection_stats = automatic_covariate_selection(
            metric_np, covariates_np, min_correlation=0.5
        )

        # Should return None if no covariate meets threshold
        assert selected_covariate is None


class TestCupedAnalysis:
    """Test main CUPED analysis functionality."""

    def test_cuped_analysis_basic(self, sample_ab_data):
        """Test basic CUPED analysis."""
        control_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "control"
        )
        treatment_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "treatment"
        )

        control_metric = control_data["metric"].to_numpy()
        treatment_metric = treatment_data["metric"].to_numpy()
        control_covariate = control_data["pre_experiment_metric"].to_numpy()
        treatment_covariate = treatment_data["pre_experiment_metric"].to_numpy()

        result = cuped_analysis(
            control_metric, treatment_metric,
            control_covariate, treatment_covariate
        )

        assert isinstance(result, CupedResult)
        assert result.method == "cuped_welch_ttest"
        assert 0 <= result.variance_reduction <= 1
        assert np.isfinite(result.theta)
        assert 0 <= result.adjusted_p_value <= 1

    def test_cuped_vs_standard_ttest(self, sample_ab_data):
        """Test CUPED improvement over standard t-test."""
        control_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "control"
        )
        treatment_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "treatment"
        )

        control_metric = control_data["metric"].to_numpy()
        treatment_metric = treatment_data["metric"].to_numpy()
        control_covariate = control_data["pre_experiment_metric"].to_numpy()
        treatment_covariate = treatment_data["pre_experiment_metric"].to_numpy()

        # Standard t-test
        standard_result = welch_ttest(control_metric, treatment_metric)

        # CUPED analysis
        cuped_result = cuped_analysis(
            control_metric, treatment_metric,
            control_covariate, treatment_covariate
        )

        # CUPED should typically improve power (lower p-value) when covariates are correlated
        if cuped_result.covariate_correlation > 0.3:
            assert cuped_result.adjusted_p_value <= standard_result.p_value
            assert cuped_result.variance_reduction > 0

    def test_cuped_with_weak_covariate(self):
        """Test CUPED with weakly correlated covariate."""
        key = jax.random.PRNGKey(42)
        n_per_group = 100

        # Generate independent data (weak covariate)
        control_metric = jax.random.normal(key, (n_per_group,))
        treatment_metric = jax.random.normal(jax.random.PRNGKey(1), (n_per_group,)) + 0.2
        control_covariate = jax.random.normal(jax.random.PRNGKey(2), (n_per_group,))
        treatment_covariate = jax.random.normal(jax.random.PRNGKey(3), (n_per_group,))

        result = cuped_analysis(
            np.array(control_metric), np.array(treatment_metric),
            np.array(control_covariate), np.array(treatment_covariate)
        )

        # With weak covariate, variance reduction should be minimal
        assert result.variance_reduction < 0.2
        assert abs(result.covariate_correlation) < 0.3

    def test_cuped_with_strong_covariate(self):
        """Test CUPED with strongly correlated covariate."""
        key = jax.random.PRNGKey(42)
        n_per_group = 100

        # Generate correlated covariate
        base_control = jax.random.normal(key, (n_per_group,))
        base_treatment = jax.random.normal(jax.random.PRNGKey(1), (n_per_group,))

        # Strong correlation between metric and covariate
        control_metric = base_control + jax.random.normal(jax.random.PRNGKey(2), (n_per_group,)) * 0.1
        treatment_metric = base_treatment + 0.5 + jax.random.normal(jax.random.PRNGKey(3), (n_per_group,)) * 0.1
        control_covariate = base_control + jax.random.normal(jax.random.PRNGKey(4), (n_per_group,)) * 0.1
        treatment_covariate = base_treatment + jax.random.normal(jax.random.PRNGKey(5), (n_per_group,)) * 0.1

        result = cuped_analysis(
            np.array(control_metric), np.array(treatment_metric),
            np.array(control_covariate), np.array(treatment_covariate)
        )

        # With strong covariate, should see good variance reduction
        assert result.variance_reduction > 0.3
        assert abs(result.covariate_correlation) > 0.7


class TestCupedTTest:
    """Test CUPED-adjusted t-test functionality."""

    def test_cuped_adjusted_ttest(self, sample_ab_data):
        """Test CUPED-adjusted t-test."""
        control_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "control"
        )
        treatment_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "treatment"
        )

        control_metric = control_data["metric"].to_numpy()
        treatment_metric = treatment_data["metric"].to_numpy()
        control_covariate = control_data["pre_experiment_metric"].to_numpy()
        treatment_covariate = treatment_data["pre_experiment_metric"].to_numpy()

        result = cuped_adjusted_ttest(
            control_metric, treatment_metric,
            control_covariate, treatment_covariate
        )

        assert isinstance(result, StatisticalResult)
        assert result.method == "cuped_adjusted_welch_ttest"  # Default method is welch_ttest
        assert 0 <= result.p_value <= 1
        assert len(result.confidence_interval) == 2


class TestRegressionAdjustment:
    """Test regression adjustment methods."""

    def test_regression_adjustment_basic(self, sample_ab_data):
        """Test basic regression adjustment."""
        metric_data = sample_ab_data["metric"].to_numpy()
        covariate_data = sample_ab_data["pre_experiment_metric"].to_numpy()

        adjusted_metric = regression_adjustment(metric_data, covariate_data)

        assert len(adjusted_metric) == len(metric_data)
        assert isinstance(adjusted_metric, np.ndarray)

        # Adjusted metric should have lower variance if covariate is correlated
        original_var = np.var(metric_data)
        adjusted_var = np.var(adjusted_metric)

        # If there's correlation, variance should be reduced
        correlation = np.corrcoef(metric_data, covariate_data)[0, 1]
        if abs(correlation) > 0.3:
            assert adjusted_var < original_var

    def test_regression_adjustment_properties(self):
        """Test mathematical properties of regression adjustment."""
        key = jax.random.PRNGKey(42)
        n_samples = 200

        # Create correlated data
        base = jax.random.normal(key, (n_samples,))
        metric = base + jax.random.normal(jax.random.PRNGKey(1), (n_samples,)) * 0.3
        covariate = base + jax.random.normal(jax.random.PRNGKey(2), (n_samples,)) * 0.2

        adjusted_metric = regression_adjustment(np.array(metric), np.array(covariate))

        # Mean should be preserved (allow for floating point precision)
        assert abs(np.mean(adjusted_metric) - np.mean(metric)) < 1e-6

        # Variance should be reduced
        assert np.var(adjusted_metric) < np.var(metric)

        # Adjusted metric should be uncorrelated with covariate
        adjusted_correlation = np.corrcoef(adjusted_metric, covariate)[0, 1]
        assert abs(adjusted_correlation) < 1e-6


class TestCupedIntegration:
    """Integration tests for CUPED with statistical tests."""

    def test_cuped_integration_with_multiple_tests(self, sample_ab_data):
        """Test CUPED integration with different statistical tests."""
        control_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "control"
        )
        treatment_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "treatment"
        )

        control_metric = control_data["metric"].to_numpy()
        treatment_metric = treatment_data["metric"].to_numpy()
        control_covariate = control_data["pre_experiment_metric"].to_numpy()
        treatment_covariate = treatment_data["pre_experiment_metric"].to_numpy()

        # Test with different underlying tests
        methods = ["welch_ttest", "student_ttest", "ztest"]

        for method in methods:
            result = cuped_analysis(
                control_metric, treatment_metric,
                control_covariate, treatment_covariate,
                test_method=method
            )

            assert isinstance(result, CupedResult)
            assert method in result.method
            assert 0 <= result.adjusted_p_value <= 1

    @pytest.mark.slow
    def test_cuped_power_improvement_simulation(self):
        """Test CUPED power improvement through simulation."""
        key = jax.random.PRNGKey(123)
        n_simulations = 100
        n_per_group = 50
        effect_size = 0.3

        cuped_significant = 0
        standard_significant = 0

        for i in range(n_simulations):
            key, subkey = jax.random.split(key)
            key1, key2, key3, key4 = jax.random.split(subkey, 4)

            # Generate correlated baseline
            baseline_control = jax.random.normal(key1, (n_per_group,))
            baseline_treatment = jax.random.normal(key2, (n_per_group,))

            # Generate metrics with effect and correlation to baseline
            control_metric = baseline_control * 0.7 + jax.random.normal(key3, (n_per_group,)) * 0.5
            treatment_metric = baseline_treatment * 0.7 + effect_size + jax.random.normal(key4, (n_per_group,)) * 0.5

            # Standard test
            standard_result = welch_ttest(
                np.array(control_metric), np.array(treatment_metric)
            )
            if standard_result.is_significant():
                standard_significant += 1

            # CUPED test
            cuped_result = cuped_analysis(
                np.array(control_metric), np.array(treatment_metric),
                np.array(baseline_control), np.array(baseline_treatment)
            )
            if cuped_result.adjusted_p_value < 0.05:
                cuped_significant += 1

        # CUPED should show higher power
        cuped_power = cuped_significant / n_simulations
        standard_power = standard_significant / n_simulations

        assert cuped_power >= standard_power
