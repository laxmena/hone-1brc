import sys
import os
import mmap
from multiprocessing import Pool, cpu_count


def process_chunk(args):
    filepath, start, end = args
    stats = {}  # station_bytes -> [min, max, sum, count]

    with open(filepath, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        pos = start
        data = mm

        while pos < end:
            # Find end of line
            nl = data.find(b'\n', pos)
            if nl == -1 or nl > end:
                nl = end
            
            line_end = nl
            # Skip empty lines
            if line_end <= pos:
                pos = nl + 1
                continue

            # Find semicolon
            semi = data.find(b';', pos, line_end)
            if semi == -1:
                pos = nl + 1
                continue

            station = data[pos:semi]
            # Parse temperature as integer (tenths of degree)
            temp_bytes = data[semi+1:line_end]
            
            # Manual integer parsing of X.X or -X.X or XX.X or -XX.X
            # Avoid float parsing entirely
            neg = False
            ti = 0
            tb = temp_bytes
            tlen = len(tb)
            
            if tlen > 0 and tb[0] == 45:  # '-'
                neg = True
                ti = 1
            
            val = 0
            while ti < tlen:
                c = tb[ti]
                if c == 46:  # '.'
                    ti += 1
                    # one decimal digit follows
                    if ti < tlen:
                        val = val * 10 + (tb[ti] - 48)
                    break
                val = val * 10 + (c - 48)
                ti += 1
            
            if neg:
                val = -val

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

            pos = nl + 1

        mm.close()

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
            # Seek to approximate end of chunk
            end = start + chunk_size
            if end >= size:
                boundaries.append((start, size))
                break
            f.seek(end)
            # Find next newline
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
    # Use more chunks than workers for better load balancing
    num_chunks = num_workers * 4
    
    boundaries = find_chunk_boundaries(filepath, num_chunks)
    
    args = [(filepath, start, end) for start, end in boundaries]
    
    with Pool(processes=num_workers) as pool:
        all_stats = pool.map(process_chunk, args)
    
    merged = merge_stats(all_stats)
    
    results = []
    for station, (mn, mx, total, count) in merged.items():
        mean_val = total / count
        # Convert from integer tenths back to float
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
