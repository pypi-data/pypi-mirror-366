# Integration Tests for pytest-conductor

This directory contains comprehensive integration tests that demonstrate all features of the pytest-conductor plugin in a real-world scenario.

## 🎯 Purpose

These tests serve multiple purposes:

1. **Demonstration**: Show how pytest-conductor works in practice
2. **Validation**: Ensure the plugin works correctly in real scenarios
3. **Documentation**: Provide examples of all features with detailed logging
4. **CI/CD**: Can be run in continuous integration environments

## 🧪 Test Overview

### Core Integration Tests

| Test | Purpose | Features Demonstrated |
|------|---------|----------------------|
| `test_build_and_install_package` | Builds and installs pytest-conductor locally | Package building, local installation |
| `test_basic_tag_ordering` | Tests basic tag ordering | Tag ordering, execution order verification |
| `test_fixture_ordering` | Tests fixture-based ordering | Fixture ordering, mode switching |
| `test_unmatched_order_first` | Tests unmatched tests running first | Unmatched order handling |
| `test_unmatched_order_last` | Tests unmatched tests running last | Unmatched order handling |
| `test_unmatched_order_none` | Tests skipping unmatched tests | New "none" feature |
| `test_fixture_scope_error` | Tests fixture scope validation | Error handling for non-global fixtures |
| `test_mixed_tag_and_fixture_ordering` | Tests mixed ordering scenarios | Complex ordering combinations |
| `test_complex_ordering_scenario` | Tests complex multi-tag ordering | Advanced ordering scenarios |
| `test_performance_comparison` | Measures ordering overhead | Performance analysis |
| `test_help_output` | Verifies help output | CLI documentation |
| `test_collection_with_ordering` | Tests collection with ordering | Collection phase behavior |

## 🚀 Running the Tests

### Quick Demo

To see pytest-conductor in action with detailed logging and explanations:

```bash
hatch run demo
```

This interactive demo shows:
- Tag ordering (fast → slow → integration)
- Fixture ordering (basic_calculator → advanced_calculator → sample_data)
- Unmatched test handling (first, last, none)
- Error handling for invalid configurations

### Prerequisites

1. Install the example project dependencies:
   ```bash
   cd example
   pip install -e .
   ```

2. Install pytest-conductor in the example environment:
   ```bash
   # From the example directory
   hatch run pip install -e ../
   ```

3. Verify the plugin is working:
   ```bash
   # From the example directory
   hatch run pytest --help | grep -A 5 "conductor:"
   ```

### Running All Integration Tests

```bash
# From the main project root
hatch run integration-tests
```

### Running Specific Test Categories

```bash
# Test ordering functionality
hatch run integration-tests -k "ordering" -v -s

# Test error handling
hatch run integration-tests -k "error" -v -s

# Test performance
hatch run integration-tests -k "performance" -v -s

# Test collection and help
hatch run integration-tests -k "collection" -v -s
```

## 📊 Expected Output

The integration tests provide detailed logging with emojis and clear descriptions:

```
============================================================
🧪 Basic Tag Ordering: fast → slow → integration
📁 Working directory: /path/to/example
🔧 Command: pytest --tag-order fast slow integration -v
============================================================
⏱️  Execution time: 2.34 seconds
📊 Exit code: 0
📤 STDOUT:
...
============================================================
```

## 🔧 Test Features

### Detailed Logging
Each test includes comprehensive logging that shows:
- What operation is being performed
- Input data and expected results
- Actual results and comparisons
- Success/failure indicators

### Performance Measurement
Tests measure execution time and compare ordered vs unordered execution to ensure minimal overhead.

### Error Validation
Tests verify that appropriate errors are raised for invalid configurations (e.g., non-global fixtures).

### Order Verification
Tests verify that tests actually run in the expected order by analyzing pytest output.

## 🎨 Test Categories

### 1. Package Management Tests
- Building the pytest-conductor package
- Installing it locally in the example project
- Verifying installation success

### 2. Ordering Functionality Tests
- Basic tag ordering (fast → slow → integration)
- Fixture ordering (basic_calculator → advanced_calculator)
- Complex multi-tag scenarios
- Mixed tag and fixture ordering

### 3. Unmatched Test Handling
- `first`: Untagged tests run before tagged tests
- `last`: Untagged tests run after tagged tests  
- `none`: Untagged tests are skipped entirely

### 4. Error Handling Tests
- Fixture scope validation errors
- Non-global fixture detection
- Appropriate error messages

### 5. Performance Tests
- Execution time comparison
- Overhead measurement
- Performance regression detection

### 6. Documentation Tests
- Help output verification
- CLI option validation
- Collection phase behavior

## 🔍 What You'll Learn

By running these tests, you'll see:

1. **How pytest-conductor works in practice** - Real examples of test ordering
2. **Performance characteristics** - Minimal overhead of ordering
3. **Error handling** - How the plugin handles invalid configurations
4. **Integration patterns** - How to integrate the plugin into real projects
5. **Debugging information** - Detailed logging for troubleshooting

## 🛠️ Customization

You can modify these tests to:

- Test different ordering scenarios
- Add new feature demonstrations
- Measure performance on your specific use cases
- Validate plugin behavior with your test suite

## 📈 CI/CD Integration

These tests are designed to run in CI/CD environments:

- They build and install packages automatically
- They provide clear pass/fail indicators
- They include performance benchmarks
- They validate all plugin features

## 🎯 Next Steps

After running these tests:

1. **Experiment with your own test suite** - Apply the patterns you see here
2. **Customize the ordering** - Modify the test scenarios for your needs
3. **Add your own integration tests** - Extend the examples for your use cases
4. **Contribute improvements** - Share your findings and improvements 