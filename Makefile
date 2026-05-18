# ==============================================================================
#                      42 FLY-IN DRONE SIMULATOR MAKEFILE
# ==============================================================================

PYTHON       := python3
VENV_DIR     := .venv
MAIN_SCRIPT  := main.py

# Detect Operating System and Shell Profiles
ifeq ($(OS),Windows_NT)
    ifneq ($(findstring /,$(SHELL)),)
        VENV_BIN    := $(VENV_DIR)/Scripts
        VENV_PYTHON := $(VENV_BIN)/python
        VENV_PIP    := $(VENV_BIN)/pip
        RM          := rm -f
        RMDIR       := rm -rf
    else
        VENV_BIN    := $(VENV_DIR)/Scripts
        VENV_PYTHON := $(VENV_BIN)/python.exe
        VENV_PIP    := $(VENV_BIN)/pip.exe
        RM          := del /q /s
        RMDIR       := rmdir /s /q
    endif
else
    VENV_BIN    := $(VENV_DIR)/bin
    VENV_PYTHON := $(VENV_BIN)/python
    VENV_PIP    := $(VENV_BIN)/pip
    RM          := rm -f
    RMDIR       := rm -rf
endif

.PHONY: all install run lint lint-strict clean help

all: install run

install: $(VENV_PYTHON)

$(VENV_PYTHON):
	@python -m venv $(VENV_DIR) > /dev/null 2>&1
	@$(VENV_PYTHON) -m pip install --upgrade pip -q > /dev/null 2>&1
	@$(VENV_PYTHON) -m pip install --no-cache-dir arcade flake8 mypy -q > /dev/null 2>&1

run: $(VENV_PYTHON)
	@$(VENV_PYTHON) $(MAIN_SCRIPT)

lint: $(VENV_PYTHON)
	@echo "Checking style guidelines (flake8)..."
	@$(VENV_BIN)/flake8 . --exclude=$(VENV_DIR),dist,build,*.egg-info --exit-zero
	@echo "Verifying type-safety constraints (mypy)..."
	@$(VENV_BIN)/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude $(VENV_DIR)

lint-strict: $(VENV_PYTHON)
	@echo "Checking strict styling parameters (flake8)..."
	@$(VENV_BIN)/flake8 . --exclude=$(VENV_DIR),dist,build,*.egg-info --exit-zero
	@echo "Verifying strict type enforcement (mypy --strict)..."
	@$(VENV_BIN)/mypy . --strict --exclude $(VENV_DIR)

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(VENV_DIR) 2>/dev/null || true
	@echo "Workspace clean complete."

