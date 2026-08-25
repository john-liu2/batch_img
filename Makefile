# Makefile to clean, lint and test with code coverage
# Copyright © 2025 - Present John Liu

# Typical workflow:
#   make test          # run all tests
#   make dist          # build sdist for distribution
#   make check         # validate the distribution files
#   make install-local # install into current venv and smoke-test

PYTHON_FILES = batch_img
VERSION ?= $(shell python -c "from batch_img.const import __version__; print(__version__)" 2>/dev/null || echo "0.0.0")

clean:
	rm -fr build .eggs batch_img.egg-info run_*.log .out dist wheels tests/data/.DS_Store
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr tests/.out tests/.DS_Store .coverage* htmlcov .pytest_cache uv.lock
	rm -fr docs/build out_*.yaml tmp_*

lint: clean
	pylint $(PYTHON_FILES) --ignore=venv,tests
	ruff check --fix --exit-non-zero-on-fix

test: lint
	pytest --cov-report=term --cov=batch_img tests

dist: clean
	# Build wheel and sdist packages
	python -m build --sdist
	@echo "Distribution files created in ./dist/"

check: dist
	# Validate the distribution files
	python -m twine check dist/*
	@echo "Distribution files validated successfully"

install-local: check
	# Install package into current environment
	pip install --upgrade pip
	pip install --force-reinstall dist/*.gz
	@echo "Package installed successfully"
	# Smoke test the installation
	batch_img --version
	batch_img --help
	@echo "Smoke test completed successfully"

.PHONY: clean lint test dist check install-local
