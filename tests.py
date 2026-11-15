"""
MSCS 532 - Assignment 5
Test suite for the two quick sort variants.

Run:  python3 tests.py

Every test is a plain function; the runner at the bottom calls them
all and reports pass/fail per test. The suite checks correctness
against the built-in sort on randomized inputs, edge cases, in-place
behavior, the O(log n) stack property of the driver, and - using the
comparison/swap counters - the worst-case and average-case complexity
claims from the README.
"""

import random
import sys

from quicksort import quick_sort, quick_sort_random


def test_empty_and_single():
    assert quick_sort([]) == []
    assert quick_sort([7]) == [7]
    assert quick_sort_random([]) == []
    assert quick_sort_random([3]) == [3]


def test_two_elements_both_orders():
    assert quick_sort([2, 1]) == [1, 2]
    assert quick_sort([1, 2]) == [1, 2]
    assert quick_sort_random([2, 1]) == [1, 2]
    assert quick_sort_random([1, 2]) == [1, 2]


def test_duplicates():
    assert quick_sort([5, 5, 3, 5, 1]) == [1, 3, 5, 5, 5]
    assert quick_sort([3, 3, 3, 3]) == [3, 3, 3, 3]
    assert quick_sort_random([5, 5, 3, 5, 1]) == [1, 3, 5, 5, 5]


def test_negatives_and_mixed():
    assert quick_sort([-2, 4, -9, 0, 7]) == [-9, -2, 0, 4, 7]
    assert quick_sort_random([-2, 4, -9, 0, 7]) == [-9, -2, 0, 4, 7]


def test_sorts_in_place():
    a = [9, 1, 5]
    out = quick_sort(a)
    assert out is a and a == [1, 5, 9]
    b = [9, 1, 5]
    out = quick_sort_random(b)
    assert out is b and b == [1, 5, 9]


def test_agrees_with_builtin_on_random_inputs():
    rng = random.Random(1234)
    for _ in range(200):
        n = rng.randint(0, 80)
        a = [rng.randint(-100, 100) for _ in range(n)]
        expect = sorted(a)
        assert quick_sort(a[:]) == expect
        assert quick_sort_random(a[:]) == expect


def test_both_variants_agree_on_same_input():
    for seed in range(50):
        a = [random.Random(seed).randint(0, 500) for _ in range(150)]
        assert quick_sort(a[:]) == quick_sort_random(a[:]) == sorted(a)


def test_degenerate_inputs_stay_on_a_shallow_stack():
    # The driver recurses into the smaller half and loops on the
    # larger one, so 10k sorted elements need only O(log n) frames
    # and must survive a 300-frame recursion limit.
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(300)
    try:
        assert quick_sort(list(range(10000))) == list(range(10000))
        assert quick_sort(list(range(10000, 0, -1))) == list(range(1, 10001))
        random.seed(4)
        assert quick_sort_random(list(range(10000))) == list(range(10000))
    finally:
        sys.setrecursionlimit(old)


def test_deterministic_worst_case_comparison_count():
    # Ascending input with a last-element pivot peels off one element
    # per partition; the exact counts below were measured once and are
    # stable because the pivot choice is deterministic.
    for n, expected in ((8, 49), (16, 165), (64, 2205)):
        s = {"comparisons": 0, "swaps": 0}
        quick_sort(list(range(1, n + 1)), stats=s)
        assert s["comparisons"] == expected, (n, s)


def test_randomized_escapes_the_worst_case():
    n = 4096
    s_det = {"comparisons": 0, "swaps": 0}
    quick_sort(list(range(1, n + 1)), stats=s_det)
    random.seed(20261109)
    s_rand = {"comparisons": 0, "swaps": 0}
    quick_sort_random(list(range(1, n + 1)), stats=s_rand)
    # deterministic: ~n^2/2 x ~1.75 ~= 8.4M; randomized: ~2 n ln n
    assert s_det["comparisons"] > 4_000_000
    assert s_rand["comparisons"] < 200_000
    assert s_det["comparisons"] > 100 * s_rand["comparisons"]


def test_randomized_tracks_2nlnn_on_random_input():
    n = 4096
    a = [random.Random(777).randint(0, 10**6) for _ in range(n)]
    expect = sorted(a)
    s = {"comparisons": 0, "swaps": 0}
    quick_sort_random(a, stats=s)
    assert a == expect
    theory = 2 * n * 8.317  # ln(4096) ~= 8.317
    assert 0.5 * theory < s["comparisons"] < 2 * theory


def test_degenerate_partitions_swap_only_linearly():
    # Peeling partitions compare O(n^2) but still swap O(n): each
    # unbalanced partition moves the pivot and crosses once.
    s = {"comparisons": 0, "swaps": 0}
    quick_sort(list(range(1, 2049)), stats=s)
    assert s["swaps"] < 2 * 2048
    assert s["comparisons"] > 100_000


def test_no_stats_means_no_bookkeeping():
    a = [3, 1, 2]
    assert quick_sort(a) == [1, 2, 3]
    assert quick_sort_random(a) == [1, 2, 3]


def test_equal_keys_end_up_sorted():
    a = [2, 1, 2, 1]
    quick_sort(a)
    assert a == [1, 1, 2, 2]
    quick_sort_random(a)
    assert a == [1, 1, 2, 2]


def main():
    tests = [name for name in globals() if name.startswith("test_")]
    failed = 0
    for name in sorted(tests):
        try:
            globals()[name]()
            print(f"PASS {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {name}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
