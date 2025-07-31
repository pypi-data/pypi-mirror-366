"""Tests for data processing functionality."""

import logging

import pytest

# Set up logging for this test module
logger = logging.getLogger(__name__)


@pytest.mark.fast()
@pytest.mark.unit()
def test_numbers_processing(sample_data):
    """Test processing of numbers from sample data."""
    logger.info("📊 Testing numbers processing")

    numbers = sample_data["numbers"]
    logger.info(f"  Numbers: {numbers}")

    length = len(numbers)
    logger.info(f"  Length: {length}")
    assert length == 5

    total = sum(numbers)
    logger.info(f"  Sum: {total}")
    assert total == 15

    maximum = max(numbers)
    logger.info(f"  Max: {maximum}")
    assert maximum == 5

    minimum = min(numbers)
    logger.info(f"  Min: {minimum}")
    assert minimum == 1

    logger.info("✅ Numbers processing test passed")


@pytest.mark.fast()
@pytest.mark.unit()
def test_strings_processing(sample_data):
    """Test processing of strings from sample data."""
    logger.info("📊 Testing strings processing")

    strings = sample_data["strings"]
    logger.info(f"  Strings: {strings}")

    length = len(strings)
    logger.info(f"  Length: {length}")
    assert length == 3

    # Check each expected string
    for expected in ["hello", "world", "test"]:
        logger.info(f"  Checking for '{expected}' in strings")
        assert expected in strings

    logger.info("✅ Strings processing test passed")


@pytest.mark.fast()
@pytest.mark.unit()
def test_mixed_data_processing(sample_data):
    """Test processing of mixed data types."""
    logger.info("📊 Testing mixed data processing")

    mixed = sample_data["mixed"]
    logger.info(f"  Mixed data: {mixed}")

    length = len(mixed)
    logger.info(f"  Length: {length}")
    assert length == 4

    # Check each expected value
    expected_values = [1, "two", 3.0, True]
    for expected in expected_values:
        logger.info(f"  Checking for {expected} in mixed data")
        assert expected in mixed

    logger.info("✅ Mixed data processing test passed")


@pytest.mark.slow()
@pytest.mark.integration()
def test_config_usage(test_config):
    """Test using test configuration."""
    logger.info("📊 Testing configuration usage")

    logger.info(f"  Config: {test_config}")

    timeout = test_config["timeout"]
    logger.info(f"  Timeout: {timeout}")
    assert timeout == 30

    retries = test_config["retries"]
    logger.info(f"  Retries: {retries}")
    assert retries == 3

    debug = test_config["debug"]
    logger.info(f"  Debug: {debug}")
    assert debug is True

    logger.info("✅ Configuration usage test passed")


@pytest.mark.slow()
@pytest.mark.integration()
def test_data_and_config_combination(sample_data, test_config):
    """Test combining sample data with test configuration."""
    logger.info("📊 Testing data and config combination")

    # Simulate some processing that uses both fixtures
    numbers = sample_data["numbers"]
    timeout = test_config["timeout"]

    logger.info(f"  Numbers: {numbers}")
    logger.info(f"  Timeout: {timeout}")

    # Simulate processing that takes time
    numbers_sum = sum(numbers)
    logger.info(f"  Sum of numbers: {numbers_sum}")

    result = numbers_sum * timeout
    logger.info(f"  Result (sum * timeout): {result}")

    expected = 15 * 30  # 450
    logger.info(f"  Expected result: {expected}")

    assert result == expected

    logger.info("✅ Data and config combination test passed")
