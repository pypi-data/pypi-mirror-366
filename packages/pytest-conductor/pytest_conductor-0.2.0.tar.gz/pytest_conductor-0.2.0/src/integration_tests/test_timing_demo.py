"""Tests for timing demo to show fixture ordering with wait times."""

import time

import pytest


@pytest.fixture()
def no_wait():
    """Fixture that doesn't wait."""
    return {"type": "no_wait", "value": "instant"}


@pytest.fixture()
def wait_3_seconds():
    """Fixture that waits 3 seconds."""
    time.sleep(3)
    return {"type": "wait_3_seconds", "value": "delayed"}


def test_no_wait_1(no_wait):
    """Test using no_wait fixture - should run quickly."""
    assert no_wait["type"] == "no_wait"
    assert no_wait["value"] == "instant"


def test_no_wait_2(no_wait):
    """Test using no_wait fixture - should run quickly."""
    assert no_wait["type"] == "no_wait"
    assert no_wait["value"] == "instant"


def test_wait_3_seconds_1(wait_3_seconds):
    """Test using wait_3_seconds fixture - should take 3 seconds."""
    assert wait_3_seconds["type"] == "wait_3_seconds"
    assert wait_3_seconds["value"] == "delayed"


def test_wait_3_seconds_2(wait_3_seconds):
    """Test using wait_3_seconds fixture - should take 3 seconds."""
    assert wait_3_seconds["type"] == "wait_3_seconds"
    assert wait_3_seconds["value"] == "delayed"
