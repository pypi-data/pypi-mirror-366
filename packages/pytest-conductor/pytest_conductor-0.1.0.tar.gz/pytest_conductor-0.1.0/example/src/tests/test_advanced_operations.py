"""Tests for advanced calculator operations."""

import logging

import pytest

# Set up logging for this test module
logger = logging.getLogger(__name__)


@pytest.mark.slow()
@pytest.mark.integration()
def test_power_operation(advanced_calculator):
    """Test power operation."""
    logger.info("🚀 Testing advanced power operations")

    result1 = advanced_calculator.power(2, 3)
    logger.info(f"  2 ^ 3 = {result1}")
    assert result1 == 8

    result2 = advanced_calculator.power(5, 0)
    logger.info(f"  5 ^ 0 = {result2}")
    assert result2 == 1

    result3 = advanced_calculator.power(2, -1)
    logger.info(f"  2 ^ -1 = {result3}")
    assert result3 == 0.5

    logger.info("✅ All power operation tests passed")


@pytest.mark.slow()
@pytest.mark.integration()
def test_square_root(advanced_calculator):
    """Test square root operation."""
    logger.info("🚀 Testing square root operations")

    result1 = advanced_calculator.square_root(4)
    logger.info(f"  √4 = {result1}")
    assert result1 == 2

    result2 = advanced_calculator.square_root(9)
    logger.info(f"  √9 = {result2}")
    assert result2 == 3

    result3 = advanced_calculator.square_root(0)
    logger.info(f"  √0 = {result3}")
    assert result3 == 0

    logger.info("✅ All square root tests passed")


@pytest.mark.slow()
@pytest.mark.integration()
def test_square_root_negative_number(advanced_calculator):
    """Test square root of negative number raises error."""
    logger.info("🚀 Testing square root error handling")

    try:
        advanced_calculator.square_root(-4)
        pytest.fail("Expected ValueError for negative square root")
    except ValueError as e:
        logger.info(f"  ✅ Correctly caught negative square root error: {e}")
        assert "Cannot calculate square root of negative number" in str(e)

    logger.info("✅ Negative square root error test passed")


@pytest.mark.slow()
@pytest.mark.integration()
def test_advanced_calculator_inheritance(advanced_calculator):
    """Test that advanced calculator inherits basic operations."""
    logger.info("🚀 Testing advanced calculator inheritance")

    # Test inherited basic operations
    result1 = advanced_calculator.add(2, 3)
    logger.info(f"  Inherited add: 2 + 3 = {result1}")
    assert result1 == 5

    result2 = advanced_calculator.multiply(4, 5)
    logger.info(f"  Inherited multiply: 4 * 5 = {result2}")
    assert result2 == 20

    # Test advanced operations
    result3 = advanced_calculator.power(2, 3)
    logger.info(f"  Advanced power: 2 ^ 3 = {result3}")
    assert result3 == 8

    logger.info("✅ Inheritance test passed")


@pytest.mark.slow()
@pytest.mark.integration()
def test_mixed_operations_history(advanced_calculator):
    """Test history with mixed basic and advanced operations."""
    logger.info("🚀 Testing mixed operations history")

    # Perform mixed operations
    advanced_calculator.add(1, 2)
    advanced_calculator.power(2, 3)
    advanced_calculator.square_root(16)

    history = advanced_calculator.get_history()
    logger.info(f"  History entries: {len(history)}")
    logger.info(f"  History content: {history}")

    assert len(history) == 3
    assert "1 + 2 = 3" in history
    assert "2 ^ 3 = 8" in history
    assert "√16 = 4.0" in history

    logger.info("✅ Mixed operations history test passed")
