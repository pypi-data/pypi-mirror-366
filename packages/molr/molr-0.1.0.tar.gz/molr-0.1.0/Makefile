# MolR Development Makefile

.PHONY: help install install-dev test test-all test-fast test-unit test-integration test-performance test-coverage clean lint format type-check docs docs-watch build publish

# Default target
help:
	@echo "MolR Development Commands:"
	@echo "  install       Install package in development mode"
	@echo "  install-dev   Install with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run comprehensive test suite (excludes slow tests)"
	@echo "  test-all      Run ALL tests including slow performance tests"
	@echo "  test-fast     Run fast tests only (unit tests)"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration Run integration tests"
	@echo "  test-performance Run performance benchmark tests"
	@echo "  test-coverage Generate test coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          Run code linting (flake8)"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run type checking with mypy"
	@echo ""
	@echo "Building:"
	@echo "  build         Build Python package"
	@echo "  publish       Publish to PyPI (requires credentials)"
	@echo ""
	@echo "Development:"
	@echo "  clean         Clean build artifacts"
	@echo "  docs          Build documentation"
	@echo "  docs-watch    Build and watch documentation with live reload"
	@echo "  docs-serve    Serve documentation locally"

# Installation
install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:
	@echo "Running all tests except slow ones..."
	pytest tests/ -v -m "not slow"

test-all:
	@echo "Running ALL tests including slow ones..."
	pytest tests/ -v

test-fast:
	@echo "Running fast unit tests only..."
	pytest tests/unit/ -v -m "not slow"

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v -m "integration"

test-performance:
	@echo "Running performance tests..."
	pytest tests/performance/ -v -m "performance"

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ -v -m "not slow" --cov=molr --cov-branch --cov-report=term-missing --cov-report=xml --cov-report=html

# Code quality
lint:
	@echo "Running flake8..."
	flake8 molr/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format:
	@echo "Formatting with black..."
	black molr/ tests/ *.py
	@echo "Sorting imports with isort..."
	isort molr/ tests/ *.py

type-check:
	@echo "Type checking with mypy..."
	mypy molr/ --ignore-missing-imports

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf */*/__pycache__/
	rm -rf */*/*/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf docs/build/
	rm -rf .tox/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name ".DS_Store" -delete

# Documentation
docs:
	@echo "Building documentation..."
	sphinx-build -b html docs/source/ docs/build/html/

docs-watch:
	@echo "Building and watching documentation with live reload..."
	@echo "Opening documentation at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	sphinx-autobuild docs/source/ docs/build/html/ --host 0.0.0.0 --port 8000 --open-browser

docs-serve:
	@echo "Serving documentation locally..."
	@if [ -f docs/build/html/index.html ]; then \
		echo "Opening documentation at http://localhost:8000"; \
		cd docs/build/html && python -m http.server 8000; \
	else \
		echo "Documentation not built. Run 'make docs' first."; \
	fi

# Package building
build:
	@echo "Building package with modern build system..."
	python -m build

publish: clean build
	@echo "Publishing to PyPI..."
	@echo "This will upload to the real PyPI. Continue? [y/N]"
	@read ans && [ $${ans:-N} = y ]
	python -m twine upload dist/*

publish-test: clean build
	@echo "Publishing to TestPyPI..."
	python -m twine upload --repository testpypi dist/*

# Development helpers
dev-install:
	@echo "Installing package in development mode with all extras..."
	pip install -e ".[dev,docs]"

check-manifest:
	@echo "Checking MANIFEST.in..."
	check-manifest

# Quick checks before committing
pre-commit: format lint type-check test-fast
	@echo "Pre-commit checks passed!"

# Create source distribution
sdist:
	python -m build --sdist

# Create wheel distribution
wheel:
	python -m build --wheel

# Check distribution
check-dist: build
	@echo "Checking distribution..."
	twine check dist/*

# Version management
version:
	@python -c "import molr; print(f'MolR version: {molr.__version__}')"

# Example usage
example:
	@echo "Running example analysis..."
	@python -c "import molr; s = molr.Structure(10); print(s)"