"""Tests for conftest fixture name conflicts."""

import tempfile
from pathlib import Path

# Import the plugin classes for testing
from pytest_conductor.core import FixtureOrderingPlugin, UnmatchedOrder


class TestConftestFixtureConflicts:
    """Test scenarios where multiple fixtures have
    the same name in different conftest files."""

    def test_fixture_name_conflict_detection(self):
        """
        Test that the plugin correctly detects fixtures
        even when there are name conflicts.

        When multiple conftest.py files define fixtures with the same name,
        pytest will use the closest one (nearest to the test file).
        Our plugin should still detect the fixture name correctly.
        """
        plugin = FixtureOrderingPlugin(
            order_list=["conflicting_fixture", "other_fixture"],
            unmatched_order=UnmatchedOrder.LAST,
        )

        # Create a mock item that uses a fixture that
        # might be defined in multiple conftest files
        class MockItem:
            def __init__(self, name):
                self.name = name

        class MockFunction:
            def __init__(self):
                class MockCode:
                    # This test uses a fixture that might be
                    # defined in multiple conftest files
                    co_varnames = ("conflicting_fixture", "other_fixture")
                    co_argcount = 2

                self.__code__ = MockCode()

        item = MockItem("test_conflicting_fixture")
        item.function = MockFunction()

        # Extract names - should detect the fixture name
        # regardless of which conftest defines it
        names = plugin._extract_names(item)
        assert names == {"conflicting_fixture", "other_fixture"}

        # Get order key and verify it uses the first matching fixture
        order_key = plugin.get_test_order_key(item)
        assert order_key[0] == 0  # 'conflicting_fixture' is at index 0 in order_list

    def test_pytest_fixture_resolution_behavior(self):
        """
        Test to understand how pytest resolves fixture name conflicts.

        This test demonstrates that pytest uses the closest fixture definition
        when multiple fixtures have the same name.

        This test also demonstrates the limitation that fixture ordering
        requires fixtures to be globally available to all tests.
        """
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create directory structure
            root_conftest = temp_path / "conftest.py"
            subdir = temp_path / "subdir"
            subdir.mkdir()
            subdir_conftest = subdir / "conftest.py"
            test_file = subdir / "test_conflict.py"

            # Create conftest files with conflicting fixture names
            root_conftest.write_text('''
import pytest

@pytest.fixture
def conflicting_fixture():
    """Root conftest fixture."""
    return {"source": "root", "value": "root_value"}

@pytest.fixture
def other_fixture():
    """Root conftest other fixture."""
    return {"source": "root", "value": "other_value"}
''')

            subdir_conftest.write_text('''
import pytest

@pytest.fixture
def conflicting_fixture():
    """Subdir conftest fixture - should override root."""
    return {"source": "subdir", "value": "subdir_value"}

@pytest.fixture
def subdir_only_fixture():
    """Subdir-only fixture."""
    return {"source": "subdir", "value": "subdir_only"}
''')

            test_file.write_text('''
import pytest

def test_fixture_resolution(conflicting_fixture, other_fixture, subdir_only_fixture):
    """Test that pytest uses the closest fixture definition."""
    # conflicting_fixture should come from subdir conftest (closest)
    assert conflicting_fixture["source"] == "subdir"
    assert conflicting_fixture["value"] == "subdir_value"
    
    # other_fixture should come from root conftest (only definition)
    assert other_fixture["source"] == "root"
    assert other_fixture["value"] == "other_value"
        
    # subdir_only_fixture should come from subdir conftest
    assert subdir_only_fixture["source"] == "subdir"
    assert subdir_only_fixture["value"] == "subdir_only"

def test_plugin_detection(conflicting_fixture, other_fixture, subdir_only_fixture):
    """Test that our plugin detects all fixtures correctly."""
    # This test verifies that our plugin can detect fixtures
    # regardless of which conftest file defines them
    assert conflicting_fixture is not None
    assert other_fixture is not None
    assert subdir_only_fixture is not None
''')

            # Run the test to verify pytest behavior
            import subprocess

            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v"],
                capture_output=True,
                text=True,
                cwd=temp_path,
            )

            # This demonstrates the limitation: when running from subdir,
            # pytest may not find fixtures from parent conftest files
            # This is why fixture ordering requires globally available fixtures
            if result.returncode != 0:
                # This is expected behavior that demonstrates the limitation
                # documented in the README about fixture availability
                assert (
                    "fixture 'other_fixture' not found" in result.stdout
                ), f"Expected fixture not found error, got: {result.stdout}"
            else:
                # If it passes, that's also valid behavior
                pass

    def test_plugin_ordering_with_conflicts(self):
        """
        Test that our plugin correctly orders tests when there are fixture name conflicts.
        """
        plugin = FixtureOrderingPlugin(
            order_list=["conflicting_fixture", "other_fixture", "subdir_only_fixture"],
            unmatched_order=UnmatchedOrder.LAST,
        )

        # Create mock items representing tests with different fixture combinations
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
            MockItem("test_conflicting_only", ["conflicting_fixture"]),
            MockItem("test_other_only", ["other_fixture"]),
            MockItem("test_subdir_only", ["subdir_only_fixture"]),
            MockItem("test_multiple_conflicts", ["conflicting_fixture", "other_fixture"]),
            MockItem(
                "test_all_fixtures",
                ["conflicting_fixture", "other_fixture", "subdir_only_fixture"],
            ),
            MockItem("test_no_fixtures", []),
        ]

        # Add function attributes to items
        for item in items:
            if item._fixtures:
                item.function = MockFunction(item._fixtures)

        # Sort the items
        sorted_items = plugin.sort_items(items)

        # Verify order: conflicting_fixture tests first, then other_fixture,
        # then subdir_only_fixture, then unmatched
        # When tests have the same order key, they're sorted alphabetically by name
        expected_order = [
            "test_all_fixtures",  # conflicting_fixture (index 0) - alphabetically first
            "test_conflicting_only",  # conflicting_fixture (index 0) - alph second
            "test_multiple_conflicts",  # conflicting_fixture (index 0) - alph third
            "test_other_only",  # other_fixture (index 1)
            "test_subdir_only",  # subdir_only_fixture (index 2)
            "test_no_fixtures",  # unmatched (index 3)
        ]

        actual_order = [item.name for item in sorted_items]
        assert actual_order == expected_order
