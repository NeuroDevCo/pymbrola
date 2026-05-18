# Minimal makefile for Sphinx documentation
# You can set these variables from the environment before running `make`.

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
PAPER         ?=
BUILDDIR      ?= _build

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The "$(SPHINXBUILD)" command was not found. Make sure you have Sphinx installed, then set the "$(SPHINXBUILD)" in your PATH. Alternatively you can specify the SPHINXBUILD environment variable to specify sphinx-build executable.)
endif

# Internal variables
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
DOCDIR          = $(CURDIR)

.PHONY: help Makefile

# Put it first so that make stops here if you make `help` first
help:
	@$(SPHINXBUILD) -M help "$(DOCDIR)" "$(BUILDDIR)" $(ALLSPHINXOPTS)

.PHONY: $(SPHINXBUILD) SPHINXBUILD
SPHINXBUILD:
	@$(SPHINXBUILD) -M html "$(DOCDIR)" "$(BUILDDIR)" $(ALLSPHINXOPTS)

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(DOCDIR)" "$(BUILDDIR)" $(ALLSPHINXOPTS)