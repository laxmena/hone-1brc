import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python solution.py <measurements_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    stats = {}  # station -> (min, max, sum, count)

    with open(filepath, "r", encoding="utf-8", buffering=65536) as f:
        for line in f:
            # Find semicolon without strip
            sep_idx = line.index(";", 0, len(line) - 1)  # ; is before final char
            station = line[:sep_idx]
            temp = float(line[sep_idx + 1:-1])  # -1 to skip newline
            
            if station in stats:
                mn, mx, total, count = stats[station]
                if temp < mn:
                    mn = temp
                if temp > mx:
                    mx = temp
                stats[station] = (mn, mx, total + temp, count + 1)
            else:
                stats[station] = (temp, temp, temp, 1)

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
