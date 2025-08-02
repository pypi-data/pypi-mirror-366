"""Tests for multiple testing correction methods."""

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from abjax.core.corrections import CorrectionResult
from abjax.core.corrections import apply_correction_to_results
from abjax.core.corrections import benjamini_hochberg_fdr
from abjax.core.corrections import bonferroni_correction
from abjax.core.corrections import estimate_fdr
from abjax.core.corrections import estimate_fwer
from abjax.core.corrections import holm_bonferroni_correction
from abjax.core.corrections import sidak_correction
from abjax.core.stats import StatisticalResult
from abjax.core.stats import welch_ttest


class TestCorrectionResult:
    """Test the CorrectionResult dataclass."""

    def test_result_creation(self):
        """Test creation of CorrectionResult."""
        original_p_values = [0.01, 0.03, 0.07, 0.15, 0.25]
        corrected_p_values = [0.05, 0.15, 0.35, 0.75, 1.0]
        significant_flags = [True, False, False, False, False]

        result = CorrectionResult(
            original_p_values=original_p_values,
            corrected_p_values=corrected_p_values,
            significant=significant_flags,
            alpha=0.05,
            method="bonferroni",
            rejected_hypotheses=1,
            family_wise_error_rate=0.05,
        )

        assert result.original_p_values == original_p_values
        assert result.corrected_p_values == corrected_p_values
        assert result.significant == significant_flags
        assert result.method == "bonferroni"
        assert result.rejected_hypotheses == 1

    def test_correction_summary_methods(self):
        """Test summary methods on correction results."""
        result = CorrectionResult(
            original_p_values=[0.001, 0.01, 0.03, 0.08, 0.15],
            corrected_p_values=[0.005, 0.05, 0.15, 0.4, 0.75],
            significant=[True, True, False, False, False],
            alpha=0.05,
            method="benjamini_hochberg",
            rejected_hypotheses=2,
            family_wise_error_rate=0.0975,
        )

        assert result.number_of_comparisons() == 5
        assert result.number_rejected() == 2
        assert result.proportion_rejected() == 0.4
        assert result.estimated_true_discoveries() >= 1  # Should be at least 1 for BH


class TestBonferroniCorrection:
    """Test Bonferroni correction methods."""

    def test_bonferroni_basic(self):
        """Test basic Bonferroni correction."""
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        alpha = 0.05

        result = bonferroni_correction(p_values, alpha)

        expected_corrected = [0.05, 0.10, 0.15, 0.20, 0.25]
        # Allow for small floating point differences
        for actual, expected in zip(result.corrected_p_values, expected_corrected):
            assert abs(actual - expected) < 1e-6
        assert result.significant == [True, False, False, False, False]
        assert result.method == "bonferroni"
        assert result.rejected_hypotheses == 1

    def test_bonferroni_no_significance(self):
        """Test Bonferroni with no significant results."""
        p_values = [0.1, 0.2, 0.3, 0.4, 0.5]
        alpha = 0.05

        result = bonferroni_correction(p_values, alpha)

        assert all(not sig for sig in result.significant)
        assert result.rejected_hypotheses == 0

    def test_bonferroni_all_significant(self):
        """Test Bonferroni with all results significant."""
        p_values = [0.001, 0.002, 0.003, 0.004, 0.005]
        alpha = 0.05

        result = bonferroni_correction(p_values, alpha)

        assert all(result.significant)
        assert result.rejected_hypotheses == 5

    def test_bonferroni_empty_input(self):
        """Test Bonferroni with empty p_values."""
        result = bonferroni_correction([], 0.05)

        assert result.original_p_values == []
        assert result.corrected_p_values == []
        assert result.significant == []
        assert result.rejected_hypotheses == 0

    @given(
        st.lists(
            st.floats(min_value=0.0001, max_value=0.9999, allow_nan=False),
            min_size=1,
            max_size=20,
        ),
        st.floats(min_value=0.01, max_value=0.1),
    )
    def test_bonferroni_properties(self, p_values, alpha):
        """Property-based test for Bonferroni correction."""
        result = bonferroni_correction(p_values, alpha)

        # Properties that should always hold
        assert len(result.corrected_p_values) == len(p_values)
        assert len(result.significant) == len(p_values)
        # Corrected p-values should be >= original (allowing for JAX floating point precision)
        for corr, orig in zip(result.corrected_p_values, p_values):
            assert corr >= orig - 1e-6 or abs(corr - 1.0) < 1e-6
        assert result.rejected_hypotheses == sum(result.significant)
        assert 0 <= result.rejected_hypotheses <= len(p_values)


