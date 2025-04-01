.PHONY: hooks-install
hooks-install:
	pre-commit install

.PHONY: hooks-update
hooks-update:
	pre-commit autoupdate


.PHONY: config
config:
	python3 scripts/update_config.py --input config.yml --output config.yml


.PHONY: check
check:
	ruff check --fix
	ruff format
	mypy app.py src tests

.PHONY: test
test:
	STREAMLIT_ENV=test pytest
