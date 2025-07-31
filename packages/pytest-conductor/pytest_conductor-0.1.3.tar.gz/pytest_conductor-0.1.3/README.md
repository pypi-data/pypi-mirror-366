# pytest-conductor

A pytest plugin that allows you to control the order in which tests run based on their tags (markers) or fixtures. Perfect for coordinating test execution in CI/CD pipelines, managing test dependencies, and optimizing test suite performance.

## ✨ Features

- **🎯 Tag-based Ordering**: Order tests by pytest markers (fast → slow → integration)
- **🔧 Fixture-based Ordering**: Order tests by the fixtures they use (db → redis → cache)
- **⚡ Unmatched Test Handling**: Control how tests without matching tags/fixtures are handled
- **🚫 Skip Unmatched Tests**: Option to skip tests that don't match the order list entirely
- **🛡️ Error Validation**: Automatic validation of fixture availability for reliable ordering
- **📊 Performance Optimized**: Minimal overhead with efficient sorting algorithms
- **🔍 Comprehensive Testing**: Full test suite with unit tests and integration tests
- **🎭 Interactive Demo**: Built-in demo showing all features with detailed logging

## Installation

```bash
pip install pytest-conductor
```

## 🎭 Quick Demo

See pytest-conductor in action with our interactive demo:

```bash
# Clone the repository
git clone https://github.com/your-username/pytest-conductor.git
cd pytest-conductor

# Run the interactive demo
hatch run demo
```

The demo shows:
- Tag ordering (fast → slow → integration)
- Fixture ordering (basic_calculator → advanced_calculator → sample_data)
- Unmatched test handling (first, last, none)
- Error handling for invalid configurations

## 📁 Example Project

The repository includes a complete example project demonstrating real-world usage:

```bash
# Navigate to the example project
cd example

# Install dependencies and pytest-conductor
hatch run pip install -e ../

# Run tests with coordination
hatch run pytest --tag-order fast slow -v
hatch run pytest --fixture-order basic_calculator advanced_calculator --ordering-mode fixture -v
```

The example project includes:
- Calculator application with basic and advanced operations
- Comprehensive test suite with different tags and fixtures
- Global and local fixtures demonstrating scope validation
- Integration tests showing all plugin features

## Usage

### Ordering Modes

The plugin supports two ordering modes:

1. **Mark Mode** (default): Order tests by their pytest markers/tags
2. **Fixture Mode**: Order tests by the fixtures they use

### Mark Mode - Basic Tag Ordering

Use the `--tag-order` option to specify the order in which tags should run:

```bash
pytest --tag-order fast slow integration
```

This will run all tests with the `fast` tag first, then `slow` tests, then `integration` tests.

### Fixture Mode - Basic Fixture Ordering

Use the `--fixture-order` option to specify the order in which fixtures should run:

```bash
pytest --fixture-order db redis cache --ordering-mode fixture
```

This will run all tests that use the `db` fixture first, then tests using `redis`, then tests using `cache`.

**⚠️ Important Limitation**: Fixture ordering only works with fixtures that are globally available to all tests. The plugin will throw an error if you try to order by a fixture that is not available to all tests in your test suite. This ensures reliable ordering behavior.

### Error Handling and Validation

The plugin includes robust error handling to prevent configuration issues:

#### Fixture Availability Validation
When using fixture ordering, the plugin validates that all specified fixtures are available to all tests:

```bash
# This will fail if 'nonexistent_fixture' is not available to all tests
pytest --fixture-order nonexistent_fixture --ordering-mode fixture
```

**Error Message**: `ValueError: Fixtures not available to all tests: nonexistent_fixture. Fixture ordering requires all fixtures to be globally available. Make sure these fixtures are defined in a conftest.py file that is accessible to all tests, or use mark ordering instead.`

#### Best Practices
- Use global fixtures defined in a root-level `conftest.py` file
- Use mark ordering for tests with local or conditional fixtures
- Test your configuration with `--collect-only` to catch issues early

### Handling Unmatched Tests

Use the `--unmatched-order` option to control how tests without matching tags/fixtures are handled:

