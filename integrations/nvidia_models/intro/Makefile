.PHONY: all format lint test tests integration_tests help

# Default target executed when no arguments are given to make.
all: help

install: ## Install the poetry environment and dependencies
	poetry install --no-root

clean: ## Clean up cache directories and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.pyc" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	rm -rf dist/
	rm -rf build/

######################
# LINTING AND FORMATTING
######################

# Define a variable for Python and notebook files.
PYTHON_FILES=.
MYPY_CACHE=.mypy_cache
lint: ## Run code quality tools
	poetry run ruff check $(PYTHON_FILES)
	poetry run ruff format $(PYTHON_FILES) --check

format: ## Format code using ruff
	poetry run ruff format $(PYTHON_FILES)
	poetry run ruff check $(PYTHON_FILES) --fix

######################
# HELP
######################

help:
	@echo '----'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
