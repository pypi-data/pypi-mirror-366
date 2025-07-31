# Calculator Example Project

This example demonstrates how to use the `pytest-conductor` plugin in a real Python project structure. It shows how to organize your code with `src/main` and `src/tests` directories, and how to configure the plugin in your `pyproject.toml`.

## Project Structure

```
example/
├── pyproject.toml              # Project configuration with pytest-conductor
├── README.md                   # This file
└── src/
    ├── calculator/             # Main package
    │   ├── __init__.py
    │   └── calculator.py       # Calculator implementation
    └── tests/                  # Test package
        ├── __init__.py
        ├── conftest.py         # Global fixtures
        ├── test_basic_operations.py
        ├── test_advanced_operations.py
        ├── test_data_processing.py
        ├── test_no_tags.py
        └── advanced/           # Subdirectory with local fixtures
            ├── __init__.py
            ├── conftest.py     # Local fixtures (will cause errors)
            └── test_advanced_features.py
```

## Installation

1. **Install the project in development mode:**
   ```bash
   cd example
   pip install -e .
   ```

2. **Install pytest-conductor:**
   ```bash
   # Option 1: Install from PyPI
   pip install pytest-conductor
   
   # Option 2: Install the local development version (recommended for testing)
   hatch run pip install -e ../
   
   # Option 3: Install with dev dependencies
   pip install -e ".[dev]"
   ```

## Configuration

The `pyproject.toml` file shows how to configure pytest-conductor:

### Basic Configuration
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q"
testpaths = ["src/tests"]
markers = [
    "fast: marks tests as fast",
    "slow: marks tests as slow", 
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
]
```

### Using pytest-conductor in pyproject.toml
You can configure test ordering directly in your `pyproject.toml` by uncommenting and modifying the example configurations:

```toml
[tool.pytest.ini_options.addopts]
# Run fast tests first, then slow tests
addopts = "-ra -q --tag-order fast slow"

# Run unit tests first, then integration tests  
addopts = "-ra -q --tag-order unit integration"

# Run tests with basic_calculator first, then advanced_calculator
addopts = "-ra -q --fixture-order basic_calculator advanced_calculator --ordering-mode fixture"

# Run unmatched tests last
addopts = "-ra -q --tag-order fast slow --unmatched-order last"

# Skip unmatched tests entirely
addopts = "-ra -q --tag-order fast slow --unmatched-order none"
```

## Running Tests

### Interactive Demo

To see pytest-conductor in action with detailed explanations:

```bash
cd ..  # Go back to main project root
hatch run demo
```

This demo shows all features with step-by-step explanations and detailed logging.

### Basic Test Execution

Run all tests:
```bash
hatch run pytest
```

Run with verbose output:
```bash
hatch run pytest -v
```

Run with output capture disabled (see print statements):
```bash
hatch run pytest -s
```

### Test Coordination Examples

Run tests with tag ordering:
```bash
hatch run pytest --tag-order fast slow -v
```

Run tests with fixture ordering:
```bash
hatch run pytest --fixture-order basic_calculator advanced_calculator --ordering-mode fixture -v
```

Run tests with unmatched tests first:
```bash
hatch run pytest --tag-order fast slow --unmatched-order first -v
```

Skip unmatched tests entirely:
```bash
hatch run pytest --tag-order fast slow --unmatched-order none -v
```

### Integration Tests

The project includes comprehensive integration tests that demonstrate all pytest-conductor features:

```bash
# Run all integration tests
pytest ../src/integration_tests/ -v -s

# Run specific integration test categories
pytest ../src/integration_tests/ -k "ordering" -v -s  # Ordering functionality
pytest ../src/integration_tests/ -k "error" -v -s     # Error handling
pytest ../src/integration_tests/ -k "performance" -v -s  # Performance tests
```

See [Integration Tests README](../src/integration_tests/README.md) for detailed information.

### 1. Basic Tag Ordering

Run fast tests first, then slow tests:
```bash
pytest --tag-order fast slow -v
```

Run unit tests first, then integration tests:
```bash
pytest --tag-order unit integration -v
```

### 2. Fixture Ordering

Run tests with basic_calculator first, then advanced_calculator:
```bash
pytest --fixture-order basic_calculator advanced_calculator --ordering-mode fixture -v
```

Run tests with sample_data first, then test_config:
```bash
pytest --fixture-order sample_data test_config --ordering-mode fixture -v
```

### 3. Handling Unmatched Tests

Run unmatched tests first:
```bash
pytest --tag-order fast slow --unmatched-order first -v
```

Run unmatched tests last:
```bash
pytest --tag-order fast slow --unmatched-order last -v
```

Skip unmatched tests entirely:
```bash
pytest --tag-order fast slow --unmatched-order none -v
```

### 4. Fixture Validation Error

This demonstrates the fixture validation error:
```bash
# This will fail because local_advanced_fixture is not globally available
pytest --fixture-order local_advanced_fixture --ordering-mode fixture -v
```

The error occurs because `local_advanced_fixture` is defined in `src/tests/advanced/conftest.py` and is only available to tests in the `advanced/` directory, but not to all tests in the project.

### 5. Multiple Tags and Fixtures

Tests can have multiple tags and use multiple fixtures:
```bash
# Test with multiple tags
pytest --tag-order fast slow integration -v

# Test with multiple fixtures
pytest --fixture-order basic_calculator sample_data test_config --ordering-mode fixture -v
```

## Test Categories

- **Fast tests** (`@pytest.mark.fast`): Basic operations, quick to run
- **Slow tests** (`@pytest.mark.slow`): Advanced operations, take longer
- **Unit tests** (`@pytest.mark.unit`): Test individual components
- **Integration tests** (`@pytest.mark.integration`): Test component interactions

## Fixtures

### Global Fixtures (in `src/tests/conftest.py`)
Available to all tests:
- `basic_calculator`: Basic calculator instance
- `advanced_calculator`: Advanced calculator instance
- `sample_data`: Sample data for testing
- `test_config`: Test configuration

### Local Fixtures (in `src/tests/advanced/conftest.py`)
Only available to tests in `advanced/` directory:
- `local_advanced_fixture`: Advanced fixture data
- `specialized_config`: Specialized configuration

## Expected Behavior

1. **Tag ordering**: Tests run in the order specified by `--tag-order`
2. **Fixture ordering**: Tests run in the order specified by `--fixture-order`
3. **Multiple matches**: Tests with multiple tags/fixtures use the first one in the order
4. **Unmatched tests**: Handled according to `--unmatched-order` setting
5. **Fixture validation**: Errors thrown for fixtures not available to all tests

## Integration with CI/CD

You can integrate pytest-conductor into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run fast tests first
  run: pytest --tag-order fast slow --unmatched-order last

- name: Run unit tests first
  run: pytest --tag-order unit integration --unmatched-order last

- name: Run fixture-ordered tests
  run: pytest --fixture-order basic_calculator advanced_calculator --ordering-mode fixture
```

## Benefits of This Structure

1. **Real-world organization**: Uses standard Python project structure
2. **Package management**: Shows how to include pytest-conductor as a dependency
3. **Configuration**: Demonstrates pyproject.toml configuration
4. **Scalability**: Structure supports growing test suites
5. **Maintainability**: Clear separation of concerns between main code and tests 