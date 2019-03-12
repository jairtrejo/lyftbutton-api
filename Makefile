.PHONY: all nodeps test check lint coverage package deploy clean

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

package: all
	sam package --s3-bucket artifacts.jairtrejo.mx --output-template-file packaged-template.yaml

deploy: package
ifneq ($(PROD), true)
	sam deploy --template-file packaged-template.yaml --stack-name lyftbutton-api-dev --capabilities CAPABILITY_IAM --parameter-overrides CorsDomain=http://localhost:9966
else
	sam deploy --template-file packaged-template.yaml --stack-name lyftbutton-api --capabilities CAPABILITY_IAM --parameter-overrides Stage=Prod CorsDomain=https://www.lyftbutton.com DomainName=api.lyftbutton.com SSLCertificateArn=arn:aws:acm:us-east-1:501965419031:certificate/64366556-0f07-47a3-8e64-856e3092a26a HostedZoneId=Z2R6LE4JEIXXVR
endif

clean:
ifneq ($(wildcard dist/**),)
	rm -r ./dist/**
endif
	coverage erase
