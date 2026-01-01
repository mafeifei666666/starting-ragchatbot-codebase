# Quick Start - Running Tests

## Install Dependencies
```bash
uv sync
```

## Basic Commands

### Run All Tests
```bash
pytest
# or
uv run pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Only API Tests
```bash
pytest -m api
```

### Run Specific Test File
```bash
pytest backend/tests/test_api.py
```

### Run Specific Test Class
```bash
pytest backend/tests/test_api.py::TestQueryEndpoint
```

### Run Specific Test Method
```bash
pytest backend/tests/test_api.py::TestQueryEndpoint::test_query_with_session_id
```

## Current Test Results

✅ **26 tests** - All passing
⚡ **0.13s** - Fast execution
📦 **3 fixtures** - Reusable test data

## Test Coverage

- `/api/query` - 7 tests
- `/api/courses` - 4 tests
- `/api/sessions/{session_id}` - 4 tests
- `/health` - 1 test
- Integration - 3 tests
- Validation - 4 tests
- Async - 3 tests

## Next Steps

See `README.md` for comprehensive documentation on:
- Writing new tests
- Available fixtures
- Test organization
- Best practices
