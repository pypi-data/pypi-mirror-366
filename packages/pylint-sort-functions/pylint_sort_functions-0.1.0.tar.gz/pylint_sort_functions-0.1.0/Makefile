ROOT := $(shell pwd)

.PHONY: coverage docs mypy ruff-check ruff-fix ruff-format test test-plugin tox
.PHONY: publish-to-pypi rstcheck

coverage:
	coverage run -m pytest tests
	coverage report -m

coverage-html:
	coverage run -m pytest tests
	coverage html

docs:
	cd "$(ROOT)"/docs && make clean && make html

mypy:
	mypy src/ tests/

pre-commit:
	pre-commit run --all-files

publish-to-pypi:
	uv build
	twine upload dist/*

# NOTE: to avoid rstcheck to fail on info-level messages, we set the report-level to WARNING
rstcheck:
	rstcheck --report-level=WARNING -r docs/

ruff-check:
	ruff check src tests

ruff-fix:
	ruff check --fix src tests

ruff-format:
	ruff format src tests

test:
	pytest tests/

test-plugin:
	pylint --load-plugins=pylint_sort_functions src/
	pylint --load-plugins=pylint_sort_functions tests/

tox:
	tox

view-docs:
	@xdg-open "file://$(ROOT)/docs/_build/html/index.html"
