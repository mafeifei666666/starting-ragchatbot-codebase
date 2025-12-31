# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Retrieval-Augmented Generation (RAG) system for course materials that uses OpenAI's GPT models for AI generation and ChromaDB for vector storage. The application consists of a FastAPI backend and vanilla JavaScript frontend.

## Key Commands

### Development

```bash
# Install dependencies
uv sync

# Run server (development with auto-reload)
cd backend && uv run uvicorn app:app --reload --port 8000

# Quick start script
./run.sh
```

### Environment Setup

- Create `.env` in project root with: `OPENAI_API_KEY=your_key_here`
- Currently configured to use `gpt-5.2` model (see `backend/config.py`)

## Architecture Overview

### RAG Pipeline Flow

1. **Document Ingestion** (`document_processor.py`): Parses course documents with specific format (title, instructor, lessons), chunks text with overlap
2. **Vector Storage** (`vector_store.py`): Dual ChromaDB collections:
   - `course_catalog`: Course metadata for semantic course name matching
   - `course_content`: Chunked lesson content for retrieval
3. **Query Processing** (`rag_system.py`): Orchestrates search → AI generation → response
4. **AI Generation** (`ai_generator.py`): OpenAI API integration with function calling for search tools

### OpenAI Tool Calling Integration

The system uses OpenAI's function calling to let the AI decide when to search course content:

**Tool Definition Format** (`search_tools.py`):

- OpenAI requires `{"type": "function", "function": {...}}` wrapper
- Tool name is nested: `tool_def["function"]["name"]` not `tool_def["name"]`
- The `register_tool()` method handles this nesting

**Tool Execution Flow**:

1. AI decides to call `search_course_content` function
2. `ToolManager` executes search via `CourseSearchTool`
3. Results returned to AI with `role: "tool"` messages
4. AI synthesizes final response

### API Parameter Compatibility

**Important**: Newer GPT models (gpt-5.x) use different parameters:

- Use `max_completion_tokens` instead of `max_tokens`
- This is already configured in `ai_generator.py`

### Document Format

Course documents in `docs/` folder must follow this structure:

```
Course Title: [title]
Course Link: [url]
Course Instructor: [name]

Lesson 0: Introduction
Lesson Link: [url]
[lesson content]

Lesson 1: Next Topic
...
```

### Vector Store Design

**Two-collection approach**:

- `course_catalog`: Enables fuzzy course name matching (user says "MCP" → finds "MCP: Build Rich-Context AI Apps")
- `course_content`: Stores actual searchable chunks with metadata filters

**Metadata structure**:

- Course chunks: `{course_title, lesson_number, chunk_index}`
- Catalog entries: `{title, instructor, course_link, lessons_json, lesson_count}`

### Session Management

Sessions track conversation history for context:

- `SessionManager` stores per-session message history
- Limited to `MAX_HISTORY` exchanges (configured in `config.py`)
- History passed to AI as string in system prompt

## Frontend-Backend Communication

**Frontend** (`frontend/script.js`):

- Vanilla JavaScript, no framework
- Sends POST to `/api/query` with `{query, session_id}`
- Displays sources returned from tool searches

**Backend** (`backend/app.py`):

- FastAPI with CORS enabled
- Serves static frontend from `frontend/`
- Auto-loads documents from `docs/` on startup

## Configuration

All settings in `backend/config.py`:

- `OPENAI_API_KEY`: from environment
- `OPENAI_MODEL`: currently "gpt-5.2"
- `EMBEDDING_MODEL`: "all-MiniLM-L6-v2" for vector embeddings
- `CHUNK_SIZE`: 800 chars with 100 char overlap
- `MAX_RESULTS`: 5 search results returned to AI

## Important Implementation Details

### Chunking Strategy

- Sentence-based chunking with overlap (not character-based)
- Preserves sentence boundaries
- First chunk of each lesson includes "Lesson X content:" prefix for context

### Tool Calling Differences from Anthropic

This codebase was migrated from Anthropic's Claude API to OpenAI. Key differences:

- Anthropic: `input_schema` → OpenAI: `parameters`
- Anthropic: `tool_choice: {"type": "auto"}` → OpenAI: `tool_choice: "auto"`
- Anthropic: `response.stop_reason == "tool_use"` → OpenAI: `response.choices[0].finish_reason == "tool_calls"`
- Message format: OpenAI requires system message in messages array, not separate parameter

### Development Mode

- FastAPI runs with `--reload` for auto-restart on code changes
- Frontend has cache-busting headers in development (`DevStaticFiles` class)
