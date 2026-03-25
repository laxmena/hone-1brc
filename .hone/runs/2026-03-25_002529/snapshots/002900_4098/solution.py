import sys
import os
import mmap
from multiprocessing import Pool, cpu_count


def process_chunk(args):
    filepath, start, end = args
    stats = {}

    with open(filepath, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        chunk = mm[start:end]
        mm.close()

    for line in chunk.split(b'\n'):
        if not line:
            continue

        # Use partition - single C-level call, no index needed
        station, sep, tb = line.partition(b';')
        if not sep:
            continue

        # Temperature always has exactly 1 decimal place
        # Format: [-]D.D or [-]DD.D
        # The dot is always 2nd from last char
        # So: last char = decimal digit, [-3] = '.', rest = integer
        d0 = tb[-1] - 48
        if tb[0] == 45:  # '-'
            if len(tb) == 4:  # -D.D
                val = -((tb[1] - 48) * 10 + d0)
            else:             # -DD.D
                val = -((tb[1] - 48) * 100 + (tb[2] - 48) * 10 + d0)
        else:
            if len(tb) == 3:  # D.D
                val = (tb[0] - 48) * 10 + d0
            else:             # DD.D
                val = (tb[0] - 48) * 100 + (tb[1] - 48) * 10 + d0

        entry = stats.get(station)
        if entry:
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
            entry = merged.get(station)
            if entry:
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
    num_chunks = num_workers * 8

    boundaries = find_chunk_boundaries(filepath, num_chunks)
    args = [(filepath, start, end) for start, end in boundaries]

    with Pool(processes=num_workers) as pool:
        all_stats = pool.map(process_chunk, args)

    merged = merge_stats(all_stats)

    results = []
    for station, (mn, mx, total, count) in merged.items():
        mean_val = total / count
        results.append((
            station.decode('utf-8'),
            mn / 10.0,
            mx / 10.0,
            mean_val / 10.0
        ))

    results.sort(key=lambda x: x[0])

    out = [f"{s}={mn:.1f}/{mean:.1f}/{mx:.1f}" for s, mn, mx, mean in results]
    print("{" + ", ".join(out) + "}")


if __name__ == "__main__":
    main()
