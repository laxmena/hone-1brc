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
            # Use split instead of index + slicing
            parts = line.split(';', 1)
            if len(parts) != 2:
                continue
            station = parts[0]
            temp = float(parts[1])
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

    # Sort stations and build output in one pass
    sorted_stations = sorted(stats.keys())
    parts = []
    for station in sorted_stations:
        mn, mx, total, count = stats[station]
        mean = total / count
        parts.append(f"{station}={mn:.1f}/{mean:.1f}/{mx:.1f}")

    print("{", ", ".join(parts), "}", sep="")


if __name__ == "__main__":
    main()
