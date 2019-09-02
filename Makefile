SHELL := bash
DOCKER=docker-compose run --rm
PYTHON=python3.7


install:
		pip install -q -r requirements.txt

install-dev: install
		pip install -q -r requirements-test.txt

venv:
		$(PYTHON) -m venv --prompt hub venv
		source venv/bin/activate
		pip install --quiet --upgrade pip

lint:
		pycodestyle hub/ tests/

clean-pyc:
		find . -name '__pycache__' -exec rm -r "{}" +
		find . -name '*.pyc' -delete
		find . -name '*~' -delete

test: clean-pyc lint
		pytest
		coveralls

travis-test:
		pip install -q pycodestyle
		$(MAKE) lint
		$(MAKE) docker-build
		$(DOCKER) hub scripts/test.sh
		$(MAKE) docker-stop

docker-test: docker-build
		# Clean up even if there's an error
		$(DOCKER) hub scripts/test.sh || $(MAKE) docker-stop
		$(MAKE) docker-stop

docker-build: clean-pyc
		docker-compose build
		touch docker-build

docker-stop:
		docker-compose stop
		docker-compose rm -f

clean-docker:
		docker-compose down --rmi local
		rm docker-build

docker-shell: docker-build
		# Clean up even if there's an error
		$(DOCKER) hub scripts/devwrapper.sh bash || $(MAKE) docker-stop
		$(MAKE) docker-stop


.PHONY: install install-dev lint clean-pyc test docker-stop clean-docker shell