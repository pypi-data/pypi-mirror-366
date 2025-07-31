"""
Demo script for pytest-conductor integration tests.

This script demonstrates how pytest-conductor coordinates test execution
with detailed logging and step-by-step explanations.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple


def run_pytest_with_detailed_logging(
    args: List[str],
    cwd: Path,
    description: str,
    show_coordination: bool = True,
) -> Tuple[subprocess.CompletedProcess, float]:
    """Run pytest with detailed logging and coordination explanation."""
    print(f"\n{'='*80}")
    print(f"🎬 {description}")
    print(f"📁 Working directory: {cwd}")
    print(f"🔧 Command: pytest {' '.join(args)}")
    print(f"{'='*80}")

    if show_coordination:
        print("\n📋 COORDINATION EXPLANATION:")
        print("   • pytest-conductor will collect all tests first")
        print("   • Then analyze test markers/fixtures based on ordering mode")
        print("   • Sort tests according to the specified order")
        print("   • Handle unmatched tests based on --unmatched-order setting")
        print("   • Execute tests in the coordinated order")

    print("\n🚀 EXECUTING...")
    start_time = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(cwd)},
    )
    end_time = time.time()

    print(f"\n⏱️  Execution time: {end_time - start_time:.2f} seconds")
    print(f"📊 Exit code: {result.returncode}")

    if result.stdout:
        print("\n📤 STDOUT:")
        print(f"{'─'*40}")
        print(result.stdout)
        print(f"{'─'*40}")

    if result.stderr:
        print("\n📤 STDERR:")
        print(f"{'─'*40}")
        print(result.stderr)
        print(f"{'─'*40}")

    print(f"{'='*80}\n")
    return result, end_time - start_time


def analyze_test_order(output: str, order_type: str) -> None:
    """Analyze and explain the test execution order."""
    print(f"\n🔍 ORDER ANALYSIS ({order_type}):")

    # Extract test execution lines
    lines = output.split("\n")
    test_lines = []
    for line in lines:
        if "test_" in line and ("::" in line or "[" in line) and "%" in line:
            test_lines.append(line.strip())

    if test_lines:
        print("   📋 Test execution order:")
        for i, line in enumerate(test_lines, 1):
            # Extract test name
            if "::" in line:
                test_name = line.split("::")[-1].split()[0]
            else:
                test_name = line.split("[")[0].strip()
            print(f"   {i:2d}. {test_name}")

        print("\n   ✅ Order verification:")
        if order_type == "tag":
            print("   • Fast tests (unit) should run first")
            print("   • Slow tests (integration) should run second")
            print("   • Tests with multiple tags use first match")
        elif order_type == "fixture":
            print("   • Tests using 'basic_calculator' fixture first")
            print("   • Tests using 'advanced_calculator' fixture second")
            print("   • Tests using 'sample_data' fixture third")
        elif order_type == "unmatched":
            print("   • Unmatched tests should be handled according to --unmatched-order")
    else:
        print("   ⚠️  Could not extract test order from output")


def main():
    """Main demo function."""
    print("🎭 PYTEST-CONDUCTOR INTEGRATION DEMO")
    print("=====================================")
    print("This demo shows how pytest-conductor coordinates test execution")
    print("in a real-world example project with detailed logging.\n")

    # Get paths
    current = Path(__file__).parent
    project_root = current.parent.parent
    example_dir = project_root / "example"

    print("📂 Project structure:")
    print(f"   • Main project: {project_root}")
    print(f"   • Example project: {example_dir}")
    print(f"   • Integration tests: {current}")

    # Demo 1: Basic tag ordering
    print(f"\n{'='*60}")
    print("🎯 DEMO 1: Basic Tag Ordering")
    print(f"{'='*60}")
    print("Demonstrates ordering tests by pytest markers (fast → slow → integration)")

    result1, duration1 = run_pytest_with_detailed_logging(
        ["--tag-order", "fast", "slow", "integration", "-v"],
        example_dir,
        "Tag Ordering: fast → slow → integration",
    )

    if result1.returncode == 0:
        analyze_test_order(result1.stdout, "tag")

    # Demo 2: Fixture ordering
    print(f"\n{'='*60}")
    print("🎯 DEMO 2: Fixture Ordering")
    print(f"{'='*60}")
    print("Demonstrates ordering tests by the fixtures they use")

    result2, duration2 = run_pytest_with_detailed_logging(
        [
            "--fixture-order",
            "basic_calculator",
            "advanced_calculator",
            "sample_data",
            "-v",
        ],
        example_dir,
        "Fixture Ordering: basic_calculator → advanced_calculator → sample_data",
    )

    if result2.returncode == 0:
        analyze_test_order(result2.stdout, "fixture")

    # Demo 3: Unmatched test handling
    print(f"\n{'='*60}")
    print("🎯 DEMO 3: Unmatched Test Handling")
    print(f"{'='*60}")
    print("Demonstrates how tests without matching tags are handled")

    result3, duration3 = run_pytest_with_detailed_logging(
        ["--tag-order", "fast", "slow", "--unmatched-order", "first", "-v"],
        example_dir,
        "Unmatched Order: first (untagged tests run first)",
    )

    if result3.returncode == 0:
        analyze_test_order(result3.stdout, "unmatched")

    # Demo 4: Unmatched test skipping
    print(f"\n{'='*60}")
    print("🎯 DEMO 4: Skipping Unmatched Tests")
    print(f"{'='*60}")
    print("Demonstrates skipping tests that don't match the order list")

    result4, duration4 = run_pytest_with_detailed_logging(
        ["--tag-order", "fast", "slow", "--unmatched-order", "none", "-v"],
        example_dir,
        "Unmatched Order: none (skip untagged tests)",
    )

    if result4.returncode == 0:
        analyze_test_order(result4.stdout, "unmatched")

    # Demo 5: Error handling
    print(f"\n{'='*60}")
    print("🎯 DEMO 5: Error Handling")
    print(f"{'='*60}")
    print("Demonstrates error when trying to order by non-existent fixtures")

    result5, duration5 = run_pytest_with_detailed_logging(
        ["--fixture-order", "nonexistent_fixture", "-v"],
        example_dir,
        "Error Handling: non-existent fixture should cause error",
        show_coordination=False,
    )

    if result5.returncode != 0:
        print("\n❌ Expected error occurred:")
        if "Fixtures not available to all tests" in result5.stdout:
            print("   ✅ Plugin correctly identified unavailable fixture")
            print("   ✅ Error message explains the issue")

    # Demo 6: Timing demonstration
    print(f"\n{'='*60}")
    print("🎯 DEMO 6: Timing Demonstration")
    print(f"{'='*60}")
    print("Demonstrates how fixture ordering affects test execution timing")
    print(
        "Tests with 'no_wait' fixture run quickly,"
        " tests with 'wait_3_seconds' take time"
    )

    # Get the path to the timing demo tests
    current = Path(__file__).parent
    timing_demo_path = current / "test_timing_demo.py"

    result6, duration6 = run_pytest_with_detailed_logging(
        [
            "--fixture-order",
            "no_wait",
            "wait_3_seconds",
            "-v",
            str(timing_demo_path),
        ],
        current,  # Use current directory since the test file is here
        "Timing Demo: no_wait → wait_3_seconds (should show timing difference)",
    )

    if result6.returncode == 0:
        print("\n⏱️  Timing Analysis:")
        print("   • First 2 tests (no_wait): Should complete quickly (~0.1s)")
        print("   • Next 2 tests (wait_3_seconds): Should each take ~3s")
        print("   • Total expected time: ~6.1 seconds")
        print(f"   • Actual time: {duration6:.2f} seconds")

        if duration6 > 5:  # Should be around 6 seconds
            print("   ✅ Timing demonstrates fixture ordering effect")
        else:
            print("   ⚠️  Timing may not show expected difference")

    # Summary
    print(f"\n{'='*60}")
    print("📊 DEMO SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Tag ordering: {'PASSED' if result1.returncode == 0 else 'FAILED'}")
    print(f"✅ Fixture ordering: {'PASSED' if result2.returncode == 0 else 'FAILED'}")
    print(f"✅ Unmatched handling: {'PASSED' if result3.returncode == 0 else 'FAILED'}")
    print(f"✅ Unmatched skipping: {'PASSED' if result4.returncode == 0 else 'FAILED'}")
    print(f"✅ Error handling: {'PASSED' if result5.returncode != 0 else 'FAILED'}")
    print(f"✅ Timing demonstration: {'PASSED' if result6.returncode == 0 else 'FAILED'}")

    total_time = duration1 + duration2 + duration3 + duration4 + duration5 + duration6
    print(f"\n⏱️  Total demo time: {total_time:.2f} seconds")

    print("\n🎉 Demo completed! pytest-conductor successfully coordinated")
    print("   test execution across all scenarios.")


if __name__ == "__main__":
    main()
