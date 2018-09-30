all: clean
	pip install -t dist .

nodeps:
	pip install --no-deps --upgrade -t dist .

clean:
ifneq ($(wildcard dist/**),)
	rm -r ./dist/**
endif
