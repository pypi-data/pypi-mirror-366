"""Tests for the 'none' unmatched-order functionality."""

from pytest_conductor.core import (
    FixtureOrderingPlugin,
    MarkOrderingPlugin,
    UnmatchedOrder,
)


class TestUnmatchedNone:
    """Test that unmatched tests are filtered out when unmatched_order is NONE."""

    def test_mark_plugin_none_unmatched_order(self):
        """Test that mark plugin filters out unmatched
        tests when unmatched_order is NONE."""
        plugin = MarkOrderingPlugin(
            order_list=["fast", "slow"],
            unmatched_order=UnmatchedOrder.NONE,
        )

        # Create mock items
        class MockItem:
            def __init__(self, name, markers=None):
                self.name = name
                self._markers = markers or []

            def iter_markers(self):
                return self._markers

        class MockMarker:
            def __init__(self, name):
                self.name = name

        # Create test items with different marker combinations
        items = [
            MockItem("test_fast", [MockMarker("fast")]),
            MockItem("test_slow", [MockMarker("slow")]),
            MockItem("test_fast_and_slow", [MockMarker("fast"), MockMarker("slow")]),
            MockItem("test_unmatched", [MockMarker("other")]),  # Not in order list
            MockItem("test_no_markers", []),  # No markers at all
        ]

        # Sort items
        sorted_items = plugin.sort_items(items)

        # Should only include tests with matching markers
        assert len(sorted_items) == 3
        assert sorted_items[0].name == "test_fast"
        assert sorted_items[1].name == "test_fast_and_slow"
        assert sorted_items[2].name == "test_slow"

    def test_fixture_plugin_none_unmatched_order(self):
        """Test that fixture plugin filters out
        unmatched tests when unmatched_order is NONE."""
        plugin = FixtureOrderingPlugin(
            order_list=["db", "redis"],
            unmatched_order=UnmatchedOrder.NONE,
        )

        # Create mock items
        class MockItem:
            def __init__(self, name, fixtures=None):
                self.name = name
                self._fixtures = fixtures or []

            @property
            def function(self):
                class MockFunction:
                    def __init__(self, fixtures):
                        class MockCode:
                            def __init__(self, fixtures):
                                self.co_varnames = fixtures
                                self.co_argcount = len(fixtures)

                        self.__code__ = MockCode(fixtures)

                return MockFunction(self._fixtures)

        # Create test items with different fixture combinations
        items = [
            MockItem("test_db", ["db"]),
            MockItem("test_redis", ["redis"]),
            MockItem("test_db_and_redis", ["db", "redis"]),
            MockItem("test_other_fixture", ["cache"]),  # Not in order list
            MockItem("test_no_fixtures", []),  # No fixtures at all
        ]

        # Sort items
        sorted_items = plugin.sort_items(items)

        # Should only include tests with matching fixtures
        assert len(sorted_items) == 3
        assert sorted_items[0].name == "test_db"
        assert sorted_items[1].name == "test_db_and_redis"
        assert sorted_items[2].name == "test_redis"

    def test_none_vs_other_options(self):
        """Test that NONE behaves differently from other unmatched_order options."""
        # Test with NONE
        plugin_none = MarkOrderingPlugin(
            order_list=["fast"],
            unmatched_order=UnmatchedOrder.NONE,
        )

        # Test with ANY
        plugin_any = MarkOrderingPlugin(
            order_list=["fast"],
            unmatched_order=UnmatchedOrder.ANY,
        )

        # Create mock items
        class MockItem:
            def __init__(self, name, markers=None):
                self.name = name
                self._markers = markers or []

            def iter_markers(self):
                return self._markers

        class MockMarker:
            def __init__(self, name):
                self.name = name

        items = [
            MockItem("test_fast", [MockMarker("fast")]),
            MockItem("test_unmatched", [MockMarker("other")]),
        ]

        # NONE should filter out unmatched tests
        sorted_none = plugin_none.sort_items(items)
        assert len(sorted_none) == 1
        assert sorted_none[0].name == "test_fast"

        # ANY should include all tests
        sorted_any = plugin_any.sort_items(items)
        assert len(sorted_any) == 2
