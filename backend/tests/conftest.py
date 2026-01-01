"""
Pytest configuration and shared fixtures for RAG system tests.

This module provides:
- Test application factory (without static file mounting)
- Mock configurations and dependencies
- Shared test data and fixtures
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, List
import sys
import os

# Add backend directory to Python path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# Import models and components
from config import Config
from models import Course, Lesson, CourseChunk


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing"""
    config = Mock(spec=Config)
    config.OPENAI_API_KEY = "test-api-key"
    config.OPENAI_MODEL = "gpt-4"
    config.EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    config.CHUNK_SIZE = 800
    config.CHUNK_OVERLAP = 100
    config.MAX_RESULTS = 5
    config.MAX_HISTORY = 2
    config.CHROMA_PATH = "./test_chroma_db"
    return config


@pytest.fixture
def sample_course():
    """Provide a sample course for testing"""
    return Course(
        title="Introduction to Machine Learning",
        instructor="Dr. Jane Smith",
        course_link="https://example.com/ml-course",
        lessons=[
            Lesson(
                lesson_number=0,
                title="Introduction",
                lesson_link="https://example.com/ml-course/lesson-0",
                content="Welcome to the Machine Learning course. This course covers fundamental concepts of ML."
            ),
            Lesson(
                lesson_number=1,
                title="Supervised Learning",
                lesson_link="https://example.com/ml-course/lesson-1",
                content="Supervised learning involves training models with labeled data. Key algorithms include linear regression and decision trees."
            )
        ]
    )


@pytest.fixture
def sample_course_chunks(sample_course):
    """Provide sample course chunks for testing"""
    return [
        CourseChunk(
            course_title=sample_course.title,
            lesson_number=0,
            chunk_index=0,
            text="Welcome to the Machine Learning course. This course covers fundamental concepts of ML.",
            metadata={
                "course_title": sample_course.title,
                "lesson_number": 0,
                "chunk_index": 0
            }
        ),
        CourseChunk(
            course_title=sample_course.title,
            lesson_number=1,
            chunk_index=0,
            text="Supervised learning involves training models with labeled data.",
            metadata={
                "course_title": sample_course.title,
                "lesson_number": 1,
                "chunk_index": 0
            }
        )
    ]


@pytest.fixture
def mock_rag_system():
    """Provide a mock RAG system for testing"""
    rag_system = MagicMock()

    # Mock query method - returns tuple of (answer, sources list)
    # Sources are dicts with 'text' and 'url' keys
    rag_system.query.return_value = (
        "Machine learning is a field of artificial intelligence that focuses on building systems that can learn from data.",
        [
            {
                "text": "Introduction to Machine Learning - Lesson 0",
                "url": "https://example.com/ml-course/lesson-0"
            }
        ]
    )

    # Mock session manager
    rag_system.session_manager.create_session.return_value = "test_session_123"
    rag_system.session_manager.sessions = {}

    # Mock analytics method
    rag_system.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Introduction to Machine Learning", "Advanced Deep Learning"]
    }

    return rag_system


@pytest.fixture
def mock_vector_store():
    """Provide a mock vector store for testing"""
    vector_store = MagicMock()
    vector_store.search_courses.return_value = [
        {
            "title": "Introduction to Machine Learning",
            "instructor": "Dr. Jane Smith",
            "course_link": "https://example.com/ml-course"
        }
    ]
    vector_store.search_content.return_value = [
        {
            "text": "Machine learning is a field of AI.",
            "metadata": {
                "course_title": "Introduction to Machine Learning",
                "lesson_number": 0
            }
        }
    ]
    vector_store.get_course_count.return_value = 2
    vector_store.get_existing_course_titles.return_value = [
        "Introduction to Machine Learning",
        "Advanced Deep Learning"
    ]
    return vector_store


@pytest.fixture
def mock_ai_generator():
    """Provide a mock AI generator for testing"""
    ai_generator = MagicMock()
    ai_generator.generate_response.return_value = "Machine learning is a field of artificial intelligence."
    return ai_generator


@pytest.fixture
def test_app(mock_rag_system):
    """
    Create a test FastAPI application without static file mounting.

    This avoids the issue where the frontend directory doesn't exist in tests.
    We recreate the API endpoints without the static file mounting.
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List, Optional

    # Create test app
    app = FastAPI(title="Course Materials RAG System - Test")

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Pydantic models (same as in app.py)
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class Source(BaseModel):
        text: str
        url: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[Source]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    class ClearSessionResponse(BaseModel):
        message: str
        session_id: str

    # API Endpoints (same as in app.py)
    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()

            answer, sources = mock_rag_system.query(request.query, session_id)

            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/sessions/{session_id}", response_model=ClearSessionResponse)
    async def clear_session(session_id: str):
        try:
            if not session_id:
                raise HTTPException(status_code=400, detail="No session ID provided")

            if session_id not in mock_rag_system.session_manager.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            mock_rag_system.session_manager.clear_session(session_id)

            return ClearSessionResponse(
                message="Session cleared successfully",
                session_id=session_id
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


@pytest.fixture
def client(test_app):
    """Provide a synchronous test client for the FastAPI app"""
    return TestClient(test_app)


@pytest.fixture
async def async_client(test_app):
    """Provide an async test client for the FastAPI app"""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def sample_query_request():
    """Provide a sample query request for testing"""
    return {
        "query": "What is machine learning?",
        "session_id": "test_session_123"
    }


@pytest.fixture
def sample_query_response():
    """Provide a sample query response for testing"""
    return {
        "answer": "Machine learning is a field of artificial intelligence that focuses on building systems that can learn from data.",
        "sources": [
            {
                "text": "Introduction to Machine Learning - Lesson 0",
                "url": "https://example.com/ml-course/lesson-0"
            }
        ],
        "session_id": "test_session_123"
    }


@pytest.fixture(autouse=True)
def reset_mocks(mock_rag_system):
    """Automatically reset all mocks after each test"""
    yield
    mock_rag_system.reset_mock()
