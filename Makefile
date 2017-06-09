.PHONY: docs

run-tests:
	pipenv run pytest
init:
	python setup.py install
	pip install pipenv
	pipenv install --dev
docs:
	cd docs && make html
