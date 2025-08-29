# ------------------------------------------------------------------------------
# DEFAULT_GOAL
# ------------------------------------------------------------------------------
.DEFAULT_GOAL := all

# ------------------------------------------------------------------------------
# PROJECT_NAME: vedro
# ------------------------------------------------------------------------------
PROJECT_NAME=vedro

# ------------------------------------------------------------------------------
# install
# Purpose: Set up the Python environment for the project.
# Details:
# - Upgrades pip to the latest version.
# - Installs dependencies from both requirements.txt and requirements-dev.txt.
# ------------------------------------------------------------------------------
.PHONY: install
install:
	pip3 install --quiet --upgrade pip
	pip3 install --quiet -r requirements.txt -r requirements-dev.txt

# ------------------------------------------------------------------------------
# build
# Purpose: Create distribution packages (source and wheel) for the project.
# Details:
# - Upgrades pip, setuptools, wheel, and twine.
# - Builds the distribution packages using setup.py.
# ------------------------------------------------------------------------------
.PHONY: build
build:
	pip3 install --quiet --upgrade pip
	pip3 install --quiet --upgrade setuptools wheel twine
	python3 setup.py sdist bdist_wheel

# ------------------------------------------------------------------------------
# test
# Purpose: Run the project's tests.
# Details:
# - Executes tests using pytest and vedro.
# ------------------------------------------------------------------------------
.PHONY: test
test:
	python3 -m pytest
	python3 -m vedro tests/

# ------------------------------------------------------------------------------
# coverage
# Purpose: Measure test coverage for both pytest and vedro tests.
# Details:
# - Runs pytest tests with coverage tracking.
# - Runs vedro tests with coverage tracking (appending to existing data).
# - Merges coverage data from both test runners.
# - Outputs a report in the terminal and writes an XML report.
# ------------------------------------------------------------------------------
.PHONY: coverage
coverage:
	python3 -m coverage erase
	python3 -m coverage run -a -m pytest
	python3 -m coverage run -a -m vedro run tests/

	python3 -m coverage report
	python3 -m coverage xml -o $(or $(COV_REPORT_DEST),coverage.xml)

# ------------------------------------------------------------------------------
# check-types
# Purpose: Ensure type correctness with strict checking.
# Details:
# - Runs mypy on the project directory (vedro) with strict settings.
# ------------------------------------------------------------------------------
.PHONY: check-types
check-types:
	python3 -m mypy ${PROJECT_NAME} --strict

# ------------------------------------------------------------------------------
# check-imports
# Purpose: Validate that import statements are properly sorted.
# Details:
# - Checks the import order in both the project and tests directories (without making changes).
# ------------------------------------------------------------------------------
.PHONY: check-imports
check-imports:
	python3 -m isort ${PROJECT_NAME} tests --check-only

# ------------------------------------------------------------------------------
# sort-imports
# Purpose: Automatically sort and organize import statements.
# Details:
# - Applies isort to both the project and tests directories to rearrange imports.
# ------------------------------------------------------------------------------
.PHONY: sort-imports
sort-imports:
	python3 -m isort ${PROJECT_NAME} tests

# ------------------------------------------------------------------------------
# check-style
# Purpose: Ensure code style consistency.
# Details:
# - Runs flake8 on the project and tests directories to enforce style guidelines.
# ------------------------------------------------------------------------------
.PHONY: check-style
check-style:
	python3 -m flake8 ${PROJECT_NAME} tests

# ------------------------------------------------------------------------------
# lint
# Purpose: Perform comprehensive code quality checks.
# Details:
# - Combines type checking, style checking, and import order verification.
# ------------------------------------------------------------------------------
.PHONY: lint
lint: check-types check-style check-imports

# ------------------------------------------------------------------------------
# all
# Purpose: Set up, lint, and test the project.
# Details:
# - Runs install, lint, and test commands sequentially.
# ------------------------------------------------------------------------------
.PHONY: all
all: install lint test

# ------------------------------------------------------------------------------
# test-in-docker
# Purpose: Run tests inside a Docker container.
# IMPORTANT: Useful for testing against different Python versions.
# Usage: For example, run with a specific version: PYTHON_VERSION=3.10 make test-in-docker
# Details:
# - Mounts the current directory into a Docker container using a Python image.
# - Executes the install and test commands inside the container.
# ------------------------------------------------------------------------------
.PHONY: test-in-docker
test-in-docker:
	docker run -v `pwd`:/tmp/app -w /tmp/app python:$(or $(PYTHON_VERSION),3.12) make install test

# ------------------------------------------------------------------------------
# all-in-docker
# Purpose: Run all commands (install, lint, test) inside a Docker container.
# IMPORTANT: Useful for running the full suite on different Python versions.
# Usage: For example, run with a specific version: PYTHON_VERSION=3.10 make all-in-docker
# Details:
# - Similar to test-in-docker, but executes the 'all' command.
# ------------------------------------------------------------------------------
.PHONY: all-in-docker
all-in-docker:
	docker run -v `pwd`:/tmp/app -w /tmp/app python:$(or $(PYTHON_VERSION),3.12) make all

# ------------------------------------------------------------------------------
# bump
# Purpose: Increment the project version.
# IMPORTANT: This command should only be run by repository maintainers.
# Details:
# - Uses bump2version with a target (specified as an argument) to update the version.
# - Displays the latest commit and verifies both the commit and the corresponding tag.
# - Note: The git push command is commented out; push changes manually when needed.
# ------------------------------------------------------------------------------
.PHONY: bump
bump:
	bump2version $(filter-out $@,$(MAKECMDGOALS))
	@git --no-pager show HEAD
	@echo
	@git verify-commit HEAD
	@git verify-tag `git describe`
	@echo
	# git push origin main --tags

# ------------------------------------------------------------------------------
# publish
# Purpose: Publish the built distribution packages.
# IMPORTANT: This command should only be run by repository maintainers.
# Details:
# - Uses twine to upload all files from the dist/ directory to a package repository (PyPI).
# ------------------------------------------------------------------------------
.PHONY: publish
publish:
	twine upload dist/*

# ------------------------------------------------------------------------------
# Default unknown command handler
# Purpose: Provide feedback when an unknown Makefile target is used.
# ------------------------------------------------------------------------------
.DEFAULT:
	@echo "Error: Unknown command"
	@echo "Please check the Makefile for available commands and usage instructions"
