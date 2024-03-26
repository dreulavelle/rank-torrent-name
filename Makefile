.PHONY: install lint format check test clean coverage benchmark pr-ready publish

SRC_DIR := ./RTN

# Install dependencies
install:
	poetry install

# Clean up pyc files and __pycache__ directories
clean:
	@find . -type f -name '*.pyc' -exec rm -f {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '.pytest_cache' -exec rm -rf {} +
	@find . -type d -name '.ruff_cache' -exec rm -rf {} +

# Run linters
lint:
	poetry run ruff check $(SRC_DIR)
	poetry run isort --check-only $(SRC_DIR)

# Format code
format:
	poetry run isort $(SRC_DIR)
	poetry run black $(SRC_DIR)

# Type checking
check:
	poetry run pyright

# Run tests
test:
	@poetry run pytest

# Run tests with coverage
coverage:
	@poetry run coverage xml
	@poetry run coverage html
	@poetry run coverage report -m

benchmark:
	poetry run python benchmarks/rank.py

pr-ready: clean format lint check test

publish:
	poetry publish --build