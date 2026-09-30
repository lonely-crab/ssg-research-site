PYTHON ?= python3

.PHONY: experiment lint build serve sphinx measure

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
