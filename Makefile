.PHONY: all nodeps lint test clean

all: clean check
	pip install -t dist .

nodeps:
	pip install --no-deps --upgrade -t dist .

check: lint test

lint:
	black --line-length 79 --check --exclude dist .
	flake8 --exclude dist .
	isort --check --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width=79 lyftbutton/**/*.py test/**/*.py

test:
	pytest

clean:
ifneq ($(wildcard dist/**),)
	rm -r ./dist/**
endif
