VENV ?= venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

run: setup
	$(PYTHON) app.py
.PHONY: run

setup:
	test -d venv || python3 -m venv $(VENV)
	. "$(VENV)"/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
.PHONY: setup

clean:
	rm -rf __pycache__
	rm -rf $(VENV)
.PHONY: clean
