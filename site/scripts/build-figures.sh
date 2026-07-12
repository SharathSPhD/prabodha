#!/usr/bin/env bash
# Compile every pgfplots/TikZ figure fragment from docs/paper_icml/figures/
# into a standalone SVG under site/public/figures/.
#
# Requires: pdflatex (texlive with pgfplots + standalone) and pdftocairo.
# Usage: bash site/scripts/build-figures.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FIGS="$ROOT/docs/paper_icml/figures"
OUT="$ROOT/site/public/figures"
TMP="$(mktemp -d)"
mkdir -p "$OUT"

for f in "$FIGS"/fig_*.tex; do
  name="$(basename "$f" .tex)"
  cat > "$TMP/$name.tex" <<'PREAMBLE'
\documentclass[tikz,border=6pt]{standalone}
\usepackage{amsmath,amssymb}
\usepackage{pgfplots}
\pgfplotsset{compat=1.17}
\usepgfplotslibrary{groupplots}
\usetikzlibrary{positioning,arrows.meta,calc,fit,matrix,shapes.geometric,decorations.pathreplacing,patterns}
\newlength{\mycolumnwidth}
\setlength{\mycolumnwidth}{3.25in}
\makeatletter
\let\columnwidth\mycolumnwidth
\makeatother
\begin{document}
PREAMBLE
  cat "$f" >> "$TMP/$name.tex"
  echo '\end{document}' >> "$TMP/$name.tex"
  if (cd "$TMP" && pdflatex -interaction=nonstopmode -halt-on-error "$name.tex" > "$name.log" 2>&1); then
    pdftocairo -svg "$TMP/$name.pdf" "$OUT/$name.svg"
    echo "OK   $name"
  else
    echo "FAIL $name (see $TMP/$name.log)"
  fi
done
echo "SVGs in $OUT"
