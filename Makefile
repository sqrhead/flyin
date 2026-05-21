# Fly-In — Windows (Git Bash / MSYS) + Linux / Debian

MAIN := main.py
MAP  ?= maps/easy/01_linear_path.txt
VENV := .venv
STAMP := $(VENV)/.install-stamp

ifeq ($(OS),Windows_NT)
    PYTHON  := $(VENV)/Scripts/python.exe
    FLAKE8  := $(VENV)/Scripts/flake8.exe
    VENV_PY := python
else
    PYTHON  := $(VENV)/bin/python
    FLAKE8  := $(VENV)/bin/flake8
    VENV_PY := python3
endif

EXCLUDE := --exclude $(VENV)

MYPY_FLAGS := \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

.PHONY: all install run debug lint lint-strict clean

all: run

$(PYTHON):
	$(VENV_PY) -m venv $(VENV)

# Runs once until you make clean
install: $(STAMP)

$(STAMP): $(PYTHON)
	$(PYTHON) -m pip install -q --no-cache-dir --upgrade pip
	$(PYTHON) -m pip install -q --no-cache-dir arcade flake8 mypy
	@touch $(STAMP)

run: install
	$(PYTHON) $(MAIN) $(MAP)

debug: install
	$(PYTHON) -m pdb $(MAIN) $(MAP)

lint: install
	$(FLAKE8) . $(EXCLUDE)
	$(PYTHON) -m mypy . $(EXCLUDE) $(MYPY_FLAGS)

lint-strict: install
	$(FLAKE8) . $(EXCLUDE)
	$(PYTHON) -m mypy . $(EXCLUDE) --strict

clean:
	rm -rf $(VENV) output.txt
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