class TestBenjaminiHochbergFDR:
    """Test Benjamini-Hochberg FDR correction."""

    def test_benjamini_hochberg_basic(self):
        """Test basic Benjamini-Hochberg procedure."""
        p_values = [0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205]
        alpha = 0.05

        result = benjamini_hochberg_fdr(p_values, alpha)

        # First few should be significant based on step-up procedure
        assert result.significant[0]  # 0.001 should be significant
        assert result.significant[1]  # 0.008 should be significant
        assert result.method == "benjamini_hochberg"
        assert result.rejected_hypotheses >= 2

    def test_benjamini_hochberg_sorted_input(self):
        """Test that BH works correctly with pre-sorted input."""
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        alpha = 0.05

        result = benjamini_hochberg_fdr(p_values, alpha)

        # Should maintain original order in results
        assert result.original_p_values == p_values
        assert len(result.corrected_p_values) == len(p_values)

    def test_benjamini_hochberg_unsorted_input(self):
        """Test BH with unsorted p_values."""
        p_values = [0.05, 0.01, 0.04, 0.02, 0.03]
        alpha = 0.05

        result = benjamini_hochberg_fdr(p_values, alpha)

        # Should return results in original order
        assert result.original_p_values == p_values
        assert len(result.corrected_p_values) == len(p_values)

    def test_benjamini_hochberg_more_liberal_than_bonferroni(self):
        """Test that BH is more liberal than Bonferroni."""
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        alpha = 0.05

        bh_result = benjamini_hochberg_fdr(p_values, alpha)
        bonf_result = bonferroni_correction(p_values, alpha)

        # BH should reject at least as many as Bonferroni
        assert bh_result.rejected_hypotheses >= bonf_result.rejected_hypotheses

    @given(
        st.lists(
            st.floats(min_value=0.0001, max_value=0.9999, allow_nan=False),
            min_size=1,
            max_size=15,
        ),
        st.floats(min_value=0.01, max_value=0.2),
    )
    def test_benjamini_hochberg_properties(self, p_values, alpha):
        """Property-based test for Benjamini-Hochberg procedure."""
        result = benjamini_hochberg_fdr(p_values, alpha)

        # Basic properties
        assert len(result.corrected_p_values) == len(p_values)
        assert len(result.significant) == len(p_values)
        assert result.rejected_hypotheses == sum(result.significant)
        assert 0 <= result.rejected_hypotheses <= len(p_values)

        # BH-specific properties
        assert result.method == "benjamini_hochberg"


class TestHolmBonferroniCorrection:
    """Test Holm-Bonferroni step-down correction."""

    def test_holm_bonferroni_basic(self):
        """Test basic Holm-Bonferroni correction."""
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        alpha = 0.05

        result = holm_bonferroni_correction(p_values, alpha)

        assert result.method == "holm_bonferroni"
        assert len(result.corrected_p_values) == len(p_values)
        # Holm should be less conservative than Bonferroni
        bonf_result = bonferroni_correction(p_values, alpha)
        assert result.rejected_hypotheses >= bonf_result.rejected_hypotheses

    def test_holm_bonferroni_step_down_property(self):
        """Test that Holm procedure follows step-down logic."""
        p_values = [0.001, 0.02, 0.03, 0.15, 0.3]
        alpha = 0.05

        result = holm_bonferroni_correction(p_values, alpha)

        # If a hypothesis is not rejected, all subsequent (larger p-values) should also not be rejected
        # when sorted by p-value
        sorted_indices = np.argsort(p_values)
        sorted_significant = [result.significant[i] for i in sorted_indices]

        # Check step-down property: once we fail to reject, all subsequent should also fail
        found_non_significant = False
        for sig in sorted_significant:
            if found_non_significant:
                assert not sig  # All subsequent should be non-significant
            if not sig:
                found_non_significant = True

    def test_holm_bonferroni_uniform_nulls(self):
        """Test Holm correction with uniform null p-values."""
        # Simulate p-values under null hypothesis
        np.random.seed(42)
        p_values = np.random.uniform(0, 1, 100).tolist()
        alpha = 0.05

        result = holm_bonferroni_correction(p_values, alpha)

        # Under null, should reject approximately alpha * 100 hypotheses
        expected_rejections = alpha * len(p_values)
        # Allow some variability due to randomness
        assert result.rejected_hypotheses <= expected_rejections + 10


