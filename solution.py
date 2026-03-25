import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python solution.py <measurements_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    stats = {}  # station -> [min, max, sum, count]

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            sep = line.index(";")
            station = line[:sep]
            temp = float(line[sep + 1:])
            if station in stats:
                entry = stats[station]
                if temp < entry[0]:
                    entry[0] = temp
                if temp > entry[1]:
                    entry[1] = temp
                entry[2] += temp
                entry[3] += 1
            else:
                stats[station] = [temp, temp, temp, 1]

    results = []
    for station, (mn, mx, total, count) in stats.items():
        results.append((station, mn, mx, total / count))

    results.sort(key=lambda x: x[0])

    print("{", end="")
    for i, (station, mn, mx, mean) in enumerate(results):
        if i:
            print(", ", end="")
        print(f"{station}={mn:.1f}/{mean:.1f}/{mx:.1f}", end="")
    print("}")


if __name__ == "__main__":
    main()
