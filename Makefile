.PHONY: hooks-install
hooks-install:
	pre-commit install

.PHONY: hooks-update
hooks-update:
	pre-commit autoupdate

.PHONY: check
check:
	ruff check --fix
	ruff format
	mypy app.py src tests

.PHONY: test
test:
	pytest
