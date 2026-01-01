#!/bin/bash
# Run linting checks without modifying code

set -e

echo "Checking import sorting with isort..."
uv run isort --check-only --diff .

echo "Checking code formatting with black..."
uv run black --check --diff .

echo "Running flake8 for code quality..."
uv run flake8 .

echo "Running mypy for type checking (informational)..."
uv run mypy backend/ main.py || echo "⚠ Type checking found issues (non-blocking)"

echo "All critical lint checks passed!"
