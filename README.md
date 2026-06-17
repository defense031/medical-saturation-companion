# Forward Surgical Saturation

Two deliverables answering OTSG RFI Q522 and its companion KSIL Q187: a manuscript and an
interactive companion site, both built on one queueing model of a forward surgical team
under casualty surge.

## The paper
`PAPER.pdf` is the manuscript (elsarticle format). Its source lives in `paper/`; rebuild with

    cd paper && latexmk -pdf PAPER.tex

The posture-model provenance (the consolidate-vs-distribute engine behind the crossover) is in
`paper/model/`.

## The companion
`index.html` is the interactive briefing site; open it in a browser. It is generated from the
panels in `sections/` by `build_unified.py`:

    python3 build_unified.py

The companion bibliography is `references.bib` (same folder); the source PDFs it cites sit
under `papers/`.

## Reproducing the numbers
`calibration/` holds the committed discrete-event engines. Every number on the companion's
Results tab reproduces from one command, which prints each engine value beside the displayed
value with the gap (worst gap 0.50 pt, Monte-Carlo noise):

    node calibration/companion_findings.js

Findings 1 and 2 also reproduce standalone from `node calibration/estimand.js`. The analysis
of record, including the survival-clock basis and every calibration decision, is
`calibration/RESULTS.md`.

## archive/
Superseded drafts, session notes, the memo version of the paper, old showcase builds, the prior
validation site, and scratch. Nothing here is load-bearing for the two deliverables.
