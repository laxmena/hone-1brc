import sys
import os
import mmap
from multiprocessing import Pool, cpu_count


def process_chunk(args):
    filepath, start, end = args
    stats = {}  # station_bytes -> [min, max, sum, count]

    with open(filepath, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        # Read the chunk as bytes
        chunk = mm[start:end]
        mm.close()

    # Split into lines using fast C-level split
    lines = chunk.split(b'\n')

    for line in lines:
        if not line:
            continue

        # Find semicolon
        semi = line.find(b';')
        if semi == -1:
            continue

        station = line[:semi]
        temp_bytes = line[semi+1:]

        # Parse temperature as integer (tenths of degree)
        # Format: optional '-', digits, '.', one digit
        # e.g. b'-12.3' -> -123, b'4.5' -> 45
        tb = temp_bytes
        if tb[0] == 45:  # '-'
            # negative
            # find dot position
            dot = tb.find(b'.', 1)
            if dot == -1:
                continue
            # integer part: tb[1:dot], decimal: tb[dot+1]
            int_part = tb[1:dot]
            if len(int_part) == 1:
                val = -(( (int_part[0] - 48) * 10) + (tb[dot+1] - 48))
            else:  # 2 digits
                val = -(( (int_part[0] - 48) * 100 + (int_part[1] - 48) * 10) + (tb[dot+1] - 48))
        else:
            dot = tb.find(b'.', 1)
            if dot == -1:
                continue
            int_part = tb[:dot]
            if len(int_part) == 1:
                val = (int_part[0] - 48) * 10 + (tb[dot+1] - 48)
            else:  # 2 digits
                val = (int_part[0] - 48) * 100 + (int_part[1] - 48) * 10 + (tb[dot+1] - 48)

        if station in stats:
            entry = stats[station]
            if val < entry[0]:
                entry[0] = val
            if val > entry[1]:
                entry[1] = val
            entry[2] += val
            entry[3] += 1
        else:
            stats[station] = [val, val, val, 1]

    return stats


def merge_stats(all_stats):
    merged = {}
    for stats in all_stats:
        for station, (mn, mx, total, count) in stats.items():
            if station in merged:
                entry = merged[station]
                if mn < entry[0]:
                    entry[0] = mn
                if mx > entry[1]:
                    entry[1] = mx
                entry[2] += total
                entry[3] += count
            else:
                merged[station] = [mn, mx, total, count]
    return merged


def find_chunk_boundaries(filepath, num_chunks):
    size = os.path.getsize(filepath)
    chunk_size = size // num_chunks
    boundaries = []

    with open(filepath, 'rb') as f:
        start = 0
        for i in range(num_chunks):
            if i == num_chunks - 1:
                boundaries.append((start, size))
                break
            end = start + chunk_size
            if end >= size:
                boundaries.append((start, size))
                break
            f.seek(end)
            rest = f.read(4096)
            nl_pos = rest.find(b'\n')
            if nl_pos == -1:
                boundaries.append((start, size))
                break
            end = end + nl_pos + 1
            boundaries.append((start, end))
            start = end

    return boundaries


def main():
    if len(sys.argv) < 2:
        print("Usage: python solution.py <measurements_file>")
        sys.exit(1)

    filepath = sys.argv[1]

    num_workers = cpu_count()
    num_chunks = num_workers * 4

    boundaries = find_chunk_boundaries(filepath, num_chunks)

    args = [(filepath, start, end) for start, end in boundaries]

    with Pool(processes=num_workers) as pool:
        all_stats = pool.map(process_chunk, args)

    merged = merge_stats(all_stats)

    results = []
    for station, (mn, mx, total, count) in merged.items():
        mean_val = total / count
        mn_f = mn / 10.0
        mx_f = mx / 10.0
        mean_f = mean_val / 10.0
        results.append((station.decode('utf-8'), mn_f, mx_f, mean_f))

    results.sort(key=lambda x: x[0])

    print("{", end="")
    for i, (station, mn, mx, mean) in enumerate(results):
        if i:
            print(", ", end="")
        print(f"{station}={mn:.1f}/{mean:.1f}/{mx:.1f}", end="")
    print("}")


if __name__ == "__main__":
    main()