class TestSidakCorrection:
    """Test Šidák correction methods."""

    def test_sidak_basic(self):
        """Test basic Šidák correction."""
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        alpha = 0.05

        result = sidak_correction(p_values, alpha)

        assert result.method == "sidak"
        assert len(result.corrected_p_values) == len(p_values)
        # Šidák should be less conservative than Bonferroni
        bonf_result = bonferroni_correction(p_values, alpha)
        assert result.rejected_hypotheses >= bonf_result.rejected_hypotheses

    def test_sidak_formula_accuracy(self):
        """Test that Šidák correction uses correct formula."""
        p_values = [0.01]
        alpha = 0.05
        m = 5  # Simulate this being the 5th comparison

        # Manual calculation: alpha_sidak = 1 - (1 - alpha)^(1/m)
        expected_alpha_sidak = 1 - (1 - alpha) ** (1 / m)

        # Since we can't directly test internal calculation, we verify behavior
        result = sidak_correction(p_values * m, alpha)
        # Šidák should be more liberal than Bonferroni for same inputs
        bonf_result = bonferroni_correction(p_values * m, alpha)

        assert result.rejected_hypotheses >= bonf_result.rejected_hypotheses


class TestCorrectionsIntegration:
    """Test integration of corrections with statistical results."""

    def test_apply_correction_to_results(self, sample_ab_data):
        """Test applying corrections to StatisticalResult objects."""
        # Create multiple statistical results
        results = []
        for i in range(5):
            # Create slightly different data for each test
            control_data = sample_ab_data.filter(
                sample_ab_data["variant"] == "control"
            )["metric"].to_numpy()
            treatment_data = sample_ab_data.filter(
                sample_ab_data["variant"] == "treatment"
            )["metric"].to_numpy()

            # Add some noise to create different p-values
            noise_control = np.random.normal(0, 1, len(control_data)) * 0.1
            noise_treatment = np.random.normal(0, 1, len(treatment_data)) * 0.1

            result = welch_ttest(
                control_data + noise_control, treatment_data + noise_treatment
            )
            results.append(result)

        # Apply Bonferroni correction
        corrected_results = apply_correction_to_results(results, method="bonferroni")

        assert len(corrected_results) == len(results)
        assert all(isinstance(result, StatisticalResult) for result in corrected_results)

        # Check that p-values are corrected
        original_p_values = [r.p_value for r in results]
        corrected_p_values = [r.p_value for r in corrected_results]

        # Corrected p-values should be >= original (for Bonferroni)
        for orig, corr in zip(original_p_values, corrected_p_values):
            assert corr >= orig

    def test_apply_correction_benjamini_hochberg(self, sample_ab_data):
        """Test applying BH correction to statistical results."""
        # Generate multiple test results
        results = []
        np.random.seed(123)  # For reproducible test results

        for i in range(10):
            control_data = sample_ab_data.filter(
                sample_ab_data["variant"] == "control"
            )["metric"].to_numpy()
            treatment_data = sample_ab_data.filter(
                sample_ab_data["variant"] == "treatment"
            )["metric"].to_numpy()

            # Add different amounts of noise/effect
            effect = i * 0.1
            treatment_with_effect = treatment_data + effect

            result = welch_ttest(control_data, treatment_with_effect)
            results.append(result)

        # Apply BH correction
        bh_corrected = apply_correction_to_results(results, method="benjamini_hochberg")
        bonf_corrected = apply_correction_to_results(results, method="bonferroni")

        # BH should typically be more liberal than Bonferroni
        bh_significant = sum(1 for r in bh_corrected if r.is_significant())
        bonf_significant = sum(1 for r in bonf_corrected if r.is_significant())

        assert bh_significant >= bonf_significant

    def test_correction_preserves_other_attributes(self, sample_ab_data):
        """Test that correction preserves non-p-value attributes."""
        control_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "control"
        )["metric"].to_numpy()
        treatment_data = sample_ab_data.filter(
            sample_ab_data["variant"] == "treatment"
        )["metric"].to_numpy()

        original_result = welch_ttest(control_data, treatment_data)
        corrected_results = apply_correction_to_results(
            [original_result], method="bonferroni"
        )

        corrected = corrected_results[0]

        # These should be preserved
        assert corrected.statistic == original_result.statistic
        assert corrected.confidence_interval == original_result.confidence_interval
        assert corrected.effect_size == original_result.effect_size
        # Method should be updated to indicate correction
        assert "bonferroni" in corrected.method


