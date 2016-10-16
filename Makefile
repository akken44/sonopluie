TEST_PATH=./
UNAME_S := $(shell uname -s)

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

lint:
	flake8 --exclude=.tox

.tox/py35:
	tox --notest

.requirements.txt-freezed: requirements.txt .tox/py35
	./.tox/py35/bin/pip install -r requirements.txt
	./.tox/py35/bin/pip freeze >  .requirements.txt-freezed

install-prod-deps: .requirements.txt-freezed

.requirements-test.txt-freezed: requirements-test.txt .requirements.txt-freezed
	./.tox/py35/bin/pip install -r requirements-test.txt
	./.tox/py35/bin/pip freeze >  .requirements-test.txt-freezed

install-test-deps: .requirements-test.txt-freezed

.requirements-dev.txt-freezed: requirements-dev.txt requirements-$(UNAME_S).txt .requirements-test.txt-freezed
	./.tox/py35/bin/pip install -r requirements-dev.txt
	./.tox/py35/bin/pip install -r requirements-$(UNAME_S).txt
	./.tox/py35/bin/pip freeze >  .requirements-dev.txt-freezed

install-dev-deps: .requirements-dev.txt-freezed

.requirements-doc.txt-freezed: requirements-doc.txt .requirements.txt-freezed
	./.tox/py35/bin/pip install -r requirements-doc.txt
	./.tox/py35/bin/pip freeze >  .requirements-doc.txt-freezed

install-doc-deps: .requirements-doc.txt-freezed

# test: clean-pyc
test: .requirements-test.txt-freezed
	./.tox/py35/bin/py.test tests --pep8 --mccabe

tdd: .requirements-dev.txt-freezed
	./.tox/py35/bin/sniffer

isort: .requirements-test.txt-freezed
	./.tox/py35/bin/isort --skip-glob=.tox --recursive --diff . 

coverage: .requirements-test.txt-freezed
	./.tox/py35/bin/coverage run -m unittest discover
	./.tox/py35/bin/coverage xml
	./.tox/py35/bin/coverage html
	./.tox/py35/bin/coverage report --fail-under 100
