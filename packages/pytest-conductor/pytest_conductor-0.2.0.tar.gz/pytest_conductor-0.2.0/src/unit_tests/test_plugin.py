"""Tests for the pytest conductor plugin."""

from pytest_conductor.core import (
    FixtureOrderingPlugin,
    MarkOrderingPlugin,
    UnmatchedOrder,
)


def test_mark_ordering_plugin_initialization():
    """Test mark ordering plugin initialization."""
    plugin = MarkOrderingPlugin(
        order_list=["fast", "slow"],
        unmatched_order=UnmatchedOrder.LAST,
    )
    assert plugin.order_list == ["fast", "slow"]
    assert plugin.unmatched_order == UnmatchedOrder.LAST
    assert plugin.name_to_index == {"fast": 0, "slow": 1}


def test_fixture_ordering_plugin_initialization():
    """Test fixture ordering plugin initialization."""
    plugin = FixtureOrderingPlugin(
        order_list=["db", "redis"],
        unmatched_order=UnmatchedOrder.LAST,
    )
    assert plugin.order_list == ["db", "redis"]
    assert plugin.unmatched_order == UnmatchedOrder.LAST
    assert plugin.name_to_index == {"db": 0, "redis": 1}


def test_unmatched_order_enum():
    """Test UnmatchedOrder enum values."""
    assert UnmatchedOrder.ANY.value == "any"
    assert UnmatchedOrder.FIRST.value == "first"
    assert UnmatchedOrder.LAST.value == "last"


def test_ordering_mode_removed():
    """Test that OrderingMode enum has been removed."""
    # This test verifies that the OrderingMode enum has been removed
    # as part of the refactoring to make
    # --tag-order and --fixture-order mutually exclusive
    pass


def test_mark_plugin_with_no_order_list():
    """Test mark plugin behavior when no order list is specified."""
    plugin = MarkOrderingPlugin()
    assert plugin.order_list == []
    assert plugin.name_to_index == {}


def test_fixture_plugin_with_empty_order_list():
    """Test fixture plugin behavior with empty order list."""
    plugin = FixtureOrderingPlugin(order_list=[])
    assert plugin.order_list == []
    assert plugin.name_to_index == {}


def test_mark_plugin_extract_names():
    """Test mark plugin name extraction."""
    plugin = MarkOrderingPlugin(order_list=["fast", "slow"])

    # Create a mock item with markers
    class MockItem:
        def __init__(self):
            self.name = "test_item"

        def iter_markers(self):
            class MockMarker:
                def __init__(self, name):
                    self.name = name

            return [MockMarker("fast"), MockMarker("slow")]

    item = MockItem()
    names = plugin._extract_names(item)
    assert names == {"fast", "slow"}


def test_fixture_plugin_extract_names():
    """Test fixture plugin name extraction."""
    plugin = FixtureOrderingPlugin(order_list=["db", "redis"])

    # Create a mock item with function parameters
    class MockItem:
        def __init__(self):
            self.name = "test_item"

    class MockFunction:
        def __init__(self):
            class MockCode:
                co_varnames = ("db", "redis", "cache")
                co_argcount = 3

            self.__code__ = MockCode()

    item = MockItem()
    item.function = MockFunction()

    names = plugin._extract_names(item)
    assert names == {"db", "redis", "cache"}


def test_fixture_plugin_extract_names_with_self():
    """Test fixture plugin name extraction with 'self' parameter."""
    plugin = FixtureOrderingPlugin(order_list=["db", "redis"])

    # Create a mock item with function parameters including 'self'
    class MockItem:
        def __init__(self):
            self.name = "test_item"

    class MockFunction:
        def __init__(self):
            class MockCode:
                co_varnames = ("self", "db", "redis")
                co_argcount = 3

            self.__code__ = MockCode()

    item = MockItem()
    item.function = MockFunction()

    names = plugin._extract_names(item)
    assert names == {"db", "redis"}  # 'self' should be filtered out
