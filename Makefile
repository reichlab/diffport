.PHONY: docs

run-tests:
	pipenv run pytest
init:
	python setup.py install
	pipenv install --dev
docs:
	cd docs && make html
