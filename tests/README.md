# 🌀 Doc Forge Test Suite

This directory contains the Eidosian test suite for Doc Forge, designed with principles of structure, precision, and comprehensive coverage.

## 📋 Test Categories

Our test suite is organized into the following categories:

1. **Unit Tests**: Testing individual components in isolation
2. **Integration Tests**: Testing interactions between components
3. **System Tests**: Testing the entire system from end to end
4. **Performance Tests**: Testing the efficiency and scalability

## 🧪 Running Tests

You can run tests using any of these methods:

### Using pytest (recommended)

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run tests from a specific file
pytest tests/test_specific_module.py

# Run a specific test
pytest tests/test_specific_module.py::test_specific_function
```

### Using unittest

```bash
python -m unittest discover -v
```

### Using Doc Forge CLI

```bash
# Run all tests
doc-forge test run

# Run with verbose output
doc-forge test run --verbose

# Run tests matching a pattern
doc-forge test run --pattern "test_update*"
```

## 📊 Test Coverage

You can generate a coverage report using:

```bash
# Using pytest with coverage plugin
pytest --cov=src/doc_forge

# Using Doc Forge test commands
doc-forge test analyze --format html
```

## 🛠️ Creating New Tests

1. Use the test template in `tests/templates/test_template.py`
2. Follow the Eidosian testing principles
3. Ensure proper isolation of test cases
4. Use meaningful assertions with clear failure messages

## 🧩 Test Organization

```
tests/
├── conftest.py              # Shared pytest fixtures
├── templates/               # Test templates
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── system/                  # System tests
└── performance/             # Performance tests
```

## 📚 Testing Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Doc Forge Test Command System](../src/doc_forge/test_command.py)
