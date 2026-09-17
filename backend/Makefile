.PHONY: help install dev test clean

help:
	@echo "make install  - install the app and its dev/test dependencies"
	@echo "make dev      - run the API with auto-reload (http://localhost:8000/docs)"
	@echo "make test     - run the test suite"
	@echo "make clean    - remove caches and build artifacts"

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

clean:
	rm -rf .pytest_cache **/__pycache__ *.egg-info