```bash
# Run unmatched tests first
pytest --tag-order fast slow --unmatched-order first
pytest --fixture-order db redis --ordering-mode fixture --unmatched-order first

# Run unmatched tests last
pytest --tag-order fast slow --unmatched-order last
pytest --fixture-order db redis --ordering-mode fixture --unmatched-order last

# Run unmatched tests in any order (default)
pytest --tag-order fast slow --unmatched-order any
pytest --fixture-order db redis --ordering-mode fixture --unmatched-order any

# Skip unmatched tests entirely
pytest --tag-order fast slow --unmatched-order none
pytest --fixture-order db redis --ordering-mode fixture --unmatched-order none
```

### New in v0.1.0: Skip Unmatched Tests

The `--unmatched-order none` option is a new feature that allows you to skip tests that don't match your specified order list entirely. This is useful when you want to run only a specific subset of tests:

```bash
# Run only fast and slow tests, skip all others
pytest --tag-order fast slow --unmatched-order none

# Run only tests using specific fixtures, skip all others  
pytest --fixture-order db redis --ordering-mode fixture --unmatched-order none
```

### Example Test Structure

#### Mark Mode Example

```python
import pytest

@pytest.mark.fast
def test_fast_operation():
    """This test will run first when using --tag-order fast slow"""
    assert True

@pytest.mark.slow
def test_slow_operation():
    """This test will run second when using --tag-order fast slow"""
    assert True

def test_no_tags():
    """This test has no tags - behavior depends on --unmatched-order"""
    assert True

@pytest.mark.fast
@pytest.mark.slow
def test_multiple_tags():
    """This test has multiple tags - uses the first one in the order"""
    assert True
```

#### Fixture Mode Example

```python
import pytest

@pytest.fixture
def db():
    """Database fixture."""
    return {"type": "database"}

@pytest.fixture
def redis():
    """Redis fixture."""
    return {"type": "redis"}

def test_db_operation(db):
    """This test will run first when using --fixture-order db redis"""
    assert db["type"] == "database"

def test_redis_operation(redis):
    """This test will run second when using --fixture-order db redis"""
    assert redis["type"] == "redis"

def test_no_fixtures():
    """This test has no fixtures - behavior depends on --unmatched-order"""
    assert True

def test_multiple_fixtures(db, redis):
    """This test has multiple fixtures - uses the first one in the order"""
    assert db["type"] == "database"
    assert redis["type"] == "redis"
```

## Command Line Options

- `--tag-order TAG1 TAG2 ...`: Specify the order of tags for test execution (mark mode)
- `--fixture-order FIXTURE1 FIXTURE2 ...`: Specify the order of fixtures for test execution (fixture mode)
- `--ordering-mode {mark,fixture}`: Choose ordering mode (default: mark)
- `--unmatched-order {any,first,last,none}`: How to handle tests without matching tags/fixtures
  - `any`: Run unmatched tests in any order (default)
  - `first`: Run unmatched tests before tagged/fixture tests
  - `last`: Run unmatched tests after tagged/fixture tests
  - `none`: Skip unmatched tests entirely

## How It Works

### Mark Mode
1. The plugin extracts tags from test markers (pytest.mark)
2. Tests are sorted based on the specified tag order
3. Tests with multiple tags use the highest priority tag (first in the order)
4. Tests without tags are handled according to the `--unmatched-order` setting

### Fixture Mode
1. The plugin extracts fixture names from test function parameters
2. Tests are sorted based on the specified fixture order
3. Tests with multiple fixtures use the highest priority fixture (first in the order)
4. Tests without fixtures are handled according to the `--unmatched-order` setting

## Edge Cases and Special Behavior

### Multiple Tags/Fixtures
When a test has multiple tags or fixtures that are in your specified order, the plugin will:
- **Run the test only once** (no duplication)
- **Use the highest priority tag/fixture** (the one that appears first in your order list)

#### Example with Multiple Tags
```python
@pytest.mark.fast
@pytest.mark.slow
def test_multiple_tags():
    """This test has both 'fast' and 'slow' tags."""
    assert True
```

