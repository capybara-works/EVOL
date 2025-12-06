# EVOL Test Suite

This directory contains the test suite for EVOL.

## Structure

- `unit/` - Unit tests for individual modules
- `integration/` - Integration tests for complete workflows
- `conftest.py` - Shared pytest fixtures and configuration

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=evol

# Run specific test file
pytest tests/unit/test_github.py

# Run with verbose output
pytest -v
```

## Coverage Goals

- Overall: 70%+
- evol/collector/github.py: 80%+
- evol/api/main.py: 90%+
- evol/ui/app.py: 70%+
