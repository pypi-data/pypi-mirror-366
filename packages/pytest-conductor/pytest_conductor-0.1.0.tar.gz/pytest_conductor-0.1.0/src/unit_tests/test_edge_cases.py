"""Tests for edge cases in the pytest conductor plugin."""

from pytest_conductor.core import (
    FixtureOrderingPlugin,
    MarkOrderingPlugin,
    UnmatchedOrder,
)


class TestMultipleTagsEdgeCase:
    """Test edge cases with multiple tags."""

    def test_multiple_tags_priority_order(self):
        """Test that tests with multiple tags run with the first matching tag."""
        plugin = MarkOrderingPlugin(
            order_list=["fast", "slow", "integration"],
            unmatched_order=UnmatchedOrder.LAST,
        )

        # Create a mock item with multiple tags
        class MockItem:
            def __init__(self, name):
                self.name = name

            def iter_markers(self):
                class MockMarker:
                    def __init__(self, name):
                        self.name = name

                # This test has both 'slow' and 'integration' tags
                # 'slow' should take priority since it comes first in order_list
                return [MockMarker("slow"), MockMarker("integration")]

        item = MockItem("test_multiple_tags")

        # Extract names and verify both tags are found
        names = plugin._extract_names(item)
        assert names == {"slow", "integration"}

        # Get order key and verify it uses the first matching tag (slow = index 1)
        order_key = plugin.get_test_order_key(item)
        assert order_key[0] == 1  # 'slow' is at index 1 in order_list


class TestMultipleFixturesEdgeCase:
    """Test edge cases with multiple fixtures."""

    def test_multiple_fixtures_priority_order(self):
        """Test that tests with multiple fixtures run with the first matching fixture."""
        plugin = FixtureOrderingPlugin(
            order_list=["db", "redis", "cache"],
            unmatched_order=UnmatchedOrder.LAST,
        )

        # Create a mock item with multiple fixtures
        class MockItem:
            def __init__(self, name):
                self.name = name

        class MockFunction:
            def __init__(self):
                class MockCode:
                    # This test uses both 'redis' and 'cache' fixtures
                    # 'redis' should take priority since it comes first in order_list
                    co_varnames = ("redis", "cache", "api")
                    co_argcount = 3

                self.__code__ = MockCode()

        item = MockItem("test_multiple_fixtures")
        item.function = MockFunction()

        # Extract names and verify all fixtures are found
        names = plugin._extract_names(item)
        assert names == {"redis", "cache", "api"}

        # Get order key and verify it uses the first matching fixture (redis = index 1)
        order_key = plugin.get_test_order_key(item)
        assert order_key[0] == 1  # 'redis' is at index 1 in order_list


class TestConftestFixtures:
    """Test handling of conftest fixtures."""

    def test_conftest_fixture_detection(self):
        """Test that fixtures from conftest.py are detected."""
        plugin = FixtureOrderingPlugin(
            order_list=["conftest_db", "conftest_redis"],
            unmatched_order=UnmatchedOrder.LAST,
        )

        # Create a mock item that uses a conftest fixture
        class MockItem:
            def __init__(self, name):
                self.name = name

        class MockFunction:
            def __init__(self):
                class MockCode:
                    # This test uses a fixture that might be defined in conftest.py
                    co_varnames = ("conftest_db", "local_fixture")
                    co_argcount = 2

                self.__code__ = MockCode()

        item = MockItem("test_conftest_fixture")
        item.function = MockFunction()

        # Extract names - should detect conftest fixtures the same as regular fixtures
        names = plugin._extract_names(item)
        assert names == {"conftest_db", "local_fixture"}

        # Get order key and verify it uses the conftest fixture
        order_key = plugin.get_test_order_key(item)
        assert order_key[0] == 0  # 'conftest_db' is at index 0 in order_list


