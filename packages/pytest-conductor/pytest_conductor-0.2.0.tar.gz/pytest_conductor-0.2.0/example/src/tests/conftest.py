"""Global fixtures for the calculator tests."""

import pytest
from calculator import AdvancedCalculator, Calculator


@pytest.fixture()
def basic_calculator():
    """Provide a basic calculator instance."""
    return Calculator()


@pytest.fixture()
def advanced_calculator():
    """Provide an advanced calculator instance."""
    return AdvancedCalculator()


@pytest.fixture()
def sample_data():
    """Provide sample data for testing."""
    return {
        "numbers": [1, 2, 3, 4, 5],
        "strings": ["hello", "world", "test"],
        "mixed": [1, "two", 3.0, True],
    }


@pytest.fixture()
def test_config():
    """Provide test configuration."""
    return {"timeout": 30, "retries": 3, "debug": True}