When running `pytest --tag-order fast slow integration`, this test will:
- Run **once** (not twice)
- Run in the **fast** group (since 'fast' comes first in the order)

#### Example with Multiple Fixtures
```python
def test_multiple_fixtures(db, redis, cache):
    """This test uses multiple fixtures."""
    assert True
```

When running `pytest --fixture-order db redis cache --ordering-mode fixture`, this test will:
- Run **once** (not multiple times)
- Run in the **db** group (since 'db' comes first in the order)

### Conftest Fixtures
The plugin handles fixtures defined in `conftest.py` files the same way as regular fixtures:

- **Global conftest fixtures** (in root `conftest.py`) are detected normally
- **Nested conftest fixtures** (in subdirectory `conftest.py` files) are also detected
- The plugin looks at the test function's parameter names, regardless of where the fixture is defined

**⚠️ Fixture Availability Requirement**: For fixture ordering to work correctly, all fixtures in your `--fixture-order` list must be available to all tests that might use them. The plugin will throw an error if any fixture in your order list is not available to all tests, ensuring reliable ordering behavior.

#### Example with Nested Conftest
```
tests/
├── conftest.py          # global_fixture
├── unit/
│   ├── conftest.py      # unit_fixture
│   └── test_unit.py     # uses both global_fixture and unit_fixture
└── integration/
    ├── conftest.py      # integration_fixture
    └── test_integration.py  # uses global_fixture and integration_fixture
```

When running `pytest --fixture-order global_fixture unit_fixture integration_fixture --ordering-mode fixture`:
- Tests in `unit/` will run first if they use `global_fixture` or `unit_fixture`
- Tests in `integration/` will run first if they use `global_fixture` or `integration_fixture`
- The plugin doesn't need to know where the fixture is defined - it just looks at the test parameters

#### Handling Deeply Nested Conftest Fixtures
For deeply nested directory structures, the plugin works seamlessly:

```
tests/
├── conftest.py                    # global_fixture
├── api/
│   ├── conftest.py               # api_fixture
│   ├── v1/
│   │   ├── conftest.py           # v1_fixture
│   │   └── test_endpoints.py     # uses global_fixture, api_fixture, v1_fixture
│   └── v2/
│       ├── conftest.py           # v2_fixture
│       └── test_endpoints.py     # uses global_fixture, api_fixture, v2_fixture
└── database/
    ├── conftest.py               # db_fixture
    ├── mysql/
    │   ├── conftest.py           # mysql_fixture
    │   └── test_queries.py       # uses global_fixture, db_fixture, mysql_fixture
    └── postgresql/
        ├── conftest.py           # postgres_fixture
        └── test_queries.py       # uses global_fixture, db_fixture, postgres_fixture
```

**Key Points:**
1. **No special configuration needed** - the plugin automatically detects all fixtures used by tests
2. **Fixture scope doesn't matter** - whether fixtures are session, module, class, or function scope
3. **Conftest inheritance works** - fixtures from parent directories are available to child tests
4. **Ordering is based on test parameters** - not fixture definitions

**Best Practices for Complex Fixture Structures:**
- Use descriptive fixture names that indicate their purpose (e.g., `mysql_db`, `redis_cache`)
- Consider using fixture prefixes to group related fixtures (e.g., `api_v1_client`, `api_v2_client`)
- When ordering by fixtures, list them in the order you want tests to run

### Unmatched Tests
Tests that don't have any of the specified tags or fixtures are handled according to the `--unmatched-order` setting:

