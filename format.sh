#!/bin/bash
# Format code with isort and black

set -e

echo "Running isort to organize imports..."
uv run isort .

echo "Running black to format code..."
uv run black .

echo "Code formatting complete!"
