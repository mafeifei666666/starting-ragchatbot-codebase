#!/bin/bash
# Run all quality checks

set -e

echo "================================"
echo "Running Code Quality Checks"
echo "================================"
echo ""

echo "1. Checking import sorting..."
uv run isort --check-only --diff . > /dev/null 2>&1
echo "   ✓ Import sorting OK"
echo ""

echo "2. Checking code formatting..."
uv run black --check . > /dev/null 2>&1
echo "   ✓ Code formatting OK"
echo ""

echo "3. Running flake8 linter..."
uv run flake8 .
echo "   ✓ Flake8 checks passed"
echo ""

echo "4. Running type checker (informational)..."
if uv run mypy backend/ main.py > /dev/null 2>&1; then
    echo "   ✓ Type checking passed"
else
    echo "   ⚠ Type checking found issues (non-blocking)"
fi
echo ""

echo "================================"
echo "All critical quality checks passed! ✓"
echo "================================"
