# hone-1brc

Autonomous performance optimization of a Python solution to the 1 Billion Row Challenge.

## Goal

Minimize the wall-clock execution time of `solution.py`. The benchmark reports `Time Taken: X.XXX` — lower is better.

**Baseline**: established on the first run. A 10–20x improvement over the baseline is achievable.

## Input data

- ~44,691 unique station names, semicolon-separated from temperature: `StationName;Temperature`
- Temperatures always have exactly one decimal place, range -99.9 to 99.9
- No header line; one measurement per line

## Hardware

Apple Silicon Mac mini. Factor in core count and unified memory architecture when considering parallelism strategies.

## Rules

- **Only modify `solution.py`**. Do not touch `benchmark.py` or `prepare.py`.
- **Standard library only** — no third-party packages.
- **Correctness is non-negotiable**. Output format and computed values must not change.

## How to experiment

You are an autonomous researcher. Form a hypothesis, implement it, observe the result, and decide to keep or discard. Repeat.

Don't play it safe — be bold. Wild ideas are encouraged. If an approach stops yielding gains, throw it out entirely and try something fundamentally different. The search space is large and there are many valid paths to a fast solution. Find yours.

## When you plateau

If the score stops improving, **don't make incremental tweaks** — change your approach entirely. Note that the current solution is single-threaded and processes decoded text. Those are two major axes to explore. Challenge every assumption the current implementation makes and try something fundamentally different.
