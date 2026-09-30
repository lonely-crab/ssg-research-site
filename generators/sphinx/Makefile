SPHINXBUILD ?= sphinx-build

.PHONY: html

html:
	mkdir -p _static img
	cp -f ../../docs/generated/latency.png img/ || true
	cp -f ../../docs/generated/latency_plotly.html _static/ || true
	cp -f ../../docs/assets/pipeline.svg img/ || true
	cp -f ../../refs.bib refs.bib
	$(SPHINXBUILD) -b html . _build/html
