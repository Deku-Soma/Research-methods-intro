# Research Proposal & Honours Report Documents

This directory contains the LaTeX manuscripts and supporting CAD assets for the Honours Research Project at the University of the Witwatersrand.

---

## 1. Document Overview

* **`thesis.tex`**: The extended Honours research report / thesis manuscript incorporating comprehensive literature analysis, detailed control formulations, comparative baseline evaluations, and empirical simulation findings.
* **`main.tex`**: The original research proposal manuscript submitted for initial academic approval.
* **`references.bib`**: Master BibTeX database containing citations for RoboCup SSL rules, non-holonomic mobile robotics, LTV-MPC algorithms, ROS 2 real-time performance studies, and socioeconomic context.
* **`named-wits.bst` / `natbib.sty` / `natbib-add.tex`**: University of the Witwatersrand citation style and bibliography formatting definitions.
* **`baseline_comparison_table.md`**: Specification comparison matrix and LaTeX booktabs code comparing the custom SSL robot against the TurtleBot3 Burger and NVIDIA JetBot baselines.
* **`Models/`**: Mechanical CAD models including OpenSCAD parametric geometry (`body example.scad`).

---

## 2. Compilation Instructions

### Using GNU Make

```bash
# Compile the extended Honours thesis document (thesis.tex -> thesis.pdf)
make thesis

# Compile the research proposal document (main.tex -> main.pdf)
make proposal

# Clean auxiliary build files (*.aux, *.bbl, *.fls, *.log, *.toc)
make clean
```

### Using Windows Batch Script

On Windows systems with `latexmk` installed in PATH:
```cmd
build.bat
```

### Manual pdflatex + bibtex Cycle

If building manually from terminal:
```bash
pdflatex thesis.tex
bibtex thesis
pdflatex thesis.tex
pdflatex thesis.tex
```

---

## 3. Cleanliness Guidelines

All intermediate compilation artifacts (`*.aux`, `*.bbl`, `*.blg`, `*.fdb_latexmk`, `*.fls`, `*.log`, `*.out`, `*.synctex.gz`, `*.toc`) are ignored by the repository's `.gitignore`. 

Run `make clean` before committing changes to ensure only source documents (`.tex`, `.bib`, `.bst`, `.md`) remain in the directory.
