"""Tests for the conductor plugin."""

import pytest


@pytest.mark.fast()
def test_fast_1():
    """Fast test 1."""
    assert True


@pytest.mark.fast()
def test_fast_2():
    """Fast test 2."""
    assert True


@pytest.mark.slow()
def test_slow_1():
    """Slow test 1."""
    assert True


@pytest.mark.slow()
def test_slow_2():
    """Slow test 2."""
    assert True


@pytest.mark.integration()
def test_integration_1():
    """Integration test 1."""
    assert True


@pytest.mark.integration()
def test_integration_2():
    """Integration test 2."""
    assert True


@pytest.mark.fast()
@pytest.mark.slow()
def test_fast_and_slow():
    """Test with multiple tags - should use the first one in order."""
    assert True


def test_no_tags():
    """Test without any tags."""
    assert True


@pytest.mark.unit()
def test_unit_1():
    """Unit test 1."""
    assert True


@pytest.mark.unit()
def test_unit_2():
    """Unit test 2."""
    assert True
