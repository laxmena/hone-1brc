# hone-1brc

Autonomous performance optimization of a Python solution to the 1 Billion Row Challenge.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar24`). The branch `hone/<tag>` must not already exist — this is a fresh run.
2. **Create the branch**: `git checkout -b hone/<tag>` from current main.
3. **Read the in-scope files**: Read these files for full context:
   - `README.md` — repository context and benchmark instructions.
   - `solution.py` — the file you modify. Reads measurements, computes min/mean/max per station.
   - `benchmark.py` — fixed benchmark runner. Do not modify.
   - `prepare.py` — fixed data generator. Do not modify.
4. **Verify data exists**: Check that `data/measurements_1M.txt` exists. If not, tell the human to run `python prepare.py 1000000 data/measurements_1M.txt`.
5. **Initialize results.tsv**: Create `results.tsv` with just the header row. The baseline will be recorded after the first run.
6. **Confirm and go**: Confirm setup looks good, then kick off experimentation.

## Experimentation

**What you CAN do:**
- Modify `solution.py` — this is the only file you edit. Everything is fair game: parsing strategy, data structures, I/O approach, concurrency, algorithm.

**What you CANNOT do:**
- Modify `benchmark.py` or `prepare.py`. They are read-only.
- Install third-party packages. Standard library only — no numpy, pandas, polars, or any package not in the Python stdlib.
- Change the output format. Results must remain: `{StationA=min/mean/max, StationB=min/mean/max, ...}` sorted alphabetically.
- Corrupt correctness. The computed min, mean, and max values must be accurate.

**The goal is simple: minimize wall-clock execution time (seconds).** The benchmark runs `solution.py` end-to-end and reports `Time Taken: X.XXX`. Lower is better.

**The first run**: Always establish the baseline first by running `benchmark.py` against the unmodified `solution.py`.

**Simplicity criterion**: All else being equal, simpler is better. A tiny improvement that adds complex, hacky code is not worth it. Removing code and getting equal or better results is a great outcome. Weigh complexity cost against improvement magnitude.

## Output format

The benchmark script prints:

```
Time Taken: 0.532
```

Extract it with:

```bash
python benchmark.py data/measurements_1M.txt
```

## Logging results

Log every experiment to `results.tsv` (tab-separated — do NOT use commas). Do not commit this file, leave it untracked.

Header and 5 columns:

```
commit	time_s	status	description
```

1. git commit hash (short, 7 chars)
2. Time Taken in seconds (e.g. `0.532`) — use `0.000` for crashes
3. status: `keep`, `discard`, or `crash`
4. short description of what this experiment tried

Example:

```
commit	time_s	status	description
a1b2c3d	0.532	keep	baseline
b2c3d4e	0.441	keep	buffered reads + avoid strip()
c3d4e5f	0.601	discard	over-engineered chunking, slower
d4e5f6g	0.000	crash	mmap approach had off-by-one on chunk boundaries
```

## The experiment loop

LOOP FOREVER:

1. Look at the git state: current branch and commit.
2. Form a hypothesis — what is the bottleneck? What change will address it?
3. Modify `solution.py` with the experimental idea.
4. `git commit` with a short message describing the experiment.
5. Run: `python benchmark.py data/measurements_1M.txt > run.log 2>&1`
6. Read result: `grep "Time Taken" run.log`
7. If output is empty, the run crashed. Read `run.log` and attempt a fix. If the idea is fundamentally broken, log `crash`, revert, and move on.
8. Log the result in `results.tsv`.
9. If time improved (lower), keep the commit and advance.
10. If time is equal or worse, `git reset --hard HEAD~1` and try a different approach.

**NEVER STOP**: Once the loop begins, do NOT pause to ask the human if you should continue. The human may be away and expects you to work indefinitely until manually stopped. If you run out of ideas, think harder — see the plateau section below.

**Crashes**: If a run crashes due to a trivial bug (typo, missing import), fix and re-run. If the idea is broken, log `crash` and move on.

## Optimization strategy

Work through these levels in order. Validate before moving on.

### Level 1 — Hot loop efficiency
- Minimize dict lookups: cache the list reference after the first lookup
- Avoid `.strip()` — parse the newline directly
- Use `str.split(';', 1)` with maxsplit to avoid extra work

### Level 2 — I/O throughput
- Increase file read buffer size: `open(filepath, buffering=2**20)`
- Read large chunks at once and split on `\n` manually
- Avoid per-line function call overhead from `for line in f`

### Level 3 — Concurrency
- Use `multiprocessing` to divide the file into byte-range chunks across CPU cores
- Each worker independently aggregates its chunk; merge partial results at the end
- Use `mmap` (stdlib `mmap` module) for zero-copy reads

### Level 4 — Low-level parsing
- Avoid `float()` entirely: parse temperatures as integers (e.g. `18.3` → `183`) using `bytes.find(b'.')` and manual digit arithmetic
- Work in `bytes` rather than decoded `str` throughout the hot path
- Exploit fixed temperature format constraints (-99.9 to 99.9, always 1 decimal) for a hand-rolled parser

## When you plateau

If the score stops improving across 3+ consecutive iterations, **abandon incremental changes and try something fundamentally different**:

- If you're reading line-by-line → switch to `mmap` + chunk-based processing
- If you're using Python strings → switch entirely to `bytes` operations
- If you're single-threaded → rewrite with `multiprocessing`, splitting file by byte offset
- If you're using `float()` → write a custom integer parser that avoids it entirely
- If you've tried all of the above → combine them: multiprocessing + mmap + integer parsing together

A 10–20x improvement over the naive baseline is achievable. If you're stuck at 2x, you have not yet tried the right level. Be bold — big rewrites of `solution.py` are encouraged when incremental changes stop working.
