"""
MSCS 532 - Assignment 5
Empirical comparison of deterministic vs randomized quick sort.

Runs both variants on random, sorted, and reverse-sorted inputs of
increasing size and records two measurements:

  1. the exact number of comparisons and swaps the partition makes
     (the primary metric - it is exact, so one run is enough and
     machine noise cannot move the number), and
  2. the median wall time over repeated runs (the secondary metric).

Run:  python3 benchmark.py

Output:
    results/comparisons.csv   one row per (kind, size, algorithm)
    results/times.csv         one row per (kind, size, algorithm)
    plots/comparisons_vs_size.png
    plots/time_vs_size.png

Measurement notes:
    * Data for every (kind, size) is generated once from a seeded
      generator, so both algorithms sort exactly the same input.
    * The randomized variant re-seeds its pivot draws per run, so
      its numbers are reproducible and comparable across sizes.
    * Wall time is the median of 5 runs for sizes up to 1024 and a
      single run above that: the quadratic cases get long enough
      that one run already averages out the jitter, and running
      deterministic quick sort on 4096 sorted elements five times
      would take many minutes in pure Python.
    * The quadratic cases stop at 4096 for the same reason A3's
      benchmark stops: each doubling costs about 4x more, so three
      doublings are enough to show the O(n^2) signature.
"""

import csv
import os
import random
import statistics
import time

from quicksort import quick_sort, quick_sort_random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_SEED = 20261109
KINDS = ["random", "sorted", "reverse_sorted"]
SIZES = {
    "random": [512, 1024, 2048, 4096, 8192],
    "sorted": [512, 1024, 2048, 4096],
    "reverse_sorted": [512, 1024, 2048, 4096],
}
ALGORITHMS = [
    ("deterministic", quick_sort),
    ("randomized", quick_sort_random),
]
TIME_RUNS_SMALL = 5
SMALL_SIZE = 1024


def make_data(kind, n):
    """Build the n-element input of the requested kind (seeded)."""
    rng = random.Random(DATA_SEED + n)
    base = [rng.randint(0, n * 10) for _ in range(n)]
    if kind == "sorted":
        return sorted(base)
    if kind == "reverse_sorted":
        return sorted(base, reverse=True)
    return base


def seed_pivots(kind, n):
    """Give the randomized variant reproducible pivot draws."""
    random.seed(DATA_SEED + n * 131 + KINDS.index(kind))


def count_ops(fn, data):
    """Run one sort, return the exact comparison/swap counts."""
    stats = {"comparisons": 0, "swaps": 0}
    fn(data[:], stats=stats)
    return stats


def median_time(fn, data):
    """Return the median wall time in milliseconds over repeated runs."""
    runs = 1 if len(data) > SMALL_SIZE else TIME_RUNS_SMALL
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn(data[:])
        times.append((time.perf_counter() - t0) * 1000.0)
    return statistics.median(times)


def main():
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "plots"), exist_ok=True)

    comp_rows = []
    time_rows = []
    for kind in KINDS:
        for n in SIZES[kind]:
            data = make_data(kind, n)
            for name, fn in ALGORITHMS:
                seed_pivots(kind, n)
                ops = count_ops(fn, data)
                comp_rows.append([kind, n, name, ops["comparisons"],
                                  ops["swaps"]])
                seed_pivots(kind, n)
                ms = median_time(fn, data)
                time_rows.append([kind, n, name, ms])
                print(f"{kind:15s} n={n:5d} {name:14s} "
                      f"comparisons={ops['comparisons']:>9d} "
                      f"swaps={ops['swaps']:>7d}  median={ms:8.3f} ms")

    with open(os.path.join(HERE, "results", "comparisons.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "size", "algorithm", "comparisons", "swaps"])
        w.writerows(comp_rows)

    with open(os.path.join(HERE, "results", "times.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "size", "algorithm", "median_ms"])
        for row in time_rows:
            w.writerow([row[0], row[1], row[2], f"{row[3]:.4f}"])

    try:
        make_plots(comp_rows, time_rows)
    except ImportError:
        print("matplotlib is not installed; skipping the plots")

    print("wrote results/comparisons.csv, results/times.csv, plots/")


def make_plots(comp_rows, time_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # (color, linestyle, marker)
    STYLE = {
        ("deterministic", "random"): ("tab:blue", "-", "o"),
        ("deterministic", "sorted"): ("tab:blue", "--", "s"),
        ("deterministic", "reverse_sorted"): ("tab:blue", ":", "^"),
        ("randomized", "random"): ("tab:red", "-", "D"),
        ("randomized", "sorted"): ("tab:red", "--", "v"),
        ("randomized", "reverse_sorted"): ("tab:red", ":", "x"),
    }

    for rows, yname, title, fname in (
        (comp_rows, "comparison count",
         "Comparison count by input kind", "comparisons_vs_size.png"),
        (time_rows, "median wall time (ms)",
         "Median wall time by input kind", "time_vs_size.png"),
    ):
        fig, ax = plt.subplots(figsize=(7, 4.6))
        seen = set()
        for kind, n, name, val, *_ in rows:
            c, ls, m = STYLE[(name, kind)]
            tag = f"{name} - {kind}"
            ax.plot(n, val, color=c, linestyle=ls, marker=m,
                    label=tag if tag not in seen else None)
            seen.add(tag)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("input size n")
        ax.set_ylabel(yname)
        ax.set_title(title)
        ax.legend(fontsize=8, title="algorithm - kind")
        ax.grid(True, which="both", linestyle=":", linewidth=0.5)
        fig.tight_layout()
        fig.savefig(os.path.join(HERE, "plots", fname), dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    main()
