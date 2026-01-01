"""
API endpoint tests for the RAG system.

Tests all FastAPI endpoints:
- POST /api/query - Query processing with RAG
- GET /api/courses - Course statistics
- DELETE /api/sessions/{session_id} - Session management
- GET /health - Health check
"""

import pytest
from fastapi import status


@pytest.mark.api
class TestQueryEndpoint:
    """Tests for the /api/query endpoint"""

    def test_query_with_session_id(self, client, sample_query_request, mock_rag_system):
        """Test querying with an existing session ID"""
        response = client.post("/api/query", json=sample_query_request)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

        # Verify content
        assert data["session_id"] == sample_query_request["session_id"]
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)

        # Verify RAG system was called correctly
        mock_rag_system.query.assert_called_once_with(
            sample_query_request["query"],
            sample_query_request["session_id"]
        )

    def test_query_without_session_id(self, client, mock_rag_system):
        """Test querying without a session ID (should create new session)"""
        request_data = {"query": "What is deep learning?"}

        response = client.post("/api/query", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify new session was created
        assert "session_id" in data
        assert data["session_id"] == "test_session_123"

        # Verify session creation was called
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_query_with_empty_query(self, client):
        """Test querying with an empty query string"""
        request_data = {"query": ""}

        response = client.post("/api/query", json=request_data)

        # Should still process (empty query validation could be added)
        assert response.status_code == status.HTTP_200_OK

    def test_query_missing_query_field(self, client):
        """Test request with missing required 'query' field"""
        request_data = {"session_id": "test_123"}

        response = client.post("/api/query", json=request_data)

        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_with_sources(self, client, mock_rag_system):
        """Test that sources are properly returned"""
        request_data = {"query": "What is machine learning?"}

        response = client.post("/api/query", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify sources structure
        assert "sources" in data
        assert len(data["sources"]) > 0

        # Verify source fields
        source = data["sources"][0]
        assert "text" in source
        assert "url" in source

    def test_query_error_handling(self, client, mock_rag_system):
        """Test error handling when RAG system raises exception"""
        # Configure mock to raise exception
        mock_rag_system.query.side_effect = Exception("RAG system error")

        request_data = {"query": "Test query"}

        response = client.post("/api/query", json=request_data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "detail" in response.json()

    def test_query_with_long_text(self, client):
        """Test querying with very long query text"""
        long_query = "What is machine learning? " * 100
        request_data = {"query": long_query}

        response = client.post("/api/query", json=request_data)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestCoursesEndpoint:
    """Tests for the /api/courses endpoint"""

    def test_get_course_stats_success(self, client, mock_rag_system):
        """Test getting course statistics successfully"""
        response = client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "total_courses" in data
        assert "course_titles" in data

        # Verify content
        assert data["total_courses"] == 2
        assert isinstance(data["course_titles"], list)
        assert len(data["course_titles"]) == 2

        # Verify RAG system was called
        mock_rag_system.get_course_analytics.assert_called_once()

    def test_get_course_stats_empty_catalog(self, client, mock_rag_system):
        """Test getting stats when no courses exist"""
        # Configure mock to return empty catalog
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": []
        }

        response = client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_get_course_stats_error_handling(self, client, mock_rag_system):
        """Test error handling in course stats endpoint"""
        # Configure mock to raise exception
        mock_rag_system.get_course_analytics.side_effect = Exception("Database error")

        response = client.get("/api/courses")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "detail" in response.json()

    def test_get_course_stats_content_type(self, client):
        """Test that response has correct content type"""
        response = client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers["content-type"]


@pytest.mark.api
class TestSessionEndpoint:
    """Tests for the /api/sessions/{session_id} endpoint"""

    def test_clear_session_success(self, client, mock_rag_system):
        """Test clearing a session successfully"""
        session_id = "test_session_123"

        # Add session to mock
        mock_rag_system.session_manager.sessions = {session_id: []}

        response = client.delete(f"/api/sessions/{session_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "message" in data
        assert "session_id" in data

        # Verify content
        assert data["message"] == "Session cleared successfully"
        assert data["session_id"] == session_id

        # Verify clear_session was called
        mock_rag_system.session_manager.clear_session.assert_called_once_with(session_id)

    def test_clear_nonexistent_session(self, client, mock_rag_system):
        """Test clearing a session that doesn't exist"""
        session_id = "nonexistent_session"

        # Ensure session doesn't exist
        mock_rag_system.session_manager.sessions = {}

        response = client.delete(f"/api/sessions/{session_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.json()

    def test_clear_session_empty_id(self, client):
        """Test clearing session with empty ID"""
        response = client.delete("/api/sessions/")

        # FastAPI will return 404 for missing path parameter
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_clear_session_error_handling(self, client, mock_rag_system):
        """Test error handling in clear session endpoint"""
        session_id = "test_session_123"
        mock_rag_system.session_manager.sessions = {session_id: []}

        # Configure mock to raise exception
        mock_rag_system.session_manager.clear_session.side_effect = Exception("Clear failed")

        response = client.delete(f"/api/sessions/{session_id}")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.api
class TestHealthEndpoint:
    """Tests for the /health endpoint"""

    def test_health_check(self, client):
        """Test basic health check endpoint"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.api
class TestEndpointIntegration:
    """Integration tests for multiple endpoints"""

    def test_query_then_check_courses(self, client, mock_rag_system):
        """Test querying and then checking course stats"""
        # First, make a query
        query_response = client.post("/api/query", json={"query": "What is ML?"})
        assert query_response.status_code == status.HTTP_200_OK

        # Then check courses
        courses_response = client.get("/api/courses")
        assert courses_response.status_code == status.HTTP_200_OK

        courses_data = courses_response.json()
        assert courses_data["total_courses"] > 0

    def test_create_session_and_clear(self, client, mock_rag_system):
        """Test creating a session via query and then clearing it"""
        # Create session via query
        query_response = client.post("/api/query", json={"query": "Test"})
        assert query_response.status_code == status.HTTP_200_OK

        session_id = query_response.json()["session_id"]

        # Add session to mock for clearing
        mock_rag_system.session_manager.sessions = {session_id: []}

        # Clear the session
        clear_response = client.delete(f"/api/sessions/{session_id}")
        assert clear_response.status_code == status.HTTP_200_OK

    def test_multiple_queries_same_session(self, client, mock_rag_system):
        """Test multiple queries with the same session ID"""
        session_id = "persistent_session"

        # First query
        response1 = client.post("/api/query", json={
            "query": "What is ML?",
            "session_id": session_id
        })
        assert response1.status_code == status.HTTP_200_OK

        # Second query with same session
        response2 = client.post("/api/query", json={
            "query": "What is deep learning?",
            "session_id": session_id
        })
        assert response2.status_code == status.HTTP_200_OK

        # Both should use the same session
        assert response1.json()["session_id"] == session_id
        assert response2.json()["session_id"] == session_id


@pytest.mark.api
class TestRequestValidation:
    """Tests for request validation and error cases"""

    def test_invalid_json_payload(self, client):
        """Test sending malformed JSON"""
        response = client.post(
            "/api/query",
            data="invalid json{{{",
            headers={"content-type": "application/json"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_wrong_content_type(self, client):
        """Test sending request with wrong content type"""
        response = client.post(
            "/api/query",
            data="query=test",
            headers={"content-type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_extra_fields_ignored(self, client):
        """Test that extra fields in request are handled gracefully"""
        request_data = {
            "query": "What is ML?",
            "session_id": "test_123",
            "extra_field": "should be ignored"
        }

        response = client.post("/api/query", json=request_data)

        # Should succeed despite extra field
        assert response.status_code == status.HTTP_200_OK

    def test_null_values_in_optional_fields(self, client):
        """Test null values in optional fields"""
        request_data = {
            "query": "What is ML?",
            "session_id": None
        }

        response = client.post("/api/query", json=request_data)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Async tests for API endpoints"""

    async def test_async_query(self, async_client, mock_rag_system):
        """Test query endpoint with async client"""
        response = await async_client.post("/api/query", json={"query": "Test"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "answer" in data

    async def test_async_courses(self, async_client):
        """Test courses endpoint with async client"""
        response = await async_client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_courses" in data

    async def test_async_health(self, async_client):
        """Test health endpoint with async client"""
        response = await async_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
