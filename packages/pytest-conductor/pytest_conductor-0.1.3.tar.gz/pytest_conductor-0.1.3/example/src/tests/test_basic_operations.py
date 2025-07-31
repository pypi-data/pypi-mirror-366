"""Tests for basic calculator operations."""

import logging

import pytest

# Set up logging for this test module
logger = logging.getLogger(__name__)


@pytest.mark.fast()
@pytest.mark.unit()
def test_addition(basic_calculator):
    """Test basic addition."""
    logger.info("🧮 Testing basic addition operations")

    result1 = basic_calculator.add(2, 3)
    logger.info(f"  2 + 3 = {result1}")
    assert result1 == 5

    result2 = basic_calculator.add(-1, 1)
    logger.info(f"  -1 + 1 = {result2}")
    assert result2 == 0

    result3 = basic_calculator.add(0, 0)
    logger.info(f"  0 + 0 = {result3}")
    assert result3 == 0

    logger.info("✅ All addition tests passed")


@pytest.mark.fast()
@pytest.mark.unit()
def test_subtraction(basic_calculator):
    """Test basic subtraction."""
    logger.info("🧮 Testing basic subtraction operations")

    result1 = basic_calculator.subtract(5, 3)
    logger.info(f"  5 - 3 = {result1}")
    assert result1 == 2

    result2 = basic_calculator.subtract(1, 1)
    logger.info(f"  1 - 1 = {result2}")
    assert result2 == 0

    result3 = basic_calculator.subtract(0, 5)
    logger.info(f"  0 - 5 = {result3}")
    assert result3 == -5

    logger.info("✅ All subtraction tests passed")


@pytest.mark.fast()
@pytest.mark.unit()
def test_multiplication(basic_calculator):
    """Test basic multiplication."""
    logger.info("🧮 Testing basic multiplication operations")

    result1 = basic_calculator.multiply(2, 3)
    logger.info(f"  2 * 3 = {result1}")
    assert result1 == 6

    result2 = basic_calculator.multiply(-2, 3)
    logger.info(f"  -2 * 3 = {result2}")
    assert result2 == -6

    result3 = basic_calculator.multiply(0, 5)
    logger.info(f"  0 * 5 = {result3}")
    assert result3 == 0

    logger.info("✅ All multiplication tests passed")


@pytest.mark.fast()
@pytest.mark.unit()
def test_division(basic_calculator):
    """Test basic division."""
    logger.info("🧮 Testing basic division operations")

    result1 = basic_calculator.divide(6, 2)
    logger.info(f"  6 / 2 = {result1}")
    assert result1 == 3

    result2 = basic_calculator.divide(5, 2)
    logger.info(f"  5 / 2 = {result2}")
    assert result2 == 2.5

    result3 = basic_calculator.divide(0, 5)
    logger.info(f"  0 / 5 = {result3}")
    assert result3 == 0

    logger.info("✅ All division tests passed")


@pytest.mark.fast()
@pytest.mark.unit()
def test_division_by_zero(basic_calculator):
    """Test division by zero raises error."""
    logger.info("🧮 Testing division by zero error handling")

    try:
        basic_calculator.divide(5, 0)
        pytest.fail("Expected ValueError for division by zero")
    except ValueError as e:
        logger.info(f"  ✅ Correctly caught division by zero error: {e}")
        assert "Cannot divide by zero" in str(e)

    logger.info("✅ Division by zero test passed")


@pytest.mark.fast()
@pytest.mark.unit()
def test_calculation_history(basic_calculator):
    """Test that calculations are recorded in history."""
    logger.info("🧮 Testing calculation history functionality")

    # Perform some calculations
    basic_calculator.add(1, 2)
    basic_calculator.multiply(3, 4)

    history = basic_calculator.get_history()
    logger.info(f"  History entries: {len(history)}")
    logger.info(f"  History content: {history}")

    assert len(history) == 2
    assert "1 + 2 = 3" in history
    assert "3 * 4 = 12" in history

    logger.info("✅ Calculation history test passed")


@pytest.mark.fast()
@pytest.mark.unit()
def test_clear_history(basic_calculator):
    """Test clearing calculation history."""
    logger.info("🧮 Testing history clearing functionality")

    # Add some calculations
    basic_calculator.add(1, 2)
    logger.info(f"  History before clear: {len(basic_calculator.get_history())} entries")

    # Clear history
    basic_calculator.clear_history()
    history_length = len(basic_calculator.get_history())
    logger.info(f"  History after clear: {history_length} entries")

    assert history_length == 0

    logger.info("✅ History clearing test passed")
