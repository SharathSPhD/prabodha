MAIN = paper
LATEX = pdflatex
FLAGS = -interaction=nonstopmode -halt-on-error

SECTIONS = $(wildcard sections/*.tex)
FIGURES  = $(wildcard figures/*.tex)

all: $(MAIN).pdf

figures:
	python3 generate_figures.py

$(MAIN).pdf: $(MAIN).tex $(SECTIONS) $(FIGURES) references.bib icml2026.sty icml2026.bst
	$(LATEX) $(FLAGS) $(MAIN)
	bibtex $(MAIN)
	$(LATEX) $(FLAGS) $(MAIN)
	$(LATEX) $(FLAGS) $(MAIN)

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out $(MAIN).toc

distclean: clean
	rm -f $(MAIN).pdf

.PHONY: all clean distclean figures
