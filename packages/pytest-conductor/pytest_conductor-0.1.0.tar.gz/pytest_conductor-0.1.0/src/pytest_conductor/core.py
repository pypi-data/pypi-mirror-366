"""Core functionality for pytest conductor plugin."""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

import pytest


class UnmatchedOrder(Enum):
    """Enum for handling unmatched tags."""

    ANY = "any"
    FIRST = "first"
    LAST = "last"
    NONE = "none"


class OrderingMode(Enum):
    """Enum for ordering mode."""

    MARK = "mark"
    FIXTURE = "fixture"


class BaseOrderingPlugin:
    """Base class for ordering plugins."""

    def __init__(
        self,
        order_list: Optional[List[str]] = None,
        unmatched_order: UnmatchedOrder = UnmatchedOrder.ANY,
    ):
        """
        Initialize the ordering plugin.

        Args:
            order_list: List of names in the order they should run
            unmatched_order: How to handle tests without matching items
        """
        self.order_list = order_list or []
        self.unmatched_order = unmatched_order
        self.name_to_index: Dict[str, int] = {
            name: idx for idx, name in enumerate(self.order_list)
        }

    def get_test_order_key(self, item: pytest.Item) -> Tuple[int, str]:
        """
        Get the ordering key for a test item.

        Args:
            item: The pytest test item

        Returns:
            Tuple of (order_index, test_name) for sorting
        """
        # Extract names from the test item
        names = self._extract_names(item)

        if not names:
            # No names found, handle based on unmatched_order setting
            if self.unmatched_order == UnmatchedOrder.FIRST:
                return (-1, item.name)
            if self.unmatched_order == UnmatchedOrder.LAST:
                return (len(self.order_list), item.name)
            return (0, item.name)

        # Find the highest priority name (lowest index) for this test
        min_index = min(
            self.name_to_index.get(name, len(self.order_list)) for name in names
        )

        return (min_index, item.name)

    def _extract_names(self, item: pytest.Item) -> Set[str]:
        """
        Extract names from a pytest test item. To be implemented by subclasses.

        Args:
            item: The pytest test item

        Returns:
            Set of names found on the test
        """
        raise NotImplementedError

    def sort_items(self, items: List[pytest.Item]) -> List[pytest.Item]:
        """
        Sort test items based on order list.

        Args:
            items: List of pytest test items

        Returns:
            Sorted list of test items
        """
        if self.unmatched_order == UnmatchedOrder.NONE:
            # Filter out unmatched tests when NONE is specified
            matched_items = []
            for item in items:
                names = self._extract_names(item)
                if names and any(name in self.name_to_index for name in names):
                    matched_items.append(item)
            return sorted(matched_items, key=self.get_test_order_key)
        return sorted(items, key=self.get_test_order_key)


class MarkOrderingPlugin(BaseOrderingPlugin):
    """Plugin for ordering pytest tests by marks/tags."""

    def _extract_names(self, item: pytest.Item) -> Set[str]:
        """
        Extract mark names from a pytest test item.

        Args:
            item: The pytest test item

        Returns:
            Set of mark names found on the test
        """
        names = set()

        # Check for markers (pytest.mark)
        for marker in item.iter_markers():
            if marker.name not in ["parametrize", "skip", "xfail", "filterwarnings"]:
                names.add(marker.name)

        return names


class FixtureOrderingPlugin(BaseOrderingPlugin):
    """Plugin for ordering pytest tests by fixtures."""

    def _extract_names(self, item: pytest.Item) -> Set[str]:
        """
        Extract fixture names from a pytest test item.

        Args:
            item: The pytest test item

        Returns:
            Set of fixture names found on the test
        """
        names = set()

        # Get the function signature to find fixture parameters
        if hasattr(item, "function") and hasattr(item.function, "__code__"):
            # Get parameter names from the function
            param_names = item.function.__code__.co_varnames[
                : item.function.__code__.co_argcount
            ]

            # Filter out 'self' and 'cls' parameters
            fixture_names = [name for name in param_names if name not in ["self", "cls"]]
            names.update(fixture_names)

        return names


