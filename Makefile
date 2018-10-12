.PHONY: all nodeps lint test clean

all: clean check
	pip install -t dist .

nodeps:
	pip install --no-deps --upgrade -t dist .

check: lint test

lint:
	black --line-length 79 --check --exclude dist .
	flake8 --exclude dist .

test:
	pytest

clean:
ifneq ($(wildcard dist/**),)
	rm -r ./dist/**
endif
