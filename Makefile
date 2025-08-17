# Makefile to clean, lint and test with code coverage
# Copyright © 2025 John Liu

PYTHON_FILES = batch_img

clean:
	rm -fr build .eggs batch_img.egg-info run_*.log .out dist wheels tests/data/.DS_Store
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr tests/.out tests/.DS_Store .coverage htmlcov .pytest_cache uv.lock
	rm -fr docs/build out_*.yaml tmp_*

lint: clean
	pylint $(PYTHON_FILES) --ignore=venv,tests
	ruff check --fix --exit-non-zero-on-fix

test: lint
	pytest --cov-report=term --cov=batch_img tests
