"""Advanced tests that use local fixtures."""

import logging

import pytest

# Set up logging for this test module
logger = logging.getLogger(__name__)


@pytest.mark.slow()
@pytest.mark.integration()
def test_local_advanced_fixture(local_advanced_fixture):
    """Test using the local advanced fixture."""
    logger.info("🔬 Testing local advanced fixture")

    logger.info(f"  Fixture data: {local_advanced_fixture}")

    fixture_type = local_advanced_fixture["type"]
    logger.info(f"  Type: {fixture_type}")
    assert fixture_type == "advanced"

    scope = local_advanced_fixture["scope"]
    logger.info(f"  Scope: {scope}")
    assert scope == "local"

    data = local_advanced_fixture["data"]
    logger.info(f"  Data: {data}")

    data_length = len(data)
    logger.info(f"  Data length: {data_length}")
    assert data_length == 5

    data_sum = sum(data)
    logger.info(f"  Data sum: {data_sum}")
    assert data_sum == 150

    logger.info("✅ Local advanced fixture test passed")


@pytest.mark.slow()
@pytest.mark.integration()
def test_specialized_config(specialized_config):
    """Test using the specialized configuration."""
    logger.info("🔬 Testing specialized configuration")

    logger.info(f"  Config: {specialized_config}")

    advanced_mode = specialized_config["advanced_mode"]
    logger.info(f"  Advanced mode: {advanced_mode}")
    assert advanced_mode is True

    precision = specialized_config["precision"]
    logger.info(f"  Precision: {precision}")
    assert precision == "high"

    cache_size = specialized_config["cache_size"]
    logger.info(f"  Cache size: {cache_size}")
    assert cache_size == 1000

    logger.info("✅ Specialized config test passed")


@pytest.mark.slow()
@pytest.mark.integration()
def test_combined_local_fixtures(local_advanced_fixture, specialized_config):
    """Test using both local fixtures together."""
    logger.info("🔬 Testing combined local fixtures")

    data = local_advanced_fixture["data"]
    cache_size = specialized_config["cache_size"]

    logger.info(f"  Data: {data}")
    logger.info(f"  Cache size: {cache_size}")

    # Simulate some advanced processing
    data_sum = sum(data)
    logger.info(f"  Data sum: {data_sum}")

    cache_factor = cache_size / 1000
    logger.info(f"  Cache factor: {cache_factor}")

    result = data_sum * cache_factor
    logger.info(f"  Result (sum * cache_factor): {result}")

    expected = 150 * 1  # 150
    logger.info(f"  Expected result: {expected}")

    assert result == expected

    logger.info("✅ Combined local fixtures test passed")
