import subprocess
import sys
import time
import os

DEFAULT_MEASUREMENTS_FILE = os.path.join(os.path.dirname(__file__), "data", "measurements.txt")
SOLUTION_FILE = os.path.join(os.path.dirname(__file__), "solution.py")


def main():
    measurements_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MEASUREMENTS_FILE

    if not os.path.exists(measurements_file):
        print(f"Error: measurements file not found at {measurements_file}", file=sys.stderr)
        print("Run: python prepare.py <num_lines>", file=sys.stderr)
        sys.exit(1)

    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, SOLUTION_FILE, measurements_file],
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    print(f"Time Taken: {elapsed:.3f}")


if __name__ == "__main__":
    main()
