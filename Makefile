UV = uv
MIX = mix

.PHONY: all install install-elixir install-python run run-python test lint validate clean

all: install

install: install-elixir install-python

install-elixir:
	$(MIX) deps.get

install-python:
	cd pythonbridge && $(UV) sync

run:
	$(MIX) run

# TODO: Temporary until Elixir webhook server is set up
run-python:
	cd pythonbridge && PYTHONPATH=$(PWD) $(UV) run python -m pythonbridge.main

test:
	$(MIX) test
	cd pythonbridge && PYTHONPATH=$(PWD) $(UV) run python -m unittest discover -s tests -v

format:
	$(MIX) format
	cd pythonbridge && $(UV) run ruff format .

lint:
	$(MIX) format --check-formatted
	cd pythonbridge && $(UV) run ruff check .

validate: format lint test

clean:
	rm -rf _build deps
	rm -rf pythonbridge/.venv pythonbridge/__pycache__
