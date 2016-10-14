TEST_PATH=./

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

virtualenv:
	virtualenv -p `which python3` virtualenv

.requirements.txt-freezed: requirements.txt virtualenv
	./virtualenv/bin/pip install -r requirements.txt
	./virtualenv/bin/pip freeze >  .requirements.txt-freezed

install-prod-deps: .requirements.txt-freezed

.requirements-test.txt-freezed: requirements-test.txt .requirements.txt-freezed
	./virtualenv/bin/pip install -r requirements-test.txt
	./virtualenv/bin/pip freeze >  .requirements-test.txt-freezed

install-test-deps: .requirements-test.txt-freezed

.requirements-dev.txt-freezed: requirements-dev.txt .requirements-test.txt-freezed
	./virtualenv/bin/pip install -r requirements-dev.txt
	./virtualenv/bin/pip freeze >  .requirements-dev.txt-freezed

install-dev-deps: .requirements-dev.txt-freezed

.requirements-doc.txt-freezed: requirements-doc.txt .requirements.txt-freezed
	./virtualenv/bin/pip install -r requirements-doc.txt
	./virtualenv/bin/pip freeze >  .requirements-doc.txt-freezed

install-doc-deps: .requirements-doc.txt-freezed

# test: clean-pyc
test: .requirements-test.txt-freezed
	./virtualenv/bin/nosetests

tdd: .requirements-test.txt-freezed
	./virtualenv/bin/sniffer

coverage: .requirements-test.txt-freezed
	./virtualenv/bin/coverage run -m unittest discover
	./virtualenv/bin/coverage xml
	./virtualenv/bin/coverage html
	./virtualenv/bin/coverage report --fail-under 100
