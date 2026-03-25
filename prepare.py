import random
import sys
import os

STATIONS_FILE = os.path.join(os.path.dirname(__file__), "data", "weather_stations.txt")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "data", "measurements.txt")


def load_stations(path):
    stations = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            sep = line.index(";")
            name = line[:sep]
            mean_temp = float(line[sep + 1:])
            stations.append((name, mean_temp))
    return stations


def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare.py <num_lines> [output_file]")
        sys.exit(1)

    num_lines = int(sys.argv[1])
    output_file = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE
    stations = load_stations(STATIONS_FILE)
    num_stations = len(stations)

    print(f"Loaded {num_stations} stations. Generating {num_lines:,} measurements -> {output_file}")

    with open(output_file, "w", encoding="utf-8") as out:
        for _ in range(num_lines):
            name, mean = stations[random.randrange(num_stations)]
            temp = random.gauss(mean, 10.0)
            temp = max(-99.9, min(99.9, temp))
            out.write(f"{name};{temp:.1f}\n")

    print("Done.")


if __name__ == "__main__":
    main()
