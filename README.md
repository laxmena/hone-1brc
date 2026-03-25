# Hone vs. The 1 Billion Row Challenge

A baseline Python implementation of the [1 Billion Row Challenge](https://github.com/gunnarmorling/1brc), used as a starting point for automated performance optimization with [Hone](https://laxmena.com/hone-vs-the-1-billion-row-challenge).

The challenge: parse a text file with one billion rows of weather station measurements and compute the **min**, **mean**, and **max** temperature for each station.

## Repository Structure

```
hone-1brc/
├── data/
│   ├── weather_stations.txt   # Station list with mean temperatures (~45k stations)
│   └── measurements_*.txt     # Generated input files (not committed)
├── prepare.py                 # Generates the measurements input file
├── solution.py                # Computes min/mean/max per station
└── benchmark.py               # Times solution.py for use with Hone
```

## Setup

### Install Hone

```bash
pip install hone-ai
```

### Solution dependencies

No dependencies beyond the Python standard library.

### 1. Generate the measurements file

```bash
# Generate 1 billion rows (the full challenge)
python prepare.py 1000000000 data/measurements_1B.txt

# Generate a smaller dataset for testing
python prepare.py 1000000 data/measurements_1M.txt
python prepare.py 100000000 data/measurements_100M.txt
```

Output defaults to `data/measurements.txt` if no filename is given.

### 2. Run the solution

```bash
python solution.py data/measurements.txt
```

**Example output:**
```
{Abha=-23.0/18.0/59.2, Abidjan=-16.2/26.0/67.4, ...}
```

## Input Format

Each line in the measurements file follows the format:

```
StationName;Temperature
```

**Constraints:**
- Up to 10,000 unique station names
- Station names: 1–100 bytes
- Temperatures: -99.9 to 99.9 (always one decimal place)

## Benchmarking with Hone

`benchmark.py` times `solution.py` end-to-end and prints the elapsed time in a format Hone can parse.

```bash
# defaults to data/measurements.txt
python benchmark.py

# explicit input file
python benchmark.py data/measurements_1M.txt
# Time Taken: 0.569
```

To run Hone against the baseline:

```bash
hone "Optimize solution.py to process measurements faster" \
     --bench "python benchmark.py data/measurements_1M.txt" \
     --files "solution.py" \
     --optimize lower \
     --score-pattern "Time Taken:\s*(\d+\.\d+)" \
     --budget 1.0
```

## Approach

The baseline solution is intentionally naive — no tricks, no concurrency, no memory mapping. It reads the file line by line, accumulates stats in a plain dict, and prints sorted results. This establishes the performance floor that Hone will attempt to optimize automatically.
