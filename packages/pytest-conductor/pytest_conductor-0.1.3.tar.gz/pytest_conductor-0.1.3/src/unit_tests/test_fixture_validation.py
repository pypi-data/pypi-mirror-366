"""Tests for fixture validation error behavior."""

import subprocess
from pathlib import Path


class TestFixtureValidation:
    """Test that the plugin throws errors for unavailable fixtures."""

    def test_error_for_nonexistent_fixture(self):
        """Test that an error is thrown when ordering by a nonexistent fixture."""
        # Run pytest with a fixture that doesn't exist
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "src/unit_tests/test_fixture_ordering.py",
                "--fixture-order",
                "nonexistent_fixture",
                "--ordering-mode",
                "fixture",
                "--collect-only",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Should fail with a ValueError about unavailable fixtures
        assert result.returncode != 0
        assert "Fixtures not available to all tests: nonexistent_fixture" in result.stdout
        assert (
            "Fixture ordering requires all fixtures to be globally available"
            in result.stdout
        )

    def test_error_for_multiple_nonexistent_fixtures(self):
        """Test that an error is thrown when multiple fixtures don't exist."""
        # Run pytest with multiple fixtures that don't exist
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "src/unit_tests/test_fixture_ordering.py",
                "--fixture-order",
                "nonexistent_fixture",
                "another_nonexistent",
                "--ordering-mode",
                "fixture",
                "--collect-only",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Should fail with a ValueError about unavailable fixtures
        assert result.returncode != 0
        # The order of fixtures in the error message may vary, so check for both fixtures
        assert "Fixtures not available to all tests:" in result.stdout
        assert "nonexistent_fixture" in result.stdout
        assert "another_nonexistent" in result.stdout

    def test_no_error_for_available_fixtures(self):
        """Test that no error is thrown when all fixtures are available."""
        # Run pytest with fixtures that exist in the test file
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "src/unit_tests/test_fixture_ordering.py",
                "--fixture-order",
                "db",
                "redis",
                "--ordering-mode",
                "fixture",
                "--collect-only",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Should succeed because db and redis fixtures are available
        assert result.returncode == 0

    def test_no_error_for_mark_mode(self):
        """Test that no error is thrown when using mark mode."""
        # Run pytest with mark mode (should not validate fixtures)
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "src/unit_tests/test_tag_ordering.py",
                "--tag-order",
                "fast",
                "slow",
                "--collect-only",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            check=True,
        )

        # Should succeed because mark mode doesn't validate fixtures
        assert result.returncode == 0