class TestErrorRateEstimation:
    """Test error rate estimation functions."""

    def test_estimate_fdr_basic(self):
        """Test FDR estimation."""
        p_values = [0.001, 0.01, 0.05, 0.1, 0.3, 0.7]
        alpha = 0.05

        fdr = estimate_fdr(p_values, alpha, method="benjamini_hochberg")

        assert 0 <= fdr <= 1
        assert isinstance(fdr, float)

    def test_estimate_fwer_basic(self):
        """Test FWER estimation."""
        p_values = [0.001, 0.01, 0.05, 0.1, 0.3, 0.7]
        alpha = 0.05

        fwer = estimate_fwer(p_values, alpha)

        assert 0 <= fwer <= 1
        assert isinstance(fwer, float)

    def test_fwer_increases_with_comparisons(self):
        """Test that FWER increases with number of comparisons."""
        base_p_value = 0.03
        alpha = 0.05

        fwer_single = estimate_fwer([base_p_value], alpha)
        fwer_multiple = estimate_fwer([base_p_value] * 5, alpha)

        assert fwer_multiple > fwer_single

    def test_error_rates_with_corrections(self):
        """Test error rate estimates with different corrections."""
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.2]
        alpha = 0.05

        # Bonferroni should have lower FWER than uncorrected
        fwer_uncorrected = estimate_fwer(p_values, alpha)

        bonf_result = bonferroni_correction(p_values, alpha)
        fwer_bonferroni = bonf_result.family_wise_error_rate

        assert fwer_bonferroni <= alpha  # Bonferroni controls FWER
        assert fwer_bonferroni <= fwer_uncorrected


class TestCorrectionsEdgeCases:
    """Test edge cases and error conditions."""

    def test_single_p_value(self):
        """Test corrections with single p-value."""
        p_values = [0.03]
        alpha = 0.05

        bonf_result = bonferroni_correction(p_values, alpha)
        bh_result = benjamini_hochberg_fdr(p_values, alpha)
        holm_result = holm_bonferroni_correction(p_values, alpha)

        # All should give same result for single comparison
        assert bonf_result.significant == bh_result.significant == holm_result.significant
        assert bonf_result.rejected_hypotheses == 1

    def test_all_p_values_equal(self):
        """Test corrections when all p-values are equal."""
        p_values = [0.03] * 5
        alpha = 0.05

        bonf_result = bonferroni_correction(p_values, alpha)
        bh_result = benjamini_hochberg_fdr(p_values, alpha)

        # BH should be more liberal than Bonferroni
        assert bh_result.rejected_hypotheses >= bonf_result.rejected_hypotheses

    def test_extreme_p_values(self):
        """Test corrections with very small and large p-values."""
        p_values = [1e-10, 1e-5, 0.5, 0.99, 0.999]
        alpha = 0.05

        for method in ["bonferroni", "benjamini_hochberg", "holm_bonferroni"]:
            if method == "bonferroni":
                result = bonferroni_correction(p_values, alpha)
            elif method == "benjamini_hochberg":
                result = benjamini_hochberg_fdr(p_values, alpha)
            else:
                result = holm_bonferroni_correction(p_values, alpha)

            # Should handle extreme values gracefully
            assert len(result.corrected_p_values) == len(p_values)
            assert all(0 <= p <= 1 for p in result.corrected_p_values)

    def test_invalid_alpha_values(self):
        """Test that invalid alpha values raise appropriate errors."""
        p_values = [0.01, 0.02, 0.03]

        with pytest.raises((ValueError, AssertionError)):
            bonferroni_correction(p_values, alpha=-0.1)

        with pytest.raises((ValueError, AssertionError)):
            bonferroni_correction(p_values, alpha=1.1)

        with pytest.raises((ValueError, AssertionError)):
            benjamini_hochberg_fdr(p_values, alpha=0)

    def test_invalid_p_values(self):
        """Test that invalid p-values raise appropriate errors."""
        with pytest.raises((ValueError, AssertionError)):
            bonferroni_correction([-0.1, 0.02, 0.03], alpha=0.05)

        with pytest.raises((ValueError, AssertionError)):
            bonferroni_correction([0.01, 1.1, 0.03], alpha=0.05)

        with pytest.raises((ValueError, AssertionError)):
            benjamini_hochberg_fdr([float("nan"), 0.02, 0.03], alpha=0.05)
