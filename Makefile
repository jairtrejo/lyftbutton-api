.PHONY: all nodeps test check lint coverage clean

all: clean check
	pip install -t dist .

nodeps:
	pip install --no-deps --upgrade -t dist .

test:
	pytest

check: lint coverage

lint:
	black --line-length 79 --check --exclude dist .
	flake8 --exclude dist .
	isort --check --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width=79 lyftbutton/**/*.py test/**/*.py

coverage:
	coverage run --source lyftbutton -m py.test
	coverage report --fail-under 75

clean:
ifneq ($(wildcard dist/**),)
	rm -r ./dist/**
endif
	coverage erase
