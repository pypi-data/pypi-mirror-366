"""Tests for conductor fixture ordering functionality."""

import pytest


@pytest.fixture()
def db():
    """Database fixture."""
    return {"type": "database", "data": "db_data"}


@pytest.fixture()
def redis():
    """Redis fixture."""
    return {"type": "redis", "data": "redis_data"}


@pytest.fixture()
def cache():
    """Cache fixture."""
    return {"type": "cache", "data": "cache_data"}


@pytest.fixture()
def api():
    """API fixture."""
    return {"type": "api", "data": "api_data"}


def test_db_only(db):
    """Test using only database fixture."""
    assert db["type"] == "database"


def test_redis_only(redis):
    """Test using only redis fixture."""
    assert redis["type"] == "redis"


def test_cache_only(cache):
    """Test using only cache fixture."""
    assert cache["type"] == "cache"


def test_api_only(api):
    """Test using only API fixture."""
    assert api["type"] == "api"


def test_db_and_redis(db, redis):
    """Test using database and redis fixtures."""
    assert db["type"] == "database"
    assert redis["type"] == "redis"


def test_redis_and_cache(redis, cache):
    """Test using redis and cache fixtures."""
    assert redis["type"] == "redis"
    assert cache["type"] == "cache"


def test_all_fixtures(db, redis, cache, api):
    """Test using all fixtures."""
    assert db["type"] == "database"
    assert redis["type"] == "redis"
    assert cache["type"] == "cache"
    assert api["type"] == "api"


def test_no_fixtures():
    """Test without any fixtures."""
    assert True


class TestClass:
    """Test class to demonstrate fixture ordering with class methods."""

    def test_class_method_with_db(self, db):
        """Class method using database fixture."""
        assert db["type"] == "database"

    def test_class_method_with_redis(self, redis):
        """Class method using redis fixture."""
        assert redis["type"] == "redis"

    def test_class_method_no_fixtures(self):
        """Class method without fixtures."""
        assert True
