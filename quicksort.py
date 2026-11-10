"""
MSCS 532 - Assignment 5
Quicksort Algorithm: Implementation, Analysis, and Randomization

By: Alfredo Rosado
Date: 11-09-26

Two in-place quicksort variants built on the same Hoare partition:

  quick_sort         - deterministic: the last element of the subarray
                       is the pivot, the classic naive choice.
  quick_sort_random  - randomized: a uniformly random element of the
                       subarray is the pivot, so no input order can
                       force the worst case.

Both sort in increasing order in place. When a stats dict is passed,
the partition counts its comparisons and swaps into it; the empirical
analysis in the README is built on those counts.
"""

import random


def quick_sort(a):
    """Sort a list of comparable elements IN PLACE in increasing order.

    Deterministic pivot choice: the LAST element of the subarray.
    Still a stub - partition and the recursive driver land in the
    next commit.
    """
    raise NotImplementedError("deterministic quick sort not implemented yet")


def quick_sort_random(a):
    """Sort a list of comparable elements IN PLACE in increasing order.

    Randomized pivot choice: a uniformly random element of the
    subarray. Stub until the partition is in place.
    """
    raise NotImplementedError("randomized quick sort not implemented yet")


def main():
    samples = [
        [61, 4, 72, 19, 38, 25],
        [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        [5, 5, 3, 5, 1],
        [-2, 4, -9, 0, 7],
    ]
    for sample in samples:
        print(f"input:      {sample}")
        print(f"quick_sort: {quick_sort(sample[:])}")
        print(f"randomized: {quick_sort_random(sample[:])}")
        print()


if __name__ == "__main__":
    main()
