"""Practical examples demonstrating edge cases in pytest-conductor."""

import pytest

# ============================================================================
# Edge Case 1: Tests with multiple tags
# ============================================================================


@pytest.mark.fast()
@pytest.mark.slow()
def test_multiple_tags_fast_and_slow():
    """
    This test has both 'fast' and 'slow' tags.

    When running: pytest --tag-order fast slow integration
    Expected behavior: Runs once in the 'fast' group (first matching tag)
    """
    assert True


@pytest.mark.slow()
@pytest.mark.integration()
def test_multiple_tags_slow_and_integration():
    """
    This test has both 'slow' and 'integration' tags.

    When running: pytest --tag-order fast slow integration
    Expected behavior: Runs once in the 'slow' group (first matching tag)
    """
    assert True


@pytest.mark.fast()
@pytest.mark.slow()
@pytest.mark.integration()
def test_multiple_tags_all_three():
    """
    This test has all three tags: 'fast', 'slow', and 'integration'.

    When running: pytest --tag-order fast slow integration
    Expected behavior: Runs once in the 'fast' group (first matching tag)
    """
    assert True


# ============================================================================
# Edge Case 2: Tests with multiple fixtures
# ============================================================================


@pytest.fixture()
def db():
    """Database fixture."""
    return {"type": "database"}


@pytest.fixture()
def redis():
    """Redis fixture."""
    return {"type": "redis"}


@pytest.fixture()
def cache():
    """Cache fixture."""
    return {"type": "cache"}


def test_multiple_fixtures_db_and_redis(db, redis):
    """
    This test uses both 'db' and 'redis' fixtures.

    When running: pytest --fixture-order db redis cache
    Expected behavior: Runs once in the 'db' group (first matching fixture)
    """
    assert db["type"] == "database"
    assert redis["type"] == "redis"


def test_multiple_fixtures_redis_and_cache(redis, cache):
    """
    This test uses both 'redis' and 'cache' fixtures.

    When running: pytest --fixture-order db redis cache
    Expected behavior: Runs once in the 'redis' group (first matching fixture)
    """
    assert redis["type"] == "redis"
    assert cache["type"] == "cache"


def test_multiple_fixtures_all_three(db, redis, cache):
    """
    This test uses all three fixtures: 'db', 'redis', and 'cache'.

    When running: pytest --fixture-order db redis cache
    Expected behavior: Runs once in the 'db' group (first matching fixture)
    """
    assert db["type"] == "database"
    assert redis["type"] == "redis"
    assert cache["type"] == "cache"


# ============================================================================
# Edge Case 3: Tests without any tags/fixtures (unmatched)
# ============================================================================


def test_no_tags_or_fixtures():
    """
    This test has no tags and no fixtures.

    When running: pytest --tag-order fast slow --unmatched-order last
    Expected behavior: Runs after all tagged tests

    When running: pytest --tag-order fast slow --unmatched-order first
    Expected behavior: Runs before all tagged tests

    When running: pytest --tag-order fast slow --unmatched-order any
    Expected behavior: Runs in any order (default)
    """
    assert True


# ============================================================================
# Edge Case 4: Mixed scenarios
# ============================================================================


@pytest.mark.fast()
def test_fast_with_db_fixture(db):
    """
    This test has a 'fast' tag and uses the 'db' fixture.

    When running: pytest --tag-order fast slow
    Expected behavior: Runs in the 'fast' group

    When running: pytest --fixture-order db redis
    Expected behavior: Runs in the 'db' group
    """
    assert db["type"] == "database"


@pytest.mark.slow()
def test_slow_with_redis_fixture(redis):
    """
    This test has a 'slow' tag and uses the 'redis' fixture.

    When running: pytest --tag-order fast slow
    Expected behavior: Runs in the 'slow' group

    When running: pytest --fixture-order db redis
    Expected behavior: Runs in the 'redis' group
    """
    assert redis["type"] == "redis"


# ============================================================================
# Edge Case 5: Tests that demonstrate the "run once" guarantee
# ============================================================================


@pytest.mark.fast()
@pytest.mark.slow()
def test_guaranteed_run_once():
    """
    This test demonstrates that tests run only once, even with multiple tags.

    When running: pytest --tag-order fast slow integration
    Expected behavior:
    - Runs exactly once (not twice)
    - Runs in the 'fast' group
    - Does NOT run in the 'slow' group
    """
    # This test should only run once, not multiple times
    assert True


def test_guaranteed_run_once_fixtures(db, redis):
    """
    This test demonstrates that tests run only once, even with multiple fixtures.

    When running: pytest --fixture-order db redis cache
    Expected behavior:
    - Runs exactly once (not multiple times)
    - Runs in the 'db' group
    - Does NOT run in the 'redis' group
    """
    # This test should only run once, not multiple times
    assert db["type"] == "database"
    assert redis["type"] == "redis"


# ============================================================================
# Edge Case 6: Class-based tests with multiple tags/fixtures
# ============================================================================


@pytest.mark.fast()
class TestFastClass:
    """Test class with 'fast' tag."""

    def test_class_method_no_fixtures(self):
        """Class method without fixtures."""
        assert True

    def test_class_method_with_db(self, db):
        """Class method with db fixture."""
        assert db["type"] == "database"


@pytest.mark.slow()
class TestSlowClass:
    """Test class with 'slow' tag."""

    def test_class_method_with_redis(self, redis):
        """Class method with redis fixture."""
        assert redis["type"] == "redis"

    def test_class_method_with_cache(self, cache):
        """Class method with cache fixture."""
        assert cache["type"] == "cache"


@pytest.mark.fast()
@pytest.mark.slow()
class TestMultipleTagsClass:
    """Test class with multiple tags."""

    def test_class_method_multiple_tags(self):
        """
        Class method with multiple tags on the class.

        When running: pytest --tag-order fast slow
        Expected behavior: Runs in the 'fast' group (first matching tag)
        """
        assert True
