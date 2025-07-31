"""Tests without any tags to demonstrate unmatched test handling."""

import logging

# Set up logging for this test module
logger = logging.getLogger(__name__)


def test_simple_calculation():
    """A simple test without any tags or fixtures."""
    logger.info("🔢 Testing simple calculations (no tags)")

    result1 = 2 + 2
    logger.info(f"  2 + 2 = {result1}")
    assert result1 == 4

    result2 = 3 * 4
    logger.info(f"  3 * 4 = {result2}")
    assert result2 == 12

    result3 = 10 / 2
    logger.info(f"  10 / 2 = {result3}")
    assert result3 == 5

    logger.info("✅ Simple calculation test passed")


def test_string_operations():
    """Another test without tags or fixtures."""
    logger.info("🔤 Testing string operations (no tags)")

    text = "hello world"
    logger.info(f"  Text: '{text}'")

    length = len(text)
    logger.info(f"  Length: {length}")
    assert length == 11

    logger.info("  Checking for 'hello' in text")
    assert "hello" in text

    logger.info("  Checking for 'world' in text")
    assert "world" in text

    logger.info("✅ String operations test passed")


def test_list_operations():
    """Test list operations without tags or fixtures."""
    logger.info("📋 Testing list operations (no tags)")

    numbers = [1, 2, 3, 4, 5]
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

    logger.info("✅ List operations test passed")