- **`any`** (default): Run unmatched tests in any order
- **`first`**: Run unmatched tests before all tagged/fixture tests
- **`last`**: Run unmatched tests after all tagged/fixture tests
- **`none`**: Skip unmatched tests entirely (they won't run)

### Test Execution Order Guarantees
The plugin guarantees that:
1. **No test runs twice** - even with multiple matching tags/fixtures
2. **Tests run in the specified order** - within each priority group
3. **Unmatched tests are handled predictably** - based on your `--unmatched-order` setting
4. **Fixture dependencies are respected** - pytest's own fixture ordering still applies

## Examples

### Mark Mode Examples

#### Run fast tests first, then slow tests
```bash
pytest --tag-order fast slow
```

#### Run unit tests first, then integration tests, with untagged tests last
```bash
pytest --tag-order unit integration --unmatched-order last
```

#### Run smoke tests first, then full test suite
```bash
pytest --tag-order smoke full --unmatched-order last
```

### Fixture Mode Examples

#### Run database tests first, then cache tests
```bash
pytest --fixture-order db cache --ordering-mode fixture
```

#### Run API tests first, then database tests, with tests without fixtures last
```bash
pytest --fixture-order api db --ordering-mode fixture --unmatched-order last
```

#### Run tests with expensive fixtures last
```bash
pytest --fixture-order simple expensive --ordering-mode fixture --unmatched-order first
```

## Testing Edge Cases

The plugin includes comprehensive tests for edge cases. To verify the behavior:

### Run Edge Case Tests
```bash
# Run the edge case test suite
pytest src/unit_tests/test_edge_cases.py -v

# Run practical examples
pytest src/unit_tests/test_edge_case_examples.py -v
```

### Test Multiple Tags Ordering
```bash
# Test that tests with multiple tags run only once
pytest src/unit_tests/test_edge_case_examples.py --tag-order fast slow integration -v
```

### Test Multiple Fixtures Ordering
```bash
# Test that tests with multiple fixtures run only once
pytest src/unit_tests/test_edge_case_examples.py --fixture-order db redis cache --ordering-mode fixture -v
```

### Test Unmatched Test Handling
```bash
# Test unmatched tests running first
pytest src/unit_tests/test_edge_case_examples.py --tag-order fast slow --unmatched-order first -v

# Test unmatched tests running last
pytest src/unit_tests/test_edge_case_examples.py --tag-order fast slow --unmatched-order last -v
```

## 🛠️ Development

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/pytest-conductor.git
cd pytest-conductor

# Install in development mode
pip install -e .
```

### Test Structure

The project uses a comprehensive test structure:

```
src/
├── pytest_conductor/          # Main plugin code
├── unit_tests/               # Unit tests for the plugin itself
│   ├── test_tag_ordering.py
│   ├── test_fixture_ordering.py
│   ├── test_fixture_validation.py
│   ├── test_unmatched_none.py
│   └── ... (8 test files total)
└── integration_tests/        # Integration tests using the example project
    ├── test_pytest_conductor_integration.py
    └── README.md
```

### Running Tests

```bash
# Run unit tests only (test the plugin's core functionality)
hatch run unit-tests

# Run integration tests only (test with real-world example project)
hatch run integration-tests

# Run all tests
hatch run unit-tests && hatch run integration-tests

# Run the interactive demo (shows test coordination with detailed logging)
hatch run demo
```

### Example Project Testing

```bash
# Navigate to example project
cd example

# Install pytest-conductor in the example environment
hatch run pip install -e ../

# Run example tests with coordination
hatch run pytest --tag-order fast slow -v
hatch run pytest --fixture-order basic_calculator advanced_calculator --ordering-mode fixture -v
```

## 📋 Project Structure

```
pytest-conductor/
├── src/
│   ├── pytest_conductor/          # Main plugin code
│   ├── unit_tests/               # Unit tests for the plugin
│   └── integration_tests/        # Integration tests with example project
├── example/                      # Complete example project
│   ├── src/
│   │   ├── calculator/           # Example application
│   │   └── tests/               # Example tests with various tags/fixtures
│   └── pyproject.toml           # Example project configuration
├── pyproject.toml               # Main project configuration
└── README.md                    # This file
```

## Marker Registration

To avoid warnings about unknown markers, you can register your custom markers in your `pyproject.toml` or `pytest.ini` file:

```toml
[tool.pytest.ini_options]
markers = [
    "fast: marks tests as fast",
    "slow: marks tests as slow", 
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

Or in `pytest.ini`:

```ini
[tool:pytest]
markers =
    fast: marks tests as fast
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
``` 