def pytest_configure(config: pytest.Config) -> None:
    """Configure the plugin with command line options."""
    config.addinivalue_line(
        "markers",
        "conductor: mark tests with tags for ordering",
    )


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command line options for test ordering."""
    group = parser.getgroup("conductor")

    group.addoption(
        "--tag-order",
        action="store",
        nargs="+",
        help="Order of tags for test execution (e.g., --tag-order fast slow integration)",
    )

    group.addoption(
        "--fixture-order",
        action="store",
        nargs="+",
        help="Order of fixtures for test execution "
        "(e.g., --fixture-order db redis cache)",
    )

    group.addoption(
        "--ordering-mode",
        action="store",
        choices=["mark", "fixture"],
        default="mark",
        help="Ordering mode: mark (for tags) or fixture (for fixtures)",
    )

    group.addoption(
        "--unmatched-order",
        action="store",
        choices=["any", "first", "last", "none"],
        default="any",
        help="How to handle tests without matching tags/fixtures: "
        "any, first, last, or none (skip unmatched tests)",
    )


def _validate_fixture_availability(
    items: List[pytest.Item],
    fixture_order: List[str],
) -> None:
    """
    Validate that all fixtures in the order list are available to all tests.

    Args:
        items: List of collected test items
        fixture_order: List of fixture names to validate

    Raises:
        ValueError: If any fixture is not available to all tests
    """
    if not fixture_order:
        return

    # Get all available fixtures from the collected test items
    available_fixtures = set()

    # Collect fixtures from all test items to see what's actually available
    for item in items:
        if hasattr(item, "function") and hasattr(item.function, "__code__"):
            param_names = item.function.__code__.co_varnames[
                : item.function.__code__.co_argcount
            ]
            available_fixtures.update(
                name for name in param_names if name not in ["self", "cls"]
            )

    # Also check pytest's built-in fixtures
    builtin_fixtures = {
        "tmp_path",
        "tmp_path_factory",
        "tmpdir",
        "tmpdir_factory",
        "capsys",
        "capsysbinary",
        "capfd",
        "capfdbinary",
        "capteesys",
        "caplog",
        "monkeypatch",
        "recwarn",
        "pytestconfig",
        "record_property",
        "record_testsuite_property",
        "record_xml_attribute",
        "cache",
        "doctest_namespace",
    }
    available_fixtures.update(builtin_fixtures)

    # Check which fixtures from the order list are not available
    unavailable_fixtures = set(fixture_order) - available_fixtures

    if unavailable_fixtures:
        raise ValueError(
            f"Fixtures not available to all tests: {', '.join(unavailable_fixtures)}. "
            f"Fixture ordering requires all fixtures to be globally available. "
            f"Make sure these fixtures are defined in a conftest.py file that is "
            f"accessible to all tests, or use mark ordering instead.",
        )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: List[pytest.Item],
) -> None:
    """Modify the collection order based on test ordering."""
    tag_order = config.getoption("--tag-order")
    fixture_order = config.getoption("--fixture-order")
    ordering_mode = OrderingMode(config.getoption("--ordering-mode"))
    unmatched_order_str = config.getoption("--unmatched-order")

    # Determine which order to use based on mode and provided options
    order_list = tag_order if ordering_mode == OrderingMode.MARK else fixture_order

    if not order_list:
        return  # No ordering specified

    unmatched_order = UnmatchedOrder(unmatched_order_str)

    # Validate fixture availability for fixture ordering mode
    if ordering_mode == OrderingMode.FIXTURE:
        _validate_fixture_availability(items, fixture_order)

    # Create appropriate plugin based on mode
    if ordering_mode == OrderingMode.MARK:
        plugin = MarkOrderingPlugin(
            order_list=order_list,
            unmatched_order=unmatched_order,
        )
    else:  # OrderingMode.FIXTURE
        plugin = FixtureOrderingPlugin(
            order_list=order_list,
            unmatched_order=unmatched_order,
        )

    # Sort the items
    sorted_items = plugin.sort_items(items)

    # Replace the items list with the sorted version
    items[:] = sorted_items
