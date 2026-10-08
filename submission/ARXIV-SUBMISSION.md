# arXiv submission

Start it at https://arxiv.org/submit after the Zenodo record is published. You are endorsed for math.CO, so the primary category is open to you.

## File to upload

Upload `submission/arxiv/uno_arxiv.tar.gz` as a single file. It holds `uno.tex` and the three figures `shortest.png`, `tail.png` and `fluid_limit.png` in one flat folder. The bibliography is written inside the `.tex` file, so there is no `.bib` or `.bbl` to add.

The tarball was unpacked into an empty folder and compiled with pdflatex alone, which is how arXiv processes it. It gave 8 pages with no errors and no undefined references, and its text is identical to `paper/uno.pdf`. `submission/arxiv/uno_arxiv_preview.pdf` is that build, so you can compare it with the PDF arXiv shows you before you confirm.

The source differs from `paper/uno.tex` in one way. The `\graphicspath` line was removed because the figures sit beside the `.tex` file. The date is fixed at 8 October 2026 in both, so the arXiv build matches the Zenodo PDF.

## Metadata

**Primary category**

```
math.CO
```

**Cross-list**

```
math.PR
```

Most of the paper is probability, so math.PR is the natural second home. Add cs.GT as well only if you want the strategy section to reach game theorists. arXiv advises one or two cross-lists at most.

**Title**

```
How long is a game of Uno? A counting law for large hands and the Wild Draw Four hoard
```

**Authors**

```
Pragyaan Gaur
```

**Abstract**

Paste the contents of `submission/abstract.txt`. It is 1449 characters, under the 1920 limit, and it is plain ASCII with no LaTeX to escape.

**Comments**

```
8 pages, 3 figures, 4 tables. Code and data: https://doi.org/10.5281/zenodo.NNNNNNNN
```

Replace `NNNNNNNN` with the number from the Zenodo record. If you submit before the Zenodo record exists, use `Code and data: https://github.com/pragyaangaur/Uno-Reverse-Engineered` instead.

**MSC class**

```
00A08, 60C05, 91A46, 60J10
```

These are the same classes as in the paper: recreational mathematics, combinatorial probability, combinatorial games, and discrete-time Markov chains.

**License**

CC BY 4.0, to match the Zenodo record.

**Journal reference and DOI**

Leave both empty.

## Things to check before confirming

The paper's acknowledgements say that a large language model helped with the wording, the organization and the simulation code, and that you directed and checked the work. This follows the wording of the A390200 paper, extended to the code because the code is a large part of this paper. Read it once and change it if it does not describe the work as you see it.

math.CO moderators can reclassify a paper or decline it, as happened twice with the A390200 preprint. This paper has proofs in Sections 3 and 5 and a large simulation component. If it is reclassified to math.PR, that is a reasonable outcome and needs no appeal.

The arXiv version is permanent once announced. Corrections can be posted later as v2.