class TestUnmatchedHandling:
    """Test handling of unmatched tests."""

    def test_unmatched_tests_first(self):
        """Test that unmatched tests run first when configured."""
        plugin = MarkOrderingPlugin(
            order_list=["fast", "slow"],
            unmatched_order=UnmatchedOrder.FIRST,
        )

        class MockItem:
            def __init__(self, name):
                self.name = name

            def iter_markers(self):
                return []  # No markers

        item = MockItem("test_no_tags")

        # Extract names - should be empty
        names = plugin._extract_names(item)
        assert names == set()

        # Get order key - should be -1 for first priority
        order_key = plugin.get_test_order_key(item)
        assert order_key[0] == -1

    def test_unmatched_tests_last(self):
        """Test that unmatched tests run last when configured."""
        plugin = MarkOrderingPlugin(
            order_list=["fast", "slow"],
            unmatched_order=UnmatchedOrder.LAST,
        )

        class MockItem:
            def __init__(self, name):
                self.name = name

            def iter_markers(self):
                return []  # No markers

        item = MockItem("test_no_tags")

        # Get order key - should be len(order_list) for last priority
        order_key = plugin.get_test_order_key(item)
        assert order_key[0] == 2  # len(["fast", "slow"]) = 2

    def test_unmatched_tests_any(self):
        """Test that unmatched tests run in any order when configured."""
        plugin = MarkOrderingPlugin(
            order_list=["fast", "slow"],
            unmatched_order=UnmatchedOrder.ANY,
        )

        class MockItem:
            def __init__(self, name):
                self.name = name

            def iter_markers(self):
                return []  # No markers

        item = MockItem("test_no_tags")

        # Get order key - should be 0 for any order
        order_key = plugin.get_test_order_key(item)
        assert order_key[0] == 0


class TestIntegrationEdgeCases:
    """Integration tests for edge cases."""

    def test_sorting_with_multiple_tags(self):
        """Test that sorting works correctly with multiple tags."""
        plugin = MarkOrderingPlugin(
            order_list=["fast", "slow", "integration"],
            unmatched_order=UnmatchedOrder.LAST,
        )

        # Create multiple test items with different tag combinations
        class MockItem:
            def __init__(self, name, markers):
                self.name = name
                self._markers = markers

            def iter_markers(self):
                class MockMarker:
                    def __init__(self, name):
                        self.name = name

                return [MockMarker(m) for m in self._markers]

        items = [
            MockItem("test_fast_only", ["fast"]),
            MockItem("test_slow_and_integration", ["slow", "integration"]),
            MockItem("test_integration_only", ["integration"]),
            MockItem("test_no_tags", []),
            MockItem("test_fast_and_slow", ["fast", "slow"]),
        ]

        # Sort the items
        sorted_items = plugin.sort_items(items)

        # Verify order: fast tests first, then slow, then integration, then unmatched
        # Within same priority, tests are sorted alphabetically by name
        expected_order = [
            "test_fast_and_slow",  # fast (index 0) - alphabetically first
            "test_fast_only",  # fast (index 0) - alphabetically second
            "test_slow_and_integration",  # slow (index 1) - uses first matching tag
            "test_integration_only",  # integration (index 2)
            "test_no_tags",  # unmatched (index 3)
        ]

        actual_order = [item.name for item in sorted_items]
        assert actual_order == expected_order

    def test_sorting_with_multiple_fixtures(self):
        """Test that sorting works correctly with multiple fixtures."""
        plugin = FixtureOrderingPlugin(
            order_list=["db", "redis", "cache"],
            unmatched_order=UnmatchedOrder.LAST,
        )

        # Create multiple test items with different fixture combinations
        class MockItem:
            def __init__(self, name, fixtures):
                self.name = name
                self._fixtures = fixtures

        class MockFunction:
            def __init__(self, fixtures):
                class MockCode:
                    def __init__(self, fixtures):
                        self.co_varnames = fixtures
                        self.co_argcount = len(fixtures)

                self.__code__ = MockCode(fixtures)

        items = [
            MockItem("test_db_only", ["db"]),
            MockItem("test_redis_and_cache", ["redis", "cache"]),
            MockItem("test_cache_only", ["cache"]),
            MockItem("test_no_fixtures", []),
            MockItem("test_db_and_redis", ["db", "redis"]),
        ]

        # Add function attributes to items
        for item in items:
            if item._fixtures:
                item.function = MockFunction(item._fixtures)

        # Sort the items
        sorted_items = plugin.sort_items(items)

        # Verify order: db tests first, then redis, then cache, then unmatched
        # Within same priority, tests are sorted alphabetically by name
        expected_order = [
            "test_db_and_redis",  # db (index 0) - alphabetically first
            "test_db_only",  # db (index 0) - alphabetically second
            "test_redis_and_cache",  # redis (index 1) - uses first matching fixture
            "test_cache_only",  # cache (index 2)
            "test_no_fixtures",  # unmatched (index 3)
        ]

        actual_order = [item.name for item in sorted_items]
        assert actual_order == expected_order
