"""Integration tests for pytest-conductor demonstrating all features with logging."""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

import pytest


class TestPytestConductorIntegration:
    """Integration tests that demonstrate pytest-conductor features."""

    @pytest.fixture()
    def project_root(self) -> Path:
        """Get the pytest-conductor project root directory."""
        # Navigate up from src/integration_tests to the main project root
        current = Path(__file__).parent
        return current.parent.parent

    @pytest.fixture()
    def example_dir(self) -> Path:
        """Get the example directory."""
        return Path(__file__).parent.parent.parent / "example"

    def run_pytest_with_logging(
        self,
        args: List[str],
        cwd: Path,
        description: str,
    ) -> Tuple[subprocess.CompletedProcess, float]:
        """Run pytest with timing and logging."""
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"📁 Working directory: {cwd}")
        print(f"🔧 Command: pytest {' '.join(args)}")
        print(f"{'='*60}")

        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pytest"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(cwd)},
        )
        end_time = time.time()

        print(f"⏱️  Execution time: {end_time - start_time:.2f} seconds")
        print(f"📊 Exit code: {result.returncode}")

        if result.stdout:
            print(f"📤 STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"📤 STDERR:\n{result.stderr}")

        print(f"{'='*60}\n")
        return result, end_time - start_time

    def test_build_and_install_package(self):
        """Test building and installing the pytest-conductor package locally."""
        pytest.skip("Build test temporarily disabled - requires build tools")

        # This test would normally:
        # 1. Build the package using hatch build
        # 2. Find the wheel file in dist/
        # 3. Install it in the example directory
        # 4. Verify the plugin works in the example project

    def test_basic_tag_ordering(self, example_dir: Path):
        """Test basic tag ordering functionality."""
        result, duration = self.run_pytest_with_logging(
            ["--tag-order", "fast", "slow", "integration", "-v"],
            example_dir,
            "Basic Tag Ordering: fast → slow → integration",
        )

        assert result.returncode == 0, "Basic tag ordering should succeed"
        assert duration < 10, "Test should complete quickly"

        # Verify order in output
        output_lines = result.stdout.split("\n")
        test_lines = [
            line for line in output_lines if "test_" in line and "PASSED" in line
        ]

        # Check that fast tests come before slow tests
        fast_tests = [line for line in test_lines if "fast" in line.lower()]
        slow_tests = [line for line in test_lines if "slow" in line.lower()]

        if fast_tests and slow_tests:
            first_fast_idx = test_lines.index(fast_tests[0])
            first_slow_idx = test_lines.index(slow_tests[0])
            assert (
                first_fast_idx < first_slow_idx
            ), "Fast tests should run before slow tests"

    def test_fixture_ordering(self, example_dir: Path):
        """Test fixture ordering functionality."""
        result, duration = self.run_pytest_with_logging(
            [
                "--fixture-order",
                "basic_calculator",
                "advanced_calculator",
                "sample_data",
                "--ordering-mode",
                "fixture",
                "-v",
            ],
            example_dir,
            "Fixture Ordering: basic_calculator → advanced_calculator → sample_data",
        )

        assert result.returncode == 0, "Fixture ordering should succeed"
        assert duration < 10, "Test should complete quickly"

    def test_unmatched_order_first(self, example_dir: Path):
        """Test unmatched tests running first."""
        result, duration = self.run_pytest_with_logging(
            ["--tag-order", "fast", "slow", "--unmatched-order", "first", "-v"],
            example_dir,
            "Unmatched Order FIRST: untagged tests run first",
        )

        assert result.returncode == 0, "Unmatched order first should succeed"

        # Verify that untagged tests run first
        output_lines = result.stdout.split("\n")
        test_lines = [
            line for line in output_lines if "test_" in line and "PASSED" in line
        ]

        # Find test_no_tags tests (these should be first)
        no_tag_tests = [line for line in test_lines if "test_no_tags" in line]
        if no_tag_tests:
            first_no_tag_idx = test_lines.index(no_tag_tests[0])
            # Check that no_tag tests come before tagged tests
            for line in test_lines:
                if "fast" in line.lower() or "slow" in line.lower():
                    tagged_idx = test_lines.index(line)
                    assert (
                        first_no_tag_idx < tagged_idx
                    ), "Untagged tests should run first"

    def test_unmatched_order_last(self, example_dir: Path):
        """Test unmatched tests running last."""
        result, duration = self.run_pytest_with_logging(
            ["--tag-order", "fast", "slow", "--unmatched-order", "last", "-v"],
            example_dir,
            "Unmatched Order LAST: untagged tests run last",
        )

        assert result.returncode == 0, "Unmatched order last should succeed"

        # Verify that untagged tests run last
        output_lines = result.stdout.split("\n")
        test_lines = [
            line for line in output_lines if "test_" in line and "PASSED" in line
        ]

        # Find test_no_tags tests (these should be last)
        no_tag_tests = [line for line in test_lines if "test_no_tags" in line]
        if no_tag_tests:
            last_no_tag_idx = test_lines.index(no_tag_tests[-1])
            # Check that no_tag tests come after tagged tests
            for line in test_lines:
                if "fast" in line.lower() or "slow" in line.lower():
                    tagged_idx = test_lines.index(line)
                    assert (
                        tagged_idx < last_no_tag_idx
                    ), "Tagged tests should run before untagged tests"

    def test_unmatched_order_none(self, example_dir: Path):
        """Test unmatched tests being skipped."""
        result, duration = self.run_pytest_with_logging(
            ["--tag-order", "fast", "slow", "--unmatched-order", "none", "-v"],
            example_dir,
            "Unmatched Order NONE: untagged tests are skipped",
        )

        assert result.returncode == 0, "Unmatched order none should succeed"

        # Verify that untagged tests are not run
        output_lines = result.stdout.split("\n")
        test_lines = [
            line for line in output_lines if "test_" in line and "PASSED" in line
        ]

        # Check that no test_no_tags tests are in the output
        no_tag_tests = [line for line in test_lines if "test_no_tags" in line]
        assert len(no_tag_tests) == 0, "Untagged tests should be skipped"

    def test_fixture_scope_error(self, example_dir: Path):
        """Test that fixture scope error is properly raised."""
        result, duration = self.run_pytest_with_logging(
            [
                "--fixture-order",
                "nonexistent_fixture",
                "--ordering-mode",
                "fixture",
                "-v",
            ],
            example_dir,
            "Fixture Scope Error: non-existent fixture should cause error",
        )

        assert result.returncode != 0, "Fixture scope error should cause failure"
        assert "Fixtures not available to all tests: nonexistent_fixture" in result.stdout

    def test_mixed_tag_and_fixture_ordering(self, example_dir: Path):
        """Test ordering with both tags and fixtures."""
        result, duration = self.run_pytest_with_logging(
            [
                "--tag-order",
                "fast",
                "slow",
                "--fixture-order",
                "basic_calculator",
                "advanced_calculator",
                "--ordering-mode",
                "mark",
                "-v",
            ],
            example_dir,
            "Mixed Ordering: tags (mark mode) with fixture order specified",
        )

        assert result.returncode == 0, "Mixed ordering should succeed"

        # In mark mode, fixture-order should be ignored,
        # so this should work like tag ordering
        output_lines = result.stdout.split("\n")
        test_lines = [
            line for line in output_lines if "test_" in line and "PASSED" in line
        ]

        # Should see fast tests before slow tests
        fast_tests = [line for line in test_lines if "fast" in line.lower()]
        slow_tests = [line for line in test_lines if "slow" in line.lower()]

        if fast_tests and slow_tests:
            first_fast_idx = test_lines.index(fast_tests[0])
            first_slow_idx = test_lines.index(slow_tests[0])
            assert (
                first_fast_idx < first_slow_idx
            ), "Fast tests should run before slow tests in mark mode"

    def test_complex_ordering_scenario(self, example_dir: Path):
        """Test a complex ordering scenario with multiple tags and fixtures."""
        result, duration = self.run_pytest_with_logging(
            [
                "--tag-order",
                "unit",
                "integration",
                "fast",
                "slow",
                "--unmatched-order",
                "last",
                "-v",
            ],
            example_dir,
            "Complex Ordering: unit → integration → fast → slow → untagged",
        )

        assert result.returncode == 0, "Complex ordering should succeed"

        # Verify the order: unit tests first, then integration,
        # then fast/slow, then untagged
        output_lines = result.stdout.split("\n")
        test_lines = [
            line for line in output_lines if "test_" in line and "PASSED" in line
        ]

        # Find indices of different test types
        unit_tests = [line for line in test_lines if "unit" in line.lower()]
        integration_tests = [line for line in test_lines if "integration" in line.lower()]
        no_tag_tests = [line for line in test_lines if "test_no_tags" in line]

        if unit_tests and integration_tests:
            first_unit_idx = test_lines.index(unit_tests[0])
            first_integration_idx = test_lines.index(integration_tests[0])
            assert (
                first_unit_idx < first_integration_idx
            ), "Unit tests should run before integration tests"

        if integration_tests and no_tag_tests:
            last_integration_idx = test_lines.index(integration_tests[-1])
            first_no_tag_idx = test_lines.index(no_tag_tests[0])
            assert (
                last_integration_idx < first_no_tag_idx
            ), "Integration tests should run before untagged tests"

    def test_performance_comparison(self, example_dir: Path):
        """Test performance comparison between ordered and unordered execution."""
        print("\n⚡ Performance Comparison Test")

        # Run without ordering
        unordered_result, unordered_duration = self.run_pytest_with_logging(
            ["-v"],
            example_dir,
            "Unordered Execution (baseline)",
        )

        # Run with ordering
        ordered_result, ordered_duration = self.run_pytest_with_logging(
            [
                "--tag-order",
                "fast",
                "slow",
                "integration",
                "--unmatched-order",
                "last",
                "-v",
            ],
            example_dir,
            "Ordered Execution",
        )

        assert unordered_result.returncode == 0, "Unordered execution should succeed"
        assert ordered_result.returncode == 0, "Ordered execution should succeed"

        # Calculate overhead
        overhead = ordered_duration - unordered_duration
        overhead_percentage = (
            (overhead / unordered_duration) * 100 if unordered_duration > 0 else 0
        )

        print("📊 Performance Results:")
        print(f"   Unordered: {unordered_duration:.3f}s")
        print(f"   Ordered:   {ordered_duration:.3f}s")
        print(f"   Overhead:  {overhead:.3f}s ({overhead_percentage:.1f}%)")

        # Ordering overhead should be minimal (< 50% increase)
        assert (
            overhead_percentage < 50
        ), f"Ordering overhead too high: {overhead_percentage:.1f}%"

    def test_help_output(self, example_dir: Path):
        """Test that help output shows all pytest-conductor options."""
        result, duration = self.run_pytest_with_logging(
            ["--help"],
            example_dir,
            "Help Output: Verify pytest-conductor options are shown",
        )

        assert result.returncode == 0, "Help should succeed"

        help_output = result.stdout
        expected_options = [
            "--tag-order",
            "--fixture-order",
            "--ordering-mode",
            "--unmatched-order",
        ]

        for option in expected_options:
            assert option in help_output, f"Help should include {option}"

    def test_collection_with_ordering(self, example_dir: Path):
        """Test that collection works correctly with ordering enabled."""
        result, duration = self.run_pytest_with_logging(
            ["--tag-order", "fast", "slow", "--collect-only", "-v"],
            example_dir,
            "Collection Test: Verify tests are collected in correct order",
        )

        assert result.returncode == 0, "Collection should succeed"

        # Verify that collection output shows the correct order
        output_lines = result.stdout.split("\n")
        collect_lines = [line for line in output_lines if "<Function test_" in line]

        # Should have collected tests
        assert len(collect_lines) > 0, "Should collect some tests"

        # Check that fast tests are listed before slow tests in collection
        fast_collect = [line for line in collect_lines if "fast" in line.lower()]
        slow_collect = [line for line in collect_lines if "slow" in line.lower()]

        if fast_collect and slow_collect:
            first_fast_idx = collect_lines.index(fast_collect[0])
            first_slow_idx = collect_lines.index(slow_collect[0])
            assert (
                first_fast_idx < first_slow_idx
            ), "Fast tests should be collected before slow tests"
