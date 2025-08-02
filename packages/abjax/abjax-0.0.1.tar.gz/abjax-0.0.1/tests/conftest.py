"""Shared pytest fixtures and configuration for ABJAX tests."""

import numpy as np
import polars as pl
import pytest
from hypothesis import settings

# Configure Hypothesis for property-based testing
settings.register_profile("ci", max_examples=100, deadline=None)
settings.register_profile("dev", max_examples=10, deadline=None)
settings.load_profile("dev")


@pytest.fixture
def sample_ab_data():
    """Generate sample AB test data for testing."""
    np.random.seed(42)  # For reproducible tests

        # Control group
    control_size = 1000
    control_data = {
        "user_id": list(range(control_size)),
        "variant": ["control"] * control_size,
        "metric": np.random.normal(100, 15, control_size).tolist(),
        "pre_experiment_metric": np.random.normal(95, 12, control_size).tolist(),
    }

    # Treatment group (with small positive effect)
    treatment_size = 1000
    treatment_data = {
        "user_id": list(range(control_size, control_size + treatment_size)),
        "variant": ["treatment"] * treatment_size,
        "metric": np.random.normal(105, 15, treatment_size).tolist(),  # 5% lift
        "pre_experiment_metric": np.random.normal(95, 12, treatment_size).tolist(),
    }

    # Combine data
    all_data = {}
    for key in control_data.keys():
        all_data[key] = control_data[key] + treatment_data[key]

    return pl.DataFrame(all_data)


@pytest.fixture
def small_ab_data():
    """Generate small sample AB test data for edge case testing."""
    np.random.seed(123)

    data = {
        "user_id": list(range(20)),
        "variant": ["control"] * 10 + ["treatment"] * 10,
        "metric": np.random.normal(100, 10, 20).tolist(),
        "pre_experiment_metric": np.random.normal(95, 8, 20).tolist(),
    }

    return pl.DataFrame(data)


@pytest.fixture
def large_ab_data():
    """Generate large sample AB test data for performance testing."""
    np.random.seed(456)

    # Large dataset for performance testing
    size = 100000
    data = {
        "user_id": list(range(size)),
        "variant": ["control"] * (size // 2) + ["treatment"] * (size // 2),
        "metric": np.random.normal(100, 15, size).tolist(),
        "pre_experiment_metric": np.random.normal(95, 12, size).tolist(),
    }

    return pl.DataFrame(data)


@pytest.fixture
def unbalanced_ab_data():
    """Generate unbalanced AB test data."""
    np.random.seed(789)

    # Unbalanced groups
    control_size = 800
    treatment_size = 200

    data = {
        "user_id": list(range(control_size + treatment_size)),
        "variant": ["control"] * control_size + ["treatment"] * treatment_size,
        "metric": np.random.normal(100, 15, control_size + treatment_size).tolist(),
        "pre_experiment_metric": np.random.normal(95, 12, control_size + treatment_size).tolist(),
    }

    return pl.DataFrame(data)


@pytest.fixture
def missing_data_ab_test():
    """Generate AB test data with missing values."""
    np.random.seed(101)

    size = 100
    data = {
        "user_id": list(range(size)),
        "variant": ["control"] * (size // 2) + ["treatment"] * (size // 2),
        "metric": np.random.normal(100, 15, size).tolist(),
        "pre_experiment_metric": np.random.normal(95, 12, size).tolist(),
    }

    # Introduce some missing values
    df = pl.DataFrame(data)
    # Set some metric values to null
    mask = np.random.choice([True, False], size=size, p=[0.1, 0.9])
    df = df.with_columns(
        pl.when(pl.Series(mask)).then(None).otherwise(pl.col("metric")).alias("metric")
    )

    return df
