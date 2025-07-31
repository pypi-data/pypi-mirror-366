"""Local fixtures for advanced tests - this will cause fixture ordering errors."""

import pytest


@pytest.fixture()
def local_advanced_fixture():
    """A fixture that's only available in this subdirectory."""
    return {"type": "advanced", "scope": "local", "data": [10, 20, 30, 40, 50]}


@pytest.fixture()
def specialized_config():
    """A specialized configuration only for advanced tests."""
    return {"advanced_mode": True, "precision": "high", "cache_size": 1000}
