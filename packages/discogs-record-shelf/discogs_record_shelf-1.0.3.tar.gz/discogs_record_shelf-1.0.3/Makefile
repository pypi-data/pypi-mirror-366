.PHONY: help install install-dev test lint format type-check security clean build upload docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install       Install package in development mode"
	@echo "  install-dev   Install package with development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run all linting tools"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run mypy type checking"
	@echo "  security      Run security checks"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  upload        Upload package to PyPI"
	@echo "  docs          Build documentation"
	@echo "  tox           Run all tox environments"
	@echo "  setup         Initial project setup"

setup:
	@echo "Setting up development environment..."
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -e ".[dev]"
	@echo "Setup complete! Activate with: source venv/bin/activate"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=record_shelf --cov-report=html --cov-report=term-missing

lint:
	black --check --diff record_shelf tests
	isort --check-only --diff record_shelf tests
	flake8 record_shelf tests
	pylint record_shelf

format:
	black record_shelf tests
	isort record_shelf tests

type-check:
	mypy record_shelf

security:
	bandit -r record_shelf
	safety check

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .tox/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

docs:
	cd docs && python -m sphinx -b html . _build/html

docs-serve:
	cd docs/_build/html && python3 -m http.server 8000

docs-clean:
	rm -rf docs/_build docs/api/_autosummary

docs-rebuild: docs-clean docs
	@echo "Documentation rebuilt successfully!"

tox:
	tox

tox-parallel:
	tox -p auto

# Development shortcuts
dev-test: format lint type-check test
	@echo "All development checks passed!"

ci: lint type-check security test-cov
	@echo "CI checks completed!"

# Quick commands
qtest:
	pytest -x -v

qcov:
	pytest --cov=record_shelf --cov-report=term-missing -x

# Install pre-commit hooks
pre-commit:
	pip install pre-commit
	pre-commit install

pre-commit-all:
	pre-commit run --all-files

