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


def _hoare_partition(a, lo, hi, pivot_index, stats):
    """Partition a[lo..hi] around the pivot with the Hoare scheme.

    The pivot is first swapped to the front of the subarray, then two
    cursors walk toward each other: the left one stops on an element
    >= pivot, the right one on an element <= pivot, and the pair is
    swapped until they cross. The call returns j, the index where the
    left and right halves split: everything in a[lo..j] is <= pivot
    and everything in a[j+1..hi] is >= pivot.

    Compared with the Lomuto scheme this does about half as many
    swaps, which is the scheme Hoare originally described.

    Parameters: a           - the list
                lo, hi      - inclusive bounds of the subarray
                pivot_index - position of the chosen pivot
                stats       - dict to count comparisons and swaps in,
                              or None to skip the bookkeeping
    Return:      j, the split index (lo <= j < hi)
    """
    if pivot_index != lo:
        a[pivot_index], a[lo] = a[lo], a[pivot_index]
        if stats is not None:
            stats["swaps"] += 1
    pivot = a[lo]
    i = lo - 1
    j = hi + 1
    while True:
        while True:
            j -= 1
            if stats is not None:
                stats["comparisons"] += 1
            if a[j] <= pivot:
                break
        while True:
            i += 1
            if stats is not None:
                stats["comparisons"] += 1
            if a[i] >= pivot:
                break
        if i < j:
            a[i], a[j] = a[j], a[i]
            if stats is not None:
                stats["swaps"] += 1
        else:
            return j


def _quicksort(a, lo, hi, randomize, stats):
    """Recursive driver for both variants; bounds are inclusive.

    Hoare partition returns a split index, so the two halves are
    a[lo..j] and a[j+1..hi] (unlike Lomuto, the pivot itself is not
    isolated, and both halves can be non-empty even when the pivot
    lands in the middle).

    The recursion always descends into the SMALLER half first and
    treats the larger half as the next loop iteration. The call
    stack therefore holds one frame per level of smaller halves,
    which is O(log n) even when the partitions are maximally
    unbalanced, so a degenerate input takes O(n^2) time but only
    O(log n) stack.
    """
    while lo < hi:
        if randomize:
            pivot_index = random.randint(lo, hi)
        else:
            pivot_index = hi
        j = _hoare_partition(a, lo, hi, pivot_index, stats)
        if j - lo < hi - j:
            _quicksort(a, lo, j, randomize, stats)
            lo = j + 1
        else:
            _quicksort(a, j + 1, hi, randomize, stats)
            hi = j


def quick_sort(a, stats=None):
    """Sort a list of comparable elements IN PLACE in increasing order.

    Deterministic pivot choice: the LAST element of the subarray.
    The choice depends on the input order, so an already sorted or
    reverse-sorted list peels off one element per partition and takes
    the O(n^2) worst case.

    Parameters: a     - list of comparable elements
                stats - optional dict; if given, filled with the
                        running "comparisons" and "swaps" counts
    Return:    the same list object, sorted in increasing order

    Complexity:
        Time   - O(n log n) best and average, O(n^2) worst case.
        Space  - O(log n) call stack in all cases: the recursion
                 descends into the smaller half only, the larger
                 half is the next loop iteration.
    """
    if len(a) < 2:
        return a
    _quicksort(a, 0, len(a) - 1, randomize=False, stats=stats)
    return a


def quick_sort_random(a, stats=None):
    """Sort a list of comparable elements IN PLACE in increasing order.

    Randomized pivot choice: a uniformly random element of the
    subarray, picked fresh for every partition. No input order is
    a guaranteed worst case anymore - on every input the expected
    number of comparisons is the same, about 2 n ln n, and hitting
    the quadratic case would take n unlucky pivots in a row.

    Parameters: a     - list of comparable elements
                stats - optional dict; if given, filled with the
                        running "comparisons" and "swaps" counts
    Return:    the same list object, sorted in increasing order

    Complexity:
        Time   - O(n log n) expected on every input; the O(n^2)
                 worst case still exists for a fixed unlucky pivot
                 sequence but is no longer tied to the input order.
        Space  - O(log n) call stack in all cases, same driver as
                 the deterministic variant.
    """
    if len(a) < 2:
        return a
    _quicksort(a, 0, len(a) - 1, randomize=True, stats=stats)
    return a


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
