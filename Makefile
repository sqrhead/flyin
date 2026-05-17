PYTHON = python3
MAIN = main.py

all: run

install:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install arcade
	.venv/bin/python -m pip install build mypy flake8
	.venv/bin/python -m build
	.venv/bin/python -m pip install dist/mazegen-1.0.0-py3-none-any.whl

run:
	.venv/bin/python $(MAIN)

debug:
	.venv/bin/python -m pdb $(MAIN)

lint:
	.venv/bin/flake8 . --exclude=.venv,dist,build
	.venv/bin/mypy . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude .venv

lint-strict:
	.venv/bin/flake8 . --exclude=.venv,dist,build
	.venv/bin/mypy . --strict --exclude .venv

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .venv

.PHONY: all install run debug lint lint-strict clean