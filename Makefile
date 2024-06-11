.PHONY: install lint check test clean coverage benchmark pr-ready publish sort

SRC_DIR := ./RTN

# Install dependencies (with dev deps for development)
install:
	@poetry install --with dev

# Clean up pyc files and __pycache__ directories
clean:
	@find . -type f -name '*.pyc' -exec rm -f {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '.pytest_cache' -exec rm -rf {} +
	@find . -type d -name '.ruff_cache' -exec rm -rf {} +

# Run linters
lint:
	@poetry run ruff check $(SRC_DIR)
	@poetry run isort $(SRC_DIR)

# Sort imports
sort:
	@poetry run isort $(SRC_DIR)

# Type checking
check:
	@poetry run pyright

# Run tests
test:
	@poetry run pytest
	@poetry run pyright $(SRC_DIR)

# Run tests with coverage
coverage: clean
	@poetry run pytest --cov=$(SRC_DIR) --cov-report=xml --cov-report=term
	@poetry run pyright $(SRC_DIR)

benchmark:
	@poetry run python benchmarks/rank.py --quiet

pr-ready: clean lint test

publish:
	@poetry publish --build