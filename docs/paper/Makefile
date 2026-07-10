# Makefile for prabodha paper (MDPI Symmetry)
# Uses latexmk for robust three-pass LaTeX+BibTeX cycle
# Usage:
#   make          -- build PDF (full cycle)
#   make clean    -- remove auxiliary files
#   make distclean -- remove auxiliary + PDF

MAIN   = paper
LATEXMK = ~/.local/bin/latexmk
FLAGS  = -pdf -interaction=nonstopmode -halt-on-error

.PHONY: all clean distclean

all: $(MAIN).pdf

# Use latexmk to manage the pdflatex → bibtex → pdflatex cycle
$(MAIN).pdf: $(MAIN).tex references.bib \
             sections/abstract.tex \
             sections/introduction.tex \
             sections/background.tex \
             sections/methodology.tex \
             sections/experimental_setup.tex \
             sections/results.tex \
             sections/discussion.tex \
             sections/conclusion.tex \
             sections/appendix.tex
	$(LATEXMK) $(FLAGS) $(MAIN).tex

clean:
	$(LATEXMK) -c
	rm -f $(MAIN).bbl $(MAIN).blg

distclean: clean
	$(LATEXMK) -C
	rm -f $(MAIN).pdf
