# RAG System Test Suite

Comprehensive testing framework for the RAG (Retrieval-Augmented Generation) system.

## Overview

This test suite provides:
- **API Endpoint Tests**: Complete coverage of FastAPI endpoints
- **Shared Fixtures**: Reusable test data and mocks in `conftest.py`
- **Pytest Configuration**: Clean test execution with proper markers
- **Mock-based Testing**: Isolated unit tests without external dependencies

## Test Structure

```
backend/tests/
├── __init__.py           # Package initialization
├── conftest.py           # Shared fixtures and test configuration
├── test_api.py           # API endpoint tests
└── README.md            # This file
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Markers
```bash
# Run only API tests
pytest -m api

# Run unit tests (when available)
pytest -m unit

# Run integration tests (when available)
pytest -m integration
```

### Run Specific Test Files
```bash
pytest backend/tests/test_api.py
```

### Run Specific Test Classes
```bash
pytest backend/tests/test_api.py::TestQueryEndpoint
```

### Run Specific Test Methods
```bash
pytest backend/tests/test_api.py::TestQueryEndpoint::test_query_with_session_id
```

### Verbose Output
```bash
pytest -v
```

### Show Print Statements
```bash
pytest -s
```

## Test Configuration

Test configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
addopts = ["-v", "--strict-markers", "--tb=short"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests for individual components",
    "integration: Integration tests for component interactions",
    "api: API endpoint tests",
    "slow: Tests that take longer to run",
]
```

## Available Fixtures

### Configuration Fixtures
- `mock_config`: Mock Config object with test settings
- `test_app`: FastAPI test application (without static file mounting)
- `client`: Synchronous TestClient for API requests
- `async_client`: Asynchronous client for async endpoint tests

### Component Fixtures
- `mock_rag_system`: Mock RAG system with predefined responses
- `mock_vector_store`: Mock vector store for search operations
- `mock_ai_generator`: Mock AI generator for response generation

### Data Fixtures
- `sample_course`: Sample Course object for testing
- `sample_course_chunks`: Sample CourseChunk objects
- `sample_query_request`: Sample API query request
- `sample_query_response`: Sample API query response

## Test Coverage

### API Endpoint Tests (`test_api.py`)

#### `/api/query` Endpoint
- ✅ Query with session ID
- ✅ Query without session ID (auto-create)
- ✅ Empty query handling
- ✅ Missing required fields
- ✅ Source citation in responses
- ✅ Error handling
- ✅ Long query text

#### `/api/courses` Endpoint
- ✅ Get course statistics
- ✅ Empty catalog handling
- ✅ Error handling
- ✅ Content type validation

#### `/api/sessions/{session_id}` Endpoint
- ✅ Clear session successfully
- ✅ Non-existent session handling
- ✅ Empty session ID
- ✅ Error handling

#### `/health` Endpoint
- ✅ Health check response

#### Integration Tests
- ✅ Query then check courses
- ✅ Create and clear session
- ✅ Multiple queries same session

#### Request Validation Tests
- ✅ Invalid JSON payload
- ✅ Wrong content type
- ✅ Extra fields handling
- ✅ Null values in optional fields

#### Async Tests
- ✅ Async query endpoint
- ✅ Async courses endpoint
- ✅ Async health endpoint

## Writing New Tests

### Example Unit Test
```python
import pytest

@pytest.mark.unit
def test_my_component(mock_config):
    """Test description"""
    # Arrange
    component = MyComponent(mock_config)

    # Act
    result = component.do_something()

    # Assert
    assert result == expected_value
```

### Example API Test
```python
import pytest
from fastapi import status

@pytest.mark.api
def test_new_endpoint(client):
    """Test new API endpoint"""
    response = client.get("/api/new-endpoint")

    assert response.status_code == status.HTTP_200_OK
    assert "expected_field" in response.json()
```

### Example Async Test
```python
import pytest

@pytest.mark.api
@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    """Test async endpoint"""
    response = await async_client.post("/api/endpoint", json={"data": "value"})

    assert response.status_code == 200
```

## Mock vs Real Components

### When to Use Mocks
- ✅ Testing API endpoints in isolation
- ✅ Testing error handling
- ✅ Fast unit tests
- ✅ Avoiding external dependencies (OpenAI API, ChromaDB)

### When to Use Real Components
- ❌ Integration tests (requires real ChromaDB)
- ❌ End-to-end tests (requires full system)
- ❌ Performance testing

## Best Practices

1. **Use Descriptive Test Names**: Test names should clearly describe what they test
2. **Follow AAA Pattern**: Arrange, Act, Assert
3. **One Assertion Per Test**: Focus each test on a single behavior
4. **Use Fixtures**: Leverage shared fixtures for common setup
5. **Mark Tests Appropriately**: Use pytest markers for organization
6. **Test Error Cases**: Don't just test the happy path
7. **Keep Tests Independent**: Tests should not depend on each other

## Troubleshooting

### Import Errors
If you encounter import errors, ensure you're running pytest from the project root:
```bash
cd /path/to/project
pytest
```

### Static File Errors
The test suite uses a modified test app that doesn't mount static files. If you see static file errors, you're likely importing the wrong app.

### Async Warnings
If you see async warnings, ensure `pytest-asyncio` is installed:
```bash
uv add pytest-asyncio
```

## Future Enhancements

- [ ] Unit tests for document_processor.py
- [ ] Unit tests for vector_store.py
- [ ] Unit tests for ai_generator.py
- [ ] Unit tests for search_tools.py
- [ ] Integration tests with real ChromaDB
- [ ] Performance tests
- [ ] Code coverage reports
- [ ] CI/CD integration

## Dependencies

Required packages (already in pyproject.toml):
- `pytest>=8.0.0` - Testing framework
- `pytest-asyncio>=0.23.0` - Async test support
- `httpx>=0.27.0` - Async HTTP client for FastAPI testing
- `fastapi` - Web framework
- `pydantic` - Data validation

## Contributing

When adding new tests:
1. Add appropriate pytest markers
2. Use existing fixtures when possible
3. Update this README with new test coverage
4. Ensure tests are independent and can run in any order
5. Follow the existing test structure and naming conventions
