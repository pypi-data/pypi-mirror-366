import numpy as np


def find_runs(x):
    """Find runs of consecutive items in an array."""
    n = len(x)
    if n == 0:
        return np.array([]), np.array([]), np.array([])

    loc_start = np.zeros(n, dtype=bool)
    loc_start[0] = True
    np.not_equal(x[:-1], x[1:], out=loc_start[1:])
    starts = np.flatnonzero(loc_start)

    values = x[starts]
    lengths = np.diff(np.append(starts, n))

    return values, starts, lengths


def find_ranges(ix):
    """Find sequences in an array on integers,
       which can be defined with limits and step
    """
    if len(ix) == 0:
        return []
    rng_list = []
    first, last, step, count = 0, 0, 1, 0
    for t in ix:
        if count == 0:
            first = t
            count = 1
        elif count == 1:
            count = 2
            step = t - last
        else:
            s = t - last
            if step == s:
                count += 1
            elif count == 2:
                rng_list.append((first, first, 1, 1))
                first = last
                step = s
                count = 2
            else:
                rng_list.append((first, last, step, count))
                first = t
                count = 1
        last = t

    rng_list.append((first, last, step, count))
    return sorted(rng_list)


def find_ranges_of_patterns(nptrn, ix, tid):
    """Find train ranges for a number of patterns"""
    patterns = {}
    for a in range(nptrn):
        patterns[a] = find_ranges(tid[np.flatnonzero(ix == a)])

    return patterns


def compress_ranges_of_patterns(patterns, tid):
    """Merge the subsequent ranges if they were splitted
       from bigger range due to a few missed trains.
    """
    patterns_compressed = []
    for a, ranges in sorted(patterns.items(), key=lambda v: v[1][0]):
        rng_list = []

        for rng in ranges:
            rng2 = tuple(list(rng) + [0])
            s2 = rng2[2]

            while rng_list:
                rng1 = rng_list[-1]
                s1 = rng1[2]

                if (s1 == 0 and s2 == 0) or (s1 != s2 and s1 * s2 != 0):
                    break

                delta = int(rng2[0]) - int(rng1[1])
                s = max(s1, s2)

                nmissed = -1
                if (delta % s) == 0:
                    missed_trains = np.arange(rng1[1] + s, rng2[0], s,
                                              dtype=int)
                    if np.all(np.in1d(missed_trains, tid, invert=True)):
                        nmissed = len(missed_trains)

                if nmissed != -1:
                    rng2 = (rng1[0], rng2[1], s, rng1[3] + rng2[3],
                            rng1[4] + rng2[4] + nmissed)
                    rng_list.pop()
                else:
                    break

            rng_list.append(rng2)

        patterns_compressed.append((a, rng_list))

    return patterns_compressed


def expand_ranges_of_cells(cell_ranges):
    """Expand ranges to the sequence of single numbers
       if they define short sequence
    """
    int_expanded = []
    for f, l, s, n in cell_ranges:
        if n == 1:
            int_expanded.append((f,))
        elif n == 2:
            int_expanded += [(f,), (l,)]
        elif s <= 1:
            int_expanded.append((f, l + 1))
        elif n == 3:
            int_expanded += [(f,), (f + s,), (l,)]
        else:
            int_expanded.append((f, l + 1, s))

    return int_expanded
