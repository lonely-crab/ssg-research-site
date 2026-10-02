PYTHON ?= python3

.PHONY: experiment lint build serve sphinx measure helios

experiment:
	"$(PYTHON)" scripts/run_experiment.py

lint: experiment
	mkdocs build --strict

build: lint

serve: experiment
	mkdocs serve -a 127.0.0.1:8000

sphinx: experiment
	$(MAKE) -C generators/sphinx html

measure: experiment
	"$(PYTHON)" scripts/measure.py

helios:
	SITE_URL=https://se.ifmo.ru/~s336402/ "$(MAKE)" build PYTHON="$(PYTHON)"
	bash scripts/deploy_helios.sh